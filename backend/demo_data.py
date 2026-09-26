"""Curated Demo Mode dataset — XYZ Manufacturing Ltd. (fictional).

All figures are FICTIONAL sample data (₹ Crore) created for the FinSight X
prototype so the full workflow works without any LLM API key.
"""

COMPANY = {
    "name": "XYZ Manufacturing Ltd.",
    "sector": "Industrial Components & Precision Engineering",
    "listings": "NSE / BSE (fictitious ticker: XYZMFG)",
    "profile": (
        "Mid-cap manufacturer of precision industrial components operating plants in Pune and "
        "Chennai with ~4,800 employees. FY26 strategy centres on the Phase II capacity expansion "
        "(₹480 Cr programme) targeting export customers in Europe and South-East Asia."
    ),
    "currency": "₹ Crore",
}

PERIOD_ORDER = ["Q1 FY26", "Q2 FY26", "Q3 FY26"]

PERIOD_META = {
    "Q1 FY26": {"end": "June 30, 2025", "doc": "XYZ Manufacturing Ltd. — Q1 FY26 Quarterly Report"},
    "Q2 FY26": {"end": "September 30, 2025", "doc": "XYZ Manufacturing Ltd. — Q2 FY26 Quarterly Report"},
    "Q3 FY26": {"end": "December 31, 2025", "doc": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report"},
}

# ------------------------------------------------------------------ metrics
METRICS: dict[str, dict] = {
    "Q1 FY26": {
        "revenue": 1245, "revenue_yoy": 8.2, "other_income": 12,
        "raw_material_pct": 52.4, "employee_cost": 118, "gross_margin": 34.2,
        "ebitda": 248, "ebitda_margin": 19.9, "depreciation": 62, "finance_cost": 28,
        "pbt": 170, "tax": 28, "net_profit": 142, "net_margin": 11.4,
        "total_debt": 400, "short_term_debt": 120, "long_term_debt": 280,
        "cash": 186, "net_debt": 214, "capex": 95,
        "op_cashflow": 72, "investing_cashflow": -95, "financing_cashflow": 26,
        "current_assets": 690, "current_liabilities": 486, "current_ratio": 1.42,
        "receivables": 312, "inventory": 245, "receivable_days": 23, "inventory_days": 58,
        "interest_coverage": 8.9, "debt_to_ebitda": 0.40, "debt_to_equity": 0.31,
        "equity": 1280,
    },
    "Q2 FY26": {
        "revenue": 1312, "revenue_yoy": 9.6, "other_income": 11,
        "raw_material_pct": 55.1, "employee_cost": 124, "gross_margin": 32.1,
        "ebitda": 236, "ebitda_margin": 18.0, "depreciation": 68, "finance_cost": 34,
        "pbt": 145, "tax": 17, "net_profit": 128, "net_margin": 9.8,
        "total_debt": 470, "short_term_debt": 165, "long_term_debt": 305,
        "cash": 142, "net_debt": 328, "capex": 160,
        "op_cashflow": 58, "investing_cashflow": -160, "financing_cashflow": 48,
        "current_assets": 705, "current_liabilities": 551, "current_ratio": 1.28,
        "receivables": 356, "inventory": 281, "receivable_days": 25, "inventory_days": 63,
        "interest_coverage": 6.9, "debt_to_ebitda": 0.50, "debt_to_equity": 0.36,
        "equity": 1305,
    },
    "Q3 FY26": {
        "revenue": 1394, "revenue_yoy": 12.1, "other_income": 9,
        "raw_material_pct": 58.3, "employee_cost": 129, "gross_margin": 29.8,
        "ebitda": 221, "ebitda_margin": 15.9, "depreciation": 74, "finance_cost": 41,
        "pbt": 115, "tax": 6, "net_profit": 109, "net_margin": 7.8,
        "total_debt": 560, "short_term_debt": 215, "long_term_debt": 345,
        "cash": 98, "net_debt": 462, "capex": 225,
        "op_cashflow": 42, "investing_cashflow": -225, "financing_cashflow": 122,
        "current_assets": 718, "current_liabilities": 641, "current_ratio": 1.12,
        "receivables": 402, "inventory": 318, "receivable_days": 27, "inventory_days": 69,
        "interest_coverage": 5.4, "debt_to_ebitda": 0.63, "debt_to_equity": 0.42,
        "equity": 1322,
    },
}

METRIC_LABELS = {
    "revenue": "Revenue from Operations", "net_profit": "Net Profit", "ebitda": "EBITDA",
    "ebitda_margin": "EBITDA Margin", "total_debt": "Total Debt", "op_cashflow": "Operating Cash Flow",
    "finance_cost": "Finance Cost", "cash": "Cash & Equivalents", "net_profit_margin": "Net Margin",
    "net_margin": "Net Margin", "current_ratio": "Current Ratio", "interest_coverage": "Interest Coverage",
    "raw_material_pct": "Raw Material Cost (% of sales)", "receivable_days": "Receivable Days",
    "inventory_days": "Inventory Days", "capex": "Capital Expenditure",
    "short_term_debt": "Short-term Debt", "gross_margin": "Gross Margin",
}

# ------------------------------------------------------------------ management statements
MANAGEMENT_STATEMENTS = {
    "Q1 FY26": [
        {"quote": "Demand environment remains healthy and we continue to see strong order inflows across segments.",
         "section": "Management Discussion & Analysis", "page": 2},
        {"quote": "Our liquidity position is comfortable and debt levels remain well within our target leverage band.",
         "section": "Management Discussion & Analysis", "page": 2},
    ],
    "Q2 FY26": [
        {"quote": "Input cost pressure is temporary. We expect margins to recover in the second half as input prices moderate.",
         "section": "Earnings Call Commentary", "page": 2},
        {"quote": "The Phase II expansion is progressing on schedule and within the sanctioned budget.",
         "section": "Management Discussion & Analysis", "page": 2},
    ],
    "Q3 FY26": [
        {"quote": "Liquidity remains strong, with comfortable cash buffers to fund our growth plans.",
         "section": "Management Discussion & Analysis", "page": 2},
        {"quote": "We remain confident of margin recovery in the second half as input prices moderate.",
         "section": "Earnings Call Commentary", "page": 2},
        {"quote": "Our working capital discipline continues to improve, supported by better receivables management.",
         "section": "Management Discussion & Analysis", "page": 3},
    ],
}

Q3_RISKS_QUOTE = ("Key risks include commodity price volatility, customer concentration, execution risks in the "
                  "Phase II expansion, and refinancing of term loans maturing in FY27.")

# ------------------------------------------------------------------ evidence registry
EVIDENCE: list[dict] = [
    {"id": "EV-001", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 4,
     "section": "Statement of Profit & Loss", "kind": "reported_fact",
     "quote": ("Revenue from operations for the quarter ended December 31, 2025 stood at ₹1,394 crore, "
               "up 12.1% year-on-year (Q2 FY26: ₹1,312 crore; Q1 FY26: ₹1,245 crore)."), "tags": ["revenue"]},
    {"id": "EV-002", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 5,
     "section": "Balance Sheet — Borrowings", "kind": "reported_fact",
     "quote": ("Total borrowings (short-term and long-term) increased to ₹560 crore as at December 31, 2025 "
               "(₹470 crore as at September 30, 2025 and ₹400 crore as at June 30, 2025). Short-term "
               "borrowings were ₹215 crore (June 30, 2025: ₹120 crore)."), "tags": ["debt", "solvency"]},
    {"id": "EV-003", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 6,
     "section": "Cash Flow Statement", "kind": "reported_fact",
     "quote": ("Net cash generated from operating activities was ₹42 crore for the quarter (Q2 FY26: ₹58 crore; "
               "Q1 FY26: ₹72 crore)."), "tags": ["cash flow"]},
    {"id": "EV-004", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 5,
     "section": "Balance Sheet — Cash & Bank", "kind": "reported_fact",
     "quote": "Cash and cash equivalents stood at ₹98 crore (June 30, 2025: ₹186 crore).", "tags": ["liquidity"]},
    {"id": "EV-005", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 5,
     "section": "Balance Sheet — Current Liabilities", "kind": "reported_fact",
     "quote": ("Current liabilities increased to ₹641 crore (June 30, 2025: ₹486 crore), reflecting higher "
               "short-term borrowings and creditor dues."), "tags": ["liquidity", "working capital"]},
    {"id": "EV-006", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 4,
     "section": "Statement of Profit & Loss — Notes", "kind": "reported_fact",
     "quote": ("EBITDA margin declined to 15.9% (Q1 FY26: 19.9%) primarily on account of higher raw material "
               "costs, which rose to 58.3% of revenue (Q1 FY26: 52.4%)."), "tags": ["margin", "costs"]},
    {"id": "EV-007", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 5,
     "section": "Notes — Working Capital", "kind": "reported_fact",
     "quote": ("Trade receivables were ₹402 crore (Q1 FY26: ₹312 crore) and inventories ₹318 crore "
               "(Q1 FY26: ₹245 crore)."), "tags": ["working capital"]},
    {"id": "EV-008", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 7,
     "section": "Notes — Capital Expenditure", "kind": "reported_fact",
     "quote": ("Capital expenditure of ₹225 crore was incurred during the quarter towards the Phase II capacity "
               "expansion (cumulative programme: ₹480 crore)."), "tags": ["capex"]},
    {"id": "EV-009", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 4,
     "section": "Statement of Profit & Loss — Finance Costs", "kind": "reported_fact",
     "quote": ("Finance costs for the quarter were ₹41 crore (Q1 FY26: ₹28 crore), reflecting higher average "
               "borrowings and effective interest rates."), "tags": ["finance cost", "debt"]},
    {"id": "EV-010", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 2,
     "section": "Management Discussion & Analysis", "kind": "management_statement",
     "quote": "Liquidity remains strong, with comfortable cash buffers to fund our growth plans.",
     "tags": ["liquidity", "statement"]},
    {"id": "EV-011", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 2,
     "section": "Earnings Call Commentary", "kind": "management_statement",
     "quote": "We remain confident of margin recovery in the second half as input prices moderate.",
     "tags": ["margin", "guidance", "statement"]},
    {"id": "EV-012", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 3,
     "section": "Management Discussion & Analysis", "kind": "management_statement",
     "quote": "Our working capital discipline continues to improve, supported by better receivables management.",
     "tags": ["working capital", "statement"]},
    {"id": "EV-013", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 2,
     "section": "Risk Factors", "kind": "management_statement",
     "quote": Q3_RISKS_QUOTE, "tags": ["risk"]},
    {"id": "EV-014", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 4,
     "section": "Statement of Profit & Loss — Net Profit", "kind": "reported_fact",
     "quote": ("Net profit for the quarter declined to ₹109 crore (Q1 FY26: ₹142 crore), impacted by higher "
               "finance costs and margin compression."), "tags": ["profit"]},
    {"id": "EV-015", "document": "XYZ Manufacturing Ltd. — Q3 FY26 Quarterly Report", "page": 6,
     "section": "Cash Flow Statement — Investing", "kind": "reported_fact",
     "quote": "Net cash used in investing activities was ₹225 crore, primarily capital expenditure.",
     "tags": ["capex", "cash flow"]},
]

# ------------------------------------------------------------------ AI executive summary (demo)
EXEC_SUMMARY = {
    "headline": "Revenue growth is accelerating, but it is being funded by debt while margins and cash generation deteriorate.",
    "paragraphs": [
        ("XYZ Manufacturing reported Q3 FY26 revenue of ₹1,394 Cr, up 12.1% year-on-year — the strongest growth "
         "of the last three quarters, driven by the export ramp-up. However, profitability moved in the opposite "
         "direction: EBITDA margin compressed from 19.9% in Q1 to 15.9% in Q3 as raw material costs climbed from "
         "52.4% to 58.3% of sales, and net profit fell 23% over the same period to ₹109 Cr."),
        ("The balance sheet shows the clearest early-warning pattern. Total debt has risen across three consecutive "
         "quarters (₹400 Cr → ₹470 Cr → ₹560 Cr, +40% since Q1), while operating cash flow declined over the same "
         "three periods (₹72 Cr → ₹58 Cr → ₹42 Cr, −42%). The combination of rising capex (₹225 Cr in Q3) and "
         "weakening internal accruals means the Phase II expansion is being debt-funded."),
        ("Liquidity indicators are tightening: cash is down 47% since Q1 to ₹98 Cr, the current ratio slipped from "
         "1.42 to 1.12, short-term debt nearly doubled to ₹215 Cr, and interest coverage fell from 8.9x to 5.4x. "
         "None of these is a distress signal in isolation, but their simultaneous deterioration is a coherent "
         "financial-pressure pattern that merits active monitoring."),
        ("Two management statements warrant verification against the reported numbers: the claim that “liquidity "
         "remains strong” sits uncomfortably beside falling cash and rising short-term liabilities, and the "
         "margin-recovery guidance has now been repeated for two consecutive quarters while margins continued to "
         "decline. These are flagged as potential statement–data mismatches requiring analyst verification — not "
         "conclusions of wrongdoing."),
    ],
    "key_changes": [
        "Revenue ₹1,245 Cr → ₹1,394 Cr (+12% YoY in Q3); growth trend improving.",
        "EBITDA margin 19.9% → 15.9% (−400 bps over two quarters); raw material cost at 58.3% of sales.",
        "Net profit ₹142 Cr → ₹109 Cr (−23% since Q1).",
        "Total debt ₹400 Cr → ₹560 Cr (+40% since Q1, rising three consecutive quarters).",
        "Operating cash flow ₹72 Cr → ₹42 Cr (−42% since Q1, falling three consecutive quarters).",
        "Finance cost ₹28 Cr → ₹41 Cr (+46% since Q1); interest coverage down to 5.4x.",
        "Cash ₹186 Cr → ₹98 Cr (−47%); current ratio 1.42 → 1.12.",
    ],
    "guidance": [
        "Margin recovery expected in H2 FY26 as input prices moderate (repeated from Q2).",
        "Phase II expansion on schedule, cumulative capex ₹480 Cr.",
        "Management continues to characterise liquidity as strong.",
    ],
    "risks_events": [
        "Commodity price volatility affecting raw material costs (management-identified).",
        "Refinancing of term loans maturing in FY27 (management-identified).",
        "Execution risk on Phase II expansion; customer concentration.",
        "Rising share of short-term debt (38% of total debt vs 30% in Q1).",
    ],
}

# ------------------------------------------------------------------ Ask-the-Report knowledge bank (demo)
QA_BANK: list[dict] = [
    {"id": "QA-01", "patterns": ["why profit", "profit decline", "profit fell", "net profit", "profit down", "earnings decline"],
     "answer": ("Net profit declined from ₹142 Cr in Q1 to ₹109 Cr in Q3 (−23%) for two compounding reasons. "
                "First, gross margin compressed from 34.2% to 29.8% as raw material costs rose from 52.4% to 58.3% "
                "of revenue — input cost inflation that the company has not fully passed through. Second, finance "
                "cost rose from ₹28 Cr to ₹41 Cr (+46%) as borrowings increased to fund the Phase II expansion. "
                "Depreciation also increased (₹62 Cr → ₹74 Cr) as new capacity came online. So the profit decline "
                "is driven by margin compression plus a rising interest bill, not by falling revenue — revenue "
                "actually grew 12.1% YoY in Q3."),
     "evidence_ids": ["EV-014", "EV-006", "EV-009"]},
    {"id": "QA-02", "patterns": ["what changed", "changed from q2", "versus q2", "vs q2", "q2 comparison", "since last quarter"],
     "answer": ("Compared with Q2 FY26: revenue rose 6.3% (₹1,312 Cr → ₹1,394 Cr), but EBITDA fell 6.4% "
                "(₹236 Cr → ₹221 Cr) with margin down 210 bps (18.0% → 15.9%). Net profit fell 15% (₹128 Cr → ₹109 Cr). "
                "Total debt rose ₹90 Cr (₹470 Cr → ₹560 Cr, +19%), short-term debt rose from ₹165 Cr to ₹215 Cr, and "
                "operating cash flow fell from ₹58 Cr to ₹42 Cr (−28%). Cash declined from ₹142 Cr to ₹98 Cr. The "
                "quarter's defining change: growth continued while profitability, liquidity and leverage all moved "
                "further in the adverse direction."),
     "evidence_ids": ["EV-001", "EV-006", "EV-002", "EV-003", "EV-004"]},
    {"id": "QA-03", "patterns": ["why debt", "debt increase", "debt increased", "borrowing", "why did debt", "leverage rise"],
     "answer": ("Total debt increased across three consecutive periods (₹400 Cr → ₹470 Cr → ₹560 Cr) because the "
                "Phase II capacity expansion is being funded largely by borrowings rather than internal accruals. "
                "Q3 capital expenditure was ₹225 Cr while operating cash flow was only ₹42 Cr — a funding gap of "
                "roughly ₹183 Cr that was met by debt (financing cash flow of +₹122 Cr in Q3) and cash balances. "
                "Working-capital build-up added to the requirement: receivables rose to ₹402 Cr and inventories to "
                "₹318 Cr. Short-term debt nearly doubled since Q1 (₹120 Cr → ₹215 Cr), which is the more concerning "
                "composition shift."),
     "evidence_ids": ["EV-002", "EV-008", "EV-003", "EV-015", "EV-007"]},
    {"id": "QA-04", "patterns": ["risk", "risks", "risk factors", "what risks", "management risks"],
     "answer": ("Management explicitly identifies four risk factors in the Q3 report: commodity price volatility, "
                "customer concentration, execution risks in the Phase II expansion, and refinancing of term loans "
                "maturing in FY27. Beyond the management-stated risks, the reported numbers surface additional "
                "watch items: interest coverage has fallen to 5.4x, short-term debt now makes up 38% of total debt, "
                "and the current ratio has slipped to 1.12 — all of which amplify refinancing risk if the trend persists."),
     "evidence_ids": ["EV-013", "EV-002", "EV-005"]},
    {"id": "QA-05", "patterns": ["liquidity", "cash position", "cash buffer", "liquid"],
     "answer": ("The liquidity picture contradicts management's characterisation. Management states that “liquidity "
                "remains strong, with comfortable cash buffers”, but reported data shows cash down 47% since Q1 "
                "(₹186 Cr → ₹98 Cr), the current ratio slipping from 1.42 to 1.12, current liabilities up 32% to "
                "₹641 Cr, and short-term borrowings up 79% to ₹215 Cr. This is flagged as a potential statement–data "
                "mismatch requiring analyst verification — it is not an allegation of wrongdoing. Recommended next "
                "steps: obtain the cash-flow bridge, undrawn sanction limits and receivables ageing schedule."),
     "evidence_ids": ["EV-010", "EV-004", "EV-005", "EV-002"]},
    {"id": "QA-06", "patterns": ["margin", "margins", "ebitda margin", "margin decline", "gross margin"],
     "answer": ("EBITDA margin declined for two consecutive quarters: 19.9% (Q1) → 18.0% (Q2) → 15.9% (Q3), a total "
                "compression of 400 bps. The report attributes this to raw material costs rising from 52.4% to 58.3% "
                "of revenue. Gross margin fell from 34.2% to 29.8% over the same window, indicating the company has "
                "absorbed input-cost inflation rather than passing it on. Management guidance of a second-half "
                "recovery has been repeated since Q2 while margins continued to decline — a guidance-vs-outcome gap "
                "the platform has flagged for verification."),
     "evidence_ids": ["EV-006", "EV-011"]},
    {"id": "QA-07", "patterns": ["cash flow", "operating cash", "ocf", "cash generation"],
     "answer": ("Operating cash flow has declined across three consecutive periods: ₹72 Cr (Q1) → ₹58 Cr (Q2) → "
                "₹42 Cr (Q3), a cumulative fall of 42%. The deterioration outpaces the margin decline, pointing to "
                "working-capital drag: receivables (+₹90 Cr since Q1) and inventories (+₹73 Cr) are absorbing cash. "
                "Meanwhile investing outflow widened to ₹225 Cr for capex, so the company is consuming cash at an "
                "accelerating rate and covering the gap with borrowings."),
     "evidence_ids": ["EV-003", "EV-015", "EV-007"]},
    {"id": "QA-08", "patterns": ["guidance", "outlook", "management guidance", "expect", "forecast"],
     "answer": ("Management's stated guidance: (1) margin recovery in H2 FY26 as input prices moderate — a claim "
                "repeated since Q2 while margins actually declined further; (2) Phase II expansion on schedule and "
                "within budget; (3) continued strong liquidity. The platform flags the margin-recovery guidance and "
                "the liquidity characterisation as statements to verify against next quarter's reported numbers."),
     "evidence_ids": ["EV-011", "EV-010", "EV-008"]},
    {"id": "QA-09", "patterns": ["working capital", "receivable", "inventory", "debtor"],
     "answer": ("Working capital is absorbing increasing cash. Trade receivables rose 29% since Q1 to ₹402 Cr "
                "(receivable days 23 → 27) and inventories rose 30% to ₹318 Cr (inventory days 58 → 69) — both "
                "growing materially faster than the 12% revenue growth. Management's claim that working-capital "
                "discipline “continues to improve” is contrary to these reported figures and has been flagged as a "
                "potential statement–data mismatch requiring verification."),
     "evidence_ids": ["EV-007", "EV-012"]},
    {"id": "QA-10", "patterns": ["capex", "expansion", "phase ii", "capacity"],
     "answer": ("Q3 capex was ₹225 Cr, the third consecutive quarterly increase (₹95 Cr → ₹160 Cr → ₹225 Cr), toward "
                "the ₹480 Cr Phase II capacity expansion. Management says the project is on schedule and within "
                "budget. The strategic rationale is export growth (revenue +12.1% YoY), but the financing mix is the "
                "issue: internal cash generation covered only 19% of Q3 capex, with the balance funded by debt — the "
                "core driver of the leverage build-up flagged by the signal engine."),
     "evidence_ids": ["EV-008", "EV-015", "EV-003"]},
    {"id": "QA-11", "patterns": ["mismatch", "statement", "contradiction", "consistency", "verify"],
     "answer": ("The platform flagged two potential statement–data mismatches: (1) “Liquidity remains strong” vs "
                "cash −47%, current ratio 1.12 and short-term debt +79% since Q1; (2) repeated margin-recovery "
                "guidance vs margins declining for three straight periods. Both are labelled as requiring analyst "
                "verification — the platform never asserts fraud; it only surfaces gaps between narrative and numbers."),
     "evidence_ids": ["EV-010", "EV-011", "EV-004", "EV-006"]},
    {"id": "QA-12", "patterns": ["finance cost", "interest", "interest coverage", "coverage"],
     "answer": ("Finance cost rose from ₹28 Cr (Q1) to ₹41 Cr (Q3), +46%, on higher average borrowings and rates. "
                "Interest coverage (EBITDA / finance cost) correspondingly fell from 8.9x to 5.4x. Coverage is still "
                "adequate at current earnings, but if EBITDA keeps falling while debt rises, the trajectory approaches "
                "levels typically monitored under credit-review triggers. The FY27 term-loan refinancing noted by "
                "management is directly relevant here."),
     "evidence_ids": ["EV-009", "EV-002", "EV-013"]},
]

SAFETY_NOTE = ("FinSight X provides analytical support only. It does not predict stock prices, issue buy/sell "
               "recommendations, approve or reject loans, or assert fraud. All outputs distinguish "
               "Reported Fact from AI Analysis and Potential Significance.")
