"""Rule-based financial signal engine.

Works generically on any metrics dict (demo or extracted from an uploaded PDF):
  1. period-over-period deltas and ratio checks
  2. multi-indicator fusion -> named signals with severity + explanation
  3. statement-vs-data mismatch detection (keyword based, verification wording)
  4. early-signal memory (consecutive-period streaks)
  5. risk chain construction
Every signal carries evidence references where available.

Safety: outputs are framed as "Potential Significance", never fraud claims,
never buy/sell or loan decisions.
"""

from demo_data import METRIC_LABELS

SEV_ORDER = {"low": 0, "medium": 1, "high": 2}


def _pct_change(old: float, new: float) -> float | None:
    if old in (None, 0):
        return None
    return round((new - old) / abs(old) * 100.0, 1)


def _dir(pct: float | None) -> str:
    if pct is None:
        return "flat"
    if pct > 2:
        return "up"
    if pct < -2:
        return "down"
    return "flat"


def compute_deltas(metrics: dict[str, dict]) -> dict:
    """For each metric: change across available consecutive periods."""
    periods = list(metrics.keys())
    out: dict[str, dict] = {}
    for key in metrics[periods[-1]].keys():
        series = [metrics[p].get(key) for p in periods]
        if any(v is None for v in series):
            continue
        first, last = series[0], series[-1]
        out[key] = {
            "series": series,
            "cum_pct": _pct_change(first, last),
            "qoq_pct": _pct_change(series[-2], series[-1]) if len(series) >= 2 else None,
            "direction": _dir(_pct_change(first, last)) if first is not None else "flat",
            "consecutive_same_dir": _consecutive(series),
        }
    return out


def _consecutive(series: list) -> int:
    """Length of trailing streak of same-direction changes (up/down)."""
    if len(series) < 2:
        return 0
    deltas = []
    for i in range(1, len(series)):
        d = _pct_change(series[i - 1], series[i])
        deltas.append(_dir(d))
    streak = 0
    last = None
    for d in reversed(deltas):
        if d == "flat":
            break
        if last is None or d == last:
            streak += 1
            last = d
        else:
            break
    return streak if streak >= 2 else 0


def _label(key: str) -> str:
    return METRIC_LABELS.get(key, key.replace("_", " ").title())


def build_signals(metrics: dict[str, dict], evidence_ids: dict[str, list[str]] | None = None) -> list[dict]:
    """Fusion rules -> list of signals. evidence_ids maps metric-key -> [EV ids]."""
    d = compute_deltas(metrics)
    periods = list(metrics.keys())
    latest = metrics[periods[-1]]
    ev = evidence_ids or {}
    signals: list[dict] = []

    def ev_for(keys: list[str]) -> list[str]:
        ids: list[str] = []
        for k in keys:
            ids.extend(ev.get(k, []))
        return list(dict.fromkeys(ids))

    # --- SIG: Financial Pressure (the flagship fusion rule) -------------
    debt_up = d.get("total_debt", {}).get("cum_pct") or 0
    fin_up = d.get("finance_cost", {}).get("cum_pct") or 0
    ocf_down = d.get("op_cashflow", {}).get("cum_pct") or 0
    margin_down = d.get("ebitda_margin", {}).get("cum_pct") or 0
    rev_dir = d.get("revenue", {}).get("direction")
    if debt_up >= 15 and fin_up >= 15 and ocf_down <= -15 and margin_down <= -3:
        inputs = [
            {"label": "Revenue", "direction": rev_dir, "value": f"{d.get('revenue', {}).get('cum_pct', 0):+}%" if d.get("revenue", {}).get("cum_pct") is not None else "n/a"},
            {"label": "Total Debt", "direction": "up", "value": f"+{debt_up}%"},
            {"label": "Finance Cost", "direction": "up", "value": f"+{fin_up}%"},
            {"label": "Operating Cash Flow", "direction": "down", "value": f"{ocf_down}%"},
            {"label": "EBITDA Margin", "direction": "down", "value": f"{margin_down}%"},
        ]
        sev = "high" if (debt_up >= 30 and ocf_down <= -30) else "medium"
        signals.append({
            "id": "SIG-01", "title": "Financial Pressure Signal", "category": "Solvency & Cash Flow Fusion",
            "severity": sev, "status": "Active",
            "logic": "Revenue growth continuing while debt, finance cost, operating cash flow and margin deteriorate together — a multi-indicator financial pressure pattern.",
            "explanation": (
                f"Since {periods[0]}, total debt is up {debt_up}% and finance cost up {fin_up}%, while operating cash "
                f"flow fell {abs(ocf_down)}% and EBITDA margin compressed {abs(margin_down)}%. Growth is being funded "
                "by borrowings rather than internal accruals, which raises refinancing and coverage risk if the "
                "pattern persists. This is a monitoring signal, not a conclusion about the company's solvency."),
            "inputs": inputs,
            "evidence_ids": ev_for(["total_debt", "finance_cost", "op_cashflow", "ebitda_margin", "revenue"]),
        })

    # --- SIG: Liquidity Strain ------------------------------------------
    cash_down = d.get("cash", {}).get("cum_pct") or 0
    cr_series = d.get("current_ratio", {}).get("series") or []
    std_up = d.get("short_term_debt", {}).get("cum_pct") or 0
    if cash_down <= -25 or (cr_series and cr_series[-1] < 1.2):
        signals.append({
            "id": "SIG-02", "title": "Liquidity Strain Signal", "category": "Liquidity",
            "severity": "high" if cash_down <= -35 else "medium", "status": "Active",
            "logic": "Cash balance decline + current-ratio deterioration + short-term debt build-up.",
            "explanation": (
                f"Cash is down {abs(cash_down)}% since {periods[0]}"
                + (f", current ratio has slipped from {cr_series[0]:.2f} to {cr_series[-1]:.2f}" if len(cr_series) >= 2 else "")
                + (f", and short-term debt is up {std_up}%." if std_up else ".")
                + " Liquidity buffers are thinning while short-term obligations rise — active monitoring recommended."
            ),
            "inputs": [
                {"label": "Cash & Equivalents", "direction": "down", "value": f"{cash_down}%"},
                {"label": "Current Ratio", "direction": "down", "value": f"{cr_series[0]:.2f} → {cr_series[-1]:.2f}" if len(cr_series) >= 2 else "n/a"},
                {"label": "Short-term Debt", "direction": "up", "value": f"+{std_up}%"},
            ],
            "evidence_ids": ev_for(["cash", "current_ratio", "short_term_debt", "current_liabilities"]),
        })

    # --- SIG: Margin Erosion --------------------------------------------
    streak_m = d.get("ebitda_margin", {}).get("consecutive_same_dir") or 0
    m_series = d.get("ebitda_margin", {}).get("series") or []
    if margin_down <= -2 and streak_m >= 2:
        signals.append({
            "id": "SIG-03", "title": "Margin Erosion", "category": "Profitability",
            "severity": "high" if margin_down <= -15 else "medium", "status": "Active",
            "logic": f"EBITDA margin declined in {streak_m} consecutive period-over-period changes.",
            "explanation": (
                f"EBITDA margin moved {' → '.join(str(v) + '%' for v in m_series)}. "
                + (f"Raw material cost share rose to {latest.get('raw_material_pct')}% of sales, the primary driver."
                   if latest.get("raw_material_pct") else
                   "Cost pressures are outpacing pricing actions.")),
            "inputs": [{"label": "EBITDA Margin", "direction": "down", "value": f"{margin_down}%"},
                       {"label": "Raw Material % of Sales", "direction": "up",
                        "value": f"{d.get('raw_material_pct', {}).get('series', [None])[0]}% → {latest.get('raw_material_pct')}%"}],
            "evidence_ids": ev_for(["ebitda_margin", "raw_material_pct", "gross_margin"]),
        })

    # --- SIG: Working Capital Stress ------------------------------------
    rd = d.get("receivable_days", {}); inv = d.get("inventory_days", {})
    if (rd.get("cum_pct") or 0) >= 8 or (inv.get("cum_pct") or 0) >= 8:
        signals.append({
            "id": "SIG-04", "title": "Working Capital Stress", "category": "Working Capital",
            "severity": "medium", "status": "Active",
            "logic": "Receivable / inventory days rising faster than revenue growth.",
            "explanation": (
                f"Receivable days rose {rd.get('series', ['n/a'])[0]} → {rd.get('series', ['n/a'])[-1]} days and "
                f"inventory days {inv.get('series', ['n/a'])[0]} → {inv.get('series', ['n/a'])[-1]} days. Receivables "
                f"{'+' if (d.get('receivables', {}).get('cum_pct') or 0) > 0 else ''}{d.get('receivables', {}).get('cum_pct', 0)}% "
                f"vs revenue {d.get('revenue', {}).get('cum_pct', 0):+}%, indicating cash being locked in the operating cycle."),
            "inputs": [
                {"label": "Receivable Days", "direction": "up", "value": f"{rd.get('series', ['n/a'])[0]} → {rd.get('series', ['n/a'])[-1]}"},
                {"label": "Inventory Days", "direction": "up", "value": f"{inv.get('series', ['n/a'])[0]} → {inv.get('series', ['n/a'])[-1]}"},
                {"label": "Receivables", "direction": "up", "value": f"+{d.get('receivables', {}).get('cum_pct', 0)}%"},
            ],
            "evidence_ids": ev_for(["receivable_days", "inventory_days", "receivables", "inventory"]),
        })

    # --- SIG: Coverage Compression ---------------------------------------
    ic = d.get("interest_coverage", {})
    if ic.get("series") and ic["series"][-1] and ic["series"][-1] < 6.5 and (ic.get("cum_pct") or 0) <= -15:
        signals.append({
            "id": "SIG-05", "title": "Coverage Compression", "category": "Debt Service",
            "severity": "medium" if ic["series"][-1] >= 4.5 else "high", "status": "Active",
            "logic": "Interest coverage (EBITDA / finance cost) falling toward credit-review threshold.",
            "explanation": (
                f"Interest coverage declined from {ic['series'][0]}x to {ic['series'][-1]}x as finance costs rose "
                f"{d.get('finance_cost', {}).get('cum_pct', 0):+}% while EBITDA fell. Coverage remains serviceable "
                "but the trajectory warrants covenant and refinancing monitoring."),
            "inputs": [{"label": "Interest Coverage", "direction": "down", "value": f"{ic['series'][0]}x → {ic['series'][-1]}x"},
                       {"label": "Finance Cost", "direction": "up", "value": f"+{d.get('finance_cost', {}).get('cum_pct', 0)}%"}],
            "evidence_ids": ev_for(["interest_coverage", "finance_cost"]),
        })

    # --- SIG: Capex–Funding Gap ------------------------------------------
    cap = d.get("capex", {}); ocf = d.get("op_cashflow", {})
    if cap.get("series") and ocf.get("series") and cap["series"][-1] and cap["series"][-1] > ocf["series"][-1] * 2:
        signals.append({
            "id": "SIG-06", "title": "Capex–Funding Gap", "category": "Investment Funding",
            "severity": "medium", "status": "Active",
            "logic": "Capital expenditure far exceeds operating cash generation; gap funded by borrowings.",
            "explanation": (
                f"Q-to-date capex of ₹{cap['series'][-1]} Cr is covered only {round(ocf['series'][-1] / cap['series'][-1] * 100)}% "
                f"by operating cash flow (₹{ocf['series'][-1]} Cr). The balance is debt-funded, consistent with the "
                "borrowings build-up observed on the balance sheet."),
            "inputs": [{"label": "Capex", "direction": "up", "value": f"₹{cap['series'][-1]} Cr"},
                       {"label": "Operating Cash Flow", "direction": "down", "value": f"₹{ocf['series'][-1]} Cr"},
                       {"label": "Financing Cash Flow", "direction": "up", "value": f"₹{latest.get('financing_cashflow')} Cr"}],
            "evidence_ids": ev_for(["capex", "op_cashflow", "financing_cashflow"]),
        })

    # --- SIG: Early-signal memory streaks ---------------------------------
    for key, title, cat in [("total_debt", "Persistent Debt Build-up", "Early Signal Memory"),
                            ("op_cashflow", "Persistent Cash Flow Decline", "Early Signal Memory"),
                            ("ebitda_margin", "Persistent Margin Decline", "Early Signal Memory")]:
        s = d.get(key, {})
        if s.get("consecutive_same_dir", 0) >= 2 and s.get("direction") in ("up", "down"):
            streak = s["consecutive_same_dir"]
            bad = (key in ("op_cashflow", "ebitda_margin") and s["direction"] == "down") or \
                  (key == "total_debt" and s["direction"] == "up")
            signals.append({
                "id": f"SIG-{len(signals) + 1:02d}", "title": title, "category": cat,
                "severity": "high" if (bad and streak >= 3) else "medium", "status": "Memory",
                "logic": f"{_label(key)} moved in the same adverse direction for {streak} consecutive period-over-period changes.",
                "explanation": (
                    f"{_label(key)}: {' → '.join(str(v) for v in s['series'])} "
                    f"({'₹ Cr' if key in ('total_debt', 'op_cashflow') else '%'}). "
                    f"{streak} consecutive periods of {s['direction']} movement — persistent trend flagged by early-signal memory."),
                "inputs": [{"label": _label(key), "direction": s["direction"],
                            "value": " → ".join(str(v) for v in s["series"])}],
                "evidence_ids": ev_for([key]),
            })

    signals.sort(key=lambda s: (-SEV_ORDER.get(s["severity"], 0), s["id"]))
    return signals


MISMATCH_VERB = "Potential statement–data mismatch requiring analyst verification."


def build_mismatches(statements: list[dict], metrics: dict[str, dict], evidence_lookup: dict) -> list[dict]:
    """statements: [{quote, page, section, evidence_id, period}]. Generic keyword rules."""
    d = compute_deltas(metrics)
    out: list[dict] = []

    def claim(q: str, *kws: str) -> bool:
        ql = q.lower()
        return all(k in ql for k in kws)

    cash = d.get("cash", {})
    cr = d.get("current_ratio", {}).get("series") or []
    std = d.get("short_term_debt", {})
    cl = d.get("current_liabilities", {})

    for st in statements:
        q = st["quote"]
        data_points: list[dict] = []
        # liquidity claims
        if claim(q, "liquidity") or claim(q, "cash buffer"):
            if cash.get("direction") == "down":
                data_points.append({"label": "Cash & Equivalents", "detail":
                    f"{' → '.join(str(v) for v in cash['series'])} ₹ Cr ({cash['cum_pct']}%)"})
            if cr and cr[-1] < 1.3:
                data_points.append({"label": "Current Ratio", "detail": f"{cr[0]:.2f} → {cr[-1]:.2f}"})
            if std.get("direction") == "up":
                data_points.append({"label": "Short-term Debt", "detail":
                    f"{' → '.join(str(v) for v in std['series'])} ₹ Cr (+{std['cum_pct']}%)"})
            if cl.get("direction") == "up":
                data_points.append({"label": "Current Liabilities", "detail":
                    f"{' → '.join(str(v) for v in cl['series'])} ₹ Cr (+{cl['cum_pct']}%)"})
            if len(data_points) >= 2:
                out.append({
                    "id": f"MM-{len(out) + 1:02d}",
                    "statement": q, "statement_source": st.get("evidence_id"),
                    "page": st.get("page"), "section": st.get("section"), "period": st.get("period"),
                    "data_points": data_points,
                    "verdict": MISMATCH_VERB,
                    "disclaimer": "Analytical flag only — this is not, and must not be read as, an assertion of fraud or misconduct.",
                    "verification_steps": [
                        "Obtain the quarterly cash-flow bridge and bank confirmation of balances.",
                        "Request undrawn sanctioned limits and ageing schedule of receivables.",
                        "Compare the claim with the liquidity section of the next quarterly report.",
                    ],
                })
        # margin recovery guidance
        if claim(q, "margin") and ("recover" in q.lower() or "recovery" in q.lower() or "confident" in q.lower()):
            m = d.get("ebitda_margin", {})
            if m.get("direction") == "down":
                out.append({
                    "id": f"MM-{len(out) + 1:02d}",
                    "statement": q, "statement_source": st.get("evidence_id"),
                    "page": st.get("page"), "section": st.get("section"), "period": st.get("period"),
                    "data_points": [
                        {"label": "EBITDA Margin", "detail": f"{' → '.join(str(v) + '%' for v in m['series'])} ({m['cum_pct']}%)"},
                        {"label": "Raw Material % of Sales", "detail":
                            f"{' → '.join(str(v) + '%' for v in (d.get('raw_material_pct', {}).get('series') or []))} (still rising)"}
                    ],
                    "verdict": MISMATCH_VERB,
                    "disclaimer": "Guidance-vs-outcome gap flagged for verification; timing differences may be legitimate.",
                    "verification_steps": [
                        "Compare guidance with the next two quarters' reported margins.",
                        "Request management's sensitivity analysis on input costs.",
                        "Check whether pricing actions or hedging programs are in place.",
                    ],
                })
        # working capital discipline claims
        if claim(q, "working capital") and ("improve" in q.lower() or "improving" in q.lower() or "discipline" in q.lower()):
            rd = d.get("receivable_days", {}); inv = d.get("inventory_days", {})
            if rd.get("direction") == "up" or inv.get("direction") == "up":
                out.append({
                    "id": f"MM-{len(out) + 1:02d}",
                    "statement": q, "statement_source": st.get("evidence_id"),
                    "page": st.get("page"), "section": st.get("section"), "period": st.get("period"),
                    "data_points": [
                        {"label": "Receivable Days", "detail": f"{' → '.join(str(v) for v in rd.get('series', []))} days"},
                        {"label": "Inventory Days", "detail": f"{' → '.join(str(v) for v in inv.get('series', []))} days"},
                    ],
                    "verdict": MISMATCH_VERB,
                    "disclaimer": "Analytical flag only — not an assertion of wrongdoing.",
                    "verification_steps": [
                        "Request receivables ageing and inventory breakdown (raw vs finished goods).",
                        "Check for any factoring / channel-stuffing indicators in the notes.",
                    ],
                })

    return out


RISK_CHAIN_TEMPLATE = [
    {"id": "RC-1", "label": "Input Cost ↑", "metric": "raw_material_pct", "severity": "medium",
     "detail_tpl": "Raw material cost at {first}% → {last}% of revenue."},
    {"id": "RC-2", "label": "Gross Margin ↓", "metric": "gross_margin", "severity": "medium",
     "detail_tpl": "Gross margin compressed {first}% → {last}%."},
    {"id": "RC-3", "label": "EBITDA & Margin ↓", "metric": "ebitda_margin", "severity": "high",
     "detail_tpl": "EBITDA margin {first}% → {last}% across the periods."},
    {"id": "RC-4", "label": "Operating Cash Flow ↓", "metric": "op_cashflow", "severity": "high",
     "detail_tpl": "Operating cash flow ₹{first} Cr → ₹{last} Cr, while capex rose to ₹{capex} Cr."},
    {"id": "RC-5", "label": "Funding Gap", "metric": "capex", "severity": "high",
     "detail_tpl": "Internal accruals cover only {cover}% of capex; balance funded externally."},
    {"id": "RC-6", "label": "Borrowings ↑", "metric": "total_debt", "severity": "high",
     "detail_tpl": "Total debt ₹{first} Cr → ₹{last} Cr (+{pct}%)."},
    {"id": "RC-7", "label": "Finance Cost ↑", "metric": "finance_cost", "severity": "medium",
     "detail_tpl": "Finance cost ₹{first} Cr → ₹{last} Cr (+{pct}%)."},
    {"id": "RC-8", "label": "Coverage & Profit ↓", "metric": "interest_coverage", "severity": "high",
     "detail_tpl": "Interest coverage {first}x → {last}x; net profit declined alongside."},
    {"id": "RC-9", "label": "Potential Financing Pressure", "metric": None, "severity": "high",
     "detail_tpl": "If the chain persists: refinancing risk, covenant headroom erosion and elevated working-capital funding needs. Monitoring signal — not a rating action."},
]


def build_risk_chain(metrics: dict[str, dict]) -> list[dict]:
    periods = list(metrics.keys())
    first_p, last = metrics[periods[0]], metrics[periods[-1]]
    nodes: list[dict] = []
    for tpl in RISK_CHAIN_TEMPLATE:
        node = dict(tpl)
        m = tpl["metric"]
        fill = {"first": first_p.get(m), "last": last.get(m), "capex": last.get("capex")}
        if m and first_p.get(m) and last.get(m):
            fill["pct"] = abs(_pct_change(first_p[m], last[m]) or 0)
        if tpl["id"] == "RC-5" and last.get("capex") and last.get("op_cashflow"):
            fill["cover"] = round(last["op_cashflow"] / last["capex"] * 100)
        node["detail"] = tpl["detail_tpl"].format(**{**{k: "n/a" for k in ("first", "last", "capex", "pct", "cover")}, **{k: v for k, v in fill.items() if v is not None}})
        nodes.append(node)
    return nodes


def build_trend_series(metrics: dict[str, dict]) -> list[dict]:
    """Recharts-friendly rows per period."""
    rows = []
    for p, m in metrics.items():
        rows.append({
            "period": p, "revenue": m.get("revenue"), "net_profit": m.get("net_profit"),
            "ebitda": m.get("ebitda"), "ebitda_margin": m.get("ebitda_margin"),
            "total_debt": m.get("total_debt"), "op_cashflow": m.get("op_cashflow"),
            "finance_cost": m.get("finance_cost"), "cash": m.get("cash"),
            "current_ratio": m.get("current_ratio"), "interest_coverage": m.get("interest_coverage"),
            "net_margin": m.get("net_margin"), "capex": m.get("capex"),
        })
    return rows


def build_memory(metrics: dict[str, dict]) -> list[dict]:
    d = compute_deltas(metrics)
    out = []
    for key in ("total_debt", "op_cashflow", "ebitda_margin", "finance_cost", "cash", "revenue"):
        s = d.get(key, {})
        if not s.get("series"):
            continue
        streak = s.get("consecutive_same_dir", 0)
        adverse = (key in ("op_cashflow", "ebitda_margin", "cash") and s.get("direction") == "down") or \
                  (key in ("total_debt", "finance_cost") and s.get("direction") == "up")
        out.append({
            "key": key, "label": _label(key), "series": s["series"],
            "unit": "₹ Cr" if key in ("total_debt", "op_cashflow", "cash", "finance_cost") else "%",
            "cum_pct": s.get("cum_pct"), "direction": s.get("direction"),
            "streak": streak, "adverse": adverse,
            "message": (
                f"{_label(key)} {'increased' if s.get('direction') == 'up' else 'decreased'} across "
                f"{streak + 1} consecutive periods." if streak >= 2 else
                f"{_label(key)} changed over the period ({s.get('cum_pct')}%)."),
        })
    return out
