@echo off
cd /d "%~dp0"
title Urban Water Analytics - Flask Website
echo ==========================================
echo Urban Water Analytics - Flask Website
echo ==========================================
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 python -m venv .venv
  if errorlevel 1 goto python_error
)
echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto install_error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto install_error
echo.
echo Website starting at http://127.0.0.1:5000
echo Keep this window open.
start "" http://127.0.0.1:5000
".venv\Scripts\python.exe" app.py
pause
exit /b 0
:python_error
echo Python 3.10 or newer is required. Install Python and enable Add Python to PATH.
pause
exit /b 1
:install_error
echo Dependency installation failed. Check internet and retry.
pause
exit /b 1
