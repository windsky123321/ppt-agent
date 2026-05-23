@echo off
setlocal
chcp 65001 >nul
echo [检查] Windows 环境检查开始
where python >nul 2>nul && (echo [通过] Python 已安装 & python --version) || echo [失败] Python 未安装
where pip >nul 2>nul && (echo [通过] pip 可用 & pip --version) || echo [失败] pip 不可用
where node >nul 2>nul && (echo [通过] Node.js 已安装 & node -v) || echo [失败] Node.js 未安装
where npm.cmd >nul 2>nul && (echo [通过] npm 可用 & npm.cmd -v) || echo [失败] npm 不可用
if exist backend\.venv (echo [通过] backend\.venv 存在) else echo [失败] backend\.venv 不存在
if exist frontend\node_modules (echo [通过] frontend 依赖目录存在) else echo [提示] frontend\node_modules 不存在，将在启动时自动安装
if exist .env (echo [通过] .env 存在) else echo [提示] .env 不存在，将在启动时自动创建
if exist storage (echo [通过] storage 目录存在) else echo [提示] storage 目录不存在，将在运行时自动创建
if exist logs (echo [通过] logs 目录存在) else echo [提示] logs 目录不存在，将在启动时自动创建
pause
