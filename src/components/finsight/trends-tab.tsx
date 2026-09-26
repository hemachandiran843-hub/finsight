"use client";

import {
  Bar, BarChart, CartesianGrid, ComposedChart, Legend, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { History } from "lucide-react";
import type { AnalysisPackage } from "@/lib/finsight/types";
import { SectionHeader } from "./ui-bits";
import { cn } from "@/lib/utils";

const NAVY = "#1E3A5F";
const TEAL = "#0E7490";
const EMERALD = "#059669";
const AMBER = "#D97706";
const ROSE = "#DC2626";
const GOLD = "#B8860B";

const tooltipStyle = {
  borderRadius: 10,
  border: "1px solid #e2e8f0",
  boxShadow: "0 8px 24px rgba(10,27,51,0.08)",
  fontSize: 12,
};

export function TrendsTab({ pkg }: { pkg: AnalysisPackage }) {
  const data = pkg.trend_series;

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Historical Trends & Early Signal Memory"
        subtitle={`Reported figures across ${pkg.periods.join(" → ")}. Memory streaks flag persistent same-direction movements.`}
      />

      <div className="grid gap-4 xl:grid-cols-2">
        {/* Revenue / EBITDA / Net profit */}
        <ChartCard title="Growth vs profitability" note="Revenue keeps rising while EBITDA and net profit decline.">
          <ResponsiveContainer width="100%" height={260}>
            <ComposedChart data={data} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
              <XAxis dataKey="period" tick={{ fontSize: 11, fill: "#64748b" }} />
              <YAxis tick={{ fontSize: 11, fill: "#64748b" }} label={{ value: "₹ Cr", angle: -90, position: "insideLeft", style: { fontSize: 10, fill: "#94a3b8" } }} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v: number | string) => `₹${Number(v).toLocaleString("en-IN")} Cr`} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="revenue" name="Revenue" fill={NAVY} radius={[4, 4, 0, 0]} barSize={30} />
              <Line type="monotone" dataKey="ebitda" name="EBITDA" stroke={TEAL} strokeWidth={2.4} dot={{ r: 3.5 }} />
              <Line type="monotone" dataKey="net_profit" name="Net profit" stroke={AMBER} strokeWidth={2.4} dot={{ r: 3.5 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Debt vs cash flow */}
        <ChartCard title="Debt build-up vs cash generation" note="The widening scissors: borrowings up, operating cash flow down.">
          <ResponsiveContainer width="100%" height={260}>
            <ComposedChart data={data} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
              <XAxis dataKey="period" tick={{ fontSize: 11, fill: "#64748b" }} />
              <YAxis tick={{ fontSize: 11, fill: "#64748b" }} label={{ value: "₹ Cr", angle: -90, position: "insideLeft", style: { fontSize: 10, fill: "#94a3b8" } }} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v: number | string) => `₹${Number(v).toLocaleString("en-IN")} Cr`} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="total_debt" name="Total debt" fill={ROSE} radius={[4, 4, 0, 0]} barSize={30} />
              <Line type="monotone" dataKey="op_cashflow" name="Operating cash flow" stroke={EMERALD} strokeWidth={2.4} dot={{ r: 3.5 }} />
              <Line type="monotone" dataKey="cash" name="Cash & equivalents" stroke={TEAL} strokeWidth={2} strokeDasharray="5 3" dot={{ r: 3 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Margins */}
        <ChartCard title="Margin compression" note="EBITDA margin down ~400 bps over two quarters.">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={data} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
              <XAxis dataKey="period" tick={{ fontSize: 11, fill: "#64748b" }} />
              <YAxis tick={{ fontSize: 11, fill: "#64748b" }} unit="%" domain={[0, 25]} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v: number | string) => `${Number(v).toFixed(1)}%`} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Line type="monotone" dataKey="ebitda_margin" name="EBITDA margin" stroke={GOLD} strokeWidth={2.6} dot={{ r: 3.5 }} />
              <Line type="monotone" dataKey="net_margin" name="Net margin" stroke={NAVY} strokeWidth={2.2} dot={{ r: 3.5 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Coverage & liquidity */}
        <ChartCard title="Debt service & liquidity ratios" note="Interest coverage and current ratio both deteriorating.">
          <ResponsiveContainer width="100%" height={240}>
            <ComposedChart data={data} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
              <XAxis dataKey="period" tick={{ fontSize: 11, fill: "#64748b" }} />
              <YAxis yAxisId="l" tick={{ fontSize: 11, fill: "#64748b" }} unit="x" domain={[0, 10]} />
              <YAxis yAxisId="r" orientation="right" tick={{ fontSize: 11, fill: "#64748b" }} domain={[0, 2]} />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Line yAxisId="l" type="monotone" dataKey="interest_coverage" name="Interest coverage (x)" stroke={ROSE} strokeWidth={2.4} dot={{ r: 3.5 }} />
              <Line yAxisId="r" type="monotone" dataKey="current_ratio" name="Current ratio (x)" stroke={TEAL} strokeWidth={2.4} dot={{ r: 3.5 }} />
              <Bar yAxisId="l" dataKey="finance_cost" name="Finance cost (₹ Cr)" fill="#F1D9A8" radius={[4, 4, 0, 0]} barSize={26} />
            </ComposedChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Early signal memory */}
      <div>
        <div className="mb-3 flex items-center gap-2">
          <History className="h-4 w-4 text-[#0A1B33]" />
          <h3 className="text-sm font-bold text-slate-900">Early Signal Memory — consecutive-period streaks</h3>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {pkg.memory.filter((m) => m.adverse).map((m) => (
            <div key={m.key} className={cn("rounded-xl border bg-white p-4 shadow-sm", m.streak >= 2 ? "border-rose-200" : "border-slate-200")}>
              <div className="flex items-start justify-between gap-2">
                <p className="text-[13px] font-bold text-slate-800">{m.label}</p>
                {m.streak >= 2 && (
                  <span className="rounded-full border border-rose-200 bg-rose-50 px-2 py-0.5 text-[10.5px] font-bold uppercase tracking-wide text-rose-600">
                    {m.streak + 1}-period streak
                  </span>
                )}
              </div>
              <p className="mt-2 text-[12.5px] leading-relaxed text-slate-600">{m.message}</p>
              <div className="mt-3 flex items-end gap-1.5">
                {m.series.map((v, i) => {
                  const max = Math.max(...m.series, 1);
                  const min = 0;
                  const h = Math.max(8, ((v - min) / (max - min || 1)) * 64);
                  return (
                    <div key={i} className="flex flex-1 flex-col items-center gap-1">
                      <span className="text-[10px] font-semibold tabular-nums text-slate-500">{v.toLocaleString("en-IN")}</span>
                      <div className="w-full rounded-sm" style={{ height: h, backgroundColor: m.adverse ? (m.direction === "up" ? "#DC2626" : "#D97706") : "#059669", opacity: 0.35 + (i / m.series.length) * 0.65 }} />
                      <span className="text-[9.5px] text-slate-400">{pkg.periods[i]?.split(" ")[0]}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ChartCard({ title, note, children }: { title: string; note: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-[13.5px] font-bold text-slate-800">{title}</h3>
      <p className="mb-2 mt-0.5 text-[11.5px] text-slate-400">{note}</p>
      {children}
    </div>
  );
}
