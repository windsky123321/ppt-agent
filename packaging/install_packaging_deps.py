from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WHEELHOUSE = ROOT / "packaging" / "wheelhouse"


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="ignore")


def has_local_pyinstaller_wheel(wheelhouse: Path = WHEELHOUSE) -> bool:
    return any(wheelhouse.glob("pyinstaller-*.whl")) or any(wheelhouse.glob("PyInstaller-*.whl"))


def install_pyinstaller(python_exe: str = sys.executable, wheelhouse: Path = WHEELHOUSE) -> tuple[bool, str]:
    if has_local_pyinstaller_wheel(wheelhouse):
        print("检测到本地 wheelhouse，优先离线安装 PyInstaller……")
        result = _run(
            [
                python_exe,
                "-m",
                "pip",
                "install",
                "--no-index",
                "--find-links",
                str(wheelhouse),
                "pyinstaller",
            ]
        )
        if result.returncode == 0:
            return True, "已通过本地 wheelhouse 安装 PyInstaller。"
        message = (result.stdout + "\n" + result.stderr).strip()
        print(message)
        return False, "离线安装 PyInstaller 失败。"

    print("未检测到本地 wheelhouse，正在尝试在线安装 PyInstaller……")
    result = _run([python_exe, "-m", "pip", "install", "pyinstaller"])
    if result.returncode == 0:
        return True, "已通过在线方式安装 PyInstaller。"
    message = (result.stdout + "\n" + result.stderr).strip()
    if message:
        print(message)
    return False, "自动安装失败，可能是网络受限。请先执行 python -m pip install pyinstaller 后重新运行本脚本。"


def main() -> int:
    parser = argparse.ArgumentParser(description="Install packaging dependencies for Windows release build.")
    parser.add_argument("--python", default=sys.executable, help="Python executable to use.")
    args = parser.parse_args()

    success, message = install_pyinstaller(python_exe=args.python)
    print(message)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
