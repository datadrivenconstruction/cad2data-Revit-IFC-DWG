"""International use: non-ASCII / spaced / long paths, CSV for Excel, invariant numbers, ISO dates,
classification mapping. All data is synthetic (Cyrillic, Chinese, Arabic, German, Greek text)."""
import csv
import json
import os
import re
import sqlite3
from pathlib import Path

import pytest

from ddc_tools import classify, cli, paths, qto, table
from ddc_tools.columns import to_number
from ddc_tools.loader import load

NAMES = [
    "Проект Дом №1 & Co",          # Cyrillic, spaces, ampersand
    "办公楼 项目 #2 100%",          # Chinese, '#' and '%' (break file: URIs)
    "مشروع المبنى (نسخة 3)",       # Arabic, parentheses
    "Wärmeschutz Größe, Ärzte",    # German umlauts
    "Έργο Αθήνα",                  # Greek
]

ROWS = [
    {"ID": "1", "Category": "OST_Walls", "Type Name": "Стена кирпичная 380", "Level": "Этаж 1", "Area": 12.5, "Volume": 4.75},
    {"ID": "2", "Category": "OST_Walls", "Type Name": "墙 混凝土 200", "Level": "一层", "Area": 1234.5, "Volume": 246.9},
    {"ID": "3", "Category": "OST_Doors", "Type Name": "باب خشبي", "Level": "الطابق الأول", "Area": 2.1, "Volume": None},
    {"ID": "4", "Category": "OST_Floors", "Type Name": "Stahlbeton Decke 25", "Level": "EG", "Area": 80, "Volume": 20},
]


def mk_table(rows=ROWS):
    cols = list(rows[0])
    return table.Table(cols, [dict(r) for r in rows], "table", "synthetic")


# --------------------------------------------------------------------------- paths

def test_fs_extended_length_prefix_rules():
    bs = chr(92)
    long_drive = "C:" + bs + "a" * 250 + bs + "f.csv"
    assert paths.fs(long_drive, _windows=True) == bs * 2 + "?" + bs + long_drive
    unc = bs * 2 + "srv" + bs + "share" + bs + "x" * 250 + bs + "f.csv"
    assert paths.fs(unc, _windows=True) == bs * 2 + "?" + bs + "UNC" + bs + unc[2:]
    assert paths.fs("C:/short/Проект.csv", _windows=True) == "C:/short/Проект.csv"      # short paths untouched
    assert paths.fs(long_drive, _windows=False) == long_drive                           # other systems untouched
    already = bs * 2 + "?" + bs + long_drive
    assert paths.fs(already, _windows=True) == already


@pytest.mark.skipif(os.name != "nt", reason="MAX_PATH only exists on Windows")
def test_long_path_over_260_roundtrip(tmp_path):
    d = tmp_path
    while len(str(d)) < 300:
        d = d / ("Длинная папка 数据 " + "x" * 30)
    out = d / "таблица.csv"
    assert len(str(out)) > 260
    table.write_csv(mk_table(), str(paths.ensure_parent(out)))
    rows, _ = load(str(out))
    assert len(rows) == 4 and rows[0]["Type Name"] == "Стена кирпичная 380"
    x = d / "table.xlsx"
    table.write_xlsx(mk_table(), str(x))
    assert len(load(str(x))[0]) == 4


@pytest.mark.parametrize("name", NAMES)
def test_table_writers_and_loader_in_odd_folder_names(tmp_path, name):
    d = tmp_path / name
    t = mk_table()
    table.write_csv(t, str(paths.ensure_parent(d / "out.csv")))
    table.write_xlsx(t, str(d / "out.xlsx"))
    with open(d / "out.jsonl", "w", encoding="utf-8") as f:
        for r in t.rows:
            f.write(json.dumps(r, ensure_ascii=False) + chr(10))
    con = sqlite3.connect(str(d / "out.sqlite"))
    con.execute("create table elements (ID text, Category text, \"Type Name\" text)")
    con.executemany("insert into elements values (?,?,?)", [(r["ID"], r["Category"], r["Type Name"]) for r in t.rows])
    con.commit()
    con.close()
    for fn in ("out.csv", "out.xlsx", "out.jsonl", "out.sqlite"):
        rows, _ = load(str(d / fn))
        assert [r["Type Name"] for r in rows] == [r["Type Name"] for r in ROWS], fn


def test_cli_classify_apply_with_odd_paths(tmp_path, capsys):
    d = tmp_path / NAMES[0]
    src = d / "таблица.csv"
    table.write_csv(mk_table(), str(paths.ensure_parent(src)))
    mp = d / "mapping.csv"
    classify.write_template("din276", str(mp))
    with open(mp, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Category", "OST_Walls", "330", "Außenwände", ""])
        w.writerow(["Type Name", "*Decke*", "350", "", ""])
    out = d / "результат.csv"
    rc = cli.main(["classify", "apply", str(src), "--system", "din276", "--mapping", str(mp), "--csv", str(out), "-q"])
    assert rc == 0
    rows, _ = load(str(out))
    assert rows[0]["DIN 276 Code"] == "330" and rows[0]["DIN 276 Title"] == "Außenwände"
    assert rows[3]["DIN 276 Code"] == "350"
    assert rows[2].get("DIN 276 Code") is None


# --------------------------------------------------------------------------- CSV for Excel

def test_csv_default_has_bom_and_dot_decimals(tmp_path):
    p = tmp_path / "a.csv"
    table.write_csv(mk_table(), str(p))
    raw = p.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    assert "1234.5" in text and "1234,5" not in text           # invariant number format
    assert "Стена кирпичная 380" in text and "باب خشبي" in text


def test_csv_without_bom_and_delimiters(tmp_path):
    p = tmp_path / "a.csv"
    table.write_csv(mk_table(), str(p), delimiter="semicolon", bom=False)
    raw = p.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert raw.decode("utf-8").splitlines()[0] == "ID;Category;Type Name;Level;Area;Volume"
    assert load(str(p))[0][1]["Area"] == "1234.5"
    table.write_csv(mk_table(), str(p), delimiter="tab")
    assert "\t" in p.read_text(encoding="utf-8-sig").splitlines()[0]
    assert table.resolve_delimiter("auto") in (",", ";")
    assert table.resolve_delimiter(";") == ";"


def test_csv_header_units_are_opt_in(tmp_path):
    p = tmp_path / "a.csv"
    table.write_csv(mk_table(), str(p))
    assert "Area," in p.read_text(encoding="utf-8-sig").splitlines()[0] + ","
    table.write_csv(mk_table(), str(p), unit_headers=True)
    head = p.read_text(encoding="utf-8-sig").splitlines()[0]
    assert "Area [m2]" in head and "Volume [m3]" in head and "Type Name" in head
    x = tmp_path / "a.xlsx"
    table.write_xlsx(mk_table(), str(x), unit_headers=True)
    assert "Area [m2]" in load(str(x))[0][0]


@pytest.mark.parametrize("enc,delim", [("cp1251", ";"), ("utf-16", "\t"), ("cp1252", ";"), ("utf-8", ","), ("cp1253", ";")])
def test_loader_reads_csv_saved_by_excel_in_other_encodings(tmp_path, monkeypatch, enc, delim):
    from ddc_tools import loader
    monkeypatch.setattr(loader, "_ansi_codepage", lambda: enc if enc == "cp1253" else "")      # Greek vs Cyrillic is only decidable by the system code page
    sample = {"cp1251": "Стена кирпичная", "utf-16": "墙 باب Стена", "cp1252": "Wärmeschutz Größe",
              "utf-8": "Стена 墙", "cp1253": "Έργο Αθήνα"}[enc]
    p = tmp_path / "x.csv"
    p.write_bytes((delim.join(["Name", "Area"]) + "\r\n" + delim.join([sample, "12,5" if delim == ";" else "12.5"]) + "\r\n").encode(enc))
    rows, _ = load(str(p))
    assert rows[0]["Name"] == sample


# --------------------------------------------------------------------------- numbers, JSON, dates

@pytest.mark.parametrize("text,value", [
    ("12.5", 12.5), ("12,5", 12.5), ("1,234.5", 1234.5), ("1.234,5", 1234.5), ("1 234,5 m2", 1234.5),
    ("1\u00a0234,5", 1234.5), ("1.234.567,89", 1234567.89), ("-0,75", -0.75), ("3e2", 300.0),
])
def test_to_number_handles_both_decimal_conventions(text, value):
    assert to_number(text) == pytest.approx(value)


def test_json_reports_keep_unicode(tmp_path):
    out = tmp_path / "r.json"
    rc = cli.main(["qto", str(_csv(tmp_path)), "--json", str(out), "-q"])
    assert rc in (0, 1)
    raw = out.read_text(encoding="utf-8")
    assert "Стена кирпичная 380" in raw and "\\u0421" not in raw


def _csv(tmp_path):
    p = tmp_path / "in.csv"
    table.write_csv(mk_table(), str(p))
    return p


def test_report_timestamp_is_iso8601_with_offset():
    rows = [dict(r) for r in ROWS]
    res = qto.build_qto(rows)
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00", res["generated"])


def test_jsonl_output_uses_lf_only(tmp_path):
    src = _csv(tmp_path)
    mp = tmp_path / "m.csv"
    classify.write_template("cci", str(mp))
    out = tmp_path / "o.jsonl"
    assert cli.main(["classify", "apply", str(src), "--system", "cci", "--mapping", str(mp), "--jsonl", str(out), "-q"]) == 0
    assert b"\r\n" not in out.read_bytes()


# --------------------------------------------------------------------------- classification

def test_every_system_has_a_template_and_no_codes_are_bundled(tmp_path):
    assert set(classify.SYSTEMS) == {"uniclass2015", "omniclass", "masterformat", "din276", "gesn_ksr", "gbt51269", "nlsfb", "cci"}
    for sid in classify.SYSTEMS:
        p = classify.write_template(sid, str(tmp_path / f"{sid}.csv"))
        lines = p.read_text(encoding="utf-8-sig").splitlines()
        assert lines == [",".join(classify.MAPPING_HEADER)]
        assert not classify.SYSTEMS[sid].bundled
    # nothing under the package looks like a code list
    pkg = Path(classify.__file__).parent
    assert not [f for f in pkg.rglob("*") if f.suffix.lower() in (".csv", ".xlsx", ".json")]


def test_system_aliases():
    assert classify.get_system("Uniclass-2015").id == "uniclass2015"
    assert classify.get_system("GB/T 51269").id == "gbt51269"
    assert classify.get_system("NL-SfB").id == "nlsfb"
    assert classify.get_system("GESN-KSR").id == "gesn_ksr"
    with pytest.raises(classify.ClassifyError):
        classify.get_system("nope")


def test_import_then_apply_fills_titles_and_flags_unknown(tmp_path):
    lst = tmp_path / "Мой список.csv"
    lst.write_text("Шифр;Наименование\n01-01-001;Земляные работы\n02-02-002;Бетон\n", encoding="utf-8-sig")
    store = tmp_path / "store"
    dest, n = classify.import_codelist("gesn_ksr", str(lst), folder=str(store))
    assert n == 2 and dest.parent == store
    cl = classify.load_codelist("gesn_ksr", folder=str(store))
    assert cl["02-02-002"] == "Бетон"
    cols = ["Category", "Type Name"]
    rows = [{"Category": "OST_Walls", "Type Name": "Бетон В25"}, {"Category": "OST_Doors", "Type Name": "x"}]
    rules = [{"column": "Type Name", "value": "бетон*", "code": "02-02-002", "title": ""},
             {"column": "Category", "value": "OST_Doors", "code": "99-99-999", "title": ""},
             {"column": "Missing", "value": "*", "code": "1", "title": ""}]
    res = classify.apply_mapping(cols, rows, "gesn_ksr", rules, cl)
    assert rows[0]["GESN-KSR Code"] == "02-02-002" and rows[0]["GESN-KSR Title"] == "Бетон"
    assert res["unknown_codes"] == {"99-99-999": 1} and res["missing_columns"] == ["Missing"]
    assert cols[-2:] == ["GESN-KSR Code", "GESN-KSR Title"]


def test_import_xlsx_with_chinese_headers(tmp_path):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.append(["编码", "名称"])
    ws.append(["10-01.02", "墙体"])
    p = tmp_path / "gb.xlsx"
    wb.save(p)
    _, n = classify.import_codelist("gbt51269", str(p), folder=str(tmp_path / "s"))
    assert n == 1
    assert classify.load_codelist("gbt51269", folder=str(tmp_path / "s")) == {"10-01.02": "墙体"}


def test_cli_systems_and_template(tmp_path, capsys):
    assert cli.main(["classify", "systems"]) == 0
    out = capsys.readouterr().out
    assert "CC BY-ND 4.0" in out and "din276" in out
    t = tmp_path / "Шаблон & Uniclass.csv"
    assert cli.main(["classify", "template", "uniclass2015", "-o", str(t)]) == 0
    assert t.read_bytes().startswith(b"\xef\xbb\xbf")
