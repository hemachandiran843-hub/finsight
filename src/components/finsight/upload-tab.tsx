"use client";

import { useRef, useState } from "react";
import { CheckCircle2, CloudUpload, Download, FileWarning, Loader2, RefreshCcw, ShieldCheck, XCircle } from "lucide-react";
import { toast } from "sonner";
import { demoReportUrl, uploadReport } from "@/lib/finsight/api";
import type { AnalysisPackage } from "@/lib/finsight/types";
import { cn } from "@/lib/utils";

const PERIODS = ["Q1 FY26", "Q2 FY26", "Q3 FY26"];
const MAX_MB = 20;

export function UploadTab({ token, onAnalysed, onLoadDemo, busyDemo }: {
  token: string;
  onAnalysed: (pkg: AnalysisPackage, reportId: number) => void;
  onLoadDemo: () => void;
  busyDemo: boolean;
}) {
  const [drag, setDrag] = useState(false);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<{ mode: string; company: string; period: string; pages: number; metrics: string[] } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [stages, setStages] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  function validate(file: File): string | null {
    if (!file.name.toLowerCase().endsWith(".pdf")) return "Only PDF files are accepted.";
    if (file.size > MAX_MB * 1024 * 1024) return `File exceeds the ${MAX_MB} MB limit.`;
    if (file.size < 1024) return "File looks empty or corrupted.";
    return null;
  }

  async function handleFile(file: File) {
    setError(null);
    setResult(null);
    const v = validate(file);
    if (v) {
      setError(v);
      toast.error(v);
      return;
    }
    setBusy(true);
    setStages(["Validating file…"]);
    const t1 = setTimeout(() => setStages((s) => [...s, "Extracting text & tables (PyMuPDF / pdfplumber)…"]), 400);
    const t2 = setTimeout(() => setStages((s) => [...s, "Parsing financial metrics…"]), 1100);
    const t3 = setTimeout(() => setStages((s) => [...s, "Running signal engine & risk chain…"]), 1900);
    try {
      const res = await uploadReport(token, file);
      setStages((s) => [...s, "Done."]);
      setResult({
        mode: String(res.extraction.mode ?? "n/a"),
        company: String(res.extraction.company ?? res.analysis.company.name),
        period: String(res.extraction.period ?? res.analysis.period_label),
        pages: Number(res.extraction.pages ?? 0),
        metrics: (res.extraction.metrics_found as string[]) ?? [],
      });
      toast.success("Report analysed — dashboard updated.");
      setTimeout(() => onAnalysed(res.analysis, res.report_id), 500);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Upload failed.";
      setError(msg);
      toast.error(msg);
    } finally {
      clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_360px]">
      <div className="space-y-4">
        <div
          onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDrag(false);
            const f = e.dataTransfer.files?.[0];
            if (f) handleFile(f);
          }}
          onClick={() => inputRef.current?.click()}
          className={cn(
            "flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed bg-white p-10 text-center transition",
            drag ? "border-[#C9A227] bg-amber-50/40" : "border-slate-300 hover:border-[#0A1B33]/40 hover:bg-slate-50/60",
            busy && "pointer-events-none opacity-70",
          )}
        >
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf,.pdf"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) handleFile(f);
              e.target.value = "";
            }}
          />
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#0A1B33]">
            {busy ? <Loader2 className="h-6 w-6 animate-spin text-[#E4C158]" /> : <CloudUpload className="h-6 w-6 text-[#E4C158]" />}
          </div>
          <p className="mt-4 text-[15px] font-bold text-slate-800">
            {busy ? "Analysing report…" : "Drop a quarterly report PDF here"}
          </p>
          <p className="mt-1 max-w-md text-[12.5px] leading-relaxed text-slate-500">
            or click to browse. PDF only, up to {MAX_MB} MB and 200 pages. Files are validated server-side
            (magic-byte check) before parsing. Try the sample reports on the right for a guided demo.
          </p>
        </div>

        {busy && (
          <div className="rounded-xl border border-slate-200 bg-white p-4.5 shadow-sm">
            <p className="text-[12px] font-bold uppercase tracking-wider text-slate-500">Processing pipeline</p>
            <ul className="mt-2.5 space-y-1.5">
              {stages.map((s, i) => (
                <li key={i} className="flex items-center gap-2 text-[12.5px] text-slate-600">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" /> {s}
                </li>
              ))}
            </ul>
          </div>
        )}

        {error && (
          <div className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3">
            <XCircle className="mt-0.5 h-4.5 w-4.5 shrink-0 text-rose-500" />
            <div>
              <p className="text-[13px] font-bold text-rose-700">Upload rejected</p>
              <p className="mt-0.5 text-[12.5px] text-rose-600">{error}</p>
            </div>
          </div>
        )}

        {result && (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-4.5">
            <p className="flex items-center gap-2 text-[13.5px] font-bold text-emerald-800">
              <CheckCircle2 className="h-4.5 w-4.5" /> Analysis ready — loading dashboard…
            </p>
            <div className="mt-2.5 grid gap-x-6 gap-y-1 text-[12px] text-emerald-900/80 sm:grid-cols-2">
              <p><span className="font-semibold">Company:</span> {result.company}</p>
              <p><span className="font-semibold">Period:</span> {result.period}</p>
              <p><span className="font-semibold">Extraction mode:</span> {result.mode}</p>
              <p><span className="font-semibold">Pages parsed:</span> {result.pages}</p>
            </div>
          </div>
        )}

        <div className="flex items-start gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3.5">
          <ShieldCheck className="mt-0.5 h-4.5 w-4.5 shrink-0 text-emerald-600" />
          <p className="text-[12px] leading-relaxed text-slate-500">
            <span className="font-semibold text-slate-700">Security prototype:</span> role-gated upload (CEO role is
            denied), PDF magic-byte + size validation, isolated upload directory, and every action written to the
            audit log. Production scope adds MFA, encryption at rest, secure document storage and advanced RBAC.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-[13.5px] font-bold text-slate-900">Sample reports (fictitious company)</h3>
          <p className="mt-1 text-[12px] leading-relaxed text-slate-500">
            XYZ Manufacturing Ltd. quarterly filings generated for this prototype. Download one, then upload it —
            the platform recognises the company and period and loads the curated analysis.
          </p>
          <div className="mt-3.5 space-y-2">
            {PERIODS.map((p) => (
              <a
                key={p}
                href={demoReportUrl(p)}
                download
                className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50/70 px-3.5 py-2.5 text-[12.5px] font-semibold text-slate-700 transition hover:border-[#0A1B33]/25 hover:bg-white"
              >
                XYZ Manufacturing — {p}
                <Download className="h-3.5 w-3.5 text-slate-400" />
              </a>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-[#0A1B33]/15 bg-gradient-to-br from-[#0A1B33] to-[#13294B] p-5 text-white shadow-sm">
          <h3 className="text-[13.5px] font-bold">Skip the upload — instant demo</h3>
          <p className="mt-1 text-[12px] leading-relaxed text-slate-300">
            Load the full Q3 FY26 curated analysis with all signals, mismatches, risk chain and evidence.
          </p>
          <button
            onClick={onLoadDemo}
            disabled={busyDemo}
            className="mt-3.5 inline-flex items-center gap-2 rounded-lg bg-[#E4C158] px-4 py-2 text-[12.5px] font-bold text-[#0A1B33] transition hover:bg-[#F0D072] disabled:opacity-60"
          >
            {busyDemo ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCcw className="h-4 w-4" />}
            Load Demo Dataset
          </button>
        </div>

        <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50/70 px-4 py-3.5">
          <FileWarning className="mt-0.5 h-4.5 w-4.5 shrink-0 text-amber-600" />
          <p className="text-[11.5px] leading-relaxed text-amber-800">
            Unknown PDFs are handled with heuristic extraction in Demo Mode: numbers are located by pattern
            matching and flagged as <span className="font-semibold">subject to verification</span>. Figures are never invented.
          </p>
        </div>
      </div>
    </div>
  );
}
