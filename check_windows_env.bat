@echo off
setlocal
chcp 65001 >nul

echo [检查] Windows 环境检查开始

where python >nul 2>nul && (echo [通过] Python 已安装 & python --version) || echo [失败] 未找到 Python
where pip >nul 2>nul && (echo [通过] pip 可用 & pip --version) || echo [失败] pip 不可用
where node >nul 2>nul && (echo [通过] Node.js 已安装 & node -v) || echo [失败] 未找到 Node.js
where npm.cmd >nul 2>nul && (echo [通过] npm 可用 & npm.cmd -v) || echo [失败] npm 不可用

if exist backend\.venv (
  echo [通过] backend\.venv 存在
) else (
  echo [提示] backend\.venv 不存在，启动时会自动创建
)

if exist frontend\node_modules (
  echo [通过] frontend\node_modules 存在
) else (
  echo [提示] frontend\node_modules 不存在，启动时会自动安装
)

if exist .env (
  echo [通过] .env 存在
) else (
  echo [提示] .env 不存在，启动时会自动创建
)

if exist storage (
  echo [通过] storage 目录存在
) else (
  echo [提示] storage 目录不存在，运行时会自动创建
)

if exist logs (
  echo [通过] logs 目录存在
) else (
  echo [提示] logs 目录不存在，启动时会自动创建
)

pause
