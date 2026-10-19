import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "examples"))

import make_sample  # noqa: E402


@pytest.fixture()
def export_dir(tmp_path):
    d = tmp_path / "export"
    make_sample.write_all(d)
    return d


@pytest.fixture()
def rows():
    h = make_sample.HEADER
    return [dict(zip(h, r)) for r in make_sample.rows()]


@pytest.fixture()
def rules_basic():
    return ROOT / "examples" / "rules_basic.yaml"
