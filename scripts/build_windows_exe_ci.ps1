$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

Write-Host "Current directory:"
Get-Location

Write-Host "Python version:"
python --version

Write-Host "pip version:"
python -m pip --version

Write-Host "Node version:"
node --version

Write-Host "npm version:"
npm.cmd --version

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "Installing PyInstaller..."
python -m pip install pyinstaller

Write-Host "PyInstaller package info:"
python -m pip show pyinstaller

Write-Host "PyInstaller version:"
python -m PyInstaller --version

if (-not (Test-Path -LiteralPath "packaging/launcher.spec")) {
    Write-Host "Missing packaging/launcher.spec"
    exit 1
}

if (-not (Test-Path -LiteralPath "desktop/launcher.py")) {
    Write-Host "Missing desktop/launcher.py"
    exit 1
}

if (-not (Test-Path -LiteralPath "backend/app/storage")) {
    Write-Host "backend/app/storage is missing before packaging"
    exit 1
}

if (-not (Test-Path -LiteralPath "backend/app/storage/__init__.py")) {
    Write-Host "backend/app/storage/__init__.py is missing before packaging"
    exit 1
}

Write-Host "git ls-files backend/app/storage:"
git ls-files backend/app/storage

if (-not (Test-Path -LiteralPath "frontend/dist/index.html")) {
    Write-Host "frontend/dist/index.html not found. Building frontend..."
    Push-Location -LiteralPath "frontend"
    if (Test-Path -LiteralPath "package-lock.json") {
        npm.cmd ci
    }
    else {
        npm.cmd install
    }
    npm.cmd run build
    Pop-Location
}

Write-Host "launcher.spec exists:"
Test-Path -LiteralPath "packaging/launcher.spec"
Write-Host "desktop/launcher.py exists:"
Test-Path -LiteralPath "desktop/launcher.py"
Write-Host "backend/app/storage exists:"
Test-Path -LiteralPath "backend/app/storage"
Write-Host "backend/app/storage/__init__.py exists:"
Test-Path -LiteralPath "backend/app/storage/__init__.py"
Write-Host "frontend/dist/index.html exists:"
Test-Path -LiteralPath "frontend/dist/index.html"
Write-Host "launcher.spec preview:"
Get-Content -LiteralPath "packaging/launcher.spec" | Select-Object -First 80

if (Test-Path -LiteralPath "release") {
    Remove-Item -LiteralPath "release" -Recurse -Force
}
if (Test-Path -LiteralPath "build") {
    Remove-Item -LiteralPath "build" -Recurse -Force
}
if (Test-Path -LiteralPath "dist") {
    Remove-Item -LiteralPath "dist" -Recurse -Force
}

New-Item -ItemType Directory -Path "release" | Out-Null

Write-Host "Running PyInstaller..."
python -m PyInstaller packaging/launcher.spec --noconfirm --clean

if (-not (Test-Path -LiteralPath "dist/PPT-Agent.exe")) {
    Write-Host "dist/PPT-Agent.exe not found"

    if (Test-Path -LiteralPath "release") {
        Write-Host "release contents:"
        Get-ChildItem -LiteralPath "release" -Recurse -Force
    }
    else {
        Write-Host "release directory not found"
    }

    if (Test-Path -LiteralPath "dist") {
        Write-Host "dist contents:"
        Get-ChildItem -LiteralPath "dist" -Recurse -Force
    }
    else {
        Write-Host "dist directory not found"
    }

    if (Test-Path -LiteralPath "build") {
        Write-Host "build contents:"
        Get-ChildItem -LiteralPath "build" -Recurse -Force
    }
    else {
        Write-Host "build directory not found"
    }

    if (Test-Path -LiteralPath "desktop") {
        Write-Host "desktop contents:"
        Get-ChildItem -LiteralPath "desktop" -Recurse -Force
    }
    else {
        Write-Host "desktop directory not found"
    }

    if (Test-Path -LiteralPath "packaging") {
        Write-Host "packaging contents:"
        Get-ChildItem -LiteralPath "packaging" -Recurse -Force
    }
    else {
        Write-Host "packaging directory not found"
    }

    exit 1
}

Copy-Item -LiteralPath "dist/PPT-Agent.exe" -Destination "release/PPT-Agent.exe" -Force

if (Test-Path -LiteralPath "README.md") {
    Copy-Item -LiteralPath "README.md" -Destination "release/README.md" -Force
}
if (Test-Path -LiteralPath "WINDOWS_QUICKSTART.md") {
    Copy-Item -LiteralPath "WINDOWS_QUICKSTART.md" -Destination "release/WINDOWS_QUICKSTART.md" -Force
}
if (Test-Path -LiteralPath "RELEASE_NOTES.md") {
    Copy-Item -LiteralPath "RELEASE_NOTES.md" -Destination "release/RELEASE_NOTES.md" -Force
}
if (Test-Path -LiteralPath ".env.example") {
    Copy-Item -LiteralPath ".env.example" -Destination "release/.env.example" -Force
}

if (Test-Path -LiteralPath "release/.env") {
    Write-Host "release/.env must not exist"
    exit 1
}
if (Test-Path -LiteralPath "release/logs") {
    Write-Host "release/logs must not exist"
    exit 1
}
if (Test-Path -LiteralPath "release/outputs") {
    Write-Host "release/outputs must not exist"
    exit 1
}
if (Test-Path -LiteralPath "release/temp") {
    Write-Host "release/temp must not exist"
    exit 1
}
if (Test-Path -LiteralPath "release/uploads") {
    Write-Host "release/uploads must not exist"
    exit 1
}

if (-not (Test-Path -LiteralPath "release/PPT-Agent.exe")) {
    Write-Host "release/PPT-Agent.exe not found"
    exit 1
}

Write-Host "CI Windows EXE build succeeded: release/PPT-Agent.exe"
