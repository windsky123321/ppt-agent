# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


root = Path.cwd()
backend_root = root / "backend"
frontend_dist = root / "frontend" / "dist"
icon_path = root / "packaging" / "app.ico"
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

hiddenimports = collect_submodules("app") + [
    "uvicorn",
    "uvicorn.config",
    "uvicorn.logging",
    "uvicorn.loops.auto",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan.on",
]

a = Analysis(
    ["desktop/launcher.py"],
    pathex=[str(root), str(backend_root)],
    binaries=[],
    datas=[
        (str(frontend_dist), "frontend/dist"),
    ],
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
    icon=str(icon_path),
)
