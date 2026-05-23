@echo off
setlocal
chcp 65001 >nul

echo [Smoke] 正在运行 Windows smoke test...
cd /d %~dp0backend

if not exist .venv (
  echo [Smoke] 正在创建虚拟环境...
  python -m venv .venv
)

call .venv\Scripts\python.exe scripts\smoke_windows.py
if errorlevel 1 (
  echo [失败] Windows smoke test 失败。
  pause
  exit /b 1
)

echo [通过] Windows smoke test 成功。
pause
