@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

set "ROOT=%~dp0"
cd /d "%ROOT%"
set "BUILD_EXIT_CODE=0"

if not exist logs mkdir logs
if not exist release mkdir release
set "LOG_FILE=%ROOT%logs\build_windows.log"
set "FRONTEND_DIR=%ROOT%frontend"
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "(Resolve-Path -LiteralPath 'frontend').ProviderPath"`) do set "FRONTEND_DIR=%%I"
break > "%LOG_FILE%"

call :log [开始] Windows 打包构建启动
call :log [信息] 项目目录：%ROOT%
call :log [检查] 正在检查 Python 环境……

where python >nul 2>nul
if errorlevel 1 (
  call :fail 环境检查 未检测到 Python，请先安装 Python 3.11+。
  goto end
)

call :log [检查] 正在检查 Node.js 环境……
where node >nul 2>nul
if errorlevel 1 (
  call :fail 环境检查 未检测到 Node.js，请先安装 Node.js 18+。
  goto end
)

call :log [检查] 正在检查 npm 环境……
where npm.cmd >nul 2>nul
if errorlevel 1 (
  call :fail 环境检查 未检测到 npm，请检查 Node.js 安装。
  goto end
)

call :log [检查] Python / Node / npm 已检测通过

if not exist frontend\dist\index.html (
  call :log [构建] 未检测到 frontend/dist，开始安装前端依赖
  pushd "%FRONTEND_DIR%"
  call npm.cmd install >> "%LOG_FILE%" 2>&1
  if errorlevel 1 (
    popd
    call :fail 前端构建 前端依赖安装失败，请查看 logs/build_windows.log。
    goto portable_only
  )
  call :log [构建] 正在构建前端……
  call npm.cmd run build >> "%LOG_FILE%" 2>&1
  popd
  if errorlevel 1 (
    call :fail 前端构建 前端构建失败，请查看 logs/build_windows.log。
    goto portable_only
  )
) else (
  call :log [复用] 已检测到 frontend/dist，跳过前端重建
)

call :log [检查] 开始执行 Windows 打包预检
python packaging\preflight_windows.py >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :fail PyInstaller 安装或预检 Windows 打包预检失败。请先阅读日志，再按提示处理 PyInstaller 或路径问题。
  goto portable_only
)

if exist build rmdir /s /q build >> "%LOG_FILE%" 2>&1
if exist dist rmdir /s /q dist >> "%LOG_FILE%" 2>&1
del /q release\PPT-Agent.exe >> "%LOG_FILE%" 2>&1

call :log [打包] 正在打包 PPT-Agent.exe……
python -m PyInstaller packaging\launcher.spec --clean --noconfirm >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :fail spec 打包 EXE 构建失败，本次仅生成 portable 包。
  goto portable_only
)

if not exist dist\PPT-Agent.exe (
  call :fail spec 打包 未找到 dist\PPT-Agent.exe，本次仅生成 portable 包。
  goto portable_only
)

copy /Y dist\PPT-Agent.exe release\PPT-Agent.exe >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  call :fail 文件复制 无法复制 release\PPT-Agent.exe，请检查目录权限。
  goto portable_only
)

call :copy_release_docs
if errorlevel 1 (
  call :fail 文件复制 发布文档复制失败，请查看 logs/build_windows.log。
  goto portable_only
)

call :build_portable
if errorlevel 1 (
  call :fail 文件复制 Portable 包生成失败，请检查 release 目录权限。
  goto end
)
call :log [完成] EXE 已生成：release\PPT-Agent.exe
call :log [完成] Portable 包目录：release\PPT-Agent-Portable
call :log [完成] 构建日志：logs\build_windows.log
call :log [完成] 打包完成，输出目录：release/
echo.
echo [完成] EXE 已生成：release\PPT-Agent.exe
echo [完成] Portable 包目录：release\PPT-Agent-Portable
echo [完成] 构建日志：logs\build_windows.log
echo [完成] 打包完成，输出目录：release/
goto end

:portable_only
call :build_portable
if errorlevel 1 (
  call :fail 文件复制 Portable 包生成失败，请检查 release 目录权限。
  goto end
)
call :copy_release_docs
echo.
echo [提示] EXE 构建失败，本次仅生成 portable 包。
echo [提示] Portable 包目录：release\PPT-Agent-Portable
echo [提示] 构建日志：logs\build_windows.log
goto end

:copy_release_docs
copy /Y README.md release\README.md >> "%LOG_FILE%" 2>&1
if errorlevel 1 exit /b 1
copy /Y WINDOWS_QUICKSTART.md release\WINDOWS_QUICKSTART.md >> "%LOG_FILE%" 2>&1
if errorlevel 1 exit /b 1
copy /Y RELEASE_NOTES.md release\RELEASE_NOTES.md >> "%LOG_FILE%" 2>&1
if errorlevel 1 exit /b 1
copy /Y .env.example release\.env.example >> "%LOG_FILE%" 2>&1
if errorlevel 1 exit /b 1
exit /b 0

:build_portable
if exist release\PPT-Agent-Portable rmdir /s /q release\PPT-Agent-Portable >> "%LOG_FILE%" 2>&1
mkdir release\PPT-Agent-Portable >> "%LOG_FILE%" 2>&1
copy /Y start_windows.bat release\PPT-Agent-Portable\start_windows.bat >> "%LOG_FILE%" 2>&1
if errorlevel 1 exit /b 1
copy /Y stop_windows.bat release\PPT-Agent-Portable\stop_windows.bat >> "%LOG_FILE%" 2>&1
if errorlevel 1 exit /b 1
copy /Y README.md release\PPT-Agent-Portable\README.md >> "%LOG_FILE%" 2>&1
if errorlevel 1 exit /b 1
copy /Y WINDOWS_QUICKSTART.md release\PPT-Agent-Portable\WINDOWS_QUICKSTART.md >> "%LOG_FILE%" 2>&1
if errorlevel 1 exit /b 1
copy /Y .env.example release\PPT-Agent-Portable\.env.example >> "%LOG_FILE%" 2>&1
if errorlevel 1 exit /b 1
exit /b 0

:log
echo %*
>> "%LOG_FILE%" echo %*
exit /b 0

:fail
echo [失败] %~1：%~2
>> "%LOG_FILE%" echo [失败] %~1：%~2
set "BUILD_EXIT_CODE=1"
exit /b 0

:end
if defined GITHUB_ACTIONS exit /b %BUILD_EXIT_CODE%
if /I "%CI%"=="true" exit /b %BUILD_EXIT_CODE%
pause
exit /b %BUILD_EXIT_CODE%
