"""Command line: ddc check | ddc qto | ddc table | ddc convert."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__, check, convert, qto, table
from .loader import LoadError, load_ex


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("input", help="export folder or a single .xlsx/.csv/.jsonl/.json/.sqlite file")
    p.add_argument("--format", dest="fmt", help="use only this format from a folder (xlsx, csv, jsonl, sqlite)")
    p.add_argument("--sheet", help="xlsx sheet name (default: first sheet)")
    p.add_argument("--table", help="sqlite table name (default: elements, else the widest table)")
    p.add_argument("--xlsx", metavar="FILE", help="write the XLSX report here")
    p.add_argument("--json", dest="json_out", metavar="FILE", help="write the JSON report here")
    p.add_argument("-q", "--quiet", action="store_true", help="print nothing except errors")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="ddc", description="Free offline tools for DDC converter exports.")
    ap.add_argument("--version", action="version", version=f"ddc-tools {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("check", help="validate an export against YAML rules (traffic-light report)")
    _common(pc)
    pc.add_argument("--rules", required=True, metavar="FILE", help="YAML rules file")
    pc.add_argument("--fail-on", choices=["error", "warning"], default="error",
                    help="exit code 1 when rules of this severity fail (default: error)")

    pq = sub.add_parser("qto", help="quantity summary by category / type / level")
    _common(pq)
    pq.add_argument("--quantities", metavar="A,B,C", help="quantity columns (default: auto-detect Length, Area, Volume, ...)")
    pq.add_argument("--category", action="append", metavar="GLOB", help="only these categories (repeatable, e.g. 'Wall*')")
    pq.add_argument("--strict", action="store_true", help="exit code 1 if there are warnings")

    pt = sub.add_parser("table", help="flat element table (old *_rvt.xlsx layout) from RVT / IFC / DWG converter output")
    pt.add_argument("input", help="RVT <name>.converted folder (or properties.jsonl), IFC to Excel folder/file, "
                                  ".ifc file, or DWG to Excel .jsonl/.csv/.xlsx (folder)")
    pt.add_argument("--kind", choices=["rvt", "ifc-excel", "ifc-step", "dwg"], help="force the input kind (default: auto-detect)")
    pt.add_argument("--xlsx", metavar="FILE", help="write the table as XLSX (sheet Project_Data, plus an Info sheet)")
    pt.add_argument("--csv", metavar="FILE", help="write the table as CSV (UTF-8 with BOM)")
    pt.add_argument("--jsonl", metavar="FILE", help="write the table as JSON lines")
    pt.add_argument("--all", dest="include_all", action="store_true",
                    help="keep rows that are normally left out (RVT: elements without category and mesh; "
                         "IFC: project/site/building/storey/openings; DWG: blocks and table records)")
    pt.add_argument("--qualified", action="store_true", help="name IFC parameter columns 'Pset.Property' instead of 'Property'")
    pt.add_argument("--no-ifc", action="store_true", help="RVT: ignore native_graph.ifc even if present")
    pt.add_argument("--no-glb", action="store_true", help="RVT: do not compute mesh quantities from native_graph.glb")
    pt.add_argument("--columns", action="store_true", help="print the column mapping table and exit")
    pt.add_argument("-q", "--quiet", action="store_true", help="print nothing except errors")

    pv = sub.add_parser("convert", help="run the DDC converter for a .rvt/.ifc/.dwg file, then build the table (ddc table)")
    pv.add_argument("model", help="model file: .rvt, .rfa, .ifc or .dwg")
    pv.add_argument("--xlsx", metavar="FILE", help="table output (default: <model>_rvt.xlsx / _ifc.xlsx / _dwg.xlsx next to the model)")
    pv.add_argument("--csv", metavar="FILE", help="also write the table as CSV")
    pv.add_argument("--work", metavar="DIR", help="converter output folder (default: <model>.converted next to the model)")
    pv.add_argument("--converters", metavar="DIR", help="the DDC_WINDOWS_Converters folder (default: $DDC_CONVERTERS, else the one in this repository)")
    pv.add_argument("--force", action="store_true", help="convert again even if a finished output folder exists (the old one is renamed, not deleted)")
    pv.add_argument("--no-ifc", action="store_true", help="RVT: do not ask the converter for native_graph.ifc (faster, no category/type names)")
    pv.add_argument("--no-glb", action="store_true", help="RVT: no mesh quantities from the GLB")
    pv.add_argument("--qualified", action="store_true", help="name IFC parameter columns 'Pset.Property'")
    pv.add_argument("--all", dest="include_all", action="store_true", help="keep rows normally left out (see ddc table --all)")
    pv.add_argument("--json", dest="json_out", action="store_true", help="print the result as one JSON line (for scripts and n8n)")
    pv.add_argument("-q", "--quiet", action="store_true", help="print nothing except errors")
    return ap


def _out(path: Optional[str]) -> Optional[Path]:
    if not path:
        return None
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _run_check(a) -> int:
    spec = check.load_rules(a.rules)
    ld = load_ex(a.input, a.fmt, a.sheet, a.table)
    res = check.run_checks(ld.rows, spec, source=str(a.input), files=ld.files, notes=ld.notes)
    s = res["summary"]
    if a.xlsx:
        check.write_xlsx(res, str(_out(a.xlsx)))
    if a.json_out:
        _out(a.json_out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    if not a.quiet:
        print(f"{s['overall']}: {s['elements']} elements, {s['rules']} rules "
              f"({s['pass']} pass, {s['fail']} fail, {s['warn']} warn, {s['skipped']} skipped), "
              f"{s['findings_total']} findings")
        for r in res["rules"]:
            if r["status"] in ("FAIL", "WARN"):
                print(f"  [{r['status']}] {r['id']} {r['title']}: {r['failed_elements']} of {r['applicable']} elements")
    return check.exit_code(res, a.fail_on)


def _run_qto(a) -> int:
    ld = load_ex(a.input, a.fmt, a.sheet, a.table)
    qs = [x.strip() for x in a.quantities.split(",") if x.strip()] if a.quantities else None
    res = qto.build_qto(ld.rows, source=str(a.input), files=ld.files, quantities=qs, category_filter=a.category,
                        quantity_hint=ld.quantity_columns, notes=ld.notes)
    if a.xlsx:
        qto.write_xlsx(res, str(_out(a.xlsx)))
    if a.json_out:
        _out(a.json_out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    if not a.quiet:
        print(f"{res['elements']} elements, {len(res['by_category'])} categories, "
              f"quantities: {', '.join(res['quantity_columns']) or 'none'}; {len(res['warnings'])} warning(s)")
        for w in res["warnings"][:10]:
            print(f"  [{w['level']}] {w['scope']}: {w['message']}")
        if len(res["warnings"]) > 10:
            print(f"  ... {len(res['warnings']) - 10} more in the report")
    if any(w["level"] == "error" for w in res["warnings"]):
        return 2
    return 1 if (a.strict and res["warnings"]) else 0


def _run_table(a) -> int:
    if a.columns:
        print("| Column | Meaning | RVT | IFC | DWG |")
        print("|---|---|---|---|---|")
        for c in table.COLUMN_MAP:
            print("| " + " | ".join(x or "-" for x in c) + " |")
        return 0
    t = table.build_table(a.input, kind=a.kind, include_all=a.include_all, qualified=a.qualified,
                          use_ifc=not a.no_ifc, use_glb=not a.no_glb)
    if a.xlsx:
        table.write_xlsx(t, str(_out(a.xlsx)))
    if a.csv:
        table.write_csv(t, str(_out(a.csv)))
    if a.jsonl:
        with open(_out(a.jsonl), "w", encoding="utf-8") as f:
            for r in t.rows:
                f.write(json.dumps({c: r[c] for c in t.columns if r.get(c) is not None}, ensure_ascii=False) + chr(10))
    if not a.quiet:
        print(f"{t.kind}: {len(t.rows)} elements, {len(t.columns)} columns")
        for n in t.notes:
            print(f"  note: {n}")
    if not t.rows:
        print("ddc: warning: the table is empty", file=sys.stderr)
        return 1
    return 0


def _run_convert(a) -> int:
    res = convert.convert(a.model, work=a.work, xlsx=a.xlsx, csv=a.csv, converters=a.converters, force=a.force,
                          ifc=not a.no_ifc, glb=not a.no_glb, qualified=a.qualified, include_all=a.include_all)
    if a.json_out:
        print(json.dumps(res, ensure_ascii=False))
    elif not a.quiet:
        print(f"{res['kind']}: converter {res['conversion']}, {res['elements']} elements, {res['columns']} columns")
        print(f"  table: {res['xlsx']}")
        print(f"  converter output: {res['work']}")
    return 0 if res["elements"] else 1


def main(argv: Optional[List[str]] = None) -> int:
    a = build_parser().parse_args(argv)
    try:
        if a.cmd == "table":
            return _run_table(a)
        if a.cmd == "convert":
            return _run_convert(a)
        return _run_check(a) if a.cmd == "check" else _run_qto(a)
    except (LoadError, check.RuleError, OSError) as e:
        print(f"ddc: error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
