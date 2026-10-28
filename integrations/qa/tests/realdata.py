"""Helpers that build real test pairs from local sample models (tests skip when tools/files are absent)."""
from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path

import openpyxl

from ddc_qa.model import cli_path

WORK = Path(os.environ.get("DDC_QA_WORK", r"C:\tmp\modern\qawork"))
WRITER = next((p for p in (os.environ.get("RVT_WRITE"), r"C:\.rvt-w\w-write\target\release\rvt-write.exe",
                           r"C:\tmp\xcorp\rvt-write.exe") if p and os.path.exists(p)), None)
CHECK = Path(r"C:\Users\Artem\Desktop\RVT-write-check")
GEN = Path(r"C:\tmp\gen")
JOBS = Path(r"C:\rvtjobs\out")
RME = r"C:\DDC\DATA\Sample\DiffVer Revit\2023 rmeadvancedsampleproject.rvt"


def have_cli():
    if os.name != "nt":  # the real-data fixtures use fixed Windows paths
        return False
    try:
        cli_path()
        return True
    except FileNotFoundError:
        return False


def edit_pair(src, tag, n_inst=5, inst_cols=("Mark", "Comments", "Description"), type_cols=("Type Mark", "Type Comments")):
    """Export src, edit cells in the xlsx, write back with the Excel->RVT writer.
    Returns (src, out_rvt, expected) where expected = {(ElementId str, column, new str)}."""
    d = WORK / "edit" / tag
    out, stamp = d / "out.rvt", d / "expected.txt"
    if out.exists() and stamp.exists():
        exp = {tuple(l.split("\t")) for l in stamp.read_text(encoding="utf-8").splitlines() if l}
        return Path(src), out, exp
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    local = d / "in.rvt"
    shutil.copyfile(src, local)
    subprocess.run([cli_path(), str(local), "--xlsx", "--out", str(d / "conv")], capture_output=True)
    x = d / "conv" / "elements.xlsx"
    wb = openpyxl.load_workbook(x)
    ws = wb["Elements"]
    hdr = [c.value for c in ws[1]]
    ci = {h: i for i, h in enumerate(hdr)}
    exp = set()
    rows = list(ws.iter_rows(min_row=2))
    inst_col = next((c for c in inst_cols if c in ci and sum(r[ci[c]].value not in (None, "") for r in rows) >= n_inst), None)
    type_col = next((c for c in type_cols if c in ci and any(r[ci[c]].value not in (None, "") for r in rows)), None)
    cand = [r for r in rows if inst_col and r[ci[inst_col]].value not in (None, "")]
    for i, r in enumerate(cand[:n_inst]):
        r[ci[inst_col]].value = "QA-%d" % (i + 1)
        exp.add((str(r[ci["ElementId"]].value), inst_col, "QA-%d" % (i + 1)))
    if type_col:
        tn = next((r[ci["Type Name"]].value for r in ws.iter_rows(min_row=2) if r[ci[type_col]].value not in (None, "")), None)
        for r in ws.iter_rows(min_row=2):
            if r[ci["Type Name"]].value == tn and r[ci[type_col]].value not in (None, ""):
                r[ci[type_col]].value = "QA-T"
                exp.add((str(r[ci["ElementId"]].value), type_col, "QA-T"))
    edited = d / "edited.xlsx"
    wb.save(edited)
    p = subprocess.run([WRITER, "--excel", str(edited), "--in", str(local), "--out", str(out), "--allow-partial"],
                       capture_output=True, text=True)
    if not out.exists():
        raise RuntimeError("writer failed: %s" % (p.stdout + p.stderr)[-400:])
    stamp.write_text("\n".join("\t".join(e) for e in sorted(exp)), encoding="utf-8")
    return local, out, exp
