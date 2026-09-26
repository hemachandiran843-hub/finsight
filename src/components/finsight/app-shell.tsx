"use client";

import { useState } from "react";
import {
  BarChart3, Bell, FileSearch, GitBranch, History, LayoutDashboard, LogOut,
  MessageSquareText, ScrollText, ShieldAlert, Upload,
} from "lucide-react";
import type { AnalysisPackage, Evidence, Role, User } from "@/lib/finsight/types";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { OverviewTab } from "./overview-tab";
import { SignalsTab } from "./signals-tab";
import { MismatchTab } from "./mismatch-tab";
import { TrendsTab } from "./trends-tab";
import { RiskChainTab } from "./risk-chain-tab";
import { EvidenceTab } from "./evidence-tab";
import { AskTab } from "./ask-tab";
import { UploadTab } from "./upload-tab";
import { AuditTab } from "./audit-tab";
import { cn } from "@/lib/utils";

type TabId = "overview" | "signals" | "mismatch" | "trends" | "risk" | "evidence" | "ask" | "upload" | "audit";

const TABS: { id: TabId; label: string; icon: typeof LayoutDashboard; roles: Role[] }[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard, roles: ["ceo", "credit_analyst", "risk_manager"] },
  { id: "signals", label: "Signals", icon: Bell, roles: ["ceo", "credit_analyst", "risk_manager"] },
  { id: "mismatch", label: "Statement–Data Mismatch", icon: ShieldAlert, roles: ["ceo", "credit_analyst", "risk_manager"] },
  { id: "trends", label: "Historical Trends", icon: History, roles: ["ceo", "credit_analyst", "risk_manager"] },
  { id: "risk", label: "Risk Chain", icon: GitBranch, roles: ["ceo", "credit_analyst", "risk_manager"] },
  { id: "evidence", label: "Evidence", icon: FileSearch, roles: ["ceo", "credit_analyst", "risk_manager"] },
  { id: "ask", label: "Ask the Report", icon: MessageSquareText, roles: ["ceo", "credit_analyst", "risk_manager"] },
  { id: "upload", label: "Upload Report", icon: Upload, roles: ["credit_analyst", "risk_manager"] },
  { id: "audit", label: "Audit Log", icon: ScrollText, roles: ["risk_manager"] },
];

export function AppShell({ user, token, pkg, reportId, busyDemo, onLoadDemo, onAnalysed, onLogout }: {
  user: User;
  token: string;
  pkg: AnalysisPackage;
  reportId: number | null;
  busyDemo: boolean;
  onLoadDemo: () => void;
  onAnalysed: (pkg: AnalysisPackage, id: number) => void;
  onLogout: () => void;
}) {
  const [tab, setTab] = useState<TabId>("overview");
  const [evFocus, setEvFocus] = useState<string | null>(null);
  const [evDialog, setEvDialog] = useState<Evidence | null>(null);

  const visible = TABS.filter((t) => t.roles.includes(user.role));

  function openEvidence(ev: Partial<Evidence> & { id?: string }) {
    const full = ev.id ? pkg.evidence.find((e) => e.id === ev.id) : undefined;
    const target = full ?? (ev as Evidence | undefined);
    if (!target) return;
    setEvDialog(target);          // instant popup with the quote
    setEvFocus(target.id);        // and highlight it in the Evidence tab
  }

  return (
    <div className="flex min-h-screen flex-col bg-[#F4F6FA] text-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-[#0A1B33] text-white shadow-md">
        <div className="mx-auto flex max-w-[1440px] items-center justify-between gap-4 px-4 py-3 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-[#C9A227] to-[#9A7B1C]">
              <BarChart3 className="h-5 w-5 text-[#0A1B33]" strokeWidth={2.4} />
            </div>
            <div>
              <p className="text-[15px] font-bold leading-tight tracking-tight">FinSight<span className="text-[#E4C158]"> X</span></p>
              <p className="text-[9.5px] uppercase tracking-[0.18em] text-slate-400">AI Financial Intelligence & Early-Warning</p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <span className="hidden rounded-full border border-emerald-400/30 bg-emerald-400/10 px-2.5 py-1 text-[10.5px] font-semibold text-emerald-300 sm:inline-block">
              {pkg.ai_enabled ? "AI Connected" : "Demo Mode — no API key"}
            </span>
            <span className="hidden rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[10.5px] font-semibold text-slate-300 md:inline-block">
              {pkg.company.name}
            </span>
            <div className="flex items-center gap-2.5 rounded-full border border-white/10 bg-white/5 py-1 pl-1 pr-3">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[#E4C158] text-[11px] font-bold text-[#0A1B33]">
                {user.name.split(" ").map((n) => n[0]).join("")}
              </span>
              <span className="hidden leading-tight sm:block">
                <span className="block text-[11.5px] font-semibold">{user.name}</span>
                <span className="block text-[9.5px] uppercase tracking-wider text-[#E4C158]">{user.role_label}</span>
              </span>
            </div>
            <button
              onClick={onLogout}
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-white/5 transition hover:bg-white/15"
              aria-label="Log out"
              title="Log out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <nav className="border-t border-white/10">
          <div className="mx-auto flex max-w-[1440px] gap-0.5 overflow-x-auto px-4 lg:px-8" role="tablist" aria-label="Dashboard sections">
            {visible.map((t) => (
              <button
                key={t.id}
                role="tab"
                aria-selected={tab === t.id}
                onClick={() => setTab(t.id)}
                className={cn(
                  "flex shrink-0 items-center gap-1.5 border-b-2 px-3.5 py-2.5 text-[12.5px] font-semibold transition",
                  tab === t.id
                    ? "border-[#E4C158] text-white"
                    : "border-transparent text-slate-400 hover:text-slate-200",
                )}
              >
                <t.icon className="h-3.5 w-3.5" />
                {t.label}
              </button>
            ))}
          </div>
        </nav>
      </header>

      {/* Content */}
      <main className="mx-auto w-full max-w-[1440px] flex-1 px-4 py-6 lg:px-8">
        {tab === "overview" && (
          <OverviewTab pkg={pkg} role={user.role} onOpenEvidence={openEvidence} onGoTo={(t) => setTab(t as TabId)} />
        )}
        {tab === "signals" && <SignalsTab pkg={pkg} onOpenEvidence={openEvidence} />}
        {tab === "mismatch" && <MismatchTab pkg={pkg} onOpenEvidence={openEvidence} />}
        {tab === "trends" && <TrendsTab pkg={pkg} />}
        {tab === "risk" && <RiskChainTab pkg={pkg} />}
        {tab === "evidence" && <EvidenceTab pkg={pkg} focusId={evFocus} />}
        {tab === "ask" && <AskTab token={token} reportId={reportId} onOpenEvidence={openEvidence} />}
        {tab === "upload" && (
          <UploadTab token={token} onAnalysed={onAnalysed} onLoadDemo={onLoadDemo} busyDemo={busyDemo} />
        )}
        {tab === "audit" && <AuditTab token={token} />}
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-[1440px] px-4 py-4 lg:px-8">
          <p className="text-[11px] leading-relaxed text-slate-400">{pkg.safety_note}</p>
          <p className="mt-1 text-[10.5px] text-slate-300">
            FinSight X prototype · Demo company data is fictitious · Security prototype: RBAC, file validation,
            audit log — MFA, encryption & monitoring are production future scope.
          </p>
        </div>
      </footer>

      {/* Evidence dialog */}
      <Dialog open={!!evDialog} onOpenChange={(o) => !o && setEvDialog(null)}>
        <DialogContent className="max-w-xl">
          {evDialog && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2 text-[15px]">
                  <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[12px] font-bold text-slate-600">{evDialog.id}</span>
                  Evidence
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-3">
                <blockquote className="rounded-lg border-l-4 border-teal-500 bg-slate-50 px-4 py-3 text-[13px] italic leading-relaxed text-slate-700">
                  “{evDialog.quote}”
                </blockquote>
                <dl className="grid gap-x-6 gap-y-1.5 text-[12.5px] sm:grid-cols-2">
                  <div><dt className="inline font-semibold text-slate-500">Source: </dt><dd className="inline text-slate-700">{evDialog.document}</dd></div>
                  <div><dt className="inline font-semibold text-slate-500">Page: </dt><dd className="inline text-slate-700">{evDialog.page ?? "n/a"}</dd></div>
                  <div><dt className="inline font-semibold text-slate-500">Section: </dt><dd className="inline text-slate-700">{evDialog.section}</dd></div>
                  <div><dt className="inline font-semibold text-slate-500">Type: </dt><dd className="inline text-slate-700">{evDialog.kind === "management_statement" ? "Management statement" : "Reported fact"}</dd></div>
                </dl>
                <button
                  onClick={() => { setEvDialog(null); setTab("evidence"); }}
                  className="w-full rounded-lg bg-[#0A1B33] px-4 py-2 text-[12.5px] font-semibold text-white transition hover:bg-[#13294B]"
                >
                  Open full Evidence panel
                </button>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
