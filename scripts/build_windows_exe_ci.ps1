$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

Write-Host "当前目录：$(Get-Location)"
Write-Host "Python 版本："
python --version
Write-Host "pip 版本："
python -m pip --version
Write-Host "Node 版本："
node --version
Write-Host "npm 版本："
npm.cmd --version

Write-Host "正在升级 pip……"
python -m pip install --upgrade pip
Write-Host "正在安装 PyInstaller……"
python -m pip install pyinstaller
Write-Host "PyInstaller 包信息："
python -m pip show pyinstaller
Write-Host "PyInstaller 版本："
python -m PyInstaller --version

if (-not (Test-Path "packaging/launcher.spec")) {
    throw "缺少 packaging/launcher.spec"
}
if (-not (Test-Path "desktop/launcher.py")) {
    throw "缺少 desktop/launcher.py"
}
if (-not (Test-Path "frontend/dist/index.html")) {
    Write-Host "未检测到 frontend/dist/index.html，正在构建前端……"
    Set-Location -LiteralPath (Join-Path $root "frontend")
    if (Test-Path "package-lock.json") {
        npm.cmd ci
    }
    else {
        npm.cmd install
    }
    npm.cmd run build
    Set-Location -LiteralPath $root
}

Write-Host "正在清理旧构建目录……"
if (Test-Path "release") {
    Remove-Item -Recurse -Force "release"
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
New-Item -ItemType Directory -Path "release" | Out-Null

Write-Host "正在打包 PPT-Agent.exe……"
python -m PyInstaller packaging/launcher.spec --noconfirm --clean

if (-not (Test-Path "dist/PPT-Agent.exe")) {
    Write-Host "未找到 dist/PPT-Agent.exe，输出诊断信息："
    foreach ($folder in @("release", "dist", "build")) {
        if (Test-Path $folder) {
            Write-Host "目录内容：$folder"
            Get-ChildItem -Recurse -Force $folder
        }
        else {
            Write-Host "目录不存在：$folder"
        }
    }
    throw "未能生成 dist/PPT-Agent.exe"
}

Copy-Item "dist/PPT-Agent.exe" "release/PPT-Agent.exe" -Force
Copy-Item "README.md" "release/README.md" -Force
Copy-Item "WINDOWS_QUICKSTART.md" "release/WINDOWS_QUICKSTART.md" -Force
Copy-Item "RELEASE_NOTES.md" "release/RELEASE_NOTES.md" -Force
Copy-Item ".env.example" "release/.env.example" -Force

foreach ($forbidden in @(".env", "logs", "outputs", "temp", "uploads")) {
    if (Test-Path (Join-Path "release" $forbidden)) {
        throw "release 中不应包含 $forbidden"
    }
}

if (-not (Test-Path "release/PPT-Agent.exe")) {
    throw "未找到 release/PPT-Agent.exe"
}

Write-Host "GitHub Actions Windows EXE 构建成功：release/PPT-Agent.exe"
