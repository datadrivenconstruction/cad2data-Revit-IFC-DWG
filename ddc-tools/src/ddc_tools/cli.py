"""Command line: ddc check | ddc qto."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__, check, qto
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


def main(argv: Optional[List[str]] = None) -> int:
    a = build_parser().parse_args(argv)
    try:
        return _run_check(a) if a.cmd == "check" else _run_qto(a)
    except (LoadError, check.RuleError) as e:
        print(f"ddc: error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
