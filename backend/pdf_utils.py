"""PDF ingestion: page text (PyMuPDF), tables (pdfplumber), heuristic metric harvest."""
import re

import fitz  # PyMuPDF

from config import MAX_PAGES

PDF_MAGIC = b"%PDF-"


def is_valid_pdf(filename: str, head: bytes) -> tuple[bool, str]:
    if not filename.lower().endswith(".pdf"):
        return False, "Only PDF files are accepted."
    if len(head) < 1024 and PDF_MAGIC not in head:
        return False, "File does not appear to be a valid PDF."
    if PDF_MAGIC not in head[:1024]:
        return False, "File does not appear to be a valid PDF."
    return True, "ok"


def extract_pages(filepath: str) -> list[dict]:
    """Return [{'page': n, 'text': str}, ...] using PyMuPDF; tables via pdfplumber."""
    doc = fitz.open(filepath)
    if doc.page_count > MAX_PAGES:
        doc.close()
        raise ValueError(f"PDF has more than {MAX_PAGES} pages.")
    pages = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        pages.append({"page": i, "text": text})
    doc.close()

    # Best-effort table extraction with pdfplumber for financial pages.
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            for i, page in enumerate(pdf.pages[: min(len(pages), 12)]):
                tables = page.extract_tables()
                if tables:
                    flat = []
                    for tb in tables[:3]:
                        for row in tb:
                            cells = [c.strip() for c in row if c and c.strip()]
                            if cells:
                                flat.append(" | ".join(cells))
                    if flat:
                        pages[i]["tables"] = flat[:60]
    except Exception:
        pass
    return pages


PERIOD_PATTERNS = [
    (r"quarter ended\s+June 30,?\s+2025", "Q1 FY26"),
    (r"quarter ended\s+September 30,?\s+2025", "Q2 FY26"),
    (r"quarter ended\s+December 31,?\s+2025", "Q3 FY26"),
    (r"quarter ended\s+March 31,?\s+2026", "Q4 FY26"),
]

COMPANY_PATTERNS = [r"XYZ Manufacturing Ltd\.?", r"XYZ Manufacturing Limited"]

# label regexes: key -> patterns to find "<label> ... ₹<number> (crore|cr)"
NUM = r"(?:₹|Rs\.?|INR)\s*([0-9][0-9,]*(?:\.[0-9]+)?)"
METRIC_PATTERNS: dict[str, list[str]] = {
    "revenue": [r"revenue from operations[^.₹]{0,80}" + NUM, r"total income[^.₹]{0,80}" + NUM,
                r"revenue[^.₹]{0,60}" + NUM],
    "net_profit": [r"net profit[^.₹]{0,80}" + NUM, r"profit after tax[^.₹]{0,80}" + NUM,
                   r"pat[^.₹]{0,60}" + NUM],
    "ebitda": [r"ebitda[^.₹]{0,80}" + NUM],
    "total_debt": [r"total borrowings[^.₹]{0,80}" + NUM, r"total debt[^.₹]{0,80}" + NUM,
                   r"borrowings \([^)]*\)[^.₹]{0,80}" + NUM],
    "short_term_debt": [r"short-term borrowings[^.₹]{0,80}" + NUM],
    "finance_cost": [r"finance cost[^.₹]{0,80}" + NUM, r"finance costs[^.₹]{0,80}" + NUM,
                     r"interest expense[^.₹]{0,80}" + NUM],
    "op_cashflow": [r"operating activities[^.₹]{0,120}" + NUM, r"cash generated from operations[^.₹]{0,80}" + NUM],
    "cash": [r"cash and cash equivalents[^.₹]{0,80}" + NUM, r"cash and bank[^.₹]{0,80}" + NUM],
    "capex": [r"capital expenditure[^.₹]{0,80}" + NUM],
    "receivables": [r"trade receivables[^.₹]{0,80}" + NUM],
    "inventory": [r"inventor(?:y|ies)[^.₹]{0,80}" + NUM],
    "current_liabilities": [r"current liabilities[^.₹]{0,80}" + NUM],
    "current_assets": [r"current assets[^.₹]{0,80}" + NUM],
    "depreciation": [r"depreciation[^.₹]{0,80}" + NUM],
    "ebitda_margin": [r"ebitda margin (?:of |at |declined to |stood at |was )?([0-9]+(?:\.[0-9]+)?)\s*%"],
    "raw_material_pct": [r"raw material costs?,? which rose to ([0-9]+(?:\.[0-9]+)?)\s*%",
                         r"raw material (?:cost|costs)[^.%]{0,60}?([0-9]+(?:\.[0-9]+)?)\s*%\s*(?:of revenue|of sales)"],
    "interest_coverage": [r"interest coverage (?:of |at )?([0-9]+(?:\.[0-9]+)?)\s*x"],
    "current_ratio": [r"current ratio (?:of |at )?([0-9]+(?:\.[0-9]+)?)"],
}


def _to_number(s: str) -> float:
    return float(s.replace(",", ""))


def detect_company_and_period(pages: list[dict]) -> tuple[str | None, str | None]:
    full = "\n".join(p["text"] for p in pages)
    company = None
    period = None
    for pat in COMPANY_PATTERNS:
        if re.search(pat, full, re.IGNORECASE):
            company = "XYZ Manufacturing Ltd."
            break
    for pat, label in PERIOD_PATTERNS:
        if re.search(pat, full, re.IGNORECASE):
            period = label
            break
    return company, period


def harvest_metrics(pages: list[dict]) -> dict:
    """Regex-based metric harvest for unknown PDFs (demo-mode heuristic).

    Returns {key: {"value": float, "page": int, "quote": str}} so every
    harvested number carries its own evidence (page + matched sentence).
    """
    full = "\n".join(p["text"] for p in pages)
    found: dict[str, dict] = {}
    for key, pats in METRIC_PATTERNS.items():
        for pat in pats:
            hit = None
            # per-page first, so we know the source page
            for p in pages:
                m = re.search(pat, p.get("text", ""), re.IGNORECASE | re.DOTALL)
                if m:
                    hit = (p["page"], m)
                    break
            if hit is None:
                m = re.search(pat, full, re.IGNORECASE | re.DOTALL)
                if m:
                    hit = (0, m)  # 0 = found across a page boundary
            if hit:
                page_no, m = hit
                try:
                    found[key] = {
                        "value": _to_number(m.group(1)),
                        "page": page_no,
                        "quote": _sentence_around(full, m.start()),
                    }
                    break
                except ValueError:
                    continue
    return found


def _sentence_around(text: str, pos: int, max_len: int = 260) -> str:
    start = max(0, text.rfind(".", 0, pos) + 1)
    end = text.find(".", pos + 10)
    end = end + 1 if end != -1 else min(len(text), pos + max_len)
    s = text[start:end].strip()
    return (s[:max_len] + "…") if len(s) > max_len else s


def search_chunks(pages: list[dict], query: str, max_chunks: int = 6) -> list[dict]:
    """Keyword-scored retrieval over page text (demo-mode grounding)."""
    qwords = [w for w in re.findall(r"[a-zA-Z₹0-9]{3,}", query.lower()) if w not in
              {"the", "and", "for", "was", "were", "what", "why", "how", "did", "does", "from", "with", "that", "this"}]
    scored = []
    for p in pages:
        text = p.get("text", "")
        tl = text.lower()
        score = sum(tl.count(w) for w in qwords)
        if score > 0:
            scored.append({"page": p["page"], "score": score, "text": text})
    scored.sort(key=lambda x: -x["score"])
    return scored[:max_chunks]
