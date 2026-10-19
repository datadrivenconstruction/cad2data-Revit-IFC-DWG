"""Adapters that turn the converters' relational / graph outputs into one flat table.

* IFC to Excel writes a semantic model: tables Objects, Properties, Quantities, SpatialLinks,
  TypeLinks (sheets in drawing.xlsx, `{"table":..,"record":..}` lines in data.jsonl, table
  `records` in data.sqlite). `ifc_rows` joins them into one row per object.
* RVT Converter (`--properties`) writes `properties.jsonl` (schema native_stored_properties/2):
  one saved graph per element. `rvt_properties_rows` builds one row per element from the stored
  parameters. That output has category ids, not names, and no calculated quantities.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

IFC_TABLES = ("Objects", "Properties", "Quantities", "SpatialLinks", "TypeLinks", "Relations")

_QTY_BASE = {"length", "width", "height", "thickness", "perimeter", "area", "volume", "weight",
             "netarea", "grossarea", "netvolume", "grossvolume", "netsidearea", "grosssidearea",
             "unboundedheight", "depth"}
_QTY_TYPES = {"IfcAreaMeasure", "IfcVolumeMeasure", "IfcMassMeasure"}
_LEN_TYPES = {"IfcLengthMeasure", "IfcPositiveLengthMeasure"}
_LEVEL_PROPS = ("Level", "Base Constraint", "Reference Level", "Schedule Level")
_TYPE_SET = re.compile(r"(^|[_ ])type([_ ]|$)", re.I)


def _j(v: Any) -> Any:
    """xlsx stores nested values as JSON text; sqlite/jsonl hold real objects."""
    if isinstance(v, str) and v[:1] in "{[":
        try:
            return json.loads(v)
        except ValueError:
            return v
    return v


def _truthy(v: Any) -> bool:
    return v is True or (isinstance(v, str) and v.strip().lower() == "true")


def _scalar(value: Any) -> Tuple[Any, Optional[str]]:
    """IFC property value -> (python value, ifc type name)."""
    value = _j(value)
    if isinstance(value, dict):
        nv = value.get("NominalValue")
        if isinstance(nv, dict) and "value" in nv:
            return nv.get("value"), nv.get("ifc_type")
        for v in value.values():
            if isinstance(v, dict) and "value" in v:
                return v.get("value"), v.get("ifc_type")
            if isinstance(v, (int, float, str)) and not isinstance(v, bool):
                return v, None
        return json.dumps(value, ensure_ascii=False), None
    return value, None


def _number(value: Any) -> Optional[float]:
    value = _j(value)
    if isinstance(value, dict):
        for k, v in value.items():
            if k.endswith("Value") and isinstance(v, (int, float)) and not isinstance(v, bool):
                return float(v)
        for v in value.values():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return float(v)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def is_ifc_tables(names: Iterable[str]) -> bool:
    s = set(names)
    return "Objects" in s and ("Properties" in s or "Quantities" in s)


def ifc_rows(tables: Dict[str, Iterable[Dict[str, Any]]]) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
    """Return (rows, quantity_columns, notes)."""
    objects = [dict(r) for r in tables.get("Objects", [])]
    by_id = {str(o["ID"]): o for o in objects}
    parent: Dict[str, str] = {}
    for l in tables.get("SpatialLinks", []):
        parent.setdefault(str(l["child_step_id"]), str(l["parent_step_id"]))
    for rel in tables.get("Relations", []):  # an opening sits where its host element sits
        if rel.get("ifc_class") != "IfcRelVoidsElement":
            continue
        at = _j(rel.get("attributes")) or {}
        host, op = (at.get("RelatingBuildingElement") or {}), (at.get("RelatedOpeningElement") or {})
        if isinstance(host, dict) and isinstance(op, dict) and "ref" in host and "ref" in op:
            parent.setdefault(str(op["ref"]), str(host["ref"]))
    type_of: Dict[str, str] = {}
    for l in tables.get("TypeLinks", []):
        type_of.setdefault(str(l["owner_step_id"]), str(l["type_step_id"]))

    def storey(oid: str) -> Optional[str]:
        cur, hops = oid, 0
        while cur is not None and hops < 8:
            o = by_id.get(cur)
            if o is not None and o.get("Category") == "IfcBuildingStorey":
                return o.get("Name")
            cur = parent.get(cur)
            hops += 1
        return None

    values: Dict[str, Dict[str, Any]] = {}
    qty_cols: List[str] = []
    seen_q: Set[str] = set()

    def mark_q(col: str) -> None:
        if col not in seen_q:
            seen_q.add(col)
            qty_cols.append(col)

    for p in tables.get("Properties", []):
        col = f"{p['set_name']}.{p['property_name']}"
        v, t = _scalar(p.get("value"))
        values.setdefault(str(p["owner_step_id"]), {}).setdefault(col, v)
        base = re.sub(r"[\s_\-]+", "", str(p["property_name"])).lower()
        if not _TYPE_SET.search(str(p["set_name"])) and (
                t in _QTY_TYPES or (t in _LEN_TYPES and base in _QTY_BASE)):
            mark_q(col)
    for q in tables.get("Quantities", []):
        col = f"{q['set_name']}.{q['property_name']}"
        n = _number(q.get("value"))
        values.setdefault(str(q["owner_step_id"]), {})[col] = n
        mark_q(col)

    rows: List[Dict[str, Any]] = []
    for o in objects:
        if _truthy(o.get("IsType")):
            continue
        oid = str(o["ID"])
        attrs = _j(o.get("Attributes")) or {}
        tname = None
        if oid in type_of and type_of[oid] in by_id:
            tname = by_id[type_of[oid]].get("Name")
        if not tname and isinstance(attrs, dict):
            tname = attrs.get("ObjectType")
        lvl = storey(oid)
        if lvl is None:  # Revit-style fallback: the level stored as a property
            for col, v in (values.get(oid) or {}).items():
                if col.rsplit(".", 1)[-1] in _LEVEL_PROPS and isinstance(v, str) and v.strip():
                    lvl = v
                    break
        r: Dict[str, Any] = {"ElementId": oid, "GlobalId": o.get("GlobalId"), "Category": o.get("Category"),
                             "Name": o.get("Name"), "TypeName": tname or None, "Level": lvl}
        for k, v in (values.get(oid) or {}).items():
            r[k] = v if not (isinstance(v, str) and v.strip() == "") else None
        rows.append(r)
    notes = ["IFC export: quantities are the stored IfcElementQuantity values plus length/area/volume "
             "measures in property sets; Revit type property sets are not summed"]
    return rows, qty_cols, notes


# ---------------------------------------------------------------- RVT saved properties

def _rvt_value(fields: Dict[str, Any]) -> Any:
    rec = (fields or {}).get("record") or {}
    for k, v in rec.items():
        if not k.endswith(".m_value"):
            continue
        if not isinstance(v, dict):
            return None
        if "text" in v:
            return v["text"] if v["text"] != "" else None
        if "integer" in v:
            try:
                return int(v["integer"])
            except (TypeError, ValueError):
                return v["integer"]
        if "number" in v:
            return v["number"]
        if "record" in v:  # ElementId reference
            cur: Any = v
            while isinstance(cur, dict):
                if "integer" in cur:
                    return int(cur["integer"])
                cur = next(iter((cur.get("record") or {}).values()), None)
    return None


def rvt_properties_rows(lines: Iterable[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
    elements: Dict[str, Dict[str, Any]] = {}
    pending: List[Dict[str, Any]] = []
    for line in lines:
        if '"row":"record"' in line:
            d = json.loads(line)
            if d.get("row") == "record":
                elements[str(d["owner"])] = {"ElementId": str(d["owner"]), "Category": str(d.get("category_id"))}
        elif '"row":"parameter"' in line:
            d = json.loads(line)
            if d.get("row") == "parameter" and d.get("builtin_label"):
                pending.append(d)
    for d in pending:
        e = elements.get(str(d["owner"]))
        if e is None:
            continue
        e.setdefault(d["builtin_label"], _rvt_value(d.get("fields")))
    notes = ["RVT saved properties: category is a numeric id (no names in this output), values are stored "
             "values in the model's internal units, calculated quantities (area, volume) are not stored"]
    return list(elements.values()), notes
