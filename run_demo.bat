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
set DEMO_MODE=1
echo DEMO MODE: fake deterministic OCR is active. This does NOT test Cactus Mirage.
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
