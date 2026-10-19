"""Map the columns of different converter outputs to common roles."""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional

from .loader import is_empty

# role -> candidate column names, matched case-insensitively, ignoring spaces/_/-.
ALIASES: Dict[str, List[str]] = {
    "id": ["ElementId", "Element Id", "native_id", "Id", "ObjectId", "Handle", "STEP Id", "ExpressId"],
    "guid": ["GlobalId", "Global Id", "IfcGUID", "UniqueId", "unique_id", "Guid"],
    "category": ["Category", "IfcClass", "IfcType", "Entity", "source_class", "Class", "Layer", "category_id"],
    "type": ["Type Name", "TypeName", "Family and Type", "Type", "ObjectType", "Family"],
    "level": ["Level", "Base Constraint", "Reference Level", "BuildingStorey", "Storey",
              "Building Storey", "Floor", "Schedule Level"],
}

# Quantity columns recognised automatically (case-insensitive exact match or suffix).
QUANTITY_NAMES = ["Length", "Width", "Height", "Thickness", "Perimeter", "Area", "Volume",
                  "NetArea", "GrossArea", "NetVolume", "GrossVolume", "NetSideArea",
                  "GrossSideArea", "NetFootprintArea", "GrossFootprintArea", "Weight",
                  "Net Area", "Gross Area", "Net Volume", "Gross Volume"]
# Quantity kinds used to pick a nice header unit hint.
UNIT_HINT = {"length": "length", "width": "length", "height": "length", "thickness": "length",
             "perimeter": "length", "area": "area", "volume": "volume", "weight": "mass"}


def _norm(s: str) -> str:
    return re.sub(r"[\s_\-\.]+", "", str(s)).lower()


def resolve(columns: Iterable[str], role: str, override: Optional[str] = None) -> Optional[str]:
    cols = list(columns)
    if override:
        for c in cols:
            if c == override or _norm(c) == _norm(override):
                return c
        return None
    index = {_norm(c): c for c in cols}
    for a in ALIASES.get(role, []):
        if _norm(a) in index:
            return index[_norm(a)]
    # IFC-style "Pset.Prop" columns: match the part after the last dot.
    for a in ALIASES.get(role, []):
        for c in cols:
            if "." in c and _norm(c.rsplit(".", 1)[1]) == _norm(a):
                return c
    return None


def all_columns(rows: List[Dict[str, Any]]) -> List[str]:
    seen: Dict[str, None] = {}
    for r in rows:
        for k in r:
            seen.setdefault(k, None)
    return list(seen)


def to_number(v: Any) -> Optional[float]:
    """Parse numbers like 12.5, '12,5', '1 234.5 m2'. None if not numeric."""
    if is_empty(v) or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(" ", " ")
    m = re.match(r"^[-+]?\d[\d\s]*([.,]\d+)?([eE][-+]?\d+)?", s)
    if not m:
        return None
    t = m.group(0).replace(" ", "")
    if "," in t and "." in t:
        t = t.replace(",", "")
    else:
        t = t.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def quantity_columns(columns: Iterable[str]) -> List[str]:
    names = {_norm(n) for n in QUANTITY_NAMES}
    out = []
    for c in columns:
        base = c.rsplit(".", 1)[-1] if "." in c else c
        if _norm(base) in names:
            out.append(c)
    return out


def quantity_kind(col: str) -> str:
    base = _norm(col.rsplit(".", 1)[-1])
    for k in ("volume", "area", "length", "width", "height", "thickness", "perimeter", "weight"):
        if k in base:
            return UNIT_HINT[k]
    return ""
