from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = ROOT / "release"


def main() -> int:
    print(f"当前目录：{ROOT}")
    print(f"packaging/launcher.spec 是否存在：{(ROOT / 'packaging' / 'launcher.spec').exists()}")
    print(f"desktop/launcher.py 是否存在：{(ROOT / 'desktop' / 'launcher.py').exists()}")
    print(f"frontend/dist/index.html 是否存在：{(ROOT / 'frontend' / 'dist' / 'index.html').exists()}")
    if RELEASE_DIR.exists():
        print("release 目录内容：")
        for path in sorted(RELEASE_DIR.rglob("*")):
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("release 目录不存在。")

    required = [
        RELEASE_DIR / "PPT-Agent.exe",
        RELEASE_DIR / "README.md",
        RELEASE_DIR / "WINDOWS_QUICKSTART.md",
        RELEASE_DIR / ".env.example",
    ]
    for path in required:
        if not path.exists():
            if path.name == "PPT-Agent.exe":
                print("未找到 PPT-Agent.exe，请确认 PyInstaller 已安装，并重新运行 build_release_windows.bat。")
            else:
                print(f"缺少发布文件：{path.relative_to(ROOT)}")
            return 1

    forbidden = [
        RELEASE_DIR / ".env",
        RELEASE_DIR / "logs",
        RELEASE_DIR / "outputs",
        RELEASE_DIR / "temp",
        RELEASE_DIR / "uploads",
    ]
    for path in forbidden:
        if path.exists():
            print(f"发布目录中不应包含：{path.relative_to(ROOT)}")
            return 1

    print("Release check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
