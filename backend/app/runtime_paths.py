from __future__ import annotations

import os
import sys
from pathlib import Path


APP_NAME = "PPT Agent"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def is_frozen_runtime() -> bool:
    return bool(getattr(sys, "frozen", False))


def user_data_root() -> Path:
    override = os.getenv("PPT_AGENT_USER_DATA_DIR", "").strip()
    if override:
        return Path(override).resolve()
    if is_frozen_runtime():
        local_appdata = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return local_appdata / APP_NAME
    return project_root()


def skills_root() -> Path:
    return user_data_root() / "skills"


def usage_root() -> Path:
    return user_data_root() / "usage"
