import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def set_test_storage(tmp_path: Path):
    os.environ["STORAGE_DIR"] = str(tmp_path / "storage")
    yield
    os.environ.pop("STORAGE_DIR", None)
