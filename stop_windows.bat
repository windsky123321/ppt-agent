@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo [停止] 正在停止后端与前端服务...

set "BACKEND_PID_FILE=logs\backend.pid"
set "FRONTEND_PID_FILE=logs\frontend.pid"

if exist "%BACKEND_PID_FILE%" (
  set /p BACKEND_PID=<"%BACKEND_PID_FILE%"
  taskkill /PID !BACKEND_PID! /F >nul 2>nul
  del "%BACKEND_PID_FILE%" >nul 2>nul
  echo [停止] 已尝试停止后端进程，PID=!BACKEND_PID!
) else (
  echo [提示] 未找到 backend.pid，将尝试按端口查找。
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /PID %%A /F >nul 2>nul
)

if exist "%FRONTEND_PID_FILE%" (
  set /p FRONTEND_PID=<"%FRONTEND_PID_FILE%"
  taskkill /PID !FRONTEND_PID! /F >nul 2>nul
  del "%FRONTEND_PID_FILE%" >nul 2>nul
  echo [停止] 已尝试停止前端进程，PID=!FRONTEND_PID!
) else (
  echo [提示] 未找到 frontend.pid；当前版本通常由后端托管前端页面。
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do taskkill /PID %%A /F >nul 2>nul
)

echo [完成] 停止命令已执行。如端口仍被占用，请手动检查相关进程。
pause
