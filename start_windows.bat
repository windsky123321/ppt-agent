@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"

if not exist logs mkdir logs
echo [startup] starting Personalized Paper-to-PPT Agent > logs\startup.log
echo [startup] checking Python...>> logs\startup.log
where python >nul 2>nul
if errorlevel 1 (
  echo [error] Python 3.11+ is required.
  pause
  exit /b 1
)

echo [startup] checking Node.js...>> logs\startup.log
where node >nul 2>nul
if errorlevel 1 (
  echo [error] Node.js 18+ is required.
  pause
  exit /b 1
)

where npm.cmd >nul 2>nul
if errorlevel 1 (
  echo [error] npm was not found. Please check Node.js installation.
  pause
  exit /b 1
)

if not exist .env (
  copy .env.example .env >nul
  echo [startup] created .env from .env.example>> logs\startup.log
)

if not exist backend\.venv (
  echo [startup] creating backend virtual environment...
  python -m venv backend\.venv >> logs\startup.log 2>&1
)

echo [startup] installing backend dependencies...
call backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt >> logs\backend.log 2>&1
if errorlevel 1 (
  echo [error] backend dependency installation failed. Check logs\backend.log
  pause
  exit /b 1
)

echo [startup] installing frontend dependencies...
call npm.cmd install --prefix frontend >> logs\frontend.log 2>&1
if errorlevel 1 (
  echo [error] frontend dependency installation failed. Check logs\frontend.log
  pause
  exit /b 1
)

for %%P in (8000 5173) do (
  netstat -ano | findstr :%%P | findstr LISTENING >nul
  if not errorlevel 1 (
    echo [error] port %%P is already in use.
    echo [error] port %%P is already in use.>> logs\startup.log
    pause
    exit /b 1
  )
)

echo [startup] starting backend...
start "PPT Agent Backend" cmd /k "cd /d %ROOT%backend && .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 1>>..\logs\backend.log 2>>&1"
for /l %%I in (1,1,30) do (
  powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/health -TimeoutSec 2; if($r.StatusCode -eq 200){exit 0}else{exit 1}} catch { exit 1 }" >nul 2>nul
  if not errorlevel 1 goto backend_ready
  timeout /t 1 >nul
)
echo [error] backend did not start in time. Check logs\backend.log
pause
exit /b 1

:backend_ready
echo [startup] backend is ready.>> logs\startup.log

echo [startup] starting frontend...
start "PPT Agent Frontend" cmd /k "cd /d %ROOT%frontend && npm.cmd run dev -- --host 127.0.0.1 --port 5173 1>>..\logs\frontend.log 2>>&1"
for /l %%I in (1,1,30) do (
  powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173 -TimeoutSec 2; if($r.StatusCode -ge 200){exit 0}else{exit 1}} catch { exit 1 }" >nul 2>nul
  if not errorlevel 1 goto frontend_ready
  timeout /t 1 >nul
)
echo [error] frontend did not start in time. Check logs\frontend.log
pause
exit /b 1

:frontend_ready
echo [startup] frontend is ready.>> logs\startup.log
start http://127.0.0.1:5173
echo [done] Browser opened: http://127.0.0.1:5173
echo [done] To stop, run stop_windows.bat
pause
