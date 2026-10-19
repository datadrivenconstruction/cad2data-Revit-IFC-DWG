"""Read a converter export (folder or single file) into a list of flat row dicts.

Supported: .xlsx, .csv, .jsonl/.ndjson, .json (list of objects), .sqlite/.db.
Values are kept as read; empty cells become None.
"""
from __future__ import annotations

import csv
import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

Row = Dict[str, Any]

# Preference when a folder holds several formats of the same export.
_ORDER = [".sqlite", ".sqlite3", ".db", ".jsonl", ".ndjson", ".xlsx", ".csv", ".json"]
# Auxiliary files that are not element tables.
_SKIP_STEMS = re.compile(
    r"(geometry_index|property_scopes|manifest|summary|report|timings|identity|"
    r"tables|columns|~\$)", re.I)


class LoadError(Exception):
    pass


def is_empty(v: Any) -> bool:
    return v is None or (isinstance(v, str) and v.strip() == "")


def _clean(v: Any) -> Any:
    if isinstance(v, str):
        v = v.strip()
        return v if v != "" else None
    return v


def _flatten(obj: Any, prefix: str = "") -> Row:
    out: Row = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}{k}"
            if isinstance(v, dict):
                out.update(_flatten(v, key + "."))
            elif isinstance(v, list):
                out[key] = json.dumps(v, ensure_ascii=False)
            else:
                out[key] = _clean(v)
    return out


def _read_xlsx(path: Path, sheet: Optional[str]) -> List[Row]:
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        if sheet:
            if sheet not in wb.sheetnames:
                raise LoadError(f"sheet {sheet!r} not found in {path.name}: {wb.sheetnames}")
            ws = wb[sheet]
        else:
            ws = wb[wb.sheetnames[0]]
        it = ws.iter_rows(values_only=True)
        header = None
        for first in it:
            if first and any(c is not None for c in first):
                header = [str(c).strip() if c is not None else "" for c in first]
                break
        if header is None:
            return []
        rows = []
        for r in it:
            if r is None or all(c is None for c in r):
                continue
            rows.append({h: _clean(c) for h, c in zip(header, r) if h})
        return rows
    finally:
        wb.close()


def _read_csv(path: Path) -> List[Row]:
    csv.field_size_limit(1 << 30)
    with open(path, newline="", encoding="utf-8-sig") as f:
        first = f.readline()
        f.seek(0)
        # delimiter from the header line only; quoting stays standard (no dialect guessing)
        delim = max(",;	", key=lambda d: first.count(d))
        rd = csv.DictReader(f, delimiter=delim)
        return [{(k or "").strip(): _clean(v) for k, v in r.items() if k} for r in rd]


def _read_jsonl(path: Path) -> List[Row]:
    rows: List[Row] = []
    with open(path, encoding="utf-8-sig") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise LoadError(f"{path.name}:{n}: invalid JSON ({e.msg})")
            if isinstance(obj, dict):
                rows.append(_flatten(obj))
    return rows


def _read_json(path: Path) -> List[Row]:
    with open(path, encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, dict):
        for k in ("elements", "rows", "data", "items"):
            if isinstance(data.get(k), list):
                data = data[k]
                break
    if not isinstance(data, list):
        raise LoadError(f"{path.name}: expected a list of objects")
    return [_flatten(o) for o in data if isinstance(o, dict)]


def _read_sqlite(path: Path, table: Optional[str]) -> List[Row]:
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        con.row_factory = sqlite3.Row
        names = [r[0] for r in con.execute(
            "select name from sqlite_master where type in ('table','view') order by name")]
        if not names:
            raise LoadError(f"{path.name}: no tables")
        if table:
            if table not in names:
                raise LoadError(f"table {table!r} not found in {path.name}: {names}")
            chosen = table
        else:
            pref = [n for n in names if n.lower() in ("elements", "objects", "data", "properties")]
            if pref:
                chosen = pref[0]
            else:  # otherwise the widest table
                chosen = max(names, key=lambda n: len(con.execute(
                    f'pragma table_info("{n}")').fetchall()))
        cur = con.execute(f'select * from "{chosen}"')
        return [{k: _clean(r[k]) for k in r.keys()} for r in cur]
    finally:
        con.close()


def read_file(path: Path, sheet: Optional[str] = None, table: Optional[str] = None) -> List[Row]:
    ext = path.suffix.lower()
    if ext == ".xlsx":
        return _read_xlsx(path, sheet)
    if ext == ".csv":
        return _read_csv(path)
    if ext in (".jsonl", ".ndjson"):
        return _read_jsonl(path)
    if ext == ".json":
        return _read_json(path)
    if ext in (".sqlite", ".sqlite3", ".db"):
        return _read_sqlite(path, table)
    raise LoadError(f"unsupported file type: {path.name}")


def pick_files(folder: Path, fmt: Optional[str] = None) -> List[Path]:
    cands = [p for p in folder.iterdir()
             if p.is_file() and p.suffix.lower() in _ORDER and not _SKIP_STEMS.search(p.stem)]
    if fmt:
        want = "." + fmt.lower().lstrip(".")
        cands = [p for p in cands if p.suffix.lower() == want]
    cands.sort(key=lambda p: (_ORDER.index(p.suffix.lower()), p.name.lower()))
    return cands


def load(path: str, fmt: Optional[str] = None, sheet: Optional[str] = None,
         table: Optional[str] = None) -> Tuple[List[Row], List[str]]:
    """Return (rows, source_files). For a folder the preferred format present is used
    and all files of that format are concatenated (one file per model)."""
    p = Path(path)
    if not p.exists():
        raise LoadError(f"path not found: {path}")
    if p.is_file():
        return read_file(p, sheet, table), [p.name]
    files = pick_files(p, fmt)
    if not files:
        raise LoadError(f"no export files (xlsx/csv/jsonl/sqlite/json) in {path}")
    ext = files[0].suffix.lower()
    group = [f for f in files if f.suffix.lower() == ext]
    rows: List[Row] = []
    for f in group:
        for r in read_file(f, sheet, table):
            if len(group) > 1:
                r.setdefault("_source_file", f.name)
            rows.append(r)
    return rows, [f.name for f in group]
