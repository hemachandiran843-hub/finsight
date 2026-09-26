"use client";

import { useEffect, useRef, useState } from "react";
import { Bot, CornerDownLeft, Loader2, MessagesSquare, ShieldCheck, User } from "lucide-react";
import { ask, getSuggestedQuestions } from "@/lib/finsight/api";
import type { AskResponse, Evidence } from "@/lib/finsight/types";
import { EvidenceChip } from "./ui-bits";

interface Msg {
  role: "user" | "assistant";
  text: string;
  resp?: AskResponse;
}

export function AskTab({ token, reportId, onOpenEvidence }: {
  token: string;
  reportId: number | null;
  onOpenEvidence: (ev: Evidence) => void;
}) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [suggested, setSuggested] = useState<string[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getSuggestedQuestions(token).then((r) => setSuggested(r.questions)).catch(() => {});
  }, [token]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  async function send(q: string) {
    const question = q.trim();
    if (!question || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: question }]);
    setBusy(true);
    try {
      const resp = await ask(token, question, reportId);
      setMessages((m) => [...m, { role: "assistant", text: resp.answer, resp }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", text: e instanceof Error ? e.message : "The report engine could not be reached." }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_300px]">
      {/* chat column */}
      <div className="flex min-h-[540px] flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 bg-[#0A1B33] px-5 py-3">
          <div className="flex items-center gap-2.5">
            <MessagesSquare className="h-4.5 w-4.5 text-[#E4C158]" />
            <div>
              <h3 className="text-[13.5px] font-bold text-white">Ask the Report</h3>
              <p className="text-[11px] text-slate-400">Grounded in the uploaded report — answers carry page-level evidence</p>
            </div>
          </div>
          <span className="rounded-full border border-white/15 bg-white/10 px-2.5 py-1 text-[10.5px] font-semibold uppercase tracking-wide text-slate-200">
            Demo Mode
          </span>
        </div>

        <div ref={scrollRef} className="max-h-[56vh] min-h-[380px] flex-1 space-y-4 overflow-y-auto p-5 scroll-smooth">
          {!messages.length && (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100">
                <Bot className="h-6 w-6 text-slate-400" />
              </div>
              <p className="mt-3 max-w-sm text-[13px] leading-relaxed text-slate-500">
                Ask anything about the analysed report — profit drivers, debt build-up, liquidity claims, guidance or
                risks. Answers are grounded in the document and never speculate beyond it.
              </p>
            </div>
          )}

          {messages.map((m, i) =>
            m.role === "user" ? (
              <div key={i} className="flex justify-end gap-2.5">
                <div className="max-w-[80%] rounded-2xl rounded-br-md bg-[#0A1B33] px-4 py-2.5 text-[13px] font-medium leading-relaxed text-white">
                  {m.text}
                </div>
                <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-200">
                  <User className="h-3.5 w-3.5 text-slate-500" />
                </span>
              </div>
            ) : (
              <div key={i} className="flex gap-2.5">
                <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#EAF2EF]">
                  <Bot className="h-3.5 w-3.5 text-teal-700" />
                </span>
                <div className="max-w-[85%] space-y-2">
                  <div className="rounded-2xl rounded-tl-md border border-slate-200 bg-slate-50/80 px-4 py-3 text-[13px] leading-relaxed text-slate-700">
                    {m.text}
                  </div>
                  {m.resp?.evidence?.length ? (
                    <div className="rounded-xl border border-teal-100 bg-teal-50/60 p-3">
                      <p className="text-[10.5px] font-bold uppercase tracking-wider text-teal-700">Evidence</p>
                      <div className="mt-1.5 flex flex-wrap gap-1.5">
                        {m.resp.evidence.map((ev, j) => (
                          <EvidenceChip key={j} ev={ev} onClick={() => onOpenEvidence(ev as Evidence)} />
                        ))}
                      </div>
                      <div className="mt-2 space-y-1.5">
                        {m.resp.evidence.slice(0, 2).map((ev, j) => (
                          <p key={j} className="border-l-2 border-teal-300 pl-2.5 text-[11.5px] italic leading-relaxed text-slate-500">
                            “{ev.quote}” — {ev.document}{ev.page ? `, p.${ev.page}` : ""}
                          </p>
                        ))}
                      </div>
                    </div>
                  ) : null}
                  {m.resp && (
                    <p className="text-[10.5px] text-slate-400">
                      answer mode: {m.resp.mode} · {m.resp.demo_mode ? "Demo Mode knowledge base" : "live LLM"}
                    </p>
                  )}
                </div>
              </div>
            ),
          )}

          {busy && (
            <div className="flex gap-2.5">
              <span className="mt-0.5 flex h-7 w-7 items-center justify-center rounded-full bg-[#EAF2EF]">
                <Bot className="h-3.5 w-3.5 text-teal-700" />
              </span>
              <div className="flex items-center gap-2 rounded-2xl rounded-tl-md border border-slate-200 bg-slate-50/80 px-4 py-3 text-[12.5px] text-slate-500">
                <Loader2 className="h-3.5 w-3.5 animate-spin" /> Searching the report…
              </div>
            </div>
          )}
        </div>

        <form
          className="border-t border-slate-100 p-3.5"
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
        >
          <div className="flex items-center gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="e.g. Why did debt increase?"
              className="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-[13px] outline-none transition focus:border-[#0A1B33] focus:ring-2 focus:ring-[#0A1B33]/10"
            />
            <button
              type="submit"
              disabled={busy || !input.trim()}
              className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#0A1B33] text-white transition hover:bg-[#13294B] disabled:opacity-40"
              aria-label="Send question"
            >
              <CornerDownLeft className="h-4 w-4" />
            </button>
          </div>
        </form>
      </div>

      {/* suggested column */}
      <div className="space-y-4">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <h4 className="text-[12px] font-bold uppercase tracking-wider text-slate-500">Suggested questions</h4>
          <div className="mt-2.5 space-y-2">
            {suggested.map((q) => (
              <button
                key={q}
                onClick={() => send(q)}
                disabled={busy}
                className="w-full rounded-lg border border-slate-100 bg-slate-50/70 px-3 py-2 text-left text-[12.5px] font-medium text-slate-600 transition hover:border-[#0A1B33]/25 hover:bg-white disabled:opacity-50"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-4">
          <p className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-emerald-700">
            <ShieldCheck className="h-3.5 w-3.5" /> Grounding rules
          </p>
          <ul className="mt-2 space-y-1.5 text-[12px] leading-relaxed text-emerald-800">
            <li>· Answers use only report content — no outside market data.</li>
            <li>· No stock predictions, buy/sell views, or loan decisions.</li>
            <li>· Discrepancies are flagged for verification, never called fraud.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
