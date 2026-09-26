"use client";

import { useEffect, useState } from "react";
import { Loader2, ScrollText } from "lucide-react";
import { getAudit } from "@/lib/finsight/api";
import type { AuditEntry } from "@/lib/finsight/types";

const ACTION_STYLE: Record<string, string> = {
  login_success: "bg-emerald-50 text-emerald-700 border-emerald-200",
  login_failed: "bg-rose-50 text-rose-700 border-rose-200",
  upload_ok: "bg-teal-50 text-teal-700 border-teal-200",
  upload_rejected: "bg-rose-50 text-rose-700 border-rose-200",
  ask_question: "bg-slate-50 text-slate-600 border-slate-200",
  view_demo_dataset: "bg-sky-50 text-sky-700 border-sky-200",
  view_report: "bg-sky-50 text-sky-700 border-sky-200",
  download_sample_report: "bg-violet-50 text-violet-700 border-violet-200",
};

export function AuditTab({ token }: { token: string }) {
  const [entries, setEntries] = useState<AuditEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAudit(token)
      .then((r) => setEntries(r.entries))
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load audit log"));
  }, [token]);

  if (error) {
    return <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>;
  }
  if (!entries) {
    return (
      <div className="flex items-center justify-center py-16 text-slate-400">
        <Loader2 className="h-5 w-5 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="mb-1 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-slate-900">Audit Log</h2>
          <p className="mt-0.5 text-sm text-slate-500">
            Immutable prototype trail of platform activity — logins, uploads, queries and downloads. Only the Risk
            Manager role can view this tab.
          </p>
        </div>
        <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11.5px] font-semibold text-slate-500">
          {entries.length} events
        </span>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="max-h-[62vh] overflow-y-auto">
          <table className="w-full text-left text-[12.5px]">
            <thead className="sticky top-0 bg-slate-50 text-[11px] uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-4 py-2.5 font-bold">Timestamp (UTC)</th>
                <th className="px-4 py-2.5 font-bold">Actor</th>
                <th className="px-4 py-2.5 font-bold">Role</th>
                <th className="px-4 py-2.5 font-bold">Action</th>
                <th className="px-4 py-2.5 font-bold">Detail</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {entries.map((e, i) => (
                <tr key={i} className="transition hover:bg-slate-50/60">
                  <td className="whitespace-nowrap px-4 py-2.5 font-mono text-[11.5px] text-slate-500">{e.ts.replace("T", " ")}</td>
                  <td className="px-4 py-2.5 font-medium text-slate-700">{e.actor}</td>
                  <td className="px-4 py-2.5 text-slate-500">{e.role}</td>
                  <td className="px-4 py-2.5">
                    <span className={`inline-block rounded-md border px-2 py-0.5 text-[11px] font-semibold ${ACTION_STYLE[e.action] ?? "border-slate-200 bg-slate-50 text-slate-600"}`}>
                      {e.action}
                    </span>
                  </td>
                  <td className="max-w-[380px] truncate px-4 py-2.5 text-slate-500" title={e.detail}>{e.detail}</td>
                </tr>
              ))}
              {!entries.length && (
                <tr>
                  <td colSpan={5} className="px-4 py-10 text-center text-slate-400">
                    <ScrollText className="mx-auto mb-2 h-6 w-6" />
                    No audit events yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <p className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-[11.5px] leading-relaxed text-slate-500">
        Production security roadmap: multi-factor authentication, field-level encryption, tamper-evident log
        storage, granular RBAC policies, SIEM integration and real-time anomaly monitoring.
      </p>
    </div>
  );
}
