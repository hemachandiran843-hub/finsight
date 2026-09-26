"use client";

import { useCallback, useState } from "react";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Toaster } from "@/components/ui/sonner";
import { getDemoDataset } from "@/lib/finsight/api";
import type { AnalysisPackage, User } from "@/lib/finsight/types";
import { LoginScreen } from "@/components/finsight/login-screen";
import { AppShell } from "@/components/finsight/app-shell";

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [pkg, setPkg] = useState<AnalysisPackage | null>(null);
  const [reportId, setReportId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [busyDemo, setBusyDemo] = useState(false);

  const handleLogin = useCallback(async (u: User, t: string, demoMode: boolean) => {
    setUser(u);
    setToken(t);
    setLoading(true);
    try {
      const data = await getDemoDataset(t);
      setPkg(data);
      setReportId(null);
      if (demoMode) {
        toast.info("Demo Mode active", { description: "No LLM API key configured — the curated XYZ Manufacturing analysis is loaded." });
      }
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Could not load the analysis workspace.");
      setUser(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadDemo = useCallback(async () => {
    if (!token) return;
    setBusyDemo(true);
    try {
      const data = await getDemoDataset(token);
      setPkg(data);
      setReportId(null);
      toast.success("Demo dataset loaded", { description: "Q3 FY26 curated analysis with full evidence trail." });
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Could not load the demo dataset.");
    } finally {
      setBusyDemo(false);
    }
  }, [token]);

  const handleAnalysed = useCallback((data: AnalysisPackage, id: number) => {
    setPkg(data);
    setReportId(id);
  }, []);

  const handleLogout = useCallback(() => {
    setUser(null);
    setToken(null);
    setPkg(null);
    setReportId(null);
  }, []);

  if (!user || !token || !pkg) {
    if (loading) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-[#F4F6FA]">
          <Loader2 className="h-7 w-7 animate-spin text-[#0A1B33]" />
          <p className="text-sm font-medium text-slate-500">Preparing your analysis workspace…</p>
          <Toaster position="top-right" richColors />
        </div>
      );
    }
    return (
      <>
        <LoginScreen onLogin={handleLogin} />
        <Toaster position="top-right" richColors />
      </>
    );
  }

  return (
    <>
      <AppShell
        user={user}
        token={token}
        pkg={pkg}
        reportId={reportId}
        busyDemo={busyDemo}
        onLoadDemo={loadDemo}
        onAnalysed={handleAnalysed}
        onLogout={handleLogout}
      />
      <Toaster position="top-right" richColors />
    </>
  );
}
