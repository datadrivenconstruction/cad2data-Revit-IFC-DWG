"""Column sets differ between model versions (2016-2026); every tool must tolerate the gaps."""
import glob
import os

import pytest

from conftest import make_xlsx
from ddc_data import bi
from ddc_data.builtin import BUILTIN
from ddc_data.frame import load
from ddc_data.render import render_html, render_xlsx
from ddc_data.report import run_template
from ddc_data.store import to_duckdb, to_parquet

VARIANTS = {
    "2016": ["ElementId", "Category", "Family", "Type Name", "Level", "Volume (m³)"],
    "2020": ["ElementId", "UniqueId", "Category", "Family", "Type Name", "Level", "Area (m²)", "Volume (m³)"],
    "2023": ["ElementId", "GlobalId", "UniqueId", "Category", "IfcClass", "Family", "Type Name", "Level",
             "Length (m)", "Area (m²)", "Volume (m³)", "Structural Material"],
    "2026_only_params": ["ElementId", "Category", "Fire Rating", "Comments"],
}


@pytest.mark.parametrize("ver", sorted(VARIANTS))
def test_pipeline_with_column_variant(ver, tmp_path):
    h = VARIANTS[ver]
    rows = [[100 + i] + [{"Category": "Walls" if i % 2 else "Doors"}.get(c, f"{c}{i}" if "(" not in c else float(i))
                         for c in h[1:]] for i in range(6)]
    p = make_xlsx(tmp_path / "v.xlsx", header=h, rows=rows)
    to_parquet(p, str(tmp_path / "pq"), by_category=True)
    to_duckdb(p, str(tmp_path / "v.duckdb"), by_category=True)
    fr = load(p)
    for name, tpl in BUILTIN.items():
        rep = run_template(tpl, fr)
        render_xlsx(rep, str(tmp_path / f"{name}.xlsx"))
        render_html(rep, str(tmp_path / f"{name}.html"))
    out = str(tmp_path / "bi")
    bi.export(p, out)
    assert bi.check(out)["ok"] and bi.check(out, "csv")["ok"]


SAMPLES = os.environ.get("DDC_DATA_SAMPLES")


@pytest.mark.skipif(not SAMPLES, reason="set DDC_DATA_SAMPLES to a folder of converter xlsx files")
def test_real_outputs(tmp_path):
    files = sorted(glob.glob(os.path.join(SAMPLES, "**", "*.xlsx"), recursive=True))
    assert files
    for i, f in enumerate(files):
        out = str(tmp_path / f"bi{i}")
        bi.export(f, out)
        assert bi.check(out)["ok"], f
