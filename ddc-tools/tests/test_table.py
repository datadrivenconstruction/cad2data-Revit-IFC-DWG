"""Tests for ``ddc table`` on trimmed real converter output (see tests/data/README.md)."""
import json
import math
import shutil
import sqlite3
import struct
from pathlib import Path

import pytest

from ddc_tools import cli, ifcmodel, table
from ddc_tools.loader import load

DATA = Path(__file__).parent / "data"
README = Path(__file__).resolve().parents[1] / "README.md"


def by_id(t, i):
    return next(r for r in t.rows if r["ID"] == i)


# --------------------------------------------------------------------------- IFC to Excel tables

@pytest.fixture(scope="module")
def ifc_table():
    return table.build_table(str(DATA / "ifc_excel"))


def test_ifc_excel_rows_and_identity(ifc_table):
    t = ifc_table
    assert t.kind == "ifc-excel"
    # 19 objects in the fixture: 4 spatial + 3 types dropped by default -> 10 products
    assert len(t.rows) == 10
    classes = {r["IfcClass"] for r in t.rows}
    assert "IfcBuildingStorey" not in classes and "IfcOpeningElement" not in classes
    w = by_id(t, 4131)
    assert w["GlobalId"] == "2O2Fr$t4X7Zf8NOew3FNld"
    assert w["Category"] == "IfcWallStandardCase"
    assert w["Family"] == "Basic Wall"
    assert w["Type Name"] == "Interior - Partition (92mm Stud)"
    assert w["Family and Type"] == "Basic Wall: Interior - Partition (92mm Stud)"
    assert w["Level"] == "Level 1"
    assert w["Material"] == "Plasterboard; Metal - Stud Layer"


def test_ifc_quantities_and_source(ifc_table):
    w = by_id(ifc_table, 4131)
    assert w["Length"] == pytest.approx(3.7915)
    assert w["Width"] == pytest.approx(0.124)
    assert w["Height"] == pytest.approx(2.795)
    assert w["Area"] == pytest.approx(10.014485)
    assert w["Volume"] == pytest.approx(1.2417961, rel=1e-6)
    assert "Volume=property:PSet_Revit_Dimensions.Volume" in w["Quantity Source"]
    # the property that fed a quantity column is not repeated as a second column
    assert "PSet_Revit_Dimensions.Volume" not in w and "PSet_Revit_Dimensions.Area" not in w


def test_ifc_type_comes_from_type_link_for_windows(ifc_table):
    win = next(r for r in ifc_table.rows if r["IfcClass"] == "IfcWindow")
    assert win["Type Name"] == "4835mm x 2420mm"
    assert win["Family"] == "M_Fixed"
    assert win["Width"] == pytest.approx(4.835)            # from the type property set


def test_ifc_parameters_are_plain_columns_and_collisions_are_qualified(ifc_table):
    w = by_id(ifc_table, 4131)
    assert w["IsExternal"] is False or w["IsExternal"] == "False"
    assert w["Base Constraint"] == "Level 1"
    # same name, different value in another set -> qualified column, first value keeps the plain name
    assert "PSet_Revit_Type_Other.Material" in ifc_table.columns


def test_ifc_qualified_flag_and_all_rows():
    t = table.build_table(str(DATA / "ifc_excel"), qualified=True, include_all=True)
    w = by_id(t, 4131)
    assert w["Pset_WallCommon.IsExternal"] in (False, "False")
    assert {r["IfcClass"] for r in t.rows} >= {"IfcBuildingStorey", "IfcOpeningElement", "IfcProject"}


def _write_sqlite(src: Path, dst: Path):
    con = sqlite3.connect(dst)
    con.execute("create table records(table_name text not null, ordinal integer not null, record_json text not null,"
                " primary key(table_name, ordinal))")
    for line in src.read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        con.execute("insert into records values (?,?,?)", (d["table"], d["ordinal"], json.dumps(d["record"])))
    con.commit()
    con.close()


def _write_xlsx(src: Path, dst: Path):
    from openpyxl import Workbook
    recs = {}
    for line in src.read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        recs.setdefault(d["table"], []).append(d["record"])
    wb = Workbook()
    wb.remove(wb.active)
    for tbl, rows in recs.items():
        ws = wb.create_sheet(tbl)
        cols = list(dict.fromkeys(k for r in rows for k in r))
        ws.append(cols)
        for r in rows:
            ws.append([json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else
                       (str(v) if isinstance(v, bool) else v) for v in (r.get(c) for c in cols)])
    wb.save(dst)


@pytest.mark.parametrize("fmt", ["sqlite", "xlsx"])
def test_ifc_excel_all_three_formats_give_the_same_table(tmp_path, ifc_table, fmt):
    src = DATA / "ifc_excel" / "data.jsonl"
    f = tmp_path / ("data.sqlite" if fmt == "sqlite" else "drawing.xlsx")
    (_write_sqlite if fmt == "sqlite" else _write_xlsx)(src, f)
    t = table.build_table(str(tmp_path))
    assert t.kind == "ifc-excel"
    assert t.columns == ifc_table.columns
    assert t.rows == ifc_table.rows


def test_converter_subfolder_is_found(tmp_path):
    sub = tmp_path / "Duplex-440646b4da26"
    shutil.copytree(DATA / "ifc_excel", sub)
    assert len(table.build_table(str(tmp_path)).rows) == 10


# --------------------------------------------------------------------------- IFC STEP text

def test_step_tokenizer_escapes_and_nesting():
    args, _ = ifcmodel._parse_args("('a''b',#12,.T.,$,*,-1.5E-3,(1,2.,(#3)),IFCLABEL('m\\X2\\00B2\\X0\\'))", 0)
    assert args[0] == "a'b" and args[1].id == "12" and args[2] == ".T."
    assert args[3] is None and args[4] == "*" and args[5] == pytest.approx(-0.0015)
    assert args[6][2][0].id == "3"
    assert args[7].type == "IFCLABEL" and args[7].value == "m²"


def test_step_file_gives_revit_identity_rows():
    t = table.build_table(str(DATA / "rvt_converted" / "native_graph.ifc"))
    assert t.kind == "ifc-step"
    walls = [r for r in t.rows if r["IfcClass"] == "IfcWall"]
    assert len(walls) == 2
    w = walls[0]
    assert (w["ID"], w["ElementId"]) == (1001, 1001)       # Revit ElementId, not the STEP id
    assert w["Category"] == "OST_Walls" and w["Category Name"] == "Walls"
    assert (w["Family"], w["Type Name"], w["Level"]) == ("Test Wall", "Test Type A", "Level A")
    assert w["Revit Class"] == "SWall" and w["Type Id"] == 601
    assert w["Length"] == pytest.approx(2.5) and w["Width"] == pytest.approx(0.3)
    assert w["Material"] == "Test Material"
    assert w["LoadBearing"] in (False, "False")


# --------------------------------------------------------------------------- RVT

def test_rvt_properties_only_resolves_level_category_and_skips_types():
    folder = DATA / "rvt_converted"
    t = table.build_table(str(folder), use_ifc=False)
    assert t.kind == "rvt"
    ids = [r["ID"] for r in t.rows]
    assert 601 not in ids                                  # the wall type is not an element row
    wall = by_id(t, 1001)
    assert wall["Category"] == "OST_Walls" and wall["Revit Class"] == "SWall"
    assert wall["Level"] == "Level A"                       # via the Level element's text
    assert wall["Type Id"] == 601
    assert wall["Unconnected Height"] == pytest.approx(9.84251968503937)   # Revit feet
    assert "feet" in wall["Parameter Units"]
    assert any("native_graph.ifc not found" in n for n in t.notes)
    lvl = by_id(t, 501)
    assert lvl["Category"] == "OST_Levels" and lvl["Name"] == "Level A"


def test_rvt_with_ifc_adds_names_and_metric_values():
    t = table.build_table(str(DATA / "rvt_converted"))
    assert t.kind == "rvt+ifc"
    wall = by_id(t, 1001)
    assert (wall["Family"], wall["Type Name"]) == ("Test Wall", "Test Type A")
    assert wall["Height"] == pytest.approx(3.0)             # metres from the IFC, not feet
    assert wall["Top Offset"] == 0
    # all four sources agree on the element ids
    assert {r["ID"] for r in t.rows} >= {1, 501, 1001, 1002}


def _write_cube_glb(path: Path, element_id: int, edge_ft: float, scale=0.3048):
    v = [(x, y, z) for x in (0, edge_ft) for y in (0, edge_ft) for z in (0, edge_ft)]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    idx = []
    for a, b, c, d in quads:
        idx += [a, b, c, a, c, d]
    pos = b"".join(struct.pack("<3f", *p) for p in v)
    ind = b"".join(struct.pack("<H", i) for i in idx)
    ind += b"\x00" * (-len(ind) % 4)
    blob = pos + ind
    g = {"asset": {"version": "2.0"},
         "buffers": [{"byteLength": len(blob)}],
         "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": len(pos)},
                         {"buffer": 0, "byteOffset": len(pos), "byteLength": len(ind)}],
         "accessors": [{"bufferView": 0, "componentType": 5126, "count": 8, "type": "VEC3"},
                       {"bufferView": 1, "componentType": 5123, "count": len(idx), "type": "SCALAR"}],
         "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
         "nodes": [{"mesh": 0, "extras": {"element_id": element_id},
                    "matrix": [scale, 0, 0, 0, 0, 0, -scale, 0, 0, scale, 0, 0, 0, 0, 0, 1]}],
         "scenes": [{"nodes": [0]}], "scene": 0}
    js = json.dumps(g).encode()
    js += b" " * (-len(js) % 4)
    total = 12 + 8 + len(js) + 8 + len(blob)
    path.write_bytes(b"glTF" + struct.pack("<II", 2, total) + struct.pack("<I", len(js)) + b"JSON" + js
                     + struct.pack("<I", len(blob)) + b"BIN\x00" + blob)


def test_glb_mesh_quantities_are_metric_and_fill_missing_volume(tmp_path):
    folder = tmp_path / "m.converted"
    shutil.copytree(DATA / "rvt_converted", folder)
    (folder / "native_graph.ifc").unlink()
    _write_cube_glb(folder / "native_graph.glb", 1001, edge_ft=10.0)
    q = table.read_glb_quantities(folder / "native_graph.glb")["1001"]
    edge = 10.0 * 0.3048
    assert abs(q["volume"]) == pytest.approx(edge ** 3, rel=1e-5)
    assert q["area"] == pytest.approx(6 * edge ** 2, rel=1e-5)
    t = table.build_table(str(folder))
    w = by_id(t, 1001)
    assert w["Volume"] == pytest.approx(edge ** 3, rel=1e-5)
    assert w["Quantity Source"] == "Volume=glb-mesh; Area=glb-mesh"
    assert w["BBox X"] == pytest.approx(edge, rel=1e-5) and w["BBox Z"] == pytest.approx(edge, rel=1e-5)
    # --no-glb keeps the table without mesh columns
    assert "Mesh Volume" not in table.build_table(str(folder), use_glb=False).columns


def test_rvt_missing_properties_is_an_error(tmp_path):
    with pytest.raises(table.TableError):
        table.rvt_rows(tmp_path)


# --------------------------------------------------------------------------- DWG

def test_dwg_geometry_and_columns():
    t = table.build_table(str(DATA / "dwg"))
    assert t.kind == "dwg"
    cats = {r["Category"] for r in t.rows}
    assert {"LINE", "CIRCLE", "LWPOLYLINE", "ARC", "TEXT", "INSERT"} <= cats
    assert "BLOCK" not in cats and "ENDBLK" not in cats and "LAYER" not in cats
    line = next(r for r in t.rows if r["Category"] == "LINE")
    assert line["Length"] == pytest.approx(102.5946148, rel=1e-7)
    assert line["Layer"] == "Layer1" and line["Level"] == "T"
    circ = next(r for r in t.rows if r["Category"] == "CIRCLE")
    assert circ["Perimeter"] == pytest.approx(2 * math.pi * 30.0, rel=1e-9)
    assert circ["Area"] == pytest.approx(math.pi * 900, rel=1e-9)
    closed = next(r for r in t.rows if r["Category"] == "LWPOLYLINE" and r.get("Area"))
    assert closed["Perimeter"] == closed["Length"]
    ins = next(r for r in t.rows if r["Category"] == "INSERT")
    assert ins["Type Name"] == "_ArchTick"
    unknown = next(r for r in t.rows if r["Category"].startswith("UNKNOWN"))
    assert unknown["Coverage"] == "ENVELOPE_ONLY"
    # verbose nested columns are not copied
    assert not any(c.startswith(("parameters.", "metadata.")) for c in t.columns)


def test_dwg_bulge_arc_length():
    # half circle of radius 1 between (0,0) and (2,0): bulge = 1, length = pi
    row = {"vertices_json": "[[0,0],[2,0]]", "bulges_json": "[1.0, 0.0]", "closed": False}
    length, area, ok = table._poly_metrics(row)
    assert ok and length == pytest.approx(math.pi) and area is None


def test_dwg_csv_input(tmp_path):
    rows, _ = load(str(DATA / "dwg" / "sample.jsonl"))
    import csv
    p = tmp_path / "a.csv"
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if v is None else v) for k, v in r.items()})
    assert len(table.build_table(str(p)).rows) == len(table.build_table(str(DATA / "dwg")).rows)


# --------------------------------------------------------------------------- CLI and the other tools

def test_cli_writes_xlsx_csv_jsonl_and_qto_reads_the_result(tmp_path, capsys):
    x, c, j = tmp_path / "t.xlsx", tmp_path / "t.csv", tmp_path / "t.jsonl"
    assert cli.main(["table", str(DATA / "ifc_excel"), "--xlsx", str(x), "--csv", str(c), "--jsonl", str(j)]) == 0
    assert "ifc-excel: 10 elements" in capsys.readouterr().out
    from openpyxl import load_workbook
    wb = load_workbook(x, read_only=True)
    assert wb.sheetnames == ["Project_Data", "Info"]
    header = [cell for cell in next(wb["Project_Data"].iter_rows(values_only=True))]
    assert header[:4] == ["ID", "GlobalId", "Category", "Category Name"]
    wb.close()
    assert c.read_bytes().startswith(b"\xef\xbb\xbf")
    assert len(j.read_text(encoding="utf-8").splitlines()) == 10
    # the existing tools understand the table
    rows, _ = load(str(x))
    assert len(rows) == 10
    out = tmp_path / "qto.json"
    assert cli.main(["qto", str(x), "--json", str(out), "-q"]) in (0, 1)
    res = json.loads(out.read_text(encoding="utf-8"))
    assert res["elements"] == 10 and {"Volume", "Area"} <= set(res["quantity_columns"])


def test_cli_columns_and_errors(tmp_path, capsys):
    assert cli.main(["table", "x", "--columns"]) == 0
    assert "| Volume |" in capsys.readouterr().out
    assert cli.main(["table", str(tmp_path / "nope")]) == 2


def test_documented_columns_match_the_code():
    text = README.read_text(encoding="utf-8")
    for col in table.FIXED_COLUMNS:
        assert f"`{col}`" in text, f"column {col} is not documented in README.md"


def test_3d_view_flag_for_the_old_workflows():
    t = table.build_table(str(DATA / "rvt_converted"))
    assert by_id(t, 1001)["On the standard 3D View"] is True
    assert by_id(t, 501)["On the standard 3D View"] is False        # a level has no model geometry
    assert all(r["On the standard 3D View"] for r in table.build_table(str(DATA / "ifc_excel")).rows)
    d = table.build_table(str(DATA / "dwg"))
    assert by_id(d, "2E2")["On the standard 3D View"] is True        # model space
    assert by_id(d, "6F7")["On the standard 3D View"] is False       # inside a block definition
