from __future__ import annotations

import shutil
import sys
import uuid
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
LOCAL_TMP_ROOT = PROJECT_ROOT / ".test-tmp"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


@pytest.fixture
def local_tmp_dir() -> Path:
    LOCAL_TMP_ROOT.mkdir(parents=True, exist_ok=True)
    temp_dir = LOCAL_TMP_ROOT / f"run-{uuid.uuid4().hex}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
