"""ddc-data command line."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time


def resolve_input(path: str) -> str:
    """xlsx/parquet pass through; a .rvt/.rfa is converted first when ddc-converter is installed."""
    if path.lower().endswith((".rvt", ".rfa")):
        try:
            from ddc_converter.cli import convert
        except ImportError:
            sys.exit("ddc-data reads the converter's xlsx output; install ddc-converter to pass .rvt files directly")
        res = convert(path, formats=("xlsx",))
        if not res.xlsx:
            sys.exit(f"conversion produced no xlsx ({res.status})")
        return str(res.xlsx)
    return path


def _stem(p: str) -> str:
    return os.path.splitext(os.path.basename(p.rstrip("/\\")))[0]


def cmd_parquet(a):
    from .store import to_parquet

    out = a.out or _stem(a.input) + ".parquet.d"
    for p in to_parquet(resolve_input(a.input), out, a.by_category, a.include_base):
        print(p)


def cmd_duckdb(a):
    from .store import to_duckdb

    out = a.out or _stem(a.input) + ".duckdb"
    for k, v in to_duckdb(resolve_input(a.input), out, a.by_category, a.include_base).items():
        print(f"{k}\t{v}")


def cmd_report(a):
    from .builtin import BUILTIN
    from .frame import load
    from .render import render_html, render_xlsx
    from .report import run_template, load_template

    if a.list:
        for k, v in BUILTIN.items():
            print(f"{k}\t{v['description']}")
        return
    if not a.template or not a.input:
        sys.exit("usage: ddc-data report INPUT --template NAME|FILE [--format xlsx,html] [--out PREFIX]")
    tpl = load_template(a.template)
    rep = run_template(tpl, load(resolve_input(a.input), a.sheet))
    prefix = a.out or f"{_stem(a.input)}.{_stem(a.template)}"
    for fmt in a.format.split(","):
        fmt = fmt.strip().lower()
        p = f"{prefix}.{fmt}"
        {"xlsx": render_xlsx, "html": render_html}[fmt](rep, p)
        print(p)


def cmd_bi(a):
    from .bi import check, export

    out = a.out or _stem(a.input) + ".bi"
    counts = export(resolve_input(a.input), out)
    print(json.dumps(counts))
    res = check(out)
    print(json.dumps(res))
    if not res["ok"]:
        sys.exit(1)


def cmd_bicheck(a):
    from .bi import check

    res = check(a.dir, a.format)
    print(json.dumps(res, indent=1))
    sys.exit(0 if res["ok"] else 1)


def cmd_bench(a):
    import duckdb
    import pandas as pd

    from .store import to_duckdb, to_parquet

    src = a.input
    work = a.out or _stem(src) + ".bench"
    os.makedirs(work, exist_ok=True)
    t = time.perf_counter()
    to_parquet(src, work)
    t_conv = time.perf_counter() - t
    pq_path = os.path.join(work, "Elements.parquet").replace("\\", "/")
    dbp = os.path.join(work, "elements.duckdb")
    if os.path.exists(dbp):
        os.remove(dbp)
    to_duckdb(src, dbp)
    r = {"file": os.path.basename(src), "xlsx_mb": round(os.path.getsize(src) / 2**20, 2),
         "parquet_mb": round(os.path.getsize(pq_path) / 2**20, 2),
         "duckdb_mb": round(os.path.getsize(dbp) / 2**20, 2), "convert_s": round(t_conv, 2)}

    def best(fn, n=3):
        ts = []
        for _ in range(n):
            t0 = time.perf_counter()
            fn()
            ts.append(time.perf_counter() - t0)
        return min(ts)

    t0 = time.perf_counter()
    df = pd.read_excel(src, sheet_name="Elements", engine="openpyxl")
    r["pandas_xlsx_read_s"] = round(time.perf_counter() - t0, 3)
    r["rows"], r["cols"] = int(df.shape[0]), int(df.shape[1])
    del df
    r["pandas_parquet_read_s"] = round(best(lambda: pd.read_parquet(pq_path)), 3)
    r["duckdb_parquet_read_s"] = round(best(lambda: duckdb.sql(f"select * from read_parquet('{pq_path}')").arrow()), 3)

    def q_db():
        con = duckdb.connect(dbp, read_only=True)
        con.execute('select "Category", count(*), sum("Volume (m³)") from Elements group by 1').fetchall()
        con.close()

    r["duckdb_db_agg_s"] = round(best(q_db), 3)
    t0 = time.perf_counter()
    d2 = pd.read_excel(src, sheet_name="Elements", engine="openpyxl", usecols=["Category", "Volume (m³)"])
    d2.groupby("Category")["Volume (m³)"].agg(["count", "sum"])
    r["pandas_xlsx_agg_s"] = round(time.perf_counter() - t0, 3)
    r["speedup_read_pandas"] = round(r["pandas_xlsx_read_s"] / max(r["pandas_parquet_read_s"], 1e-6), 1)
    r["speedup_read_duckdb"] = round(r["pandas_xlsx_read_s"] / max(r["duckdb_parquet_read_s"], 1e-6), 1)
    r["speedup_agg"] = round(r["pandas_xlsx_agg_s"] / max(r["duckdb_db_agg_s"], 1e-6), 1)
    r["size_ratio"] = round(r["xlsx_mb"] / max(r["parquet_mb"], 1e-6), 1)
    print(json.dumps(r, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ddc-data", description=__doc__)
    sp = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, help_):
        p = sp.add_parser(name, help=help_)
        p.set_defaults(fn=fn)
        return p

    p = add("to-parquet", cmd_parquet, "xlsx -> Parquet files (one per sheet)")
    p.add_argument("input")
    p.add_argument("--out")
    p.add_argument("--by-category", action="store_true", help="hive-partition Elements by Category")
    p.add_argument("--include-base", action="store_true", help="also export the hidden _ddc_base sheet")
    p = add("to-duckdb", cmd_duckdb, "xlsx -> DuckDB database (one table per sheet)")
    p.add_argument("input")
    p.add_argument("--out")
    p.add_argument("--by-category", action="store_true", help="also create one table per category")
    p.add_argument("--include-base", action="store_true")
    p = add("report", cmd_report, "run a built-in or custom report template")
    p.add_argument("input", nargs="?")
    p.add_argument("--template", "-t")
    p.add_argument("--format", default="xlsx,html")
    p.add_argument("--out", help="output path prefix")
    p.add_argument("--sheet", default="Elements")
    p.add_argument("--list", action="store_true", help="list built-in templates")
    p = add("to-bi", cmd_bi, "star-schema dataset (CSV + Parquet) with Power BI / Tableau assets")
    p.add_argument("input")
    p.add_argument("--out")
    p = add("bi-check", cmd_bicheck, "check key integrity of a star-schema dataset with DuckDB")
    p.add_argument("dir")
    p.add_argument("--format", default="parquet", choices=["parquet", "csv"])
    p = add("bench", cmd_bench, "read-time and size comparison, xlsx vs Parquet/DuckDB")
    p.add_argument("input")
    p.add_argument("--out")
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
