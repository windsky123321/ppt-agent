# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


spec_dir = Path(SPECPATH).resolve()
project_root = spec_dir.parent
launcher_script = str(project_root / "desktop" / "launcher.py")
backend_root = project_root / "backend"
backend_app = project_root / "backend" / "app"
frontend_dist = project_root / "frontend" / "dist"
icon_path = project_root / "packaging" / "app.ico"
env_example = project_root / ".env.example"

if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

hiddenimports = collect_submodules("app") + [
    "app",
    "app.storage",
    "app.api",
    "app.agents",
    "app.schemas",
    "app.llm",
    "app.prompts",
    "app.utils",
    "uvicorn",
    "uvicorn.config",
    "uvicorn.logging",
    "uvicorn.loops.auto",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan.on",
]

datas = []
if frontend_dist.exists():
    datas.append((str(frontend_dist), "frontend/dist"))
if backend_app.exists():
    datas.append((str(backend_app), "backend/app"))
if env_example.exists():
    datas.append((str(env_example), "."))

a = Analysis(
    [launcher_script],
    pathex=[str(project_root), str(backend_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        ".env",
        "logs",
        "storage",
        "outputs",
        "temp",
        "uploads",
        "release",
        "build",
        "dist",
        "tests",
        "examples",
        "__pycache__",
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PPT-Agent",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path.exists() else None,
)
