"use client";

import { AlertTriangle, Building2, FileText, MessageSquareQuote, Sparkles, ArrowRight } from "lucide-react";
import type { AnalysisPackage, Evidence, Role, Signal } from "@/lib/finsight/types";
import { FactLegend, KpiCard, SectionHeader, SeverityBadge } from "./ui-bits";

const ROLE_FOCUS: Record<Role, { title: string; points: string[] }> = {
  ceo: {
    title: "Strategic view (CEO)",
    points: [
      "Growth is real — revenue up 12.1% YoY — but earnings quality is deteriorating.",
      "Expansion is being debt-funded; watch leverage vs the internal target band.",
      "Two management claims are flagged for verification before the next board review.",
    ],
  },
  credit_analyst: {
    title: "Credit workbench (Credit Analyst)",
    points: [
      "Interest coverage fell 8.9x → 5.4x; short-term debt nearly doubled since Q1.",
      "Upload prior-quarter PDFs to extend early-signal memory beyond three periods.",
      "Every signal driver links to page-level evidence — start with the Evidence tab.",
    ],
  },
  risk_manager: {
    title: "Risk control view (Risk Manager)",
    points: [
      "Risk chain: input costs → margins → cash flow → financing pressure (9 nodes).",
      "Three statement–data mismatches flagged; verification checklists attached.",
      "Platform audit log available under the Audit tab for this session.",
    ],
  },
};

export function OverviewTab({ pkg, role, onOpenEvidence, onGoTo }: {
  pkg: AnalysisPackage;
  role: Role;
  onOpenEvidence: (ev: Evidence) => void;
  onGoTo: (tab: string) => void;
}) {
  const m = pkg.metrics;
  const periods = pkg.periods;
  const last = m[periods[periods.length - 1]] ?? {};
  const first = m[periods[0]] ?? {};
  const d = (k: string): number | null => {
    const a = first[k], b = last[k];
    if (typeof a !== "number" || typeof b !== "number" || a === 0) return null;
    return Math.round(((b - a) / Math.abs(a)) * 1000) / 10;
  };
  const series = (k: string): number[] | undefined =>
    periods.map((p) => m[p]?.[k]).every((v) => typeof v === "number") ? periods.map((p) => m[p][k]) : undefined;

  const topSignals = pkg.signals.slice(0, 3);
  const focus = ROLE_FOCUS[role];
  const signalCount = pkg.signals.filter((s) => s.severity === "high").length;

  return (
    <div className="space-y-6">
      {/* KPI row */}
      <div>
        <SectionHeader
          title="Company snapshot"
          subtitle={`${pkg.company.name} · ${pkg.company.sector} · figures in ${pkg.company.currency}, latest quarter ${pkg.period_label}`}
          right={<FactLegend />}
        />
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
          <KpiCard label="Revenue" current={last.revenue} first={first.revenue} delta={d("revenue")} unit="₹ Cr" spark={series("revenue")} color="#1E3A5F" />
          <KpiCard label="Net Profit" current={last.net_profit} first={first.net_profit} delta={d("net_profit")} unit="₹ Cr" spark={series("net_profit")} color="#B45309" />
          <KpiCard label="EBITDA" current={last.ebitda} first={first.ebitda} delta={d("ebitda")} unit="₹ Cr" spark={series("ebitda")} color="#0E7490" />
          <KpiCard label="Total Debt" current={last.total_debt} first={first.total_debt} delta={d("total_debt")} unit="₹ Cr" invert spark={series("total_debt")} color="#DC2626" />
          <KpiCard label="Op. Cash Flow" current={last.op_cashflow} first={first.op_cashflow} delta={d("op_cashflow")} unit="₹ Cr" invert spark={series("op_cashflow")} color="#059669" />
          <KpiCard label="EBITDA Margin" current={last.ebitda_margin} first={first.ebitda_margin} delta={d("ebitda_margin")} unit="%" invert spark={series("ebitda_margin")} color="#7C2D12" />
        </div>
      </div>

      {/* Company + exec summary */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <Building2 className="h-4 w-4 text-[#0A1B33]" />
            <h3 className="text-sm font-bold text-slate-900">Company overview</h3>
          </div>
          <p className="mt-3 text-[13px] leading-relaxed text-slate-600">{pkg.company.profile}</p>
          <dl className="mt-4 space-y-2 text-xs">
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Sector</dt><dd className="text-right font-semibold text-slate-800">{pkg.company.sector}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Listings</dt><dd className="text-right font-semibold text-slate-800">{pkg.company.listings}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Reporting currency</dt><dd className="text-right font-semibold text-slate-800">{pkg.company.currency}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Periods on file</dt><dd className="text-right font-semibold text-slate-800">{periods.join(" · ")}</dd></div>
          </dl>
          {pkg.notice && (
            <p className="mt-4 rounded-lg bg-slate-50 border border-slate-100 px-3 py-2 text-[11px] leading-relaxed text-slate-500">{pkg.notice}</p>
          )}
        </div>

        <div className="lg:col-span-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-[#0A1B33]" />
              <h3 className="text-sm font-bold text-slate-900">AI Executive Summary</h3>
            </div>
            <span className="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-[10.5px] font-semibold uppercase tracking-wide text-slate-500">
              {pkg.ai_enabled ? "LLM-generated" : "Demo Mode — rule-based"}
            </span>
          </div>
          <p className="mt-3 rounded-lg border-l-4 border-[#C9A227] bg-amber-50/50 px-3.5 py-2.5 text-[13.5px] font-semibold leading-relaxed text-slate-800">
            {pkg.exec_summary.headline}
          </p>
          <div className="mt-3 space-y-2.5">
            {pkg.exec_summary.paragraphs.map((p, i) => (
              <p key={i} className="text-[13px] leading-relaxed text-slate-600">{p}</p>
            ))}
          </div>
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            {[
              { title: "Key financial changes", items: pkg.exec_summary.key_changes, icon: FileText },
              { title: "Management guidance", items: pkg.exec_summary.guidance, icon: MessageSquareQuote },
              { title: "Important risks & events", items: pkg.exec_summary.risks_events, icon: AlertTriangle },
            ].map((blk) => (
              <div key={blk.title}>
                <p className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  <blk.icon className="h-3.5 w-3.5" /> {blk.title}
                </p>
                {blk.items.length ? (
                  <ul className="mt-2 space-y-1.5">
                    {blk.items.slice(0, 4).map((it, i) => (
                      <li key={i} className="flex gap-1.5 text-[12px] leading-snug text-slate-600">
                        <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-slate-300" />{it}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-2 text-[12px] italic text-slate-400">None extracted for this report.</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Important signals preview + role focus */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-rose-500" />
              <h3 className="text-sm font-bold text-slate-900">Important signals</h3>
            </div>
            <button onClick={() => onGoTo("signals")} className="inline-flex items-center gap-1 text-xs font-semibold text-teal-700 hover:text-teal-900">
              All {pkg.signals.length} signals <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            {signalCount} high-severity signal{signalCount === 1 ? "" : "s"} active · multi-indicator fusion with evidence links
          </p>
          <div className="mt-3 space-y-2.5">
            {topSignals.map((s: Signal) => (
              <button
                key={s.id}
                onClick={() => onGoTo("signals")}
                className="flex w-full items-center gap-3 rounded-lg border border-slate-100 bg-slate-50/60 px-3.5 py-2.5 text-left transition hover:border-slate-200 hover:bg-slate-50"
              >
                <SeverityBadge severity={s.severity} />
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-[13px] font-bold text-slate-800">{s.title}</span>
                  <span className="block truncate text-[11.5px] text-slate-500">{s.logic}</span>
                </span>
                <ArrowRight className="h-4 w-4 shrink-0 text-slate-300" />
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-[#0A1B33]/15 bg-gradient-to-br from-[#0A1B33] to-[#13294B] p-5 text-white shadow-sm">
          <h3 className="text-sm font-bold">{focus.title}</h3>
          <ul className="mt-3 space-y-2.5">
            {focus.points.map((pt, i) => (
              <li key={i} className="flex gap-2 text-[12.5px] leading-relaxed text-slate-200">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#E4C158]" />{pt}
              </li>
            ))}
          </ul>
          <div className="mt-4 flex flex-wrap gap-2">
            {role !== "ceo" && (
              <button onClick={() => onGoTo("upload")} className="rounded-lg bg-white/10 px-3 py-1.5 text-[11.5px] font-semibold transition hover:bg-white/20">
                Upload report
              </button>
            )}
            <button onClick={() => onGoTo("ask")} className="rounded-lg bg-white/10 px-3 py-1.5 text-[11.5px] font-semibold transition hover:bg-white/20">
              Ask the Report
            </button>
            <button onClick={() => onGoTo("risk")} className="rounded-lg bg-white/10 px-3 py-1.5 text-[11.5px] font-semibold transition hover:bg-white/20">
              View risk chain
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
