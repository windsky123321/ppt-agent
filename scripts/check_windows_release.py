from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = ROOT / "release"


def main() -> int:
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

    print("Windows 发布目录检查通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
