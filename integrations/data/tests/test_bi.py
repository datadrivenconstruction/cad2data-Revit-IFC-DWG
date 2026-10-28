import duckdb
import pandas as pd
import pytest

from conftest import ROWS, make_xlsx
from ddc_data import bi
from ddc_data.cli import main


def test_star_integrity_parquet_and_csv(xlsx, tmp_path):
    out = str(tmp_path / "bi")
    counts = bi.export(xlsx, out)
    assert counts["fact_elements"] == len(ROWS)
    for fmt in ("parquet", "csv"):
        r = bi.check(out, fmt)
        assert r["ok"], r
        assert r["fact_rows"] == r["joined_rows"] == len(ROWS)
    for f in ("powerbi/DDC_StarSchema.pq", "powerbi/DDC_tables.pq", "powerbi/README.md", "tableau/README.md",
              "relationships.json"):
        assert (tmp_path / "bi" / f).exists()


def test_unassigned_members_and_sums(xlsx, tmp_path):
    out = (tmp_path / "bi").as_posix()
    bi.export(xlsx, out)
    con = duckdb.connect()
    for t in bi.TABLES:
        con.execute(f"create table {t} as select * from read_parquet('{out}/parquet/{t}.parquet')")
    assert con.execute("select count(*) from fact_elements f join dim_level l using(level_key) "
                       "where l.level='(unassigned)'").fetchone()[0] == 1
    v = con.execute("select sum(volume_m3) from fact_elements f join dim_category c using(category_key) "
                    "where c.category='Walls'").fetchone()[0]
    assert v == pytest.approx(12.6)
    m = dict(con.execute("select m.material, count(*) from fact_elements f join dim_material m using(material_key) "
                         "group by 1").fetchall())
    assert m["Concrete"] == 2 and m["Oak"] == 2 and m["(unassigned)"] == 3


def test_orphans_are_detected(xlsx, tmp_path):
    out = str(tmp_path / "bi")
    bi.export(xlsx, out)
    p = f"{out}/csv/dim_level.csv"
    d = pd.read_csv(p)
    d[d.level_key != 1].to_csv(p, index=False)
    r = bi.check(out, "csv")
    assert not r["ok"] and r["fact_elements.level_key->dim_level"] > 0


def test_missing_columns_unicode_and_empty(tmp_path):
    p = make_xlsx(tmp_path / "a.xlsx", header=["ElementId", "Category", "Level"],
                  rows=[[1, "Mauern ü", "Ebene Ä"], [2, "Mauern ü", None], [3, None, None]])
    out = str(tmp_path / "bi")
    bi.export(p, out)
    assert bi.check(out)["ok"] and bi.check(out, "csv")["ok"]
    e = make_xlsx(tmp_path / "e.xlsx", rows=[])
    bi.export(e, str(tmp_path / "be"))
    assert bi.check(str(tmp_path / "be"))["ok"]


def test_cli_to_bi(xlsx, tmp_path, capsys):
    main(["to-bi", xlsx, "--out", str(tmp_path / "b")])
    assert '"ok": true' in capsys.readouterr().out
    with pytest.raises(SystemExit) as e:
        main(["bi-check", str(tmp_path / "b"), "--format", "csv"])
    assert e.value.code == 0


def test_m_script_lists_all_tables(xlsx, tmp_path):
    bi.export(xlsx, str(tmp_path / "b"))
    m = (tmp_path / "b" / "powerbi" / "DDC_StarSchema.pq").read_text(encoding="utf-8")
    for t in bi.TABLES:
        assert f"{t}.csv" in m
    assert "Int64.Type" in m and "type number" in m
