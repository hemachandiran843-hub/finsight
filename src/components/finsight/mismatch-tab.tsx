"use client";

import { Quote, Database, ShieldQuestion, ClipboardList, AlertOctagon } from "lucide-react";
import type { AnalysisPackage, Evidence, Mismatch } from "@/lib/finsight/types";
import { EvidenceChips, SectionHeader } from "./ui-bits";

export function MismatchTab({ pkg, onOpenEvidence }: {
  pkg: AnalysisPackage;
  onOpenEvidence: (ev: Evidence) => void;
}) {
  if (!pkg.mismatches.length) {
    return (
      <div>
        <SectionHeader title="Statement–Data Mismatch" subtitle="Management narrative vs reported numbers." />
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
          No statement–data mismatches were detected for the analysed filing. This does not constitute any assurance;
          verification remains the analyst&apos;s responsibility.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <SectionHeader
        title="Statement–Data Mismatch"
        subtitle="Management statements are compared with reported figures. Mismatches are verification flags — never conclusions of wrongdoing."
      />

      <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
        <ShieldQuestion className="mt-0.5 h-4.5 w-4.5 shrink-0 text-amber-600" />
        <p className="text-[12.5px] leading-relaxed text-amber-800">
          <span className="font-bold">Platform policy:</span> the engine never alleges fraud. A mismatch means the
          narrative and the numbers diverge enough to <span className="font-semibold">require analyst verification</span>.
          Timing differences, definitional differences or new events may explain the gap.
        </p>
      </div>

      {pkg.mismatches.map((mm) => <MismatchCard key={mm.id} mm={mm} pkg={pkg} onOpenEvidence={onOpenEvidence} />)}
    </div>
  );
}

function MismatchCard({ mm, pkg, onOpenEvidence }: { mm: Mismatch; pkg: AnalysisPackage; onOpenEvidence: (ev: Evidence) => void }) {
  const statementEv = mm.statement_source ? pkg.evidence.find((e) => e.id === mm.statement_source) : undefined;
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50/70 px-5 py-2.5">
        <span className="font-mono text-[11px] font-bold text-slate-400">{mm.id}</span>
        {mm.period && <span className="text-[11px] font-semibold text-slate-500">Statement period: {mm.period}</span>}
      </div>

      <div className="grid gap-0 lg:grid-cols-2">
        {/* Statement side */}
        <div className="border-b border-slate-100 p-5 lg:border-b-0 lg:border-r">
          <p className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            <Quote className="h-3.5 w-3.5" /> Management statement
          </p>
          <blockquote className="mt-2.5 rounded-lg border-l-4 border-[#0A1B33] bg-slate-50 px-4 py-3 text-[13.5px] font-medium italic leading-relaxed text-slate-800">
            “{mm.statement}”
          </blockquote>
          <p className="mt-2 text-[11.5px] text-slate-500">
            {statementEv ? statementEv.document : "Management narrative"}{mm.page ? ` · page ${mm.page}` : ""}{mm.section ? ` · ${mm.section}` : ""}
          </p>
          {statementEv && (
            <div className="mt-2.5"><EvidenceChips ids={[statementEv.id]} registry={pkg.evidence} onOpen={onOpenEvidence} /></div>
          )}
        </div>

        {/* Data side */}
        <div className="p-5">
          <p className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            <Database className="h-3.5 w-3.5" /> Reported data
          </p>
          <div className="mt-2.5 space-y-2">
            {mm.data_points.map((dp, i) => (
              <div key={i} className="flex items-center justify-between gap-3 rounded-lg border border-slate-100 bg-slate-50/60 px-3.5 py-2">
                <span className="text-xs font-medium text-slate-700">{dp.label}</span>
                <span className="text-xs font-bold tabular-nums text-rose-600">{dp.detail}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="border-t border-slate-100 bg-amber-50/60 px-5 py-3">
        <p className="flex items-center gap-2 text-[12.5px] font-bold text-amber-800">
          <AlertOctagon className="h-4 w-4" /> {mm.verdict}
        </p>
        <p className="mt-1 text-[11.5px] italic text-amber-700">{mm.disclaimer}</p>
      </div>

      <div className="px-5 py-4">
        <p className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
          <ClipboardList className="h-3.5 w-3.5" /> Suggested verification steps
        </p>
        <ol className="mt-2 space-y-1.5">
          {mm.verification_steps.map((s, i) => (
            <li key={i} className="flex gap-2 text-[12.5px] leading-relaxed text-slate-600">
              <span className="flex h-4.5 w-4.5 shrink-0 items-center justify-center rounded-full bg-slate-100 text-[10px] font-bold text-slate-500">{i + 1}</span>
              {s}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
