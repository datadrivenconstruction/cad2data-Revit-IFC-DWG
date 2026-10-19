import pytest

from ddc_tools import columns as C
from ddc_tools.loader import LoadError, load


@pytest.mark.parametrize("fmt", ["xlsx", "csv", "jsonl", "sqlite"])
def test_all_formats_give_same_rows(export_dir, fmt):
    rows, files = load(str(export_dir), fmt=fmt)
    assert len(rows) == 18
    assert files == [f"sample_model.{fmt}"]
    assert rows[0]["Category"] == "Walls"
    # empty cells are None in every format
    empty = [r for r in rows if r["Category"] == "Generic Models"][0]
    assert empty["Mark"] is None


def test_folder_prefers_sqlite_then_single_file(export_dir):
    _, files = load(str(export_dir))
    assert files == ["sample_model.sqlite"]
    rows, _ = load(str(export_dir / "sample_model.csv"))
    assert len(rows) == 18


def test_errors(tmp_path):
    with pytest.raises(LoadError):
        load(str(tmp_path / "missing"))
    with pytest.raises(LoadError):
        load(str(tmp_path))  # empty folder


def test_jsonl_nested_properties_are_flattened(tmp_path):
    p = tmp_path / "m.jsonl"
    p.write_text('{"GlobalId":"a","IfcClass":"IfcWall","Pset_WallCommon":{"FireRating":"EI 60"}}\n\n',
                 encoding="utf-8")
    rows, _ = load(str(p))
    assert rows == [{"GlobalId": "a", "IfcClass": "IfcWall", "Pset_WallCommon.FireRating": "EI 60"}]
    assert C.resolve(rows[0].keys(), "category") == "IfcClass"
    assert C.resolve(rows[0].keys(), "guid") == "GlobalId"


def test_aux_files_are_ignored(tmp_path):
    (tmp_path / "geometry_index.jsonl").write_text('{"native_id":"1"}\n', encoding="utf-8")
    (tmp_path / "elements.csv").write_text("native_id,source_class\n1,Wall\n", encoding="utf-8")
    rows, files = load(str(tmp_path))
    assert files == ["elements.csv"] and rows[0]["source_class"] == "Wall"


def test_to_number():
    assert C.to_number("12,5") == 12.5
    assert C.to_number("1 234.5 m2") == 1234.5
    assert C.to_number("n/a") is None
    assert C.to_number(None) is None
    assert C.to_number(True) is None


def test_csv_quoted_multiline_and_semicolon(tmp_path):
    p = tmp_path / "a.csv"
    p.write_bytes('Id;Name\n1;"two\nlines; with semicolon"\n2;x\n'.encode("utf-8"))
    rows, _ = load(str(p))
    assert len(rows) == 2 and rows[0]["Name"] == "two\nlines; with semicolon"
