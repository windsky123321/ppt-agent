@echo off
setlocal
chcp 65001 >nul
echo [stop] attempting to stop backend and frontend...
for %%P in (8000 5173) do (
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr :%%P ^| findstr LISTENING') do (
    taskkill /PID %%A /F >nul 2>nul
  )
)
echo [stop] attempted to release ports 8000 and 5173.
pause
