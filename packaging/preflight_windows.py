from __future__ import annotations

import argparse
import importlib.util
import py_compile
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIST = ROOT / "frontend" / "dist" / "index.html"
RELEASE_DIR = ROOT / "release"
SPEC_PATH = ROOT / "packaging" / "launcher.spec"
ICON_PATH = ROOT / "packaging" / "app.ico"
LAUNCHER_PATH = ROOT / "desktop" / "launcher.py"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import _frontend_dist_dir  # noqa: E402


def _pip_available(python_exe: str) -> bool:
    result = subprocess.run(
        [python_exe, "-m", "pip", "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    return result.returncode == 0


def _pyinstaller_available() -> bool:
    return importlib.util.find_spec("PyInstaller") is not None


def _release_dir_writable(release_dir: Path) -> bool:
    release_dir.mkdir(parents=True, exist_ok=True)
    probe = release_dir / ".write_test.tmp"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def run_preflight(auto_install: bool = True, python_exe: str = sys.executable) -> tuple[bool, list[str]]:
    messages: list[str] = []

    if sys.version_info < (3, 11):
        messages.append("Python 版本过低，请使用 Python 3.11 或更高版本。")

    if not _pip_available(python_exe):
        messages.append("未检测到可用的 pip，请先修复 Python / pip 环境。")

    if not FRONTEND_DIST.exists():
        messages.append("未检测到 frontend/dist/index.html，请先构建前端资源。")

    try:
        static_dir = _frontend_dist_dir()
        if not static_dir.exists():
            messages.append("后端静态资源路径不可用，请检查 frontend/dist 与后端托管配置。")
    except Exception as exc:
        messages.append(f"后端静态资源路径检查失败：{exc}")

    if not SPEC_PATH.exists():
        messages.append("缺少 packaging/launcher.spec。")

    if not ICON_PATH.exists():
        messages.append("缺少 packaging/app.ico。")

    try:
        py_compile.compile(str(LAUNCHER_PATH), doraise=True)
    except Exception as exc:
        messages.append(f"launcher.py 编译检查失败：{exc}")

    if not _release_dir_writable(RELEASE_DIR):
        messages.append("release 目录不可写，请检查目录权限。")

    if messages:
        return False, messages

    if not _pyinstaller_available():
        print("未检测到 PyInstaller，正在尝试自动安装……")
        if auto_install:
            from install_packaging_deps import install_pyinstaller

            success, message = install_pyinstaller(python_exe=python_exe)
            print(message)
            if not success:
                return False, [message]
        else:
            return False, ["未检测到 PyInstaller，正在尝试自动安装……"]

    return True, ["Windows 打包预检通过。"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Windows release preflight checks.")
    parser.add_argument("--no-auto-install", action="store_true", help="Do not attempt automatic PyInstaller installation.")
    args = parser.parse_args()

    ok, messages = run_preflight(auto_install=not args.no_auto_install, python_exe=sys.executable)
    for message in messages:
        print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
