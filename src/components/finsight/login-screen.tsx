"use client";

import { useState } from "react";
import { BarChart3, FileSearch, ShieldCheck, Workflow, Loader2, Lock, LineChart, GitBranch } from "lucide-react";
import { login } from "@/lib/finsight/api";
import { ROLE_DEMO_ACCOUNTS, type Role, type User } from "@/lib/finsight/types";
import { cn } from "@/lib/utils";

const FLOW = [
  { icon: FileSearch, text: "Upload financial report" },
  { icon: Workflow, text: "Extract text & financial data" },
  { icon: LineChart, text: "AI summary · signal detection · risk analysis" },
  { icon: GitBranch, text: "Evidence-backed analyst dashboard" },
];

export function LoginScreen({ onLogin }: { onLogin: (user: User, token: string, demoMode: boolean) => void }) {
  const [email, setEmail] = useState("analyst@finsightx.demo");
  const [password, setPassword] = useState("demo1234");
  const [busy, setBusy] = useState<Role | "form" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function doLogin(em: string, pw: string, tag: Role | "form") {
    setBusy(tag);
    setError(null);
    try {
      const res = await login(em, pw);
      onLogin(res.user, res.token, res.demo_mode);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Login failed");
      setBusy(null);
    }
  }

  return (
    <div className="min-h-screen bg-[#F4F6FA] text-slate-900 lg:grid lg:grid-cols-[1.05fr_1fr]">
      {/* Brand panel */}
      <div className="relative overflow-hidden bg-[#0A1B33] px-8 py-12 text-white lg:px-14 lg:py-16">
        <div className="pointer-events-none absolute -right-40 -top-40 h-96 w-96 rounded-full bg-[#12315C] blur-3xl" />
        <div className="pointer-events-none absolute -bottom-48 -left-24 h-96 w-96 rounded-full bg-[#0E2947] blur-3xl" />
        <div className="relative">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-[#C9A227] to-[#9A7B1C] shadow-lg">
              <BarChart3 className="h-6 w-6 text-[#0A1B33]" strokeWidth={2.4} />
            </div>
            <div>
              <p className="text-xl font-bold tracking-tight">FinSight<span className="text-[#E4C158]"> X</span></p>
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Financial Intelligence Platform</p>
            </div>
          </div>

          <h1 className="mt-12 max-w-lg text-3xl font-bold leading-snug lg:text-4xl">
            Turn financial reports into <span className="text-[#E4C158]">early-warning intelligence</span>.
          </h1>
          <p className="mt-4 max-w-md text-[15px] leading-relaxed text-slate-300">
            FinSight X compresses quarterly reports, earnings calls and disclosures into evidence-backed
            summaries, fused financial signals and risk chains — built for bank credit and risk teams.
          </p>

          <div className="mt-10 space-y-3.5">
            {FLOW.map((f, i) => (
              <div key={i} className="flex items-center gap-3 text-sm text-slate-300">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-white/5">
                  <f.icon className="h-4 w-4 text-[#E4C158]" />
                </span>
                {f.text}
              </div>
            ))}
          </div>

          <div className="mt-12 flex items-start gap-3 rounded-xl border border-white/10 bg-white/5 p-4 text-[12.5px] leading-relaxed text-slate-300">
            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
            <p>
              Analytical support only — FinSight X never predicts stock prices, issues buy/sell
              recommendations, approves loans, or alleges fraud. Every output separates
              <span className="font-semibold text-white"> Reported Fact</span> from
              <span className="font-semibold text-white"> AI Analysis</span> and
              <span className="font-semibold text-white"> Potential Significance</span>.
            </p>
          </div>
        </div>
      </div>

      {/* Login panel */}
      <div className="flex items-center justify-center px-6 py-12 lg:px-14">
        <div className="w-full max-w-md">
          <h2 className="text-2xl font-bold tracking-tight">Sign in to the workspace</h2>
          <p className="mt-1.5 text-sm text-slate-500">
            Prototype environment — pick a demo persona or use the form. All accounts share password
            <span className="ml-1 rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs font-semibold text-slate-700">demo1234</span>
          </p>

          <div className="mt-6 space-y-3">
            {ROLE_DEMO_ACCOUNTS.map((acc) => (
              <button
                key={acc.role}
                type="button"
                disabled={busy !== null}
                onClick={() => {
                  setEmail(acc.email);
                  setPassword(acc.password);
                  doLogin(acc.email, acc.password, acc.role);
                }}
                className={cn(
                  "group flex w-full items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition",
                  "hover:border-[#0A1B33]/30 hover:shadow-md disabled:opacity-60",
                )}
              >
                <span>
                  <span className="block text-sm font-bold text-slate-900">Sign in as {acc.label}</span>
                  <span className="mt-0.5 block text-xs leading-relaxed text-slate-500">{acc.blurb}</span>
                  <span className="mt-1 block font-mono text-[11px] text-slate-400">{acc.email}</span>
                </span>
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[#0A1B33] text-white transition group-hover:bg-[#13294B]">
                  {busy === acc.role ? <Loader2 className="h-4 w-4 animate-spin" /> : <Lock className="h-4 w-4" />}
                </span>
              </button>
            ))}
          </div>

          <div className="my-6 flex items-center gap-3">
            <div className="h-px flex-1 bg-slate-200" />
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">or sign in manually</span>
            <div className="h-px flex-1 bg-slate-200" />
          </div>

          <form
            className="space-y-3.5"
            onSubmit={(e) => {
              e.preventDefault();
              doLogin(email, password, "form");
            }}
          >
            <div>
              <label htmlFor="email" className="mb-1.5 block text-xs font-semibold text-slate-600">Work email</label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm outline-none transition focus:border-[#0A1B33] focus:ring-2 focus:ring-[#0A1B33]/10"
                placeholder="you@bank.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="mb-1.5 block text-xs font-semibold text-slate-600">Password</label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm outline-none transition focus:border-[#0A1B33] focus:ring-2 focus:ring-[#0A1B33]/10"
                placeholder="••••••••"
              />
            </div>
            {error && (
              <p className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-medium text-rose-700">{error}</p>
            )}
            <button
              type="submit"
              disabled={busy !== null}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-[#0A1B33] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#13294B] disabled:opacity-60"
            >
              {busy === "form" && <Loader2 className="h-4 w-4 animate-spin" />}
              Sign in
            </button>
          </form>

          <p className="mt-6 text-center text-[11px] leading-relaxed text-slate-400">
            Security prototype: session tokens, role-based access, file validation and audit logging.
            Production hardening (MFA, encryption at rest, advanced RBAC, monitoring) is planned future scope.
          </p>
        </div>
      </div>
    </div>
  );
}
