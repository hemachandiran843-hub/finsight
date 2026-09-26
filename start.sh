#!/usr/bin/env bash
# FinSight X — one-command start (macOS / Linux)
set -e
cd "$(dirname "$0")"

echo "==> [1/3] FinSight X backend (FastAPI, port 8000)"
(
  cd backend
  if [ ! -d .venv ]; then
    python3 -m venv .venv
    echo "    created Python virtualenv"
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -q -r requirements.txt
  nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
  echo "    backend started (PID $!, log: backend/uvicorn.log)"
)

echo "==> [2/3] Frontend dependencies (first run may take a few minutes)"
if [ ! -d node_modules ]; then
  npm install
fi

echo "==> [3/3] Frontend (Next.js, port 3000) — open http://localhost:3000"
echo "    Demo logins (password demo1234): ceo@ / analyst@ / risk@finsightx.demo"
trap 'echo "Stopping backend..."; pkill -f "uvicorn main:app" 2>/dev/null || true' EXIT
npm run dev
