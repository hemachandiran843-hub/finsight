"use client";

import { useState } from "react";
import { FileText, MessageSquareQuote, Search, ArrowRight } from "lucide-react";
import type { AnalysisPackage, Evidence } from "@/lib/finsight/types";
import { SectionHeader } from "./ui-bits";
import { cn } from "@/lib/utils";

type Filter = "all" | "reported_fact" | "management_statement";

export function EvidenceTab({ pkg, focusId }: { pkg: AnalysisPackage; focusId: string | null }) {
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");

  const list = pkg.evidence.filter((e) => {
    if (filter !== "all" && e.kind !== filter) return false;
    if (query && !(`${e.quote} ${e.document} ${e.section}`.toLowerCase().includes(query.toLowerCase()))) return false;
    return true;
  });
  const focus = focusId ? pkg.evidence.find((e) => e.id === focusId) : undefined;

  return (
    <div className="space-y-5">
      <SectionHeader
        title="Evidence & Explainability"
        subtitle="Every AI insight resolves to source document, page, section and extracted text: AI Insight → Evidence → Original Document."
      />

      {focus && (
        <div className="rounded-xl border-2 border-teal-300 bg-teal-50/50 p-4 shadow-sm">
          <p className="text-[11px] font-bold uppercase tracking-wider text-teal-700">Evidence referenced by the insight you clicked</p>
          <div className="mt-2.5 flex items-center gap-2 text-[11.5px] text-slate-600">
            <span className="rounded-full bg-white px-2.5 py-1 font-semibold shadow-sm">AI Insight</span>
            <ArrowRight className="h-3.5 w-3.5 text-teal-500" />
            <span className="rounded-full bg-white px-2.5 py-1 font-semibold shadow-sm">Evidence {focus.id}</span>
            <ArrowRight className="h-3.5 w-3.5 text-teal-500" />
            <span className="rounded-full bg-white px-2.5 py-1 font-semibold shadow-sm">{focus.document}{focus.page ? ` · p.${focus.page}` : ""}</span>
          </div>
          <blockquote className="mt-3 rounded-lg border-l-4 border-teal-500 bg-white px-4 py-3 text-[13px] italic leading-relaxed text-slate-700">
            “{focus.quote}”
          </blockquote>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex rounded-lg border border-slate-200 bg-white p-0.5 shadow-sm">
          {([
            ["all", `All (${pkg.evidence.length})`],
            ["reported_fact", "Reported facts"],
            ["management_statement", "Management statements"],
          ] as [Filter, string][]).map(([val, label]) => (
            <button
              key={val}
              onClick={() => setFilter(val)}
              className={cn(
                "rounded-md px-3 py-1.5 text-[12px] font-semibold transition",
                filter === val ? "bg-[#0A1B33] text-white" : "text-slate-500 hover:text-slate-800",
              )}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="relative min-w-[220px] flex-1">
          <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search quotes, sections, documents…"
            className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-[13px] outline-none transition focus:border-[#0A1B33] focus:ring-2 focus:ring-[#0A1B33]/10"
          />
        </div>
      </div>

      <div className="space-y-3">
        {list.map((ev) => <EvidenceRow key={ev.id} ev={ev} highlighted={ev.id === focusId} />)}
        {!list.length && (
          <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
            No evidence matches the current filter.
          </div>
        )}
      </div>
    </div>
  );
}

function EvidenceRow({ ev, highlighted }: { ev: Evidence; highlighted: boolean }) {
  const isStatement = ev.kind === "management_statement";
  return (
    <div className={cn(
      "rounded-xl border bg-white p-4 shadow-sm transition",
      highlighted ? "border-teal-400 ring-2 ring-teal-200" : "border-slate-200",
    )}>
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[11px] font-bold text-slate-600">{ev.id}</span>
        <span className={cn(
          "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10.5px] font-semibold uppercase tracking-wide",
          isStatement ? "border border-violet-200 bg-violet-50 text-violet-700" : "border border-teal-200 bg-teal-50 text-teal-700",
        )}>
          {isStatement ? <MessageSquareQuote className="h-3 w-3" /> : <FileText className="h-3 w-3" />}
          {isStatement ? "Management statement" : "Reported fact"}
        </span>
        {ev.current === false && (
          <span className="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-[10.5px] font-semibold text-slate-500">prior filing</span>
        )}
      </div>
      <blockquote className="mt-2.5 rounded-lg bg-slate-50 px-4 py-3 text-[13px] leading-relaxed text-slate-700">
        “{ev.quote}”
      </blockquote>
      <div className="mt-2.5 grid gap-x-6 gap-y-1 text-[11.5px] text-slate-500 sm:grid-cols-3">
        <p><span className="font-semibold text-slate-600">Source:</span> {ev.document}</p>
        <p><span className="font-semibold text-slate-600">Page:</span> {ev.page ?? "n/a"}</p>
        <p><span className="font-semibold text-slate-600">Section:</span> {ev.section}</p>
      </div>
    </div>
  );
}
