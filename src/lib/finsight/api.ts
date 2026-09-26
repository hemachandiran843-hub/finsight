// FinSight X — API client.
// All calls go through the same-origin gateway using the relative path
// /api/fs/... with ?XTransformPort=8000 to reach the FastAPI backend.

import type { AskResponse, AuditEntry, AnalysisPackage, LoginResponse, ReportMeta, User } from "./types";

const BASE = "/api/fs";
const PORT = 8000;

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function url(path: string, params?: Record<string, string>): string {
  const q = new URLSearchParams({ XTransformPort: String(PORT), ...(params || {}) });
  return `${BASE}${path}?${q.toString()}`;
}

function authHeaders(token: string | null): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handle<T>(resPromise: Promise<Response>): Promise<T> {
  const res = await resPromise;
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") msg = body.detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, msg);
  }
  return res.json() as Promise<T>;
}

export async function getHealth(): Promise<{ status: string; demo_mode: boolean; ai_enabled: boolean }> {
  return handle(fetch(url("/health"), { cache: "no-store" }));
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  return handle(
    fetch(url("/auth/login"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    }),
  );
}

export async function me(token: string): Promise<{ user: User; demo_mode: boolean }> {
  return handle(fetch(url("/auth/me"), { headers: authHeaders(token), cache: "no-store" }));
}

export async function getDemoDataset(token: string): Promise<AnalysisPackage> {
  return handle(fetch(url("/demo/dataset"), { headers: authHeaders(token), cache: "no-store" }));
}

export function demoReportUrl(period: string): string {
  return url(`/demo/report/${encodeURIComponent(period)}`);
}

export async function uploadReport(token: string, file: File): Promise<{ report_id: number; analysis: AnalysisPackage; extraction: Record<string, unknown> }> {
  const form = new FormData();
  form.append("file", file);
  return handle(
    fetch(url("/reports/upload"), { method: "POST", headers: authHeaders(token), body: form }),
  );
}

export async function listReports(token: string): Promise<{ reports: ReportMeta[] }> {
  return handle(fetch(url("/reports"), { headers: authHeaders(token), cache: "no-store" }));
}

export async function ask(token: string, question: string, reportId: number | null): Promise<AskResponse> {
  return handle(
    fetch(url("/ask"), {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({ question, report_id: reportId }),
    }),
  );
}

export async function getAudit(token: string): Promise<{ entries: AuditEntry[] }> {
  return handle(fetch(url("/audit"), { headers: authHeaders(token), cache: "no-store" }));
}

export async function getSuggestedQuestions(token: string): Promise<{ questions: string[] }> {
  return handle(fetch(url("/suggested-questions"), { headers: authHeaders(token), cache: "no-store" }));
}
