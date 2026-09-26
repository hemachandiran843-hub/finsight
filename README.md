# FinSight X — AI Financial Intelligence & Early-Warning Platform

A working prototype that turns large financial reports into concise, evidence-backed
intelligence and early-warning signals for bankers and financial analysts.

**Everything in this prototype is functional — no placeholders.** It ships with a
curated fictional dataset (XYZ Manufacturing Ltd., Q1–Q3 FY26), so the full
demo runs offline in **Demo Mode** with no API key. Adding an LLM API key
switches the platform to live AI extraction and answers.

---

## Quick start

### macOS / Linux
```bash
./start.sh
```
The script creates a Python virtualenv, installs backend dependencies, starts the
FastAPI backend on port **8000**, installs frontend dependencies (first run only),
then starts the Next.js frontend on port **3000**.

Open **http://localhost:3000** when the frontend is ready.

### Windows
```bat
start.bat
```

### Manual (any platform)
```bash
# 1) Backend — Python 3.10+
cd backend
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# 2) Frontend — Node.js 18+ (from the project root, new terminal)
npm install
npm run dev          # serves http://localhost:3000
```

The SQLite database (`db/finsight.db`), demo users and the three sample PDF
reports are created automatically on first backend start.

---

## Production deployment (Vercel + Render)

The app is **two services**: a Next.js frontend and a Python FastAPI backend.
Vercel runs only the frontend — it cannot host the FastAPI/SQLite backend — so
the backend must be deployed separately (Render, Railway, Fly.io, any host
that runs uvicorn). The frontend then calls it via `NEXT_PUBLIC_API_BASE_URL`.

### 1) Deploy the FastAPI backend (Render example)

1. Push this repo to GitHub. In Render: **New → Web Service**, pick the repo.
2. Settings:
   - **Root Directory**: `backend`
   - **Runtime**: Python 3.11+ (set env var `PYTHON_VERSION=3.12.4` on Render)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Environment variables (see `backend/.env.example`):
   - `CORS_ORIGINS=https://<your-app>.vercel.app` (comma-separate extra origins,
     e.g. the preview URLs)
   - `LLM_API_KEY=` — leave empty for Demo Mode (recommended for the prototype)
   - `FS_DB_PATH=` — optional; point at a persistent disk, otherwise demo data
     re-seeds on every deploy/restart
4. Deploy. Verify: `curl https://<backend-host>/api/fs/health` returns
   `{"status":"ok",...}` and `POST /api/fs/auth/login` accepts a demo account.

Railway/Fly.io equivalent: build from `backend/`, install `requirements.txt`,
start with `uvicorn main:app --host 0.0.0.0 --port $PORT`.

### 2) Deploy the frontend on Vercel

1. In Vercel: **Add New → Project**, import the same repo (framework auto-set
   to Next.js; build command `npm run build` works as-is).
2. Environment Variables (Project → Settings → Environment Variables),
   required for Production **and** Preview:
   - `NEXT_PUBLIC_API_BASE_URL=https://<backend-host>` — the backend origin
     from step 1, **no trailing slash**, **no** `/api/fs` suffix
3. Deploy, then verify:
   - the Sign In buttons return a workspace (no "Request failed (404)")
   - browser DevTools → Network shows login going to
     `https://<backend-host>/api/fs/auth/login` (not `/api/fs` on the Vercel
     domain, and no `localhost`/`127.0.0.1` anywhere)

> `NEXT_PUBLIC_*` variables are inlined at build time — after adding or
> changing one, **redeploy** so the new value reaches the browser bundle.

### 3) Local development (unchanged)

Nothing to configure: leave `NEXT_PUBLIC_API_BASE_URL` unset and run
`./start.sh`. Requests stay same-origin `/api/fs/...` and the Next.js rewrite
(`next.config.ts`, override target with `FS_API_ORIGIN`) proxies them to
`127.0.0.1:8000`.

### Environment variables summary

| Variable | Where | Required | Purpose |
|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Vercel (frontend) | Yes in production | Absolute origin of the FastAPI backend |
| `FS_API_ORIGIN` | Frontend host | No | Rewrite target for self-hosted proxying (default `http://127.0.0.1:8000`) |
| `CORS_ORIGINS` | Backend host | Yes in production | Comma-separated allowed origins (Vercel domain(s)) |
| `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` | Backend host | No | Live AI mode; empty key = Demo Mode |
| `FS_DB_PATH` | Backend host | No | SQLite path (persistent disk in production) |

---

## Demo accounts

| Persona        | Email                    | Password    | Sees |
|----------------|--------------------------|-------------|------|
| CEO            | `ceo@finsightx.demo`     | `demo1234`  | Overview, Exec Summary, Signals, Trends, Ask the Report |
| Credit Analyst | `analyst@finsightx.demo` | `demo1234`  | Everything incl. Upload, Mismatch, Evidence, Q&A |
| Risk Manager   | `risk@finsightx.demo`    | `demo1234`  | Risk-focused view + Audit Log |

The login screen has one-click buttons for each persona. Role-based access is
enforced server-side (RBAC), e.g. only the Risk Manager can open the audit log
and only analysts/risk can upload reports.

---

## Suggested 2–3 minute demo script

1. **Login** as *Credit Analyst* (one click).
2. **Overview** — KPI cards, AI executive summary and top signals for
   XYZ Manufacturing Ltd. Q3 FY26.
3. **Signals** — the flagship *Financial Pressure Signal*: revenue ↑12%,
   debt ↑, finance cost ↑30%, operating cash flow ↓ — fused into one
   early-warning with severity and explanation.
4. **Statement vs Data** — management says liquidity "remains strong"; the data
   shows cash down, debt and short-term borrowings up. Verdict:
   *"Potential statement–data mismatch requiring analyst verification."*
   (The platform never alleges fraud — it flags divergence for humans.)
5. **Historical Trends** — debt ₹400 → ₹470 → ₹560 Cr across quarters and
   Early-Signal Memory streaks (three consecutive deteriorations).
6. **Risk Chain** — the causal chain: cost ↑ → margin ↓ → profit ↓ →
   cash flow ↓ → potential financing pressure.
7. **Evidence** — every insight traces to AI Insight → Evidence →
   Original Document (page + quoted text).
8. **Ask the Report** — ask *"Why did profit decline?"* — answers are grounded
   in the uploaded report with evidence chips.
9. **Upload** — drag in one of the sample PDFs from `backend/sample_reports/`
   and watch extraction → analysis run live.

---

## Demo Mode vs LLM Mode

| | Demo Mode (default) | LLM Mode |
|---|---|---|
| API key | not needed | set `LLM_API_KEY` in `backend/.env` |
| Extraction | curated dataset + regex heuristics | LLM summarisation on upload |
| Q&A | curated knowledge bank + retrieval | LLM RAG over report excerpts |
| Network | fully offline | calls your LLM endpoint |

```bash
cd backend
cp .env.example .env     # then edit .env
```

Works with any OpenAI-compatible endpoint (`LLM_BASE_URL` / `LLM_MODEL`).

---

## What's inside

```
├── backend/                 FastAPI + SQLite (port 8000)
│   ├── main.py              /api/fs/* routes: auth, demo dataset, upload,
│   │                        reports, ask, audit, suggested questions
│   ├── analysis.py          rule engine: fusion signals, mismatch detection,
│   │                        9-node risk chain, early-signal memory
│   ├── demo_data.py         curated XYZ Manufacturing Q1–Q3 FY26 dataset,
│   │                        15-entry evidence registry, Q&A knowledge bank
│   ├── pdf_utils.py         PyMuPDF/pdfplumber extraction + metric harvest
│   ├── llm.py               OpenAI-compatible client (optional)
│   ├── sample_reports.py    regenerates the 3 fictional quarterly PDFs
│   ├── security.py          PBKDF2 password hashing + HMAC tokens + RBAC
│   ├── database.py          SQLite (WAL): users, reports, audit_log
│   └── sample_reports/      XYZ Q1/Q2/Q3 FY26 PDFs (upload-ready)
├── src/                     Next.js 16 + TypeScript + Tailwind + Recharts
│   ├── app/page.tsx         login → analysis workspace
│   ├── components/finsight/ all tabs (overview, signals, mismatch, trends,
│   │                        risk chain, evidence, ask, upload, audit)
│   └── lib/finsight/        typed API client
├── docs/screenshots/        annotated captures of the main views
├── start.sh / start.bat     one-command startup
└── README.md
```

In **local development** frontend calls stay on relative `/api/fs/...` URLs;
`next.config.ts` rewrites them to `127.0.0.1:8000`, so no CORS setup is needed.
In **production** the frontend calls the backend directly via
`NEXT_PUBLIC_API_BASE_URL` and the backend allows those origins via
`CORS_ORIGINS` (see *Production deployment* above).

---

## Safety & compliance boundaries (by design)

The platform is decision-support only and deliberately enforces:

- **No** stock-price prediction, **no** buy/sell recommendations
- **No** automated loan approvals or rejections
- **Never** alleges fraud — statement–data divergence is labelled
  *"Potential mismatch requiring analyst verification"*
- **No** fabricated figures — every number traces to the uploaded document
  via the evidence panel; heuristic extractions are explicitly marked
  *"subject to verification"*
- Three-layer information design: **Reported Fact → AI Analysis → Potential Significance**
- Prototype-grade security: login, RBAC, audit log, upload validation
  (magic bytes + size cap). Production hardening (MFA, encryption at rest,
  SSO, monitoring) is documented as future work.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Login says *Internal Server Error* | Backend not running — start it (`cd backend && python3 -m uvicorn main:app --port 8000`) and retry. |
| **Deployed** login says *Request failed (404)* | `NEXT_PUBLIC_API_BASE_URL` missing/wrong on Vercel — set it to the backend origin (no trailing slash) and **redeploy**. |
| **Deployed** login says *Failed to fetch* / CORS error | Add the Vercel origin to `CORS_ORIGINS` on the backend host and restart it. |
| Port 8000 already in use | `uvicorn main:app --port 8001`, then change the destination in `next.config.ts` and `PORT` in `src/lib/finsight/api.ts`. |
| `pip install` fails for pymupdf/pdfplumber | Ensure Python 3.10+ and pip upgraded: `python3 -m pip install -U pip`. |
| Charts look broken | Hard-refresh the browser; dev-mode Recharts needs a moment on first paint. |
| Frontend port busy | `npm run dev -- -p 3001` and open that port instead. |

---

*Fictional data disclaimer: XYZ Manufacturing Ltd. and all its figures are
synthetic, created for demonstration only. This prototype is not investment
advice, not a credit decision tool, and not a fraud-detection product.*
