import glob
import os

import openpyxl
import pytest

from conftest import ROWS, make_xlsx, row
from ddc_data import units
from ddc_data.builtin import BUILTIN
from ddc_data.categories import canonical
from ddc_data.cli import main
from ddc_data.frame import load
from ddc_data.render import render_html, render_xlsx
from ddc_data.report import TemplateError, load_template, run_template

EX = os.path.join(os.path.dirname(__file__), "..", "examples")


def sec(rep, title):
    return next(s for s in rep.sections if s.title == title)


def test_takeoff_totals(xlsx):
    rep = run_template(BUILTIN["quantity_takeoff"], load(xlsx))
    s = sec(rep, "By category")
    d = s.df.set_index("Category")
    assert d.loc["Walls", "Volume"] == pytest.approx(12.6)
    assert d.loc["Walls", "Count"] == 3
    assert s.totals["Volume"] == pytest.approx(89.1) and s.totals["Count"] == len(ROWS)
    assert s.units["Volume"] == "m³"


def test_none_level_grouped(xlsx):
    d = sec(run_template(BUILTIN["quantity_takeoff"], load(xlsx)), "By level").df
    assert "(none)" in set(d["Level"])
    assert d["Count"].sum() == len(ROWS)


def test_schedules(xlsx):
    rep = run_template(BUILTIN["door_window_schedule"], load(xlsx))
    assert len(sec(rep, "Doors").df) == 2 and len(sec(rep, "Windows").df) == 1
    assert sec(rep, "Doors by type").df["Count"].sum() == 2
    rooms = run_template(BUILTIN["room_schedule"], load(xlsx))
    assert sec(rooms, "Rooms").df["Area"].iloc[0] == 25.5
    assert "Number" in sec(rooms, "Rooms").note  # absent column is reported, not fatal


def test_wall_types(xlsx):
    d = sec(run_template(BUILTIN["wall_types_summary"], load(xlsx)), "Wall types").df
    assert d.iloc[0]["Type Name"] == "Generic - 200mm" and d.iloc[0]["Count"] == 2
    assert d.iloc[0]["Avg width"] == pytest.approx(0.2)


def test_fill_rate(xlsx):
    rep = run_template(BUILTIN["parameter_fill_rate"], load(xlsx))
    d = sec(rep, "Fill rate by category").df
    r = d[(d["Category"] == "Walls") & (d["Parameter"] == "Fire Rating")].iloc[0]
    assert r["Filled"] == 1 and r["Total"] == 3 and r["Fill rate"] == pytest.approx(1 / 3)
    ov = sec(rep, "Fill rate overall").df.set_index("Parameter")
    assert ov.loc["ElementId", "Fill rate"] == 1.0


def test_localized_categories(tmp_path):
    p = make_xlsx(tmp_path / "de.xlsx", rows=[row(1, "Wände", length=2, vol=1.0), row(2, "Türen"),
                                              row(3, "Fenêtres")])
    fr = load(p)
    assert list(fr.df["CategoryEn"]) == ["Walls", "Doors", "Windows"]
    assert canonical("  GESCHOSSE ") == "Levels" and canonical(None) == "(none)"
    d = sec(run_template(BUILTIN["wall_types_summary"], fr), "Wall types").df
    assert d["Count"].sum() == 1


def test_empty_categories_and_no_rows(tmp_path):
    p = make_xlsx(tmp_path / "e.xlsx", rows=[])
    rep = run_template(BUILTIN["quantity_takeoff"], load(p))
    assert all(len(s.df) == 0 for s in rep.sections)
    out = tmp_path / "r"
    render_xlsx(rep, f"{out}.xlsx")
    render_html(rep, f"{out}.html")
    assert "(no rows)" in open(f"{out}.html", encoding="utf-8").read()


def test_missing_columns_everywhere(tmp_path):
    p = make_xlsx(tmp_path / "m.xlsx", header=["ElementId", "Category"], rows=[[1, "Walls"], [2, "Doors"]])
    for name in BUILTIN:
        rep = run_template(BUILTIN[name], load(p))
        render_xlsx(rep, str(tmp_path / f"{name}.xlsx"))
        render_html(rep, str(tmp_path / f"{name}.html"))
    d = sec(run_template(BUILTIN["quantity_takeoff"], load(p)), "By category").df
    assert list(d["Count"]) == [1, 1]


def test_unicode_in_outputs(xlsx, tmp_path):
    rep = run_template(BUILTIN["room_schedule"], load(xlsx))
    render_xlsx(rep, str(tmp_path / "r.xlsx"))
    render_html(rep, str(tmp_path / "r.html"))
    ws = openpyxl.load_workbook(tmp_path / "r.xlsx")["Rooms"]
    assert "Büro Ä/Ö" in [c.value for c in ws[2]]
    assert "Büro" in open(tmp_path / "r.html", encoding="utf-8").read()


def test_unit_conversion():
    assert units.factor("m³", "ft3") == pytest.approx(35.3147, rel=1e-4)
    assert units.factor("m²", "ft²") == pytest.approx(10.7639, rel=1e-4)
    assert units.factor("internal units", "m") == pytest.approx(0.3048)
    assert units.factor("m³", "L") == 1000
    with pytest.raises(ValueError):
        units.factor("m", "m²")


def test_custom_examples_run(xlsx, tmp_path):
    files = sorted(glob.glob(os.path.join(EX, "*")))
    assert len(files) >= 3
    for f in files:
        rep = run_template(load_template(f), load(xlsx))
        assert rep.sections
        render_xlsx(rep, str(tmp_path / (os.path.basename(f) + ".xlsx")))
    rep = run_template(load_template(os.path.join(EX, "wall_volume_imperial.yaml")), load(xlsx))
    assert rep.sections[0].df["Volume"].sum() == pytest.approx(12.6 * 35.3147, rel=1e-4)
    assert rep.sections[0].units["Volume"] == "ft³"
    rep = run_template(load_template(os.path.join(EX, "fire_rated_doors.json")), load(xlsx))
    assert list(rep.sections[0].df["Rating"]) == ["30m"]


def test_template_errors(xlsx):
    fr = load(xlsx)
    with pytest.raises(TemplateError):
        run_template({"filters": [{"column": "Volume"}]}, fr)
    with pytest.raises(TemplateError):
        run_template({"group_by": ["Level"], "aggregates": [{"fn": "bogus", "column": "Area"}]}, fr)
    assert len(run_template({"filters": [{"column": "Nope", "eq": 1}]}, fr).sections[0].df) == 0


def test_filter_ops(xlsx):
    fr = load(xlsx)

    def n(f):
        return len(run_template({"filters": f}, fr).sections[0].df)

    assert n([{"column": "Type Name", "contains": "brick"}]) == 1
    assert n([{"column": "Type Name", "matches": r"^\d{4} x"}]) == 3
    assert n([{"column": "Volume", "ge": 3.6}]) == 3
    assert n([{"column": "Level", "isnull": True}]) == 1
    assert n([{"column": "Category", "not_in": ["Walls"]}]) == 5


def test_cli_report(xlsx, tmp_path, capsys):
    main(["report", xlsx, "-t", "wall_types_summary", "--out", str(tmp_path / "w")])
    assert (tmp_path / "w.xlsx").exists() and (tmp_path / "w.html").exists()
    main(["report", "--list"])
    assert "quantity_takeoff" in capsys.readouterr().out
