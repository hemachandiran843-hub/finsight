"use client";

import { TrendingDown, TrendingUp, Minus } from "lucide-react";
import type { ReactNode } from "react";
import type { Evidence, SignalInput } from "@/lib/finsight/types";
import { cn } from "@/lib/utils";

// ------------------------------------------------------------------ helpers
export const fmtCr = (v: number | null | undefined, digits = 0): string =>
  v === null || v === undefined ? "n/a" : `₹${v.toLocaleString("en-IN", { maximumFractionDigits: digits })}`;

export const fmtNum = (v: number | null | undefined, digits = 1): string =>
  v === null || v === undefined ? "n/a" : v.toLocaleString("en-IN", { maximumFractionDigits: digits });

export const fmtPct = (v: number | null | undefined, digits = 1): string =>
  v === null || v === undefined ? "n/a" : `${v > 0 ? "+" : ""}${v.toFixed(digits)}%`;

// ------------------------------------------------------------------ severity
export const SEV_STYLE: Record<string, { chip: string; dot: string; bar: string; label: string }> = {
  high: { chip: "bg-rose-50 text-rose-700 border-rose-200", dot: "bg-rose-500", bar: "bg-rose-500", label: "High" },
  medium: { chip: "bg-amber-50 text-amber-700 border-amber-200", dot: "bg-amber-500", bar: "bg-amber-500", label: "Medium" },
  low: { chip: "bg-slate-50 text-slate-600 border-slate-200", dot: "bg-slate-400", bar: "bg-slate-400", label: "Low" },
};

export function SeverityBadge({ severity, status }: { severity: string; status?: string }) {
  const s = SEV_STYLE[severity] ?? SEV_STYLE.low;
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide", s.chip)}>
      <span className={cn("h-1.5 w-1.5 rounded-full", s.dot)} />
      {s.label} severity{status ? ` · ${status}` : ""}
    </span>
  );
}

export function DirChip({ label, direction, value }: { label: string; direction: string; value: string }) {
  const up = direction === "up";
  const down = direction === "down";
  return (
    <span className="inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-2 py-1 text-[11.5px] font-medium text-slate-700">
      {label}
      <span className={cn("inline-flex items-center gap-0.5 font-semibold tabular-nums",
        up && "text-rose-600", down && "text-emerald-600", !up && !down && "text-slate-500")}>
        {up && <TrendingUp className="h-3 w-3" />}
        {down && <TrendingDown className="h-3 w-3" />}
        {!up && !down && <Minus className="h-3 w-3" />}
        {value}
      </span>
    </span>
  );
}

// ------------------------------------------------------------------ kpi card
export function KpiCard({ label, current, first, delta, unit, invert, spark, color }: {
  label: string;
  current: number | null;
  first: number | null;
  delta: number | null;
  unit: "₹ Cr" | "%" | "x";
  invert?: boolean; // true when decrease is adverse (e.g. cash flow) — red if down
  spark?: number[];
  color?: string;
}) {
  const digits = unit === "%" || unit === "x" ? 1 : 0;
  const bad = delta === null ? false : invert ? delta < 0 : delta > 0;
  const good = delta === null ? false : invert ? delta > 0 : delta < 0;
  const showDelta = delta !== null && Math.abs(delta) >= 0.05;
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">{label}</p>
      <p className="mt-1.5 text-[22px] font-bold tabular-nums text-slate-900 leading-tight">
        {unit === "₹ Cr" ? fmtCr(current, digits) : `${fmtNum(current, digits)}${unit === "%" ? "%" : "x"}`}
      </p>
      <div className="mt-1 flex items-center justify-between gap-2">
        <p className="text-[11px] text-slate-400 tabular-nums">
          {unit === "₹ Cr" ? fmtCr(first, digits) : `${fmtNum(first, digits)}${unit === "%" ? "%" : "x"}`} · Q1
        </p>
        {showDelta && (
          <span className={cn("inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[11px] font-semibold tabular-nums",
            bad && "bg-rose-50 text-rose-600", good && "bg-emerald-50 text-emerald-600",
            !bad && !good && "bg-slate-50 text-slate-500")}>
            {delta > 0 ? "▲" : delta < 0 ? "▼" : "—"} {Math.abs(delta).toFixed(1)}%
          </span>
        )}
      </div>
      {spark && spark.length >= 2 && (
        <div className="mt-2 flex h-8 items-end gap-1">
          {spark.map((v, i) => {
            const max = Math.max(...spark), min = Math.min(...spark);
            const h = max === min ? 60 : 20 + ((v - min) / (max - min)) * 80;
            return (
              <div key={i} className="flex-1 rounded-sm"
                style={{ height: `${h}%`, backgroundColor: color ?? (bad ? "#e11d48" : "#0f766e"), opacity: 0.25 + (i / spark.length) * 0.75 }} />
            );
          })}
        </div>
      )}
    </div>
  );
}

// ------------------------------------------------------------------ evidence chip
export function EvidenceChip({ ev, onClick }: { ev: Pick<Evidence, "id" | "page" | "document">; onClick?: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={`${ev.document}${ev.page ? ` — page ${ev.page}` : ""}`}
      className="inline-flex max-w-full items-center gap-1 rounded-md border border-teal-200 bg-teal-50 px-2 py-0.5 text-[11px] font-semibold text-teal-800 transition hover:bg-teal-100"
    >
      <span className="font-mono">{ev.id}</span>
      {ev.page ? <span className="font-normal text-teal-600">p.{ev.page}</span> : null}
    </button>
  );
}

export function EvidenceChips({ ids, registry, onOpen }: { ids: string[]; registry: Evidence[]; onOpen?: (ev: Evidence) => void }) {
  const found = ids.map((id) => registry.find((e) => e.id === id)).filter(Boolean) as Evidence[];
  if (!found.length) return null;
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {found.map((ev) => <EvidenceChip key={ev.id} ev={ev} onClick={onOpen ? () => onOpen(ev) : undefined} />)}
    </div>
  );
}

// ------------------------------------------------------------------ fusion input chips
export function FusionInput({ input }: { input: SignalInput }) {
  const up = input.direction === "up";
  const down = input.direction === "down";
  return (
    <div className={cn("flex items-center justify-between gap-3 rounded-lg border px-3 py-2",
      up ? "border-rose-100 bg-rose-50/60" : down ? "border-emerald-100 bg-emerald-50/60" : "border-slate-100 bg-slate-50")}>
      <span className="text-xs font-medium text-slate-700">{input.label}</span>
      <span className={cn("inline-flex items-center gap-1 text-xs font-bold tabular-nums",
        up && "text-rose-600", down && "text-emerald-600", !up && !down && "text-slate-500")}>
        {up && <TrendingUp className="h-3.5 w-3.5" />}
        {down && <TrendingDown className="h-3.5 w-3.5" />}
        {!up && !down && <Minus className="h-3.5 w-3.5" />}
        {input.value}
      </span>
    </div>
  );
}

// ------------------------------------------------------------------ section header
export function SectionHeader({ title, subtitle, right }: { title: string; subtitle?: string; right?: ReactNode }) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 className="text-lg font-bold tracking-tight text-slate-900">{title}</h2>
        {subtitle && <p className="mt-0.5 text-sm text-slate-500">{subtitle}</p>}
      </div>
      {right}
    </div>
  );
}

// ------------------------------------------------------------------ fact/analysis legend
export function FactLegend() {
  return (
    <div className="flex flex-wrap items-center gap-2 text-[11px]">
      <span className="rounded-full border border-slate-300 bg-slate-50 px-2.5 py-1 font-semibold text-slate-600">Reported Fact</span>
      <span className="text-slate-300">→</span>
      <span className="rounded-full border border-teal-200 bg-teal-50 px-2.5 py-1 font-semibold text-teal-700">AI Analysis</span>
      <span className="text-slate-300">→</span>
      <span className="rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 font-semibold text-amber-700">Potential Significance</span>
    </div>
  );
}
