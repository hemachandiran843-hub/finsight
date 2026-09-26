"use client";

import { ArrowDown, GitMerge, Info } from "lucide-react";
import { useState } from "react";
import type { AnalysisPackage, Evidence, Signal } from "@/lib/finsight/types";
import { DirChip, EvidenceChips, SectionHeader, SeverityBadge } from "./ui-bits";
import { cn } from "@/lib/utils";

const FLAGSHIP_ID = "SIG-01";

export function SignalsTab({ pkg, onOpenEvidence }: {
  pkg: AnalysisPackage;
  onOpenEvidence: (ev: Evidence) => void;
}) {
  const flagship = pkg.signals.find((s) => s.id === FLAGSHIP_ID);
  const rest = pkg.signals.filter((s) => s.id !== FLAGSHIP_ID);

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Financial Signal Fusion"
        subtitle="Multiple indicators are combined into named patterns. Severity reflects the strength of the pattern, not a rating action."
        right={
          <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-[11.5px] text-slate-500">
            <GitMerge className="h-3.5 w-3.5" />
            Rule engine · {pkg.ai_enabled ? "LLM-assisted" : "Demo Mode"}
          </div>
        }
      />

      {/* Flagship fusion visual */}
      {flagship && (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-100 bg-[#0A1B33] px-5 py-3.5">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">Signal fusion</p>
            <h3 className="mt-0.5 text-base font-bold text-white">{flagship.title}</h3>
          </div>
          <div className="grid gap-6 p-5 lg:grid-cols-[minmax(280px,420px)_1fr]">
            <div className="space-y-2">
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Detected inputs</p>
              {flagship.inputs.map((inp, i) => <DirChip key={i} label={inp.label} direction={inp.direction} value={inp.value} />)}
              <div className="flex justify-center py-1">
                <ArrowDown className="h-5 w-5 animate-bounce text-[#C9A227]" />
              </div>
              <div className="rounded-lg border border-rose-200 bg-rose-50 px-3.5 py-2.5 text-center">
                <p className="text-[13px] font-bold text-rose-700">{flagship.title}</p>
                <p className="text-[11px] font-medium text-rose-500">Fused pattern · severity {flagship.severity}</p>
              </div>
            </div>
            <div className="space-y-3">
              <SeverityBadge severity={flagship.severity} status={flagship.status} />
              <div>
                <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Fusion logic</p>
                <p className="mt-1 text-[13px] leading-relaxed text-slate-600">{flagship.logic}</p>
              </div>
              <div>
                <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">AI analysis</p>
                <p className="mt-1 text-[13px] leading-relaxed text-slate-700">{flagship.explanation}</p>
              </div>
              <EvidenceChips ids={flagship.evidence_ids} registry={pkg.evidence} onOpen={onOpenEvidence} />
            </div>
          </div>
        </div>
      )}

      {/* All signals */}
      <div className="grid gap-4 xl:grid-cols-2">
        {rest.map((s) => <SignalCard key={s.id} signal={s} pkg={pkg} onOpenEvidence={onOpenEvidence} />)}
      </div>
    </div>
  );
}

function SignalCard({ signal, pkg, onOpenEvidence }: { signal: Signal; pkg: AnalysisPackage; onOpenEvidence: (ev: Evidence) => void }) {
  const [open, setOpen] = useState(false);
  const isMemory = signal.category === "Early Signal Memory";
  return (
    <div className={cn("rounded-xl border bg-white p-5 shadow-sm", signal.severity === "high" ? "border-rose-200" : "border-slate-200")}>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-[11px] font-bold text-slate-400">{signal.id}</span>
            <span className="rounded-md bg-slate-100 px-1.5 py-0.5 text-[10.5px] font-semibold uppercase tracking-wide text-slate-500">
              {signal.category}
            </span>
          </div>
          <h3 className="mt-1 text-[15px] font-bold text-slate-900">{signal.title}</h3>
        </div>
        <SeverityBadge severity={signal.severity} status={signal.status} />
      </div>

      <div className="mt-3.5 flex flex-wrap gap-1.5">
        {signal.inputs.map((inp, i) => <DirChip key={i} label={inp.label} direction={inp.direction} value={inp.value} />)}
      </div>

      <p className="mt-3 text-[13px] leading-relaxed text-slate-600">{signal.explanation}</p>

      {open && (
        <div className="mt-3 space-y-2 rounded-lg bg-slate-50 p-3.5">
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Why this fired (logic)</p>
          <p className="text-[12.5px] leading-relaxed text-slate-600">{signal.logic}</p>
        </div>
      )}

      <div className="mt-4 flex flex-wrap items-center justify-between gap-2">
        <EvidenceChips ids={signal.evidence_ids} registry={pkg.evidence} onOpen={onOpenEvidence} />
        <button
          onClick={() => setOpen((o) => !o)}
          className="inline-flex items-center gap-1 text-[11.5px] font-semibold text-slate-500 hover:text-slate-800"
        >
          <Info className="h-3.5 w-3.5" /> {open ? "Hide logic" : "Why this fired?"}
        </button>
      </div>
      {isMemory && (
        <p className="mt-2 rounded-lg border border-amber-100 bg-amber-50 px-3 py-2 text-[11.5px] text-amber-800">
          Early-signal memory: this pattern persisted across consecutive reported periods.
        </p>
      )}
    </div>
  );
}
