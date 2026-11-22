@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher was not found. Install Python 3.11 from https://www.python.org/downloads/windows/ and enable the launcher.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment with Python 3.11...
  py -3.11 -m venv .venv
  if errorlevel 1 (
    echo Python 3.11 was not found. Install Python 3.11, then run this script again.
    pause
    exit /b 1
  )
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto :failed
python -m pip install -r requirements.txt
if errorlevel 1 goto :failed
if not exist ".env" copy .env.example .env >nul

echo.
echo Dependencies installed. Next run: scripts\download_model.bat
pause
exit /b 0

:failed
echo Installation failed. Review the error above.
pause
exit /b 1
