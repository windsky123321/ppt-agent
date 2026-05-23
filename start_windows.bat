@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"
set "FRONTEND_DIR=%ROOT%frontend"
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "(Resolve-Path -LiteralPath 'frontend').ProviderPath"`) do set "FRONTEND_DIR=%%I"

if not exist logs mkdir logs
if not exist storage mkdir storage
if not exist storage\uploads mkdir storage\uploads
if not exist storage\decks mkdir storage\decks
if not exist storage\config mkdir storage\config

echo [启动] PPT Agent > logs\startup.log
echo [启动] 工作目录：%ROOT%>> logs\startup.log

where python >nul 2>nul
if errorlevel 1 (
  echo [错误] 未找到 Python，请先安装 Python 3.11+。
  echo [错误] 未找到 Python。>> logs\startup.log
  pause
  exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
  echo [错误] 未找到 Node.js，请先安装 Node.js 18+。
  echo [错误] 未找到 Node.js。>> logs\startup.log
  pause
  exit /b 1
)

where npm.cmd >nul 2>nul
if errorlevel 1 (
  echo [错误] 未找到 npm，请检查 Node.js 安装。
  echo [错误] 未找到 npm。>> logs\startup.log
  pause
  exit /b 1
)

if not exist .env (
  copy .env.example .env >nul
  echo [启动] 已根据 .env.example 创建 .env。>> logs\startup.log
)

if not exist backend\.venv (
  echo [安装] 正在创建后端虚拟环境...
  python -m venv backend\.venv >> logs\startup.log 2>&1
  if errorlevel 1 (
    echo [错误] 创建后端虚拟环境失败，请检查 Python 安装。
    pause
    exit /b 1
  )
)

echo [安装] 正在安装后端依赖...
call backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt >> logs\backend.log 2>&1
if errorlevel 1 (
  echo [错误] 后端依赖安装失败，请查看 logs\backend.log。
  pause
  exit /b 1
)

echo [安装] 正在安装前端依赖...
pushd "%FRONTEND_DIR%"
call npm.cmd install >> ..\logs\frontend.log 2>&1
if errorlevel 1 (
  popd
  echo [错误] 前端依赖安装失败，请查看 logs\frontend.log。
  pause
  exit /b 1
)

if not exist dist\index.html (
  echo [构建] 正在构建前端静态资源...
  call npm.cmd run build >> ..\logs\frontend.log 2>&1
  if errorlevel 1 (
    popd
    echo [错误] 前端构建失败，请查看 logs\frontend.log。
    pause
    exit /b 1
  )
)
popd

for %%P in (8000) do (
  netstat -ano | findstr :%%P | findstr LISTENING >nul
  if not errorlevel 1 (
    echo [错误] 端口 %%P 已被占用，请先释放后再启动。
    echo [错误] 端口 %%P 已被占用。>> logs\startup.log
    pause
    exit /b 1
  )
)

echo [启动] 正在启动后端服务...
powershell -NoProfile -Command "$p = Start-Process -FilePath '%ROOT%backend\.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory '%ROOT%backend' -RedirectStandardOutput '%ROOT%logs\backend.log' -RedirectStandardError '%ROOT%logs\backend.log' -PassThru; Set-Content -Path '%ROOT%logs\backend.pid' -Value $p.Id"

for /l %%I in (1,1,40) do (
  powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/health -TimeoutSec 2; if($r.StatusCode -eq 200){exit 0}else{exit 1}} catch { exit 1 }" >nul 2>nul
  if not errorlevel 1 goto backend_ready
  timeout /t 1 >nul
)
echo [错误] 后端未能在预期时间内启动，请查看 logs\backend.log。
pause
exit /b 1

:backend_ready
echo [启动] 后端服务已就绪。>> logs\startup.log
echo [启动] 前端静态页面由后端托管。>> logs\startup.log
start http://127.0.0.1:8000
echo [完成] 浏览器已打开：http://127.0.0.1:8000
echo [完成] 如需停止服务，请双击 stop_windows.bat
pause
