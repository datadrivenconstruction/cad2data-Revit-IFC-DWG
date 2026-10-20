"""``ddc classify``: classification columns (Uniclass, OmniClass, MasterFormat, DIN 276, GESN/KSR, GB/T 51269,
NL-SfB, CCI) for the element table.

ddc-tools ships NO classification code lists. Most of them are copyrighted or licensed (see docs/CLASSIFICATION.md).
Instead it ships

* mapping templates (``ddc classify template SYSTEM``): an empty CSV with the columns the mapping uses, and
* an importer (``ddc classify import SYSTEM FILE``): you load the list you are licensed to use (CSV or XLSX with a
  code column and a title column); it is stored in your user folder and used to fill titles and to flag unknown codes.

``ddc classify apply`` then adds ``<System> Code`` / ``<System> Title`` columns to a table by matching rules such as
"Category = OST_Walls and Type Name = Interior*  ->  Ss_25_10_30".
"""
from __future__ import annotations

import csv
import fnmatch
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import columns as C
from .loader import LoadError, is_empty, read_file
from .paths import ensure_parent, fs


@dataclass(frozen=True)
class System:
    id: str
    label: str            # prefix of the added columns
    full_name: str
    owner: str
    license: str          # what is known about redistribution
    source: str           # where to get the list
    bundled: bool = False # True only if the code list itself ships in this package (none do)


SYSTEMS: Dict[str, System] = {s.id: s for s in [
    System("uniclass2015", "Uniclass 2015", "Uniclass 2015 (UK, ISO 12006-2 based)", "NBS (Hubexo North UK Ltd)",
           "Creative Commons Attribution-NoDerivatives 4.0 (CC BY-ND 4.0): free to use and share unchanged with "
           "attribution; converted or modified copies are not covered, so the tables are not bundled",
           "https://uniclass.thenbs.com/download"),
    System("omniclass", "OmniClass", "OmniClass Construction Classification System (US/Canada)", "CSI / CSC",
           "Copyrighted, licensed by CSI (licence terms at omniclass.org/license); not redistributable",
           "https://www.csiresources.org/standards/omniclass"),
    System("masterformat", "MasterFormat", "MasterFormat (US/Canada specification divisions)", "CSI / CSC",
           "Copyrighted, licensed by CSI; not redistributable", "https://www.csiresources.org/standards/masterformat"),
    System("din276", "DIN 276", "DIN 276 Building costs (Germany, Kostengruppen)", "DIN e.V. (Beuth Verlag)",
           "Copyrighted standard sold by DIN Media; not redistributable", "https://www.dinmedia.de"),
    System("gesn_ksr", "GESN-KSR", "GESN / KSR (ГЭСН / КСР), Russian unit-rate norms and construction resource classifier",
           "Ministry of Construction of the Russian Federation, FGIS CS",
           "Official normative documents; redistribution terms of the published databases were not confirmed, "
           "so nothing is bundled", "https://fgiscs.minstroyrf.ru"),
    System("gbt51269", "GB/T 51269", "GB/T 51269 Standard for classification and coding of building information models "
           "(建筑信息模型分类和编码标准, China)", "MOHURD / SAMR (China Architecture & Building Press)",
           "Copyrighted national standard; not redistributable", "https://openstd.samr.gov.cn"),
    System("nlsfb", "NL-SfB", "NL/SfB (Netherlands)", "BIM Loket (Stichting BIM Loket)",
           "Intellectual property of BIM Loket; reuse terms were not confirmed, so nothing is bundled",
           "https://www.bimloket.nl/NL-SfB"),
    System("cci", "CCI", "CCI - Construction Classification International (ISO 12006-2 / ISO 81346 based)",
           "Construction Classification International Collaboration",
           "Core tables are reported to be CC BY 4.0, but this could not be confirmed from the publisher's own page; "
           "nothing is bundled", "https://www.cc-int.org"),
]}

MAPPING_HEADER = ["Match Column", "Match Value", "Code", "Title", "Notes"]
CODE_NAMES = ["code", "notation", "number", "item", "id", "kod", "key", "шифр", "код", "编码", "代码", "kostengruppe", "kg"]
TITLE_NAMES = ["title", "name", "description", "text", "bezeichnung", "omschrijving", "наименование", "название", "名称", "benaming"]


class ClassifyError(LoadError):
    pass


def get_system(system_id: str) -> System:
    key = system_id.lower().replace("-", "").replace("_", "").replace(" ", "").replace("/", "")
    for s in SYSTEMS.values():
        if key in (s.id.replace("_", ""), s.label.lower().replace("-", "").replace(" ", "").replace("/", "")):
            return s
    raise ClassifyError(f"unknown classification system {system_id!r}; known: {', '.join(SYSTEMS)}")


def store_dir() -> Path:
    """Where imported code lists live: $DDC_CLASSIFICATION_DIR, else ~/.ddc-tools/classification."""
    env = os.environ.get("DDC_CLASSIFICATION_DIR")
    return Path(env) if env else Path.home() / ".ddc-tools" / "classification"


def codelist_path(system: System, folder: Optional[str] = None) -> Path:
    return (Path(folder) if folder else store_dir()) / f"{system.id}.csv"


# --------------------------------------------------------------------------- template

def write_template(system_id: str, path: str, delimiter: str = ",") -> Path:
    """Empty mapping template (header only), UTF-8 with BOM for Excel."""
    get_system(system_id)
    out = ensure_parent(path)
    with open(fs(out), "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f, delimiter=delimiter).writerow(MAPPING_HEADER)
    return out


# --------------------------------------------------------------------------- code list import / load

def _pick(columns: List[str], names: List[str], override: Optional[str]) -> Optional[str]:
    if override:
        for c in columns:
            if c == override or C._norm(c) == C._norm(override):
                return c
        raise ClassifyError(f"column {override!r} not found; columns: {columns}")
    index = {C._norm(c): c for c in columns}
    for n in names:
        if C._norm(n) in index:
            return index[C._norm(n)]
    return None


def import_codelist(system_id: str, source: str, code_col: Optional[str] = None, title_col: Optional[str] = None,
                    sheet: Optional[str] = None, folder: Optional[str] = None) -> Tuple[Path, int]:
    """Read your licensed list (CSV or XLSX, one code and one title column) and store it normalised
    (``Code,Title``). Returns (stored file, number of codes)."""
    s = get_system(system_id)
    rows = read_file(Path(source), sheet=sheet)
    if not rows:
        raise ClassifyError(f"{source}: no rows")
    cols = list(rows[0].keys())
    cc = _pick(cols, CODE_NAMES, code_col) or cols[0]
    tc = _pick(cols, TITLE_NAMES, title_col) or (cols[1] if len(cols) > 1 else None)
    out: Dict[str, str] = {}
    for r in rows:
        code = r.get(cc)
        if is_empty(code):
            continue
        out.setdefault(str(code).strip(), "" if tc is None or is_empty(r.get(tc)) else str(r.get(tc)).strip())
    if not out:
        raise ClassifyError(f"{source}: no codes found in column {cc!r}")
    dest = ensure_parent(codelist_path(s, folder))
    with open(fs(dest), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Code", "Title"])
        for k, v in out.items():
            w.writerow([k, v])
    return dest, len(out)


def load_codelist(system_id: str, folder: Optional[str] = None) -> Dict[str, str]:
    """Imported list as {code: title}; empty when none was imported."""
    p = codelist_path(get_system(system_id), folder)
    if not Path(fs(p)).is_file():
        return {}
    with open(fs(p), newline="", encoding="utf-8-sig") as f:
        return {r["Code"]: r.get("Title", "") for r in csv.DictReader(f) if r.get("Code")}


# --------------------------------------------------------------------------- mapping + apply

def load_mapping(path: str) -> List[Dict[str, str]]:
    rows = read_file(Path(path))
    rules = []
    for i, r in enumerate(rows, 2):
        low = {C._norm(k): v for k, v in r.items()}
        code = low.get("code")
        if is_empty(code):
            continue
        col = low.get("matchcolumn")
        val = low.get("matchvalue")
        if is_empty(col) or is_empty(val):
            raise ClassifyError(f"{path}: line {i}: 'Match Column' and 'Match Value' are required for code {code}")
        rules.append({"column": str(col).strip(), "value": str(val).strip(), "code": str(code).strip(),
                      "title": "" if is_empty(low.get("title")) else str(low.get("title")).strip()})
    return rules


def apply_mapping(columns: List[str], rows: List[Dict[str, Any]], system_id: str, rules: List[Dict[str, str]],
                  codelist: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Add ``<label> Code`` and ``<label> Title`` to ``columns``/``rows`` in place. The first matching rule wins.
    Match Value is a case-insensitive glob (``Interior*``, ``*Beton*``, ``OST_Walls``)."""
    s = get_system(system_id)
    ccol, tcol = f"{s.label} Code", f"{s.label} Title"
    resolved = []
    for rule in rules:
        col = C.resolve(columns, "", override=rule["column"])
        if col is None:
            col = C.resolve(columns, rule["column"].lower())          # a role name: id, guid, category, type, level
        resolved.append((col, rule["value"].lower(), rule))
    codelist = codelist or {}
    matched = 0
    unknown: Dict[str, int] = {}
    for r in rows:
        hit = None
        for col, pat, rule in resolved:
            if col is None or is_empty(r.get(col)):
                continue
            if fnmatch.fnmatchcase(str(r[col]).lower(), pat):
                hit = rule
                break
        if hit is None:
            continue
        matched += 1
        r[ccol] = hit["code"]
        title = hit["title"] or codelist.get(hit["code"], "")
        if title:
            r[tcol] = title
        if codelist and hit["code"] not in codelist:
            unknown[hit["code"]] = unknown.get(hit["code"], 0) + 1
    for c in (ccol, tcol):
        if c not in columns:
            columns.append(c)
    missing = sorted({rule["column"] for col, _, rule in resolved if col is None})
    return {"system": s.id, "rules": len(rules), "matched": matched, "unmatched": len(rows) - matched,
            "unknown_codes": unknown, "missing_columns": missing, "columns": [ccol, tcol]}
