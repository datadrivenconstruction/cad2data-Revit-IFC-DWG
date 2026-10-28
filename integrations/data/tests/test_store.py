import duckdb
import pyarrow.parquet as pq

from conftest import ROWS, make_xlsx, row
from ddc_data.store import to_duckdb, to_parquet
from ddc_data.xlsxio import read_workbook, split_unit


def test_split_unit():
    assert split_unit("Area (m²)") == ("Area", "m²")
    assert split_unit("Depth (parameter) (internal units)") == ("Depth (parameter)", "internal units")
    assert split_unit("Type Name") == ("Type Name", None)


def test_types_and_units(xlsx, tmp_path):
    to_parquet(xlsx, str(tmp_path / "o"))
    t = pq.read_table(tmp_path / "o" / "Elements.parquet")
    assert str(t.schema.field("ElementId").type) == "int64"
    f = t.schema.field("Volume (m³)")
    assert str(f.type) == "double" and f.metadata[b"unit"] == "m³".encode()
    assert str(t.schema.field("Category").type) == "string"
    assert t.num_rows == len(ROWS)
    assert t.column("Type Name").to_pylist()[6] == "Büro Ä/Ö"
    assert (tmp_path / "o" / "ddc_meta.parquet").exists() and (tmp_path / "o" / "ddc_units.parquet").exists()
    assert not (tmp_path / "o" / "_ddc_base.parquet").exists()


def test_include_base(xlsx):
    wb = read_workbook(xlsx, include_base=True)
    assert "_ddc_base" in wb.tables and wb.meta["format"] == "ddc-excel-base/1"


def test_category_partition(xlsx, tmp_path):
    to_parquet(xlsx, str(tmp_path / "o"), by_category=True)
    d = tmp_path / "o" / "Elements"
    parts = sorted(p.name for p in d.iterdir())
    assert "Category=Walls" in parts and "Category=Doors" in parts
    glob = (d / "**" / "*.parquet").as_posix()
    n = duckdb.connect().execute(f"select count(*) from read_parquet('{glob}', hive_partitioning=true)").fetchone()[0]
    assert n == len(ROWS)


def test_duckdb_tables_and_sums(xlsx, tmp_path):
    db = str(tmp_path / "x.duckdb")
    counts = to_duckdb(xlsx, db, by_category=True)
    assert counts["Elements"] == len(ROWS) and counts["Elements__walls"] == 3
    con = duckdb.connect(db, read_only=True)
    assert con.execute("select sum(\"Volume (m³)\") from Elements where Category='Walls'").fetchone()[0] == 12.6
    assert con.execute("select unit from ddc_units where \"column\"='Area (m²)'").fetchone()[0] == "m²"
    con.close()


def test_missing_columns_and_empty(tmp_path):
    p = make_xlsx(tmp_path / "a.xlsx", header=["ElementId", "Category"], rows=[[1, "Walls"], [2, None]])
    to_parquet(p, str(tmp_path / "o"))
    assert pq.read_table(tmp_path / "o" / "Elements.parquet").num_rows == 2
    e = make_xlsx(tmp_path / "e.xlsx", rows=[])
    to_parquet(e, str(tmp_path / "oe"))
    to_duckdb(e, str(tmp_path / "e.duckdb"), by_category=True)


def test_mixed_and_duplicate_headers(tmp_path):
    p = make_xlsx(tmp_path / "m.xlsx", header=["ElementId", "Mark", "Mark", "Volume (m³)"],
                  rows=[[1, "A", 5, 1.5], [2, 7, "x", "n/a"]], base=False)
    t = read_workbook(p).tables["Elements"]
    assert t.column_names == ["ElementId", "Mark", "Mark.1", "Volume (m³)"]
    assert str(t.schema.field("Volume (m³)").type) == "string"


def test_extra_sheet(tmp_path):
    p = make_xlsx(tmp_path / "s.xlsx", rows=[row(1, "Walls")],
                  extra_sheets={"Levels": (["ElementId", "Name", "Elevation (m)"], [[9, "L1", 0.0]])})
    out = to_parquet(p, str(tmp_path / "o"))
    assert any(x.endswith("Levels.parquet") for x in out)
