@echo off
rem FinSight X - one-command start (Windows)
setlocal
cd /d "%~dp0"

echo ==^> [1/3] FinSight X backend (FastAPI, port 8000)
cd backend
if not exist .venv (
  python -m venv .venv
  echo     created Python virtualenv
)
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
start "FinSightX backend" cmd /c "python -m uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1"
echo     backend started in a separate window (log: backend\uvicorn.log)
cd ..

echo ==^> [2/3] Frontend dependencies (first run may take a few minutes)
if not exist node_modules call npm install

echo ==^> [3/3] Frontend (Next.js, port 3000) - open http://localhost:3000
echo     Demo logins (password demo1234): ceo@ / analyst@ / risk@finsightx.demo
call npx next dev -p 3000
