import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def set_test_storage(tmp_path: Path):
    os.environ["STORAGE_DIR"] = str(tmp_path / "storage")
    os.environ["PPT_AGENT_USER_DATA_DIR"] = str(tmp_path / "user-data")
    yield
    os.environ.pop("STORAGE_DIR", None)
    os.environ.pop("PPT_AGENT_USER_DATA_DIR", None)
