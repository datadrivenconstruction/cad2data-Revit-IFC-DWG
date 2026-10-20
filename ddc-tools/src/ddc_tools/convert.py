"""``ddc convert``: run the right DDC converter for a model file, then build the flat table.

It only calls the converters' own command lines:

* ``.rvt`` / ``.rfa``: ``DDC_RVT_Converter\\cli\\RVTconverter.exe MODEL -o WORK --properties --ifc``
* ``.ifc``:           ``DDC_IFC_to_Excel\\runtime\\python.exe sources\\ifc-excel\\converter.py MODEL --output WORK``
* ``.dwg``:           ``DDC_CAD_Drawing_to_Excel\\cli\\dwg2excel.exe MODEL --output WORK --json --no-svg --no-dxf --no-xlsx``

and then ``ddc table`` on the result, written next to the model as ``<name>_rvt.xlsx`` / ``_ifc.xlsx`` /
``_dwg.xlsx`` (the names of the retired 18.x converters).
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import table
from .loader import LoadError

RVT_EXT = (".rvt", ".rfa")
SUFFIX = {"rvt": "_rvt", "ifc": "_ifc", "dwg": "_dwg"}


class ConvertError(LoadError):
    pass


def model_kind(path: Path) -> str:
    e = path.suffix.lower()
    if e in RVT_EXT:
        return "rvt"
    if e == ".ifc":
        return "ifc"
    if e == ".dwg":
        return "dwg"
    raise ConvertError(f"unsupported model file {path.name}: expected .rvt, .rfa, .ifc or .dwg")


# Folder of the DWG converter: current name first, then the name used before the rename.
DWG_DIRS = ("DDC_CAD_Drawing_to_Excel", "DDC_DWG_to_Excel")


def dwg_exe(conv: Path) -> Path:
    for d in DWG_DIRS:
        exe = conv / d / "cli" / "dwg2excel.exe"
        if exe.exists():
            return exe
    return conv / DWG_DIRS[0] / "cli" / "dwg2excel.exe"


def find_converters(explicit: Optional[str] = None) -> Path:
    """Folder DDC_WINDOWS_Converters: --converters, $DDC_CONVERTERS, the repository this tool sits in, or
    a parent of the current folder."""
    cands: List[Path] = []
    if explicit:
        cands.append(Path(explicit))
    if os.environ.get("DDC_CONVERTERS"):
        cands.append(Path(os.environ["DDC_CONVERTERS"]))
    here = Path(__file__).resolve()
    cands += [here.parents[3] / "DDC_WINDOWS_Converters"] if len(here.parents) > 3 else []
    cwd = Path.cwd().resolve()
    cands += [d / "DDC_WINDOWS_Converters" for d in [cwd, *cwd.parents]]
    for c in cands:
        if c.is_dir() and any((c / d).exists() for d in ("DDC_RVT_Converter", "DDC_IFC_to_Excel", *DWG_DIRS)):
            return c
    raise ConvertError("converters folder not found: pass --converters PATH or set DDC_CONVERTERS to the "
                       "DDC_WINDOWS_Converters folder of this repository")


def command_for(kind: str, model: Path, work: Path, conv: Path, ifc: bool = True) -> List[str]:
    if kind == "rvt":
        exe = conv / "DDC_RVT_Converter" / "cli" / "RVTconverter.exe"
        cmd = [str(exe), str(model), "-o", str(work), "--properties"]
        if ifc:
            cmd.append("--ifc")
        return cmd
    if kind == "ifc":
        d = conv / "DDC_IFC_to_Excel"
        return [str(d / "runtime" / "python.exe"), str(d / "sources" / "ifc-excel" / "converter.py"),
                str(model), "--output", str(work)]
    exe = dwg_exe(conv)
    return [str(exe), str(model), "--output", str(work), "--json", "--no-svg", "--no-dxf", "--no-xlsx"]


def _complete(kind: str, work: Path) -> bool:
    if kind == "rvt":
        return (work / "properties.jsonl").exists()
    if kind == "ifc":
        return work.is_dir() and any((d / "data.jsonl").exists() for d in work.iterdir() if d.is_dir())
    return work.is_dir() and any(p.suffix in (".jsonl", ".csv") for d in work.iterdir() if d.is_dir() for p in d.iterdir())


def convert(model: str, work: Optional[str] = None, xlsx: Optional[str] = None, csv: Optional[str] = None,
            converters: Optional[str] = None, force: bool = False, ifc: bool = True, glb: bool = True,
            qualified: bool = False, include_all: bool = False) -> Dict[str, Any]:
    m = Path(model).resolve()
    if not m.is_file():
        raise ConvertError(f"model file not found: {model}")
    kind = model_kind(m)
    conv = find_converters(converters)
    w = Path(work).resolve() if work else m.with_name(m.stem + ".converted")
    result: Dict[str, Any] = {"model": str(m), "kind": kind, "work": str(w)}
    if w.exists() and _complete(kind, w) and not force and w.stat().st_mtime >= m.stat().st_mtime:
        result["conversion"] = "reused"
    else:
        if w.exists():                                    # converters refuse an existing folder: set it aside
            aside = w.with_name(w.name + ".old-" + time.strftime("%Y%m%d-%H%M%S"))
            w.rename(aside)
            result["moved_aside"] = str(aside)
        if kind != "rvt":
            w.mkdir(parents=True, exist_ok=True)
        cmd = command_for(kind, m, w, conv, ifc=ifc)
        if not Path(cmd[0]).exists():
            raise ConvertError(f"converter not found: {cmd[0]}")
        p = subprocess.run(cmd, capture_output=True, text=True)
        result["converter_exit"] = p.returncode
        # RVT converter: 0 written, 2 written with reported gaps, 1 failure. IFC/DWG: 0 = converted.
        if p.returncode not in (0, 2) or not _complete(kind, w):
            tail = (p.stderr or p.stdout or "").strip().splitlines()[-3:]
            raise ConvertError(f"converter failed (exit {p.returncode}): " + " | ".join(tail))
        result["conversion"] = "done"
    t = table.build_table(str(w), include_all=include_all, qualified=qualified, use_ifc=ifc, use_glb=glb)
    out = Path(xlsx) if xlsx else m.with_name(m.stem + SUFFIX[kind] + ".xlsx")
    out.parent.mkdir(parents=True, exist_ok=True)
    table.write_xlsx(t, str(out))
    result["xlsx"] = str(out)
    if csv:
        Path(csv).parent.mkdir(parents=True, exist_ok=True)
        table.write_csv(t, csv)
        result["csv"] = csv
    result.update({"elements": len(t.rows), "columns": len(t.columns), "table_kind": t.kind})
    return result
