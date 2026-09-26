"""FinSight X — AI Financial Intelligence & Early-Warning Platform (backend API).

Run:  python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
All routes live under /api/fs/* and are reached through the gateway with
?XTransformPort=8000 from the Next.js frontend.
"""
import json
import re
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import analysis as A
import database as DB
import demo_data as D
import pdf_utils
from config import AI_ENABLED, MAX_UPLOAD_MB, SAMPLE_DIR, UPLOAD_DIR
from llm import chat, summarize_report
from sample_reports import generate_all, extract_pages_cache
from security import ROLE_LABELS, can, issue_token, verify_password, verify_token

app = FastAPI(title="FinSight X API", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

EV_BY_METRIC = {
    "revenue": ["EV-001"], "net_profit": ["EV-014"], "ebitda": ["EV-006"],
    "ebitda_margin": ["EV-006"], "gross_margin": ["EV-006"], "raw_material_pct": ["EV-006"],
    "total_debt": ["EV-002"], "short_term_debt": ["EV-002"], "finance_cost": ["EV-009"],
    "interest_coverage": ["EV-009"], "op_cashflow": ["EV-003"], "cash": ["EV-004"],
    "current_liabilities": ["EV-005"], "current_ratio": ["EV-005"], "receivables": ["EV-007"],
    "inventory": ["EV-007"], "receivable_days": ["EV-007"], "inventory_days": ["EV-007"],
    "capex": ["EV-008"], "financing_cashflow": ["EV-002"], "investing_cashflow": ["EV-015"],
    "debt_to_equity": ["EV-002"], "net_debt": ["EV-002", "EV-004"],
}

PERIOD_DOC = {"Q1 FY26": 1, "Q2 FY26": 2, "Q3 FY26": 3}


@app.on_event("startup")
def startup() -> None:
    DB.seed_users()
    if not list(SAMPLE_DIR.glob("*.pdf")):
        generate_all(SAMPLE_DIR)
    if not list(SAMPLE_DIR.glob("*_pages.json")):
        extract_pages_cache(SAMPLE_DIR)


# ---------------------------------------------------------------- auth utils
def get_user(request: Request) -> dict:
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(401, "Missing bearer token")
    data = verify_token(auth.split(" ", 1)[1].strip())
    if not data:
        raise HTTPException(401, "Invalid or expired token")
    return data


def require(permission: str):
    def dep(user: dict = Depends(get_user)) -> dict:
        if not can(user["role"], permission):
            label = ROLE_LABELS.get(user["role"], user["role"])
            raise HTTPException(403, f"Role '{label}' is not permitted to {permission.replace('_', ' ')}.")
        return user
    return dep


# ---------------------------------------------------------------- schemas
class LoginBody(BaseModel):
    email: str
    password: str


class AskBody(BaseModel):
    question: str
    report_id: int | None = None


# ---------------------------------------------------------------- helpers
def _demo_pages(period: str = "Q3 FY26") -> list[dict]:
    name = period.replace(" ", "_").lower() + "_pages.json"
    f = SAMPLE_DIR / name
    if not f.exists():
        generate_all(SAMPLE_DIR)
        extract_pages_cache(SAMPLE_DIR)
    return json.loads((SAMPLE_DIR / name).read_text())


def _demo_statements(period: str = "Q3 FY26") -> list[dict]:
    """Flatten curated statements into mismatch-ready dicts with evidence ids."""
    out = []
    ev_by_quote = {e["quote"]: e["id"] for e in D.EVIDENCE}
    for period_key, sts in D.MANAGEMENT_STATEMENTS.items():
        for st in sts:
            out.append({**st, "period": period_key, "evidence_id": ev_by_quote.get(st["quote"])})
    return out


def build_demo_package(period: str = "Q3 FY26") -> dict:
    metrics = {p: D.METRICS[p] for p in D.PERIOD_ORDER}
    # Mismatch detection runs against the CURRENT filing's statements (Q3).
    statements = [s for s in _demo_statements(period) if s["period"] == period]
    return {
        "kind": "demo",
        "company": D.COMPANY,
        "period_label": period,
        "periods": D.PERIOD_ORDER,
        "metrics": metrics,
        "metric_labels": D.METRIC_LABELS,
        "trend_series": A.build_trend_series(metrics),
        "exec_summary": D.EXEC_SUMMARY,
        "signals": A.build_signals(metrics, EV_BY_METRIC),
        "mismatches": A.build_mismatches(statements, metrics, None),
        "risk_chain": A.build_risk_chain(metrics),
        "memory": A.build_memory(metrics),
        "evidence": D.EVIDENCE,
        "management_statements": D.MANAGEMENT_STATEMENTS,
        "safety_note": D.SAFETY_NOTE,
        "ai_enabled": AI_ENABLED,
    }


def _template_exec_summary(company: str, metrics: dict, harvested: bool = False) -> dict:
    periods = list(metrics.keys())
    last_p, first_p = periods[-1], periods[0]
    m, f = metrics[last_p], metrics[first_p]

    def delta(k: str):
        try:
            if f.get(k) in (None, 0) or m.get(k) is None:
                return None
            return round((m[k] - f[k]) / abs(f[k]) * 100, 1)
        except Exception:
            return None

    if harvested or len(periods) == 1:
        figs = ", ".join(f"{D.METRIC_LABELS.get(k, k)} {v}" for k, v in list(m.items())[:8])
        return {
            "headline": "Single-period extraction completed in Demo Mode.",
            "paragraphs": [
                (f"{company} — automated Demo-Mode extraction from the uploaded document. The following key figures "
                 f"were located and parsed from the report text: {figs}."),
                ("Because only a single period could be parsed, trend signals require additional quarterly uploads. "
                 "Level-based checks were applied to the extracted figures (see Signals). Upload the previous "
                 "quarters' reports — or the XYZ Manufacturing samples — to unlock fusion signals, early-signal "
                 "memory and the risk chain."),
                ("All figures above are extracted from the uploaded document and remain subject to verification "
                 "against the audited financials."),
            ],
            "key_changes": [f"{D.METRIC_LABELS.get(k, k)}: {v}" for k, v in m.items()],
            "guidance": [], "risks_events": [],
        }

    rev, prof = delta("revenue"), delta("net_profit")
    debt, ocf, margin = delta("total_debt"), delta("op_cashflow"), delta("ebitda_margin")
    parts = [
        f"Revenue moved from ₹{f.get('revenue')} Cr to ₹{m.get('revenue')} Cr ({rev:+}%) over {first_p} → {last_p}." if rev is not None else "",
        f"Net profit moved from ₹{f.get('net_profit')} Cr to ₹{m.get('net_profit')} Cr ({prof:+}%)." if prof is not None else "",
        f"Total debt changed {debt:+}% and operating cash flow {ocf:+}%." if debt is not None and ocf is not None else "",
        f"EBITDA margin changed {margin:+} pts." if margin is not None else "",
    ]
    bits = []
    if rev is not None and rev > 0:
        bits.append("Revenue growth continues")
    if prof is not None and prof < 0:
        bits.append("profitability declined")
    if debt is not None and debt > 15:
        bits.append("leverage increased")
    return {
        "headline": (", ".join(bits) or "Period-over-period comparison completed") + " — Demo Mode analysis.",
        "paragraphs": [
            f"{company}: comparison across {', '.join(periods)}. " + " ".join(x for x in parts if x),
            ("Signals below are computed by the rule engine from the reported figures. Every driver is traceable "
             "to the Evidence panel. This analysis distinguishes Reported Fact from AI Analysis and Potential "
             "Significance; it is not investment advice, a rating action, or a loan decision."),
        ],
        "key_changes": [x for x in parts if x],
        "guidance": [], "risks_events": [],
    }


# ---------------------------------------------------------------- routes
@app.get("/api/fs/health")
def health():
    return {"status": "ok", "service": "FinSight X API", "version": "1.0.0",
            "ai_enabled": AI_ENABLED, "demo_mode": not AI_ENABLED}


@app.post("/api/fs/auth/login")
def login(body: LoginBody):
    row = DB.get_conn().execute("SELECT * FROM users WHERE lower(email)=lower(?)", (body.email.strip(),)).fetchone()
    if row is None or not verify_password(body.password, row["password_hash"]):
        DB.audit(body.email, "?", "login_failed", "Invalid credentials")
        raise HTTPException(401, "Invalid email or password")
    token = issue_token(row["email"], row["name"], row["role"])
    DB.audit(row["email"], row["role"], "login_success", f"Role: {row['role']}")
    return {"token": token, "user": {"email": row["email"], "name": row["name"], "role": row["role"],
                                     "role_label": ROLE_LABELS[row["role"]]},
            "demo_mode": not AI_ENABLED}


@app.get("/api/fs/auth/me")
def me(user: dict = Depends(get_user)):
    return {"user": {**user, "role_label": ROLE_LABELS.get(user["role"], user["role"])}, "demo_mode": not AI_ENABLED}


@app.get("/api/fs/demo/dataset")
def demo_dataset(request: Request, period: str = "Q3 FY26"):
    user = get_user(request)
    pkg = build_demo_package(period if period in D.PERIOD_ORDER else "Q3 FY26")
    DB.audit(user["email"], user["role"], "view_demo_dataset", f"period={pkg['period_label']}")
    return pkg


@app.get("/api/fs/demo/report/{period}")
def demo_report(period: str, request: Request):
    user = get_user(request)
    fname = f"XYZ_Manufacturing_{period.replace(' ', '_')}_Report.pdf"
    path = SAMPLE_DIR / fname
    if not path.exists():
        generate_all(SAMPLE_DIR)
    DB.audit(user["email"], user["role"], "download_sample_report", fname)
    return FileResponse(path, media_type="application/pdf", filename=fname)


@app.post("/api/fs/reports/upload")
async def upload_report(file: UploadFile = File(...), user: dict = Depends(require("upload"))):
    filename = file.filename or "report.pdf"
    head = await file.read(1024)
    ok, msg = pdf_utils.is_valid_pdf(filename, head)
    if not ok:
        DB.audit(user["email"], user["role"], "upload_rejected", f"{filename}: {msg}")
        raise HTTPException(400, msg)
    rest = await file.read()
    if len(head) + len(rest) > MAX_UPLOAD_MB * 1024 * 1024:
        DB.audit(user["email"], user["role"], "upload_rejected", f"{filename}: exceeds {MAX_UPLOAD_MB} MB")
        raise HTTPException(400, f"File exceeds {MAX_UPLOAD_MB} MB limit.")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    tmp = UPLOAD_DIR / f"{uuid.uuid4().hex}.pdf"
    tmp.write_bytes(head + rest)

    try:
        pages = pdf_utils.extract_pages(str(tmp))
    except Exception as e:
        tmp.unlink(missing_ok=True)
        raise HTTPException(400, f"Could not parse PDF: {e}")

    company, period = pdf_utils.detect_company_and_period(pages)
    full_text = "\n".join(p["text"] for p in pages)

    # ---- Case 1: known demo company & period -> curated dataset ------------
    if company and period in D.METRICS:
        statements = [s for s in _demo_statements(period) if s["period"] == period]
        # Evidence library keeps prior filings on file; the current filing is flagged.
        evidence = [dict(e, current=(e["document"].endswith("Q3 FY26 Quarterly Report") and period == "Q3 FY26"))
                    for e in D.EVIDENCE]
        ev_map = _evidence_ids_for_metrics(list(EV_BY_METRIC.keys()))
        analysis = {
            "kind": "demo_company", "company": D.COMPANY, "period_label": period,
            "periods": D.PERIOD_ORDER, "metrics": D.METRICS,
            "metric_labels": D.METRIC_LABELS,
            "trend_series": A.build_trend_series(D.METRICS),
            "exec_summary": D.EXEC_SUMMARY if period == "Q3 FY26"
                            else _template_exec_summary(company, D.METRICS),
            "signals": A.build_signals(D.METRICS, ev_map),
            "mismatches": A.build_mismatches(statements, D.METRICS, None),
            "risk_chain": A.build_risk_chain(D.METRICS),
            "memory": A.build_memory(D.METRICS),
            "evidence": evidence,
            "management_statements": D.MANAGEMENT_STATEMENTS,
            "safety_note": D.SAFETY_NOTE, "ai_enabled": AI_ENABLED,
            "notice": f"Recognised as {company} ({period}). Prior quarters shown are from the platform's historical file.",
        }
        report_id = DB.save_report(filename, company, period, user["email"], len(pages),
                                   D.METRICS[period], analysis, pages, is_demo=True)
        DB.audit(user["email"], user["role"], "upload_ok", f"{filename} → {company} {period} (curated)")
        tmp.unlink(missing_ok=True)
        return {"report_id": report_id, "analysis": analysis, "extraction": {
            "company": company, "period": period, "mode": "curated-demo-dataset", "pages": len(pages)}}

    # ---- Case 2: unknown PDF -> heuristic harvest (+ optional LLM) ---------
    harvested = pdf_utils.harvest_metrics(pages)
    metrics_simplified = {k: v["value"] for k, v in harvested.items()}
    evidence_entries, ev_map = [], {}
    for k, v in harvested.items():
        eid = f"EX-{k.upper()}"
        evidence_entries.append({"id": eid, "document": filename, "page": v["page"] or None,
                                 "section": "Auto-located extract", "kind": "reported_fact",
                                 "quote": v["quote"], "tags": [k], "current": True})
        ev_map[k] = [eid]

    llm_summary = None
    if AI_ENABLED:
        llm_summary = await summarize_report(pages, metrics_simplified)

    signals = _level_signals(metrics_simplified, ev_map)
    exec_summary = llm_summary or _template_exec_summary(
        company or Path(filename).stem, {"Single period": metrics_simplified}, harvested=True)
    analysis = {
        "kind": "generic", "company": {
            "name": company or Path(filename).stem,
            "sector": "Unidentified — single-period extraction",
            "listings": "—",
            "profile": ("Profile unavailable: the uploaded document could not be matched to a known company. "
                        "Figures below were extracted heuristically and are subject to verification."),
            "currency": "as per report",
        },
        "period_label": period or "Unidentified period",
        "periods": ["Single period"], "metrics": {"Single period": metrics_simplified},
        "metric_labels": D.METRIC_LABELS,
        "trend_series": A.build_trend_series({"Single period": metrics_simplified}),
        "exec_summary": exec_summary,
        "signals": signals,
        "mismatches": _generic_mismatches(pages, metrics_simplified),
        "risk_chain": [], "memory": [],
        "evidence": evidence_entries,
        "management_statements": {},
        "safety_note": D.SAFETY_NOTE, "ai_enabled": AI_ENABLED, "partial": True,
        "notice": ("Demo-Mode heuristic extraction: figures were located via pattern matching and are subject to "
                   "verification. For the full curated experience, upload the XYZ Manufacturing sample reports "
                   "or configure an LLM API key in backend/.env."),
    }
    report_id = DB.save_report(filename, analysis["company"]["name"], analysis["period_label"], user["email"],
                               len(pages), metrics_simplified, analysis, pages, is_demo=False)
    DB.audit(user["email"], user["role"], "upload_ok",
             f"{filename} → heuristic extraction, {len(metrics_simplified)} metrics")
    return {"report_id": report_id, "analysis": analysis, "extraction": {
        "company": analysis["company"], "period": analysis["period_label"],
        "mode": "heuristic-demo" if not AI_ENABLED else "llm+heuristic", "pages": len(pages),
        "metrics_found": list(metrics_simplified.keys())}}


def _level_signals(m: dict, ev_map: dict) -> list[dict]:
    """Level-based checks when only one period is available."""
    out = []
    if m.get("current_ratio") and m["current_ratio"] < 1.2:
        out.append({"id": "SIG-L1", "title": "Low Current Ratio", "category": "Liquidity", "severity": "high",
                    "status": "Active", "logic": "Current ratio below 1.2.",
                    "explanation": f"Current ratio of {m['current_ratio']} indicates short-term liabilities exceed a comfortable coverage level.",
                    "inputs": [{"label": "Current Ratio", "direction": "down", "value": str(m["current_ratio"])}],
                    "evidence_ids": ev_map.get("current_ratio", [])})
    if m.get("interest_coverage") and m["interest_coverage"] < 6:
        out.append({"id": "SIG-L2", "title": "Thin Interest Coverage", "category": "Debt Service", "severity": "medium",
                    "status": "Active", "logic": "Interest coverage below 6x.",
                    "explanation": f"Interest coverage of {m['interest_coverage']}x warrants monitoring of debt-service capacity.",
                    "inputs": [{"label": "Interest Coverage", "direction": "down", "value": f"{m['interest_coverage']}x"}],
                    "evidence_ids": ev_map.get("interest_coverage", [])})
    if m.get("cash") and m.get("total_debt") and m["cash"] < m["total_debt"] * 0.15:
        out.append({"id": "SIG-L3", "title": "Modest Cash Buffer vs Debt", "category": "Liquidity", "severity": "medium",
                    "status": "Active", "logic": "Cash below 15% of total debt.",
                    "explanation": "Cash balances are modest relative to total borrowings; refinancing planning becomes relevant.",
                    "inputs": [{"label": "Cash / Total Debt", "direction": "down",
                                "value": f"{round(m['cash'] / m['total_debt'] * 100)}%"}],
                    "evidence_ids": ev_map.get("cash", []) + ev_map.get("total_debt", [])})
    if not out:
        out.append({"id": "SIG-L0", "title": "No Level-Based Alerts", "category": "Baseline", "severity": "low",
                    "status": "Info", "logic": "No single-period thresholds breached.",
                    "explanation": ("No thresholds breached on the extracted figures. Upload previous quarters to "
                                    "enable trend, fusion and memory signals."),
                    "inputs": [], "evidence_ids": []})
    return out


def _generic_mismatches(pages: list[dict], m: dict) -> list[dict]:
    """Keyword scan of management narrative vs extracted data for unknown PDFs."""
    text = "\n".join(p["text"] for p in pages)
    out = []
    checks = [
        (r"liquidity (?:remains|is) strong|comfortable cash", ["cash"], "liquidity"),
        (r"margin(?:s)? (?:will |to )?recover|confident of margin", ["ebitda_margin", "gross_margin"], "margin"),
        (r"working capital (?:discipline|management) (?:continues to )?improve", ["receivable_days", "inventory_days"], "working capital"),
    ]
    for pat, keys, topic in checks:
        hit = re.search(pat, text, re.IGNORECASE)
        datapoints = [{"label": D.METRIC_LABELS.get(k, k), "detail": str(m[k])} for k in keys if k in m]
        if hit and datapoints:
            page_no = next((p["page"] for p in pages if re.search(pat, p["text"], re.IGNORECASE)), None)
            s = text[max(0, hit.start() - 40): hit.end() + 120].strip()
            out.append({"id": f"MM-{len(out) + 1:02d}", "statement": s[:220], "statement_source": None,
                        "page": page_no, "section": "Narrative section", "period": None,
                        "data_points": datapoints, "verdict": A.MISMATCH_VERB,
                        "disclaimer": "Analytical flag only — not an assertion of wrongdoing.",
                        "verification_steps": ["Reconcile the statement with the underlying financial schedules.",
                                               "Compare with the next quarterly report's reported figures."]})
    return out


@app.get("/api/fs/reports")
def reports_list(request: Request):
    user = get_user(request)
    return {"reports": DB.list_reports()}


@app.get("/api/fs/reports/{report_id}")
def report_detail(report_id: int, request: Request):
    user = get_user(request)
    r = DB.get_report(report_id)
    if not r:
        raise HTTPException(404, "Report not found")
    DB.audit(user["email"], user["role"], "view_report", f"report #{report_id}")
    return r


@app.post("/api/fs/ask")
async def ask(body: AskBody, user: dict = Depends(get_user)):
    q = body.question.strip()
    if not q:
        raise HTTPException(400, "Empty question")

    pages = _demo_pages("Q3 FY26")
    doc_name = D.PERIOD_META["Q3 FY26"]["doc"]
    evidence_pool = D.EVIDENCE
    if body.report_id:
        r = DB.get_report(body.report_id)
        if r:
            pages = r["pages_text"]
            evidence_pool = r["analysis"].get("evidence", [])
            doc_name = r["filename"]

    answer, evidence_used, mode = None, [], "demo_kb"

    # ---- LLM path (only when configured) -----------------------------------
    if AI_ENABLED:
        chunks = pdf_utils.search_chunks(pages, q, max_chunks=6)
        context = "\n\n".join(f"[page {c['page']}]\n{c['text'][:1800]}" for c in chunks) or "(no excerpts found)"
        text = await chat([{"role": "user", "content": f"REPORT EXCERPTS:\n{context}\n\nQUESTION: {q}"}])
        if text:
            answer, mode = text, "llm"
            evidence_used = [{"id": f"p{c['page']}", "document": doc_name, "page": c["page"],
                              "section": "Retrieved excerpt", "kind": "reported_fact",
                              "quote": c["text"][:280]} for c in chunks[:4]]

    # ---- Demo knowledge bank -------------------------------------------------
    if answer is None:
        ql = q.lower()
        best, best_score = None, 0
        for qa in D.QA_BANK:
            score = sum(1 for p in qa["patterns"] if p in ql)
            if score > best_score:
                best, best_score = qa, score
        if best:
            answer, mode = best["answer"], "demo_kb"
            ev_by_id = {e["id"]: e for e in evidence_pool}
            evidence_used = [ev_by_id[i] for i in best["evidence_ids"] if i in ev_by_id]
        else:
            chunks = pdf_utils.search_chunks(pages, q, max_chunks=3)
            if chunks:
                answer = ("Based on the report text, the most relevant excerpts for your question are below. "
                          "In Demo Mode the question could not be mapped to a curated topic, so the platform is "
                          "answering with direct quotations from the document.")
                mode = "demo_retrieval"
                evidence_used = [{"id": f"p{c['page']}", "document": doc_name, "page": c["page"],
                                  "section": "Retrieved excerpt", "kind": "reported_fact",
                                  "quote": c["text"][:320]} for c in chunks]
            else:
                answer = ("I could not find report content relevant to that question. Try asking about profit, "
                          "debt, cash flow, margins, liquidity, capex, working capital, guidance or risks.")
                mode = "no_match"

    DB.audit(user["email"], user["role"], "ask_question", q[:200])
    return {"question": q, "answer": answer, "evidence": evidence_used, "mode": mode,
            "demo_mode": not AI_ENABLED, "safety_note": D.SAFETY_NOTE}


@app.get("/api/fs/audit")
def audit_list(user: dict = Depends(require("audit"))):
    return {"entries": DB.list_audit()}


@app.get("/api/fs/suggested-questions")
def suggested(user: dict = Depends(get_user)):
    return {"questions": [
        "Why did profit decline?",
        "What changed from Q2?",
        "Why did debt increase?",
        "What risks did management mention?",
        "Does the liquidity claim match the data?",
        "How are the margins trending?",
        "What is driving the cash flow decline?",
        "What guidance did management give?",
    ]}


def _evidence_ids_for_metrics(metric_keys: list[str]) -> dict:
    return {k: EV_BY_METRIC[k] for k in metric_keys if k in EV_BY_METRIC}
