"""Command line: ddc check | ddc qto | ddc table | ddc convert | ddc diff | ddc bcf."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__, bcf, check, convert, diff, glbdiff, qto, table
from .loader import LoadError, load_ex


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("input", help="export folder or a single .xlsx/.csv/.jsonl/.json/.sqlite file")
    p.add_argument("--format", dest="fmt", help="use only this format from a folder (xlsx, csv, jsonl, sqlite)")
    p.add_argument("--sheet", help="xlsx sheet name (default: first sheet)")
    p.add_argument("--table", help="sqlite table name (default: elements, else the widest table)")
    p.add_argument("--xlsx", metavar="FILE", help="write the XLSX report here")
    p.add_argument("--json", dest="json_out", metavar="FILE", help="write the JSON report here")
    p.add_argument("-q", "--quiet", action="store_true", help="print nothing except errors")


def _bcf_opts(p: argparse.ArgumentParser) -> None:
    p.add_argument("--bcf", metavar="FILE", help="also write the findings as a BCF issue file (zip)")
    p.add_argument("--bcf-version", choices=bcf.VERSIONS, default="2.1", help="BCF version to write (default: 2.1)")
    p.add_argument("--bcf-per-element", action="store_true",
                   help="one BCF topic per element instead of one per rule / status and category")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="ddc", description="Free offline tools for DDC converter exports.")
    ap.add_argument("--version", action="version", version=f"ddc-tools {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("check", help="validate an export against YAML rules (traffic-light report)")
    _common(pc)
    pc.add_argument("--rules", required=True, metavar="FILE", help="YAML rules file")
    pc.add_argument("--fail-on", choices=["error", "warning"], default="error",
                    help="exit code 1 when rules of this severity fail (default: error)")
    _bcf_opts(pc)

    pq = sub.add_parser("qto", help="quantity summary by category / type / level")
    _common(pq)
    pq.add_argument("--quantities", metavar="A,B,C", help="quantity columns (default: auto-detect Length, Area, Volume, ...)")
    pq.add_argument("--category", action="append", metavar="GLOB", help="only these categories (repeatable, e.g. 'Wall*')")
    pq.add_argument("--strict", action="store_true", help="exit code 1 if there are warnings")

    pt = sub.add_parser("table", help="flat element table (old *_rvt.xlsx layout) from RVT / IFC / DWG converter output")
    pt.add_argument("input", help="RVT <name>.converted folder (or properties.jsonl), IFC to Excel folder/file, "
                                  ".ifc file, or CAD Drawing to Excel .jsonl/.csv/.xlsx (folder)")
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

    pd = sub.add_parser("diff", help="compare two exports of a model: added / removed / modified, changelog XLSX, JSON, "
                                     "status-coloured GLB")
    pd.add_argument("a", help="old version: converter output folder or file (same inputs as `ddc table`)")
    pd.add_argument("b", help="new version")
    kinds = ["rvt", "ifc-excel", "ifc-step", "dwg"]
    pd.add_argument("--kind-a", choices=kinds, help="force the input kind of A")
    pd.add_argument("--kind-b", choices=kinds, help="force the input kind of B")
    pd.add_argument("--key", metavar="COLUMN", help="match elements by this column (default: GlobalId, UniqueId, ElementId "
                                                      "or ID, whichever fits; 'fingerprint' = no key)")
    pd.add_argument("--ignore", action="append", default=[], metavar="GLOB", help="do not compare these columns (repeatable)")
    pd.add_argument("--tolerance", type=float, default=1e-6, metavar="REL",
                    help="relative tolerance for numbers (default: 1e-6)")
    pd.add_argument("--no-fingerprint", action="store_true", help="do not try to match leftover elements by fingerprint")
    pd.add_argument("--include-unchanged", action="store_true", help="list unchanged elements in the XLSX / JSON too")
    pd.add_argument("--xlsx", metavar="FILE", help="write the changelog workbook here")
    pd.add_argument("--json", dest="json_out", metavar="FILE", help="write the JSON report here")
    pd.add_argument("--glb", metavar="FILE", help="write a GLB coloured by status (needs a GLB next to the inputs or --glb-b)")
    pd.add_argument("--glb-a", metavar="FILE", help="GLB of version A (default: native_graph.glb / model.glb of A)")
    pd.add_argument("--glb-b", metavar="FILE", help="GLB of version B (default: native_graph.glb / model.glb of B)")
    pd.add_argument("--glb-unchanged", choices=["ghost", "keep", "hide"], default="ghost",
                    help="unchanged elements in the GLB: translucent grey (default), opaque grey, or removed")
    _bcf_opts(pd)
    pd.add_argument("--fail-on", default="added,removed,modified", metavar="LIST",
                    help="exit code 1 when any of these statuses occurs: comma list of added, removed, modified, or "
                         "any / none (default: added,removed,modified)")
    pd.add_argument("-q", "--quiet", action="store_true", help="print nothing except errors")

    pb = sub.add_parser("bcf", help="BCF issue files: export findings of check / diff, read any BCF into a table")
    bsub = pb.add_subparsers(dest="bcf_cmd", required=True)
    pbe = bsub.add_parser("export", help="write a BCF zip from a `ddc check --json` or `ddc diff --json` report")
    pbe.add_argument("report", help="JSON report of ddc check or ddc diff")
    pbe.add_argument("-o", "--output", required=True, metavar="FILE", help="BCF file to write (.bcf / .bcfzip)")
    pbe.add_argument("--version", choices=bcf.VERSIONS, default="2.1", help="BCF version (default: 2.1)")
    pbe.add_argument("--author", default="ddc-tools", help="creation author of the topics (BCF expects an e-mail or user id)")
    pbe.add_argument("--per-element", action="store_true",
                     help="one topic per element instead of one per rule / status and category")
    pbe.add_argument("--only", default="added,removed,modified", metavar="LIST",
                     help="diff: statuses to export (default: added,removed,modified)")
    pbe.add_argument("--max-components", type=int, default=1000, metavar="N", help="components selected per viewpoint (default: 1000)")
    pbe.add_argument("--camera", metavar="X,Y,Z,DX,DY,DZ", help="camera position and direction (metres, Z up) for every viewpoint")
    pbe.add_argument("--model-name", metavar="NAME", help="model file name written to the BCF header")
    pbr = bsub.add_parser("read", help="tabulate a BCF file: summary, topics, comments, components")
    pbr.add_argument("bcf", help="BCF zip (2.0, 2.1 or 3.0)")
    pbr.add_argument("--xlsx", metavar="FILE", help="write the workbook here")
    pbr.add_argument("--json", dest="json_out", metavar="FILE", help="write the JSON here")
    pbr.add_argument("-q", "--quiet", action="store_true", help="print nothing except errors")
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
    if a.bcf:
        b = bcf.export_report(res, str(_out(a.bcf)), version=a.bcf_version, per_element=a.bcf_per_element)
        if not a.quiet:
            print(f"BCF {b['version']}: {b['topics']} topics, {b['components']} components -> {a.bcf}")
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


def _run_diff(a) -> int:
    fail_on = diff.parse_fail_on(a.fail_on)
    res = diff.diff_paths(a.a, a.b, kind_a=a.kind_a, kind_b=a.kind_b, key=a.key, ignore=a.ignore, tol=a.tolerance,
                          fingerprint=not a.no_fingerprint)
    s = res["summary"]
    glb_stats = None
    if a.glb:
        found_b, found_a = diff.find_glb(a.b), diff.find_glb(a.a)
        gb = a.glb_b or (str(found_b) if found_b else None)
        ga = a.glb_a or (str(found_a) if found_a else None)
        if not (gb or ga):
            print("ddc: warning: no GLB found next to the inputs (use --glb-a / --glb-b); GLB not written", file=sys.stderr)
        else:
            glb_stats = glbdiff.colorize(gb, ga, res, str(_out(a.glb)), unchanged=a.glb_unchanged)
            res["glb"] = glb_stats
    if a.xlsx:
        diff.write_xlsx(res, str(_out(a.xlsx)), include_unchanged=a.include_unchanged)
    if a.json_out:
        _out(a.json_out).write_text(json.dumps(diff.public_result(res, a.include_unchanged), ensure_ascii=False, indent=2),
                                    encoding="utf-8")
    b = None
    if a.bcf:
        b = bcf.export_report(diff.public_result(res), str(_out(a.bcf)), version=a.bcf_version,
                              per_element=a.bcf_per_element)
    if not a.quiet:
        print(f"{res['a']['elements']} -> {res['b']['elements']} elements, matched by {res['key']['method']}: "
              f"{s['added']} added, {s['removed']} removed, {s['modified']} modified, {s['unchanged']} unchanged "
              f"({s['property_changes']} property, {s['quantity_changes']} quantity, {s['attribute_changes']} attribute changes)")
        for w in res["warnings"]:
            print(f"  warning: {w}")
        if glb_stats:
            print(f"  GLB: {glb_stats['linked']} nodes linked, {glb_stats['unlinked']} not linked, "
                  f"{glb_stats['removed']} removed elements copied from A -> {a.glb}")
        if b:
            print(f"  BCF {b['version']}: {b['topics']} topics, {b['components']} components -> {a.bcf}")
    return diff.exit_code(res, fail_on)


def _run_bcf(a) -> int:
    if a.bcf_cmd == "export":
        rep = bcf.load_report(a.report)
        cam = bcf.parse_camera(a.camera) if a.camera else None
        only = [x.strip() for x in a.only.split(",") if x.strip()]
        res = bcf.export_report(rep, str(_out(a.output)), version=a.version, author=a.author, per_element=a.per_element,
                                max_components=a.max_components, only=only, camera=cam, file_name=a.model_name)
        print(f"BCF {res['version']} ({res['kind']}): {res['topics']} topics, {res['viewpoints']} viewpoints, "
              f"{res['components']} components -> {a.output}")
        return 0
    res = bcf.read_bcf(a.bcf)
    if a.xlsx:
        bcf.write_read_xlsx(res, str(_out(a.xlsx)))
    if a.json_out:
        _out(a.json_out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    if not a.quiet:
        s = res["summary"]
        print(f"BCF {res['version'] or '?'}: {s['topics']} topics, {s['comments']} comments, {s['viewpoints']} viewpoints, "
              f"{s['components']} components")
        for t in res["topics"][:20]:
            print(f"  [{t['status'] or '-'}] {t['title']}")
        if len(res["topics"]) > 20:
            print(f"  ... {len(res['topics']) - 20} more")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    a = build_parser().parse_args(argv)
    try:
        if a.cmd == "table":
            return _run_table(a)
        if a.cmd == "convert":
            return _run_convert(a)
        if a.cmd == "diff":
            return _run_diff(a)
        if a.cmd == "bcf":
            return _run_bcf(a)
        return _run_check(a) if a.cmd == "check" else _run_qto(a)
    except (LoadError, check.RuleError, bcf.BcfError, glbdiff.GlbError, OSError) as e:
        print(f"ddc: error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
