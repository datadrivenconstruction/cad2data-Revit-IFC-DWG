"""Run bench + all built-in templates + BI export/check over converted xlsx files.

usage: python run_matrix.py OUT_DIR NAME=XLSX [NAME=XLSX ...]
Writes OUT_DIR/matrix.jsonl (one line per model) and per-model outputs under OUT_DIR/NAME/.
"""
import contextlib
import io
import json
import os
import sys
import time

from ddc_data import bi
from ddc_data.builtin import BUILTIN
from ddc_data.cli import main
from ddc_data.frame import load
from ddc_data.render import render_html, render_xlsx
from ddc_data.report import run_template


def run(out, name, xlsx):
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        main(["bench", xlsx, "--out", os.path.join(d, "bench")])
    r = json.loads(buf.getvalue().strip().splitlines()[-1])
    r["model"] = name
    fr = load(os.path.join(d, "bench", "Elements.parquet"))
    r["report_s"] = {}
    for t, tpl in BUILTIN.items():
        t0 = time.perf_counter()
        rep = run_template(tpl, fr)
        render_xlsx(rep, os.path.join(d, t + ".xlsx"))
        render_html(rep, os.path.join(d, t + ".html"))
        r["report_s"][t] = round(time.perf_counter() - t0, 2)
    t0 = time.perf_counter()
    counts = bi.export(os.path.join(d, "bench", "Elements.parquet"), os.path.join(d, "bi"))
    chk = bi.check(os.path.join(d, "bi"))
    chk_csv = bi.check(os.path.join(d, "bi"), "csv")
    r["bi"] = {"tables": counts, "ok_parquet": chk["ok"], "ok_csv": chk_csv["ok"],
               "orphans": sum(v for k, v in chk.items() if "->" in k), "seconds": round(time.perf_counter() - t0, 2)}
    return r


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "matrix.jsonl"), "a", encoding="utf-8") as f:
        for a in sys.argv[2:]:
            name, xlsx = a.split("=", 1)
            r = run(out, name, xlsx)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            print(name, r["rows"], r["xlsx_mb"], r["parquet_mb"], r["speedup_read_pandas"], r["speedup_read_duckdb"],
                  r["speedup_agg"], r["bi"]["ok_parquet"], r["bi"]["ok_csv"], flush=True)
