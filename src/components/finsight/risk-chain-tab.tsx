"use client";

import { ArrowDown, GitBranch, ShieldAlert } from "lucide-react";
import type { AnalysisPackage } from "@/lib/finsight/types";
import { SectionHeader } from "./ui-bits";
import { cn } from "@/lib/utils";

export function RiskChainTab({ pkg }: { pkg: AnalysisPackage }) {
  if (!pkg.risk_chain.length) {
    return (
      <div>
        <SectionHeader title="Risk Chain" subtitle="Propagation path from cost pressure to financing risk." />
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
          A risk chain needs at least one reported period with cost, margin, cash-flow and debt figures.
          Upload a quarterly report containing these sections to build the chain.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <SectionHeader
        title="Risk Chain"
        subtitle="How the reported numbers propagate from cost pressure to potential financing pressure. Each node is grounded in the Evidence panel."
      />

      <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
        <ShieldAlert className="mt-0.5 h-4.5 w-4.5 shrink-0 text-amber-600" />
        <p className="text-[12.5px] leading-relaxed text-amber-800">
          This chain is an <span className="font-semibold">analytical narrative</span> connecting reported facts — it is
          neither a credit rating, a loan decision, nor a prediction. If the underlying trends reverse, the chain weakens.
        </p>
      </div>

      <div className="mx-auto max-w-3xl">
        {pkg.risk_chain.map((node, i) => (
          <div key={node.id}>
            <div
              className={cn(
                "flex items-start gap-4 rounded-xl border bg-white p-4.5 shadow-sm transition hover:shadow-md",
                node.severity === "high" ? "border-rose-200" : node.severity === "medium" ? "border-amber-200" : "border-slate-200",
              )}
            >
              <div className={cn(
                "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-[13px] font-bold text-white",
                node.severity === "high" ? "bg-rose-500" : node.severity === "medium" ? "bg-amber-500" : "bg-slate-400",
              )}>
                {i + 1}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-[14px] font-bold text-slate-900">{node.label}</h3>
                  {i === pkg.risk_chain.length - 1 && (
                    <span className="inline-flex items-center gap-1 rounded-full bg-[#0A1B33] px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-[#E4C158]">
                      <GitBranch className="h-3 w-3" /> Chain outcome
                    </span>
                  )}
                </div>
                <p className="mt-1 text-[12.5px] leading-relaxed text-slate-600">{node.detail}</p>
              </div>
            </div>
            {i < pkg.risk_chain.length - 1 && (
              <div className="flex justify-center py-1">
                <ArrowDown className="h-5 w-5 text-slate-300" />
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mx-auto max-w-3xl rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Chain summary</p>
        <p className="mt-1.5 text-[13px] leading-relaxed text-slate-600">
          {pkg.risk_chain.length} connected nodes. Breaking the chain at the first node — input costs — is the
          management-stated lever (pricing actions, hedging). The financing-pressure outcome depends on Phase II
          completion, working-capital normalisation and the FY27 refinancing plan.
        </p>
      </div>
    </div>
  );
}
