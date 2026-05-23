@echo off
setlocal
chcp 65001 >nul
echo [smoke] running Windows smoke test...
cd /d %~dp0backend
if not exist .venv (
  echo [smoke] creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\python.exe scripts\smoke_windows.py
if errorlevel 1 (
  echo [failed] Windows smoke test failed.
  pause
  exit /b 1
)
echo [passed] Windows smoke test succeeded.
pause
