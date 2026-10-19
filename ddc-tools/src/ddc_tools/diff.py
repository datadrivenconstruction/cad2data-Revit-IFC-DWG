"""``ddc diff A B``: what changed between two exports of a model.

Both sides are read with the same adapters as ``ddc table`` (RVT ``properties.jsonl`` folder, DDC IFC to
Excel output or a plain ``.ifc``, DWG to Excel table), so one version can be a folder and the other a
file, or even two different converters, although that gives a noisier result and a warning.

Matching, in this order:

1. By a key column: ``GlobalId``, ``UniqueId``, ``ElementId``, ``ID`` (the first with enough coverage and
   overlap in both versions, or ``--key``). Added = key only in B, removed = key only in A.
2. What is left over on both sides is matched by a fingerprint (category, type, level, quantities and
   all properties, without names and ids). Only an exact, one-to-one fingerprint match counts; those
   elements are reported as unchanged with ``matched_by = fingerprint`` (their id changed).

Honest limits: Revit ElementIds can change when a model is re-created, IFC STEP ids change on every
export, and a fingerprint cannot tell apart two identical elements that moved. The report states which
key was used and how many elements were matched by fingerprint.
"""
from __future__ import annotations

import fnmatch
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from . import columns as C
from .loader import LoadError, is_empty
from .table import QUANTITY_COLUMNS, Table, build_table
from .xlsxutil import FILLS, autosize, new_workbook, title_cell, write_table

STATUSES = ("added", "removed", "modified", "unchanged")
# RGB 0..255. Used for the GLB and for BCF colouring.
STATUS_COLORS = {"added": (46, 184, 77), "removed": (219, 50, 50), "modified": (250, 158, 26),
                 "unchanged": (190, 190, 190)}
KEY_CANDIDATES = ("GlobalId", "UniqueId", "ElementId", "ID")
ID_COLUMNS = ("ID", "ElementId", "GlobalId", "UniqueId")
# derived or bookkeeping columns that are not compared
DEFAULT_IGNORE = ("Type", "Family and Type", "Quantity Source", "Parameter Units", "_source_file")
# not compared when matching by fingerprint (they carry ids or are id-dependent)
_FP_SKIP = set(ID_COLUMNS) | {"Name", "Type Id", "Level Id", "Category Id", "Quantity Source", "Parameter Units",
                              "_source_file", "Type", "Family and Type"}
ATTRIBUTE_COLUMNS = {"Category", "Category Name", "IfcClass", "Revit Class", "Family", "Type Name", "Name",
                     "Level", "Material", "Layer", "Type Id", "Level Id", "Category Id"}
EXTRA_QUANTITY = {"Mesh Volume", "Mesh Area", "BBox X", "BBox Y", "BBox Z"}
MAX_FP_GROUP = 50


class DiffError(LoadError):
    pass


# ------------------------------------------------------------------------------------------ values

def _is_num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and not (isinstance(v, float) and math.isnan(v))


def _norm(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        return s if s != "" else None
    if isinstance(v, float) and math.isnan(v):
        return None
    return v


def _as_number(v: Any) -> Optional[float]:
    if _is_num(v):
        return float(v)
    if isinstance(v, str):
        try:
            f = float(v)
        except ValueError:
            return None
        return f if math.isfinite(f) else None
    return None


def values_equal(a: Any, b: Any, tol: float) -> bool:
    a, b = _norm(a), _norm(b)
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, bool) or isinstance(b, bool):
        return str(a).lower() == str(b).lower()
    na, nb = _as_number(a), _as_number(b)
    if na is not None and nb is not None and (_is_num(a) or _is_num(b)):
        return abs(na - nb) <= max(tol * max(abs(na), abs(nb)), 1e-9)
    return str(a) == str(b)


def _show(v: Any) -> Any:
    v = _norm(v)
    return "" if v is None else v


def _round_num(v: float) -> float:
    return float(f"{v:.10g}")


# ------------------------------------------------------------------------------------------ keys

def _key_values(rows: List[Dict[str, Any]], col: str) -> List[Optional[str]]:
    out = []
    for r in rows:
        v = _norm(r.get(col))
        out.append(None if v is None else str(v))
    return out


def _coverage(vals: List[Optional[str]]) -> float:
    return (sum(v is not None for v in vals) / len(vals)) if vals else 0.0


def choose_key(ta: Table, tb: Table, requested: Optional[str] = None) -> Tuple[Optional[str], Dict[str, Any], List[str]]:
    """Return (key column or None, diagnostics, warnings)."""
    warnings: List[str] = []
    diag: Dict[str, Any] = {"candidates": []}
    if requested:
        if requested.lower() in ("fingerprint", "none"):
            return None, {"requested": requested, "candidates": []}, []
        col = next((c for c in tb.columns if c == requested or C._norm(c) == C._norm(requested)), None)
        col_a = next((c for c in ta.columns if c == requested or C._norm(c) == C._norm(requested)), None)
        if not col or not col_a:
            raise DiffError(f"key column {requested!r} must exist in both versions")
        va, vb = _key_values(ta.rows, col_a), _key_values(tb.rows, col)
        diag["candidates"].append(_cand(col, va, vb))
        return col, dict(diag, requested=requested), warnings
    best = None
    for col in KEY_CANDIDATES:
        if col not in ta.columns or col not in tb.columns:
            continue
        va, vb = _key_values(ta.rows, col), _key_values(tb.rows, col)
        cand = _cand(col, va, vb)
        diag["candidates"].append(cand)
        if min(cand["coverage_a"], cand["coverage_b"]) < 0.9:
            continue
        if cand["overlap"] >= 0.5:
            best = col
            break
        if best is None or cand["overlap"] > next(c for c in diag["candidates"] if c["column"] == best)["overlap"]:
            best = col
    if best is not None:
        c = next(c for c in diag["candidates"] if c["column"] == best)
        if c["overlap"] < 0.05:
            warnings.append(f"almost no {best} values are shared by both versions ({c['overlap']:.1%}); "
                            "matching by fingerprint only")
            best = None
        elif c["overlap"] < 0.5:
            warnings.append(f"only {c['overlap']:.1%} of {best} values are shared by both versions; "
                            "the ids may have been regenerated, check the result")
    return best, diag, warnings


def _cand(col: str, va: List[Optional[str]], vb: List[Optional[str]]) -> Dict[str, Any]:
    sa, sb = {v for v in va if v is not None}, {v for v in vb if v is not None}
    denom = max(1, min(len(sa), len(sb)))
    return {"column": col, "coverage_a": round(_coverage(va), 4), "coverage_b": round(_coverage(vb), 4),
            "shared": len(sa & sb), "overlap": round(len(sa & sb) / denom, 4),
            "duplicates_a": sum(v is not None for v in va) - len(sa),
            "duplicates_b": sum(v is not None for v in vb) - len(sb)}


# ------------------------------------------------------------------------------------------ compare

def _category(r: Dict[str, Any]) -> str:
    for c in ("Category", "Category Name", "IfcClass"):
        v = _norm(r.get(c))
        if v is not None:
            return str(v)
    return "(no category)"


def _first(r: Dict[str, Any], names: Sequence[str]) -> str:
    for n in names:
        v = _norm(r.get(n))
        if v is not None:
            return str(v)
    return ""


def _ids(r: Optional[Dict[str, Any]]) -> Dict[str, str]:
    if r is None:
        return {}
    return {c: str(_norm(r.get(c))) for c in ID_COLUMNS if _norm(r.get(c)) is not None}


def _fingerprint(r: Dict[str, Any], cols: Sequence[str]) -> Tuple:
    parts = []
    for c in cols:
        if c in _FP_SKIP:
            continue
        v = _norm(r.get(c))
        if v is None:
            continue
        n = _as_number(v) if _is_num(v) else None
        parts.append((c, f"{n:.6g}" if n is not None else str(v)))
    return tuple(parts)


def _qty_columns(cols: Iterable[str]) -> List[str]:
    cols = list(cols)
    out = [c for c in cols if c in QUANTITY_COLUMNS or c in EXTRA_QUANTITY]
    out += [c for c in C.quantity_columns(cols) if c not in out]
    return out


def _changes(ra: Dict[str, Any], rb: Dict[str, Any], cols: Sequence[str], qcols: set, tol: float) -> List[Dict[str, Any]]:
    out = []
    for c in cols:
        va, vb = ra.get(c), rb.get(c)
        if values_equal(va, vb, tol):
            continue
        ch: Dict[str, Any] = {"field": c, "old": _show(va), "new": _show(vb)}
        if c in qcols:
            ch["kind"] = "quantity"
        elif c in ATTRIBUTE_COLUMNS:
            ch["kind"] = "attribute"
        else:
            ch["kind"] = "property"
        na, nb = _as_number(va), _as_number(vb)
        if na is not None and nb is not None:
            ch["delta"] = _round_num(nb - na)
            if na != 0:
                ch["delta_pct"] = round(100.0 * (nb - na) / abs(na), 2)
        elif c in qcols and (na is not None or nb is not None):
            # a quantity appeared or disappeared
            ch["delta"] = _round_num((nb or 0.0) - (na or 0.0))
        out.append(ch)
    return out


def _element(status: str, ra: Optional[Dict[str, Any]], rb: Optional[Dict[str, Any]], key_col: Optional[str],
             matched_by: str, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
    r = rb if rb is not None else ra
    key = None
    if key_col:
        key = _first(r, [key_col]) or _first(ra or {}, [key_col])
    if not key:
        key = _first(r, ID_COLUMNS)
    return {
        "status": status, "key": key, "key_column": key_col if key_col else "", "matched_by": matched_by,
        "a": _ids(ra), "b": _ids(rb),
        "global_id": _first(r, ["GlobalId"]) or _first(ra or {}, ["GlobalId"]),
        "element_id": _first(r, ["ElementId", "ID"]),
        "category": _category(r), "type": _first(r, ["Type Name", "Type", "Family and Type"]),
        "level": _first(r, ["Level"]), "name": _first(r, ["Name"]),
        "changes": changes,
    }


def diff_tables(ta: Table, tb: Table, key: Optional[str] = None, ignore: Sequence[str] = (), tol: float = 1e-6,
                fingerprint: bool = True) -> Dict[str, Any]:
    warnings: List[str] = []
    if ta.kind != tb.kind and {ta.kind.split("+")[0], tb.kind.split("+")[0]} != {"rvt"}:
        warnings.append(f"the two versions come from different outputs ({ta.kind} vs {tb.kind}); "
                        "column names and units may differ, expect many modified elements")
    if not ta.rows and not tb.rows:
        raise DiffError("both versions are empty")
    key_col, key_diag, kw = choose_key(ta, tb, key)
    warnings += kw
    if key_col == "ID" and (ta.kind.startswith("ifc") or tb.kind.startswith("ifc")):
        warnings.append("the only usable key is the STEP id, which is not stable between IFC exports; "
                        "prefer a GlobalId column")
    if key_col is None and not fingerprint:
        raise DiffError("no usable key column in both versions and fingerprint matching is off")

    cols: List[str] = list(tb.columns) + [c for c in ta.columns if c not in tb.columns]
    ign = list(DEFAULT_IGNORE) + list(ignore)
    cols = [c for c in cols if not any(fnmatch.fnmatchcase(c, p) for p in ign)]
    # id columns identify elements, they are not "changes": the key is what was matched on, the others
    # (STEP ids, regenerated GlobalIds) are only counted and reported as a warning
    other_ids = [c for c in ID_COLUMNS if c != key_col and c in cols]
    cmp_cols = [c for c in cols if c not in ID_COLUMNS]
    qcols = set(_qty_columns(cols))

    elements: List[Dict[str, Any]] = []
    id_changed: Dict[str, int] = defaultdict(int)
    rows_a, rows_b = ta.rows, tb.rows
    used_a, used_b = [False] * len(rows_a), [False] * len(rows_b)

    # ---- 1. by key (duplicates are paired in order: key + occurrence number)
    if key_col:
        def index(rows):
            seen: Dict[str, int] = defaultdict(int)
            idx: Dict[Tuple[str, int], int] = {}
            dup = 0
            for i, r in enumerate(rows):
                v = _norm(r.get(key_col))
                if v is None:
                    continue
                n = seen[str(v)]
                seen[str(v)] += 1
                dup += n > 0
                idx[(str(v), n)] = i
            return idx, dup
        ia, dup_a = index(rows_a)
        ib, dup_b = index(rows_b)
        if dup_a or dup_b:
            warnings.append(f"{dup_a + dup_b} rows repeat a {key_col} value; repeated values are paired in file order")
        for k, i in ia.items():
            j = ib.get(k)
            if j is None:
                continue
            used_a[i] = used_b[j] = True
            ch = _changes(rows_a[i], rows_b[j], cmp_cols, qcols, tol)
            for c in other_ids:
                if not values_equal(rows_a[i].get(c), rows_b[j].get(c), 0.0):
                    id_changed[c] += 1
            elements.append(_element("modified" if ch else "unchanged", rows_a[i], rows_b[j], key_col,
                                     f"key:{key_col}", ch))

    for c, n in id_changed.items():
        if n:
            warnings.append(f"{n} matched elements have a different {c} in A and B (ids regenerated by the export?); "
                            f"{c} differences are not counted as changes")

    # ---- 2. fingerprint for the rest
    n_fp = 0
    if fingerprint:
        left_a = [i for i in range(len(rows_a)) if not used_a[i]]
        left_b = [j for j in range(len(rows_b)) if not used_b[j]]
        if left_a and left_b:
            fcols = [c for c in cols]
            groups_a: Dict[Tuple, List[int]] = defaultdict(list)
            groups_b: Dict[Tuple, List[int]] = defaultdict(list)
            for i in left_a:
                groups_a[_fingerprint(rows_a[i], fcols)].append(i)
            for j in left_b:
                groups_b[_fingerprint(rows_b[j], fcols)].append(j)
            for fp, la in groups_a.items():
                lb = groups_b.get(fp)
                if not lb or not fp:
                    continue
                if len(la) > MAX_FP_GROUP or len(lb) > MAX_FP_GROUP:
                    continue
                for i, j in zip(la, lb):
                    used_a[i] = used_b[j] = True
                    n_fp += 1
                    elements.append(_element("unchanged", rows_a[i], rows_b[j], key_col, "fingerprint", []))
            if n_fp:
                warnings.append(f"{n_fp} elements have a new id but identical category, type, level, quantities and "
                                "properties; they were matched by fingerprint and counted as unchanged")

    for i, r in enumerate(rows_a):
        if not used_a[i]:
            elements.append(_element("removed", r, None, key_col, "", []))
    for j, r in enumerate(rows_b):
        if not used_b[j]:
            elements.append(_element("added", None, r, key_col, "", []))

    order = {s: n for n, s in enumerate(STATUSES)}
    elements.sort(key=lambda e: (order[e["status"]], e["category"], e["type"], e["key"]))

    counts = {s: 0 for s in STATUSES}
    for e in elements:
        counts[e["status"]] += 1
    n_prop = sum(1 for e in elements for c in e["changes"] if c["kind"] == "property")
    n_qty = sum(1 for e in elements for c in e["changes"] if c["kind"] == "quantity")
    n_attr = sum(1 for e in elements for c in e["changes"] if c["kind"] == "attribute")
    fields: Dict[str, int] = defaultdict(int)
    for e in elements:
        for c in e["changes"]:
            fields[c["field"]] += 1

    cats: Dict[str, Dict[str, Any]] = {}
    for e in elements:
        d = cats.setdefault(e["category"], {"category": e["category"], **{s: 0 for s in STATUSES}})
        d[e["status"]] += 1
    for d in cats.values():
        d["total_a"] = d["removed"] + d["modified"] + d["unchanged"]
        d["total_b"] = d["added"] + d["modified"] + d["unchanged"]

    quantities = _quantity_totals(rows_a, rows_b, sorted(qcols))

    summary = {**counts, "total_a": len(rows_a), "total_b": len(rows_b),
               "identical": counts["added"] == counts["removed"] == counts["modified"] == 0,
               "property_changes": n_prop, "quantity_changes": n_qty, "attribute_changes": n_attr,
               "matched_by_fingerprint": n_fp}
    return {
        "tool": "ddc diff", "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "a": {"source": ta.source, "kind": ta.kind, "elements": len(rows_a)},
        "b": {"source": tb.source, "kind": tb.kind, "elements": len(rows_b)},
        "key": {"column": key_col or "", "method": f"key:{key_col}" if key_col else "fingerprint",
                "diagnostics": key_diag},
        "options": {"tolerance": tol, "ignored": ign, "fingerprint": fingerprint},
        "summary": summary, "warnings": warnings, "notes": list(dict.fromkeys(ta.notes + tb.notes)),
        "changed_fields": [{"field": f, "count": n} for f, n in sorted(fields.items(), key=lambda x: (-x[1], x[0]))],
        "by_category": sorted(cats.values(), key=lambda d: d["category"]),
        "quantities": quantities,
        "elements": elements,
    }


def _quantity_totals(rows_a, rows_b, qcols: List[str]) -> List[Dict[str, Any]]:
    tot: Dict[Tuple[str, str], List[float]] = {}
    for side, rows in ((0, rows_a), (1, rows_b)):
        for r in rows:
            cat = _category(r)
            for q in qcols:
                n = _as_number(r.get(q)) if _is_num(r.get(q)) else None
                if n is None:
                    continue
                tot.setdefault((cat, q), [0.0, 0.0])[side] += n
    out = []
    for (cat, q), (a, b) in sorted(tot.items()):
        d = {"category": cat, "quantity": q, "a": _round_num(a), "b": _round_num(b), "delta": _round_num(b - a)}
        if a != 0:
            d["delta_pct"] = round(100.0 * (b - a) / abs(a), 2)
        out.append(d)
    return out


# ------------------------------------------------------------------------------------------ inputs

def find_glb(path: str) -> Optional[Path]:
    """A GLB that belongs to an export: native_graph.glb, model.glb or the only *.glb."""
    p = Path(path)
    if p.is_file():
        for cand in (p.with_suffix(".glb"), p.parent / "native_graph.glb", p.parent / "model.glb"):
            if cand.exists():
                return cand
        return None
    for n in ("native_graph.glb", "model.glb"):
        if (p / n).exists():
            return p / n
    glbs = sorted(p.glob("*.glb"))
    return glbs[0] if len(glbs) == 1 else None


def load_side(path: str, kind: Optional[str] = None) -> Table:
    try:
        return build_table(path, kind=kind)
    except OSError as e:
        raise DiffError(str(e))


def diff_paths(a: str, b: str, kind_a: Optional[str] = None, kind_b: Optional[str] = None, **kw) -> Dict[str, Any]:
    return diff_tables(load_side(a, kind_a), load_side(b, kind_b), **kw)


# ------------------------------------------------------------------------------------------ outcome

def parse_fail_on(spec: str) -> List[str]:
    spec = (spec or "").strip().lower()
    if spec in ("", "none", "never"):
        return []
    if spec == "any":
        return ["added", "removed", "modified"]
    out = [s.strip() for s in spec.split(",") if s.strip()]
    bad = [s for s in out if s not in ("added", "removed", "modified")]
    if bad:
        raise DiffError(f"--fail-on: unknown status {bad[0]!r} (use added, removed, modified, any or none)")
    return out


def exit_code(result: Dict[str, Any], fail_on: Sequence[str]) -> int:
    s = result["summary"]
    return 1 if any(s.get(x, 0) for x in fail_on) else 0


def public_result(result: Dict[str, Any], include_unchanged: bool = False) -> Dict[str, Any]:
    """The JSON form: unchanged elements are left out unless asked for."""
    out = dict(result)
    if not include_unchanged:
        out["elements"] = [e for e in result["elements"] if e["status"] != "unchanged"]
    return out


# ------------------------------------------------------------------------------------------ XLSX

def _fmt_change(c: Dict[str, Any]) -> str:
    s = f"{c['field']}: {c['old'] if c['old'] != '' else '(empty)'} -> {c['new'] if c['new'] != '' else '(empty)'}"
    return s


_FILL = {"added": FILLS["green"], "removed": FILLS["red"], "modified": FILLS["yellow"], "unchanged": FILLS["grey"]}


def write_xlsx(result: Dict[str, Any], path: str, include_unchanged: bool = False) -> None:
    from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
    from openpyxl.styles import Font

    def x(v):
        if isinstance(v, str):
            v = ILLEGAL_CHARACTERS_RE.sub("", v)
            return v[:32000]
        return v

    s = result["summary"]
    wb, ws = new_workbook("Summary")
    title_cell(ws, "A1", "ddc diff: model changelog")
    ws["A2"] = f"Generated {result['generated']}"
    r = 4
    for label, side in (("A (old)", result["a"]), ("B (new)", result["b"])):
        ws.cell(r, 1, label).font = Font(bold=True)
        ws.cell(r, 2, side["source"])
        ws.cell(r, 3, f"{side['kind']}, {side['elements']} elements")
        r += 1
    ws.cell(r, 1, "Matched by").font = Font(bold=True)
    ws.cell(r, 2, result["key"]["method"])
    r += 2
    ws.cell(r, 1, "Status").font = Font(bold=True)
    ws.cell(r, 2, "Elements").font = Font(bold=True)
    for st in STATUSES:
        r += 1
        a = ws.cell(r, 1, st)
        a.fill = _FILL[st]
        ws.cell(r, 2, s[st])
    r += 2
    for label, n in (("Property changes", s["property_changes"]), ("Quantity changes", s["quantity_changes"]),
                     ("Attribute changes (category, type, level, name, ...)", s["attribute_changes"]),
                     ("Matched by fingerprint (id changed, content identical)", s["matched_by_fingerprint"])):
        ws.cell(r, 1, label)
        ws.cell(r, 2, n)
        r += 1
    if result["changed_fields"]:
        r += 1
        ws.cell(r, 1, "Most changed fields").font = Font(bold=True)
        for f in result["changed_fields"][:15]:
            r += 1
            ws.cell(r, 1, f["field"])
            ws.cell(r, 2, f["count"])
    if result["warnings"] or result["notes"]:
        r += 2
        ws.cell(r, 1, "Warnings and notes").font = Font(bold=True)
        for w in result["warnings"]:
            r += 1
            ws.cell(r, 1, "warning")
            ws.cell(r, 2, w)
        for n in result["notes"]:
            r += 1
            ws.cell(r, 1, "note")
            ws.cell(r, 2, n)
    ws.column_dimensions["A"].width = 52
    ws.column_dimensions["B"].width = 60
    ws.column_dimensions["C"].width = 30

    shown = [e for e in result["elements"] if include_unchanged or e["status"] != "unchanged"]

    # Changelog: one row per change; added/removed elements get one row
    ws2 = wb.create_sheet("Changelog")
    head = ["Status", "Key", "GlobalId", "Category", "Type", "Level", "Name", "Field", "Change kind",
            "Old", "New", "Delta", "Delta %"]
    rows = []
    fills = []
    for e in shown:
        base = [e["status"], e["key"], e["global_id"], e["category"], e["type"], e["level"], x(e["name"])]
        if e["changes"]:
            for c in e["changes"]:
                rows.append(base + [c["field"], c["kind"], x(c["old"]), x(c["new"]), c.get("delta"), c.get("delta_pct")])
                fills.append(e["status"])
        else:
            lab = {"added": "(element added)", "removed": "(element removed)", "unchanged": "(unchanged)"}.get(e["status"], "")
            rows.append(base + [lab, "", "", "", None, None])
            fills.append(e["status"])
    write_table(ws2, head, rows)
    for i, st in enumerate(fills, 2):
        ws2.cell(i, 1).fill = _FILL[st]
    autosize(ws2)

    ws3 = wb.create_sheet("Elements")
    head3 = ["Status", "Key", "Key column", "Matched by", "ID in A", "ID in B", "GlobalId", "Category", "Type",
             "Level", "Name", "Changes", "What changed"]
    rows3 = []
    for e in shown:
        rows3.append([e["status"], e["key"], e["key_column"], e["matched_by"],
                      e["a"].get("ElementId") or e["a"].get("ID", ""), e["b"].get("ElementId") or e["b"].get("ID", ""),
                      e["global_id"], e["category"], e["type"], e["level"], x(e["name"]), len(e["changes"]),
                      x("; ".join(_fmt_change(c) for c in e["changes"][:12]) + ("; ..." if len(e["changes"]) > 12 else ""))])
    write_table(ws3, head3, rows3)
    for i, e in enumerate(shown, 2):
        ws3.cell(i, 1).fill = _FILL[e["status"]]
    autosize(ws3)

    ws4 = wb.create_sheet("By category")
    head4 = ["Category", "Added", "Removed", "Modified", "Unchanged", "Elements in A", "Elements in B"]
    rows4 = [[d["category"], d["added"], d["removed"], d["modified"], d["unchanged"], d["total_a"], d["total_b"]]
             for d in result["by_category"]]
    write_table(ws4, head4, rows4)
    for i, d in enumerate(result["by_category"], 2):
        for col, st in ((2, "added"), (3, "removed"), (4, "modified")):
            if d[st]:
                ws4.cell(i, col).fill = _FILL[st]
    autosize(ws4)

    ws5 = wb.create_sheet("Quantities")
    head5 = ["Category", "Quantity", "Total in A", "Total in B", "Delta", "Delta %"]
    rows5 = [[q["category"], q["quantity"], q["a"], q["b"], q["delta"], q.get("delta_pct")] for q in result["quantities"]]
    write_table(ws5, head5, rows5)
    ws5.cell(len(rows5) + 3, 1, "Totals are sums over all elements of each version, so added and removed elements are included.")
    autosize(ws5)
    wb.save(path)
