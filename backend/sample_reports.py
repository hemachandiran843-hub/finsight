"""Generate the fictional XYZ Manufacturing Ltd. quarterly report PDFs (Q1/Q2/Q3 FY26).

These PDFs are the demo upload artefacts: every evidence quote used by the
platform appears verbatim (whitespace-normalised) inside the Q3 report, so the
Evidence panel is authentic. Generated with PyMuPDF; DejaVu fonts give ₹ support.
"""
import json
import re
from pathlib import Path

import fitz

import demo_data as D

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
BODY = ("dv", FONT_DIR + "DejaVuSans.ttf")
BOLD = ("dvb", FONT_DIR + "DejaVuSans-Bold.ttf")
MONO = ("dvm", FONT_DIR + "DejaVuSansMono.ttf")

W, H = 595, 842  # A4 points
MARGIN = 52
DISCLAIMER = ("FICTITIOUS SAMPLE REPORT prepared for the FinSight X prototype evaluation. "
              "XYZ Manufacturing Ltd. is not a real company and all figures are illustrative.")


def _fmt(v) -> str:
    if v is None:
        return "n/a"
    return f"{v:,.0f}" if abs(v) >= 10 else f"{v:,.1f}"


class Page:
    def __init__(self, doc: fitz.Document):
        self.page = doc.new_page(width=W, height=H)
        for name, path in (BODY, BOLD, MONO):
            self.page.insert_font(fontname=name, fontfile=path)
        self.y = MARGIN

    def text(self, s: str, size=9.5, bold=False, x=MARGIN, gap=4, color=(0.12, 0.15, 0.22)):
        rect = fitz.Rect(x, self.y, W - MARGIN, H - MARGIN)
        self.page.insert_textbox(rect, s, fontsize=size, fontname=BOLD[0] if bold else BODY[0],
                                 color=color, align=0, lineheight=1.45)
        n_lines = 0
        for para in s.split("\n"):
            n_lines += max(1, round(len(para) / ((W - 2 * MARGIN) / (size * 0.52))))
        self.y += n_lines * size * 1.5 + gap

    def heading(self, s: str, size=13):
        self.text(s, size=size, bold=True, gap=6, color=(0.04, 0.11, 0.22))

    def mono_table(self, rows: list[str], size=8.6):
        for r in rows:
            self.page.insert_text((MARGIN, self.y), r, fontsize=size, fontname=MONO[0], color=(0.1, 0.13, 0.2))
            self.y += size * 1.6
        self.y += 8

    def rule(self):
        self.page.draw_line(fitz.Point(MARGIN, self.y), fitz.Point(W - MARGIN, self.y),
                            color=(0.55, 0.6, 0.68), width=0.7)
        self.y += 10

    def footer(self, n: int):
        self.page.insert_text((MARGIN, H - 30), DISCLAIMER[:112], fontsize=6.2, fontname=BODY[0], color=(0.45, 0.48, 0.55))
        self.page.insert_text((W - MARGIN - 40, H - 30), f"Page {n}", fontsize=7, fontname=BODY[0], color=(0.45, 0.48, 0.55))


def _prior(period: str) -> list[str]:
    idx = D.PERIOD_ORDER.index(period)
    return D.PERIOD_ORDER[:idx]


# ------------------------------------------------------------- sentence builders
def s_revenue(period: str) -> str:
    m, meta, prior = D.METRICS[period], D.PERIOD_META[period], _prior(period)
    s = (f"Revenue from operations for the quarter ended {meta['end']} stood at ₹{_fmt(m['revenue'])} crore, "
         f"up {m['revenue_yoy']}% year-on-year")
    if prior:
        s += " (" + "; ".join(f"{p}: ₹{_fmt(D.METRICS[p]['revenue'])} crore" for p in reversed(prior)) + ")"
    return s + "."


def s_borrowings(period: str) -> str:
    m, meta, prior = D.METRICS[period], D.PERIOD_META[period], _prior(period)
    if prior:
        parens = " and ".join(f"₹{_fmt(D.METRICS[p]['total_debt'])} crore as at {D.PERIOD_META[p]['end']}"
                              for p in reversed(prior))
        s = (f"Total borrowings (short-term and long-term) increased to ₹{_fmt(m['total_debt'])} crore as at "
             f"{meta['end']} ({parens}).")
        s += (f" Short-term borrowings were ₹{_fmt(m['short_term_debt'])} crore "
              f"({D.PERIOD_META[prior[0]]['end']}: ₹{_fmt(D.METRICS[prior[0]]['short_term_debt'])} crore).")
    else:
        s = (f"Total borrowings (short-term and long-term) stood at ₹{_fmt(m['total_debt'])} crore as at "
             f"{meta['end']}. Short-term borrowings were ₹{_fmt(m['short_term_debt'])} crore.")
    return s


def s_ocf(period: str) -> str:
    m, prior = D.METRICS[period], _prior(period)
    s = f"Net cash generated from operating activities was ₹{_fmt(m['op_cashflow'])} crore for the quarter"
    if prior:
        s += " (" + "; ".join(f"{p}: ₹{_fmt(D.METRICS[p]['op_cashflow'])} crore" for p in reversed(prior)) + ")"
    return s + "."


def s_cash(period: str) -> str:
    m, prior = D.METRICS[period], _prior(period)
    s = f"Cash and cash equivalents stood at ₹{_fmt(m['cash'])} crore"
    if prior:
        s += f" ({D.PERIOD_META[prior[0]]['end']}: ₹{_fmt(D.METRICS[prior[0]]['cash'])} crore)"
    return s + "."


def s_current_liab(period: str) -> str:
    m, prior = D.METRICS[period], _prior(period)
    s = f"Current liabilities increased to ₹{_fmt(m['current_liabilities'])} crore"
    if prior:
        s += f" ({D.PERIOD_META[prior[0]]['end']}: ₹{_fmt(D.METRICS[prior[0]]['current_liabilities'])} crore)"
    return s + ", reflecting higher short-term borrowings and creditor dues."


def s_ebitda_margin(period: str) -> str:
    m, prior = D.METRICS[period], _prior(period)
    s = f"EBITDA margin declined to {m['ebitda_margin']}%"
    if prior:
        s += f" (Q1 FY26: {D.METRICS['Q1 FY26']['ebitda_margin']}%)"
    s += (" primarily on account of higher raw material costs, which rose to "
          f"{m['raw_material_pct']}% of revenue (Q1 FY26: {D.METRICS['Q1 FY26']['raw_material_pct']}%).")
    return s


def s_wc(period: str) -> str:
    m, prior = D.METRICS[period], _prior(period)
    s = (f"Trade receivables were ₹{_fmt(m['receivables'])} crore (Q1 FY26: "
         f"₹{_fmt(D.METRICS['Q1 FY26']['receivables'])} crore) and inventories ₹{_fmt(m['inventory'])} crore "
         f"(Q1 FY26: ₹{_fmt(D.METRICS['Q1 FY26']['inventory'])} crore).")
    return s


def s_capex(period: str) -> str:
    m = D.METRICS[period]
    return (f"Capital expenditure of ₹{_fmt(m['capex'])} crore was incurred during the quarter towards the "
            f"Phase II capacity expansion (cumulative programme: ₹480 crore).")


def s_finance_cost(period: str) -> str:
    m = D.METRICS[period]
    return (f"Finance costs for the quarter were ₹{_fmt(m['finance_cost'])} crore (Q1 FY26: "
            f"₹{_fmt(D.METRICS['Q1 FY26']['finance_cost'])} crore), reflecting higher average borrowings and "
            f"effective interest rates.")


def s_net_profit(period: str) -> str:
    m = D.METRICS[period]
    return (f"Net profit for the quarter declined to ₹{_fmt(m['net_profit'])} crore (Q1 FY26: "
            f"₹{_fmt(D.METRICS['Q1 FY26']['net_profit'])} crore), impacted by higher finance costs and margin "
            f"compression.")


def s_investing(period: str) -> str:
    m = D.METRICS[period]
    return (f"Net cash used in investing activities was ₹{_fmt(abs(m['investing_cashflow']))} crore, primarily "
            f"capital expenditure.")


def s_liquidity_claim(period: str) -> str:
    return "Liquidity remains strong, with comfortable cash buffers to fund our growth plans."


def s_margin_guidance(period: str) -> str:
    return "We remain confident of margin recovery in the second half as input prices moderate."


def s_wc_claim(period: str) -> str:
    return "Our working capital discipline continues to improve, supported by better receivables management."


def s_risks(period: str) -> str:
    return ("Key risks include commodity price volatility, customer concentration, execution risks in the "
            "Phase II expansion, and refinancing of term loans maturing in FY27.")


# ------------------------------------------------------------- report assembly
def build_report(period: str) -> fitz.Document:
    m = D.METRICS[period]
    meta = D.PERIOD_META[period]
    idx = D.PERIOD_ORDER.index(period)
    cols = D.PERIOD_ORDER[: idx + 1]

    doc = fitz.open()
    # ---------------- page 1: cover ----------------
    p = Page(doc)
    p.y = 90
    p.text("XYZ Manufacturing Ltd.", size=24, bold=True, gap=10)
    p.text("Quarterly Financial Report — " + period, size=15, bold=True, gap=14)
    p.rule()
    p.text(f"Quarter ended {meta['end']}", size=11, gap=8)
    p.text("Registered Office: 12 Industrial Estate, Pune, Maharashtra 411018", size=9.5, gap=2)
    p.text("Listed on NSE and BSE (fictitious ticker: XYZMFG)  |  CIN L29999PN1995PLC000000", size=9.5, gap=18)
    p.text("Contents", size=12, bold=True, gap=6)
    p.text("1. Management Discussion & Analysis\n2. Operational Highlights\n3. Statement of Profit & Loss\n"
           "4. Balance Sheet\n5. Cash Flow Statement\n6. Notes to the Accounts", size=10, gap=20)
    p.rule()
    p.text("Basis of preparation: These condensed financials are unaudited and prepared under Indian Accounting "
           "Standards. Amounts are in ₹ crore unless stated otherwise.", size=9, gap=8)
    p.text(DISCLAIMER, size=8, gap=0, color=(0.45, 0.48, 0.55))
    p.footer(1)

    # ---------------- page 2: MD&A ----------------
    p = Page(doc)
    p.heading("1. Management Discussion & Analysis")
    p.text(
        f"Demand environment remains healthy and we continue to see strong order inflows across segments. The "
        f"quarter saw continued ramp-up of export volumes and firm domestic demand for precision components. "
        f"Capacity utilisation improved to {82 + idx * 2}%. The Board reviewed the funding plan for Phase II and "
        f"the company continues to evaluate a mix of internal accruals and term financing for the balance capital "
        f"expenditure.", gap=8)
    p.text("“" + s_liquidity_claim(period) + "”", bold=True, gap=8)
    if idx >= 1:
        p.text("“" + s_margin_guidance(period) + "”", bold=True, gap=8)
    p.text(s_risks(period), gap=8)
    p.rule()
    p.heading("Risk update", size=11)
    p.text(
        "Commodity prices (specialty steel, aluminium alloys) remain elevated relative to prior year. The company "
        "has partially hedged next-quarter requirements. Export customers contributed 34% of revenue; the top "
        "five customers together contributed 41% of revenue.", gap=0)
    p.footer(2)

    # ---------------- page 3: operational highlights ----------------
    p = Page(doc)
    p.heading("2. Operational Highlights")
    p.text(
        f"Production volumes grew {6.5 + idx * 1.2:.1f}% quarter-on-quarter. The Phase II capacity expansion "
        f"programme (₹480 crore) progressed on schedule; commissioning of the Chennai line-2 is expected in "
        f"Q4 FY26.", gap=8)
    p.text("“" + s_wc_claim(period) + "”", bold=True, gap=8)
    p.text(
        f"Headcount stood at 4,812. Employee cost for the quarter was ₹{m['employee_cost']} crore. Manpower "
        f"productivity improved 4% year-on-year on the back of automation initiatives.", gap=8)
    p.rule()
    p.heading("Segment performance", size=11)
    p.mono_table([
        "Automotive components        52% of revenue      growth 10% YoY",
        "Industrial machinery         31% of revenue      growth 15% YoY",
        "Exports & others             17% of revenue      growth 9%  YoY",
    ])
    p.text("Customer concentration remains a monitored risk; the top five customers contribute 41% of revenue.",
           gap=0)
    p.footer(3)

    # ---------------- page 4: P&L ----------------
    p = Page(doc)
    p.heading("3. Statement of Profit & Loss")
    p.text(s_revenue(period), gap=6)
    p.text(s_ebitda_margin(period), gap=6)
    p.text(s_finance_cost(period), gap=6)
    p.text(s_net_profit(period), gap=8)
    p.rule()
    head = f"{'₹ crore':<28}" + "".join(f"{c:>12}" for c in cols)
    lines = [head, "-" * len(head)]
    table_keys = [
        ("Revenue from operations", "revenue"), ("Other income", "other_income"),
        ("Raw material cost (% sales)", "raw_material_pct"), ("Employee benefits expense", "employee_cost"),
        ("EBITDA", "ebitda"), ("EBITDA margin (%)", "ebitda_margin"),
        ("Depreciation & amortisation", "depreciation"), ("Finance costs", "finance_cost"),
        ("Profit before tax", "pbt"), ("Tax expense", "tax"), ("Net profit", "net_profit"),
        ("Net margin (%)", "net_margin"),
    ]
    for label, key in table_keys:
        lines.append(f"{label:<28}" + "".join(f"{_fmt(D.METRICS[c][key]):>12}" for c in cols))
    p.mono_table(lines)
    p.text("Other operating expenses are presented net of capitalisation. Figures may not add up due to rounding.",
           size=8, gap=0)
    p.footer(4)

    # ---------------- page 5: balance sheet ----------------
    p = Page(doc)
    p.heading("4. Balance Sheet (condensed)")
    p.text(s_borrowings(period), gap=6)
    p.text(s_cash(period), gap=6)
    p.text(s_current_liab(period), gap=6)
    p.text(s_wc(period), gap=8)
    p.rule()
    head = f"{'₹ crore':<28}" + "".join(f"{c:>12}" for c in cols)
    lines = [head, "-" * len(head)]
    bs_keys = [
        ("Cash and cash equivalents", "cash"), ("Trade receivables", "receivables"),
        ("Inventories", "inventory"), ("Current assets (A)", "current_assets"),
        ("Current liabilities (B)", "current_liabilities"), ("Current ratio (A/B)", "current_ratio"),
        ("Short-term borrowings", "short_term_debt"), ("Long-term borrowings", "long_term_debt"),
        ("Total borrowings", "total_debt"), ("Net debt", "net_debt"),
        ("Debt / equity (x)", "debt_to_equity"), ("Net worth (equity)", "equity"),
    ]
    for label, key in bs_keys:
        lines.append(f"{label:<28}" + "".join(f"{_fmt(D.METRICS[c][key]):>12}" for c in cols))
    p.mono_table(lines)
    p.text(f"Receivable days were {m['receivable_days']} (Q1 FY26: 23) and inventory days {m['inventory_days']} "
           f"(Q1 FY26: 58).", size=8, gap=0)
    p.footer(5)

    # ---------------- page 6: cash flow ----------------
    p = Page(doc)
    p.heading("5. Cash Flow Statement (condensed)")
    p.text(s_ocf(period), gap=6)
    p.text(s_investing(period), gap=8)
    p.rule()
    head = f"{'₹ crore':<28}" + "".join(f"{c:>12}" for c in cols)
    lines = [head, "-" * len(head)]
    cf_keys = [
        ("Operating cash flow", "op_cashflow"), ("Investing cash flow", "investing_cashflow"),
        ("Financing cash flow", "financing_cashflow"), ("Capital expenditure", "capex"),
    ]
    for label, key in cf_keys:
        lines.append(f"{label:<28}" + "".join(f"{_fmt(D.METRICS[c][key]):>12}" for c in cols))
    net_vals = [D.METRICS[c]["op_cashflow"] + D.METRICS[c]["investing_cashflow"] + D.METRICS[c]["financing_cashflow"]
                for c in cols]
    lines.append(f"{'Net change in cash':<28}" + "".join(f"{_fmt(v):>12}" for v in net_vals))
    p.mono_table(lines)
    p.text(f"Interest coverage (EBITDA / finance cost) for the quarter was {m['interest_coverage']}x (Q1 FY26: "
           f"8.9x). Debt / EBITDA (annualised) stood at {m['debt_to_ebitda']}x.", size=9, gap=0)
    p.footer(6)

    # ---------------- page 7: notes ----------------
    p = Page(doc)
    p.heading("6. Notes to the Accounts")
    p.text(s_capex(period), gap=6)
    p.text(
        "Term loans aggregating ₹180 crore mature in FY27 and are proposed to be refinanced. The company is in "
        "discussion with lenders; sanction is expected in Q1 FY27.", gap=8)
    p.rule()
    p.heading("Debt maturity profile", size=11)
    p.mono_table([
        f"Within 1 year          ₹{m['short_term_debt']:>7,.0f} Cr",
        f"1 - 3 years            ₹{m['long_term_debt'] * 0.55:>7,.0f} Cr",
        f"Beyond 3 years         ₹{m['long_term_debt'] * 0.45:>7,.0f} Cr",
    ])
    p.rule()
    p.text(
        "Basis of preparation: These condensed interim financials are unaudited, prepared under Ind AS, and do "
        "not include all annual disclosures. Figures in ₹ crore unless stated otherwise.", size=9, gap=8)
    p.text(DISCLAIMER, size=8, gap=0, color=(0.45, 0.48, 0.55))
    p.footer(7)
    return doc


def generate_all(outdir: Path) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for period in D.PERIOD_ORDER:
        path = outdir / f"XYZ_Manufacturing_{period.replace(' ', '_')}_Report.pdf"
        doc = build_report(period)
        doc.save(str(path), deflate=True)
        doc.close()
        paths[period] = str(path)
    return paths


def extract_pages_cache(outdir: Path) -> None:
    """Cache page text of each generated PDF for demo-mode retrieval."""
    import pdf_utils
    for period in D.PERIOD_ORDER:
        path = outdir / f"XYZ_Manufacturing_{period.replace(' ', '_')}_Report.pdf"
        cache = outdir / f"{period.replace(' ', '_').lower()}_pages.json"
        if path.exists():
            cache.write_text(json.dumps(pdf_utils.extract_pages(str(path))))


if __name__ == "__main__":
    from config import SAMPLE_DIR
    made = generate_all(SAMPLE_DIR)
    extract_pages_cache(SAMPLE_DIR)
    print(json.dumps(made, indent=1))
