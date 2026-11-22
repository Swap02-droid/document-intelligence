@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run install.bat first.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
set CACTUS_TELEMETRY=0
set HF_HUB_OFFLINE=1
set DEMO_MODE=0
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
