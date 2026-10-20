"""``ddc table``: flat element table (one row per element) from any DDC converter output.

The old 18.x converters wrote one flat sheet per model (``<name>_rvt.xlsx``, ``<name>_ifc.xlsx``,
``<name>_dwg.xlsx``) with columns such as ID, Category, Type Name, Level, Volume, Area and one column
per parameter. The current converters write other things: a saved parameter graph (RVT), entity
tables (IFC) and a record per drawing object (DWG). This module rebuilds the flat sheet from them so
that spreadsheets, notebooks and n8n steps written for the old layout keep working.

Inputs (all auto-detected):

* RVT: the folder ``<name>.converted`` written by ``RVTconverter.exe --properties`` (``properties.jsonl``).
  If ``native_graph.ifc`` (``--ifc``) and ``native_graph.glb`` are there too they add names and quantities.
* IFC: the folder/file of DDC IFC to Excel (``data.jsonl``, ``data.sqlite``, ``drawing.xlsx``) or a plain ``.ifc``.
* DWG: the ``<name>.jsonl`` / ``.csv`` / ``.xlsx`` written by ``dwg2excel.exe``.
"""
from __future__ import annotations

import csv
import json
import math
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import ifcmodel
from .columns import to_number
from .ifcmodel import Model, SKIP_BY_DEFAULT
from .loader import LoadError, is_empty, read_file

# --------------------------------------------------------------------------- column contract

# (column, meaning, RVT source, IFC source, DWG source). The documented mapping (README / docs/TABLE.md)
# is checked against this list by the tests.
COLUMN_MAP: List[Tuple[str, str, str, str, str]] = [
    ("ID", "Row key, the same value type as the old exports", "ElementId", "STEP id (or Revit ElementId in a Revit IFC)", "handle"),
    ("ElementId", "Revit element id", "ElementId", "Revit_Identity.ElementId if present", ""),
    ("GlobalId", "Global unique id", "IFC GlobalId when native_graph.ifc is present", "IfcRoot.GlobalId", ""),
    ("Category", "Old-style category code", "OST_ code from the category id (OST_Walls)", "IFC class (IfcWall) or the Revit category in a Revit IFC", "entity type (LINE, INSERT, ...)"),
    ("Category Name", "Readable category", "Revit_Identity.CategoryName", "Revit category if present, else the IFC class without Ifc", "entity type"),
    ("IfcClass", "IFC entity class", "from native_graph.ifc", "IfcRoot class", ""),
    ("Revit Class", "Revit element class", "root object class (SWall, FamilyInstance)", "Revit_Identity.Class", ""),
    ("Family", "Family name", "Revit_Identity.FamilyName", "Revit_Identity.FamilyName, else first part of 'Family:Type:Id' names", ""),
    ("Type Name", "Type name", "Revit_Identity.TypeName", "type object name, else Revit_Identity.TypeName, else middle part of 'Family:Type:Id'", "block name for INSERT"),
    ("Type", "Same as Type Name (the old exports had both columns)", "Type Name", "Type Name", "Type Name"),
    ("Family and Type", "Family: Type", "Family and Type names joined", "same", ""),
    ("Type Id", "Type element id", "root object type reference", "Revit_Identity.TypeId", ""),
    ("Name", "Element name", "first name-like stored text", "IfcRoot.Name", "text of TEXT/MTEXT"),
    ("Level", "Level / storey / layout", "associated level name", "Revit_Identity.LevelName, else the containing IfcBuildingStorey", "owner block (Model_Space, Paper_Space)"),
    ("Material", "Material names joined by '; '", "", "IfcRelAssociatesMaterial", ""),
    ("Length", "Length", "", "see Quantity rules", "LINE, ARC, CIRCLE, ELLIPSE, polyline length"),
    ("Width", "Width", "", "see Quantity rules", ""),
    ("Height", "Height", "", "see Quantity rules", ""),
    ("Perimeter", "Perimeter", "", "see Quantity rules", "closed polyline / circle"),
    ("Area", "Area", "mesh surface area (m2) from the GLB", "see Quantity rules", "circle, closed polyline (no bulges)"),
    ("Volume", "Volume", "mesh volume (m3) from the GLB, not Revit's Volume", "see Quantity rules", ""),
    ("Quantity Source", "Where Length..Volume came from", "glb-mesh", "property:Set.Name or quantity:Set.Name", "geometry"),
    ("Layer", "Drawing layer", "", "", "layer_name"),
    ("On the standard 3D View", "True when the element is part of the exported model (the old exports had a Revit view flag of this name)",
     "True when the element has a mesh in native_graph.glb or a product in native_graph.ifc", "True for every product row", "True for model space, False for paper space and blocks"),
]
FIXED_COLUMNS = [c[0] for c in COLUMN_MAP]

QUANTITY_COLUMNS = ["Length", "Width", "Height", "Perimeter", "Area", "Volume"]
# For every quantity column the names tried in order, first in properties, then in quantity sets.
QUANTITY_RULES: Dict[str, List[str]] = {
    "Length": ["Length", "NominalLength"],
    "Width": ["Width", "NominalWidth", "Thickness"],
    "Height": ["Height", "NominalHeight", "Unconnected Height"],
    "Perimeter": ["Perimeter"],
    "Area": ["Area", "NetArea", "NetSideArea", "GrossArea", "GrossSideArea", "NetFootprintArea",
             "GrossFootprintArea", "GrossSurfaceArea", "SurfaceArea"],
    "Volume": ["Volume", "NetVolume", "GrossVolume", "ClosedShellVolume"],
}
_QTY_KIND = {"Length": "Length", "Width": "Length", "Height": "Length", "Perimeter": "Length",
             "Area": "Area", "Volume": "Volume"}

# Revit BuiltInCategory ids that are certain; the others get the OST_ code from their name when it is known.
OST_BY_ID = {
    "-2000011": "OST_Walls", "-2000014": "OST_Windows", "-2000023": "OST_Doors", "-2000032": "OST_Floors",
    "-2000035": "OST_Roofs", "-2000038": "OST_Ceilings", "-2000100": "OST_Columns",
    "-2001330": "OST_StructuralColumns", "-2001320": "OST_StructuralFraming",
    "-2001300": "OST_StructuralFoundation", "-2000120": "OST_Stairs", "-2000126": "OST_StairsRailing",
    "-2000160": "OST_Rooms", "-2000080": "OST_Furniture", "-2000151": "OST_GenericModel",
    "-2000240": "OST_Levels", "-2000220": "OST_Grids",
}
_OST_IRREGULAR = {"Curtain Panels": "OST_CurtainWallPanels", "Curtain Wall Mullions": "OST_CurtainWallMullions",
                  "Generic Models": "OST_GenericModel", "Railings": "OST_StairsRailing"}


def ost_code(category_id: Optional[str], category_name: Optional[str]) -> Optional[str]:
    if category_id and str(category_id) in OST_BY_ID:
        return OST_BY_ID[str(category_id)]
    if category_name:
        if category_name in _OST_IRREGULAR:
            return _OST_IRREGULAR[category_name]
        return "OST_" + re.sub(r"[^0-9A-Za-z]+", "", category_name)
    return None


@dataclass
class Table:
    columns: List[str]
    rows: List[Dict[str, Any]]
    kind: str                                   # rvt | rvt+ifc | ifc-excel | ifc-step | dwg
    source: str = ""
    notes: List[str] = field(default_factory=list)


class TableError(LoadError):
    pass


# --------------------------------------------------------------------------- shared helpers

def _num(v: Any) -> Optional[float]:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return to_number(v)


def _round(v: float) -> float:
    return float(f"{v:.10g}")


def _add_param(row: Dict[str, Any], set_name: str, name: str, value: Any, qualified: bool) -> None:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return
    key = f"{set_name}.{name}" if qualified and set_name else name
    if key in row:
        if row[key] == value:
            return
        key = f"{set_name}.{name}" if set_name else key
        if key in row:
            return
    row[key] = value


def _finish(rows: List[Dict[str, Any]], notes: List[str], kind: str, source: str) -> Table:
    cols: Dict[str, None] = {c: None for c in FIXED_COLUMNS}
    used = set()
    for r in rows:
        used.update(r)
    head = [c for c in FIXED_COLUMNS if c in used]
    seen = set(head)
    rest: List[str] = []
    for r in rows:
        for k in r:
            if k not in seen:
                seen.add(k)
                rest.append(k)
    return Table(head + rest, rows, kind, source, notes)


# --------------------------------------------------------------------------- IFC (tables, STEP, Revit IFC)

def _pick_quantity(props, quants, col: str):
    kind = _QTY_KIND[col]
    names = QUANTITY_RULES[col]
    for n in names:
        for p in props:
            if p.name == n and _num(p.value) is not None:
                # a property is accepted when its IFC measure type fits the column
                t = (p.ifc_type or "").lower()
                if t and kind == "Length" and ("area" in t or "volume" in t):
                    continue
                if t and kind == "Area" and ("length" in t or "volume" in t):
                    continue
                if t and kind == "Volume" and ("length" in t or "area" in t):
                    continue
                return _num(p.value), f"property:{p.set_name}.{p.name}"
        for q in quants:
            if q.name == n and q.kind == kind:
                return q.value, f"quantity:{q.set_name}.{q.name}"
    return None, None


def _storey_of(m: Model, oid: str) -> Optional[str]:
    seen = set()
    cur = oid
    while cur and cur not in seen:
        seen.add(cur)
        parent = m.contained_in.get(cur) or m.aggregated_in.get(cur)
        if not parent:
            return None
        po = m.objs.get(parent)
        if po and po.cls == "IfcBuildingStorey":
            return po.name
        cur = parent
    return None


def _split_revit_name(name: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """'Basic Wall:Generic - 200mm:123456' -> ('Basic Wall', 'Generic - 200mm')."""
    if not name or ":" not in name:
        return None, None
    parts = [p.strip() for p in name.split(":")]
    if len(parts) >= 3:
        return parts[0] or None, parts[1] or None
    if len(parts) == 2:
        return parts[0] or None, parts[1] or None
    return None, None


IDENTITY_MAP = {"ElementId": "ElementId", "Class": "Revit Class", "CategoryId": "Category Id",
                "CategoryName": "Category Name", "FamilyName": "Family", "TypeName": "Type Name",
                "TypeId": "Type Id", "LevelName": "Level", "LevelId": "Level Id",
                "PhaseCreated": "Phase Created", "PhaseDemolished": "Phase Demolished"}


def ifc_rows(m: Model, include_all: bool = False, qualified: bool = False) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for oid, o in m.objs.items():
        if o.is_type:
            continue
        if not include_all and o.cls in SKIP_BY_DEFAULT:
            continue
        own = list(m.props.get(oid, []))
        tid = m.type_of.get(oid)
        tprops = list(m.props.get(tid, [])) if tid else []
        props = own + tprops
        quants = list(m.quants.get(oid, [])) + (list(m.quants.get(tid, [])) if tid else [])
        row: Dict[str, Any] = {}
        ident = {p.name: p.value for p in own if p.set_name == "Revit_Identity"}
        revit = bool(ident)
        row["ID"] = ident.get("ElementId") if revit and ident.get("ElementId") is not None else _intish(oid)
        if revit:
            row["ElementId"] = ident.get("ElementId")
        row["GlobalId"] = o.guid
        cat_name = ident.get("CategoryName") or _first_text(props, ["Category"])
        row["IfcClass"] = o.cls
        pretty = o.cls[3:] if o.cls.startswith("Ifc") else o.cls
        row["Category Name"] = cat_name or pretty
        row["Category"] = (ost_code(str(ident.get("CategoryId")) if ident.get("CategoryId") is not None else None,
                                    cat_name) if cat_name else o.cls)
        fam, typ = ident.get("FamilyName"), ident.get("TypeName")
        n_fam, n_typ = _split_revit_name(o.name)
        t_obj = m.objs.get(tid) if tid else None
        fam = fam or _first_text(props, ["Family"]) or n_fam
        typ = typ or (t_obj.name if t_obj and t_obj.name else None) or _first_text(props, ["Type", "Type Name"]) \
            or n_typ or o.object_type
        row["Family"] = fam
        row["Type Name"] = typ
        row["Type"] = typ
        if fam and typ:
            row["Family and Type"] = f"{fam}: {typ}"
        elif typ:
            row["Family and Type"] = typ
        row["Name"] = o.name or o.long_name
        row["On the standard 3D View"] = True
        row["Level"] = ident.get("LevelName") or _storey_of(m, oid) or _first_text(props, ["Level", "Base Constraint", "Reference Level"])
        mats = m.materials.get(oid) or (m.materials.get(tid) if tid else None)
        if mats:
            row["Material"] = "; ".join(dict.fromkeys(mats))
        if revit:
            for src, dst in IDENTITY_MAP.items():
                if src in ident and ident[src] is not None and dst not in row:
                    row[dst] = ident[src]
                elif src in ident and ident[src] is not None and dst in ("ElementId",):
                    pass
            if "Type Id" in row and row["Type Id"] is None:
                row.pop("Type Id")
        srcs = []
        consumed = set()
        for col in QUANTITY_COLUMNS:
            v, src = _pick_quantity(props, quants, col)
            if v is not None:
                row[col] = _round(v)
                srcs.append(f"{col}={src}")
                if src.startswith("property:"):
                    consumed.add(src[len("property:"):])
        if srcs:
            row["Quantity Source"] = "; ".join(srcs)
        # parameters: instance sets first, then type sets, one column per name
        skip_names = set(IDENTITY_MAP) if revit else set()
        for p in own:
            if p.set_name == "Revit_Identity" and p.name in skip_names:
                continue
            if f"{p.set_name}.{p.name}" in consumed:
                continue
            _add_param(row, p.set_name, p.name, _json_safe(p.value), qualified)
        for p in tprops:
            if f"{p.set_name}.{p.name}" in consumed:
                continue
            _add_param(row, p.set_name, p.name, _json_safe(p.value), qualified)
        row = {k: v for k, v in row.items() if v is not None and not (isinstance(v, str) and v == "")}
        out.append(row)
    return out


def _intish(s: str) -> Any:
    return int(s) if isinstance(s, str) and s.isdigit() else s


def _first_text(props, names: List[str]) -> Optional[str]:
    for n in names:
        for p in props:
            if p.name == n and isinstance(p.value, str) and p.value.strip():
                return p.value.strip()
    return None


def _json_safe(v: Any) -> Any:
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return json.dumps(v, ensure_ascii=False)


# --------------------------------------------------------------------------- RVT (properties.jsonl)

_NAME_KEYS = (".m_name", ".m_strName", ".m_text", ".m_viewName", ".m_sName")


def _ival(v: Any) -> Optional[str]:
    """ElementId record -> '1679'."""
    try:
        return v["record"]["ElementId.m_id"]["record"]["Identifier.m_id64"]["integer"]
    except (KeyError, TypeError):
        return None


def _scalar(v: Any) -> Any:
    if isinstance(v, dict):
        if "number" in v:
            return v["number"]
        if "integer" in v:
            try:
                return int(v["integer"])
            except ValueError:
                return v["integer"]
        if "text" in v:
            return v["text"]
        if "record" in v:
            i = _ival(v)
            if i is not None:
                return int(i) if re.fullmatch(r"-?\d+", i) else i
            rec = v["record"]
            for k in rec:
                if k.endswith(".m_value"):
                    return _scalar(rec[k])
    return None


def read_rvt_properties(path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, str], List[str]]:
    """Return (element dicts, level names by id, notes) from properties.jsonl."""
    elems: Dict[str, Dict[str, Any]] = {}
    names: Dict[str, str] = {}
    notes: List[str] = []
    saved_year = None
    with open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            if not line.strip():
                continue
            if '"row":"schema_class"' in line[:40] or '"row": "schema_class"' in line[:40]:
                continue
            d = json.loads(line)
            row = d.get("row")
            if row == "document":
                saved_year = d.get("saved_year")
            elif row == "record":
                e = elems.setdefault(str(d["owner"]), {"id": str(d["owner"]), "params": []})
                e["category_id"] = str(d.get("category_id"))
            elif row == "object":
                f = (d.get("fields") or {}).get("record") or {}
                if "Element.m_id" in f and _ival(f["Element.m_id"]) == str(d["owner"]):
                    e = elems.setdefault(str(d["owner"]), {"id": str(d["owner"]), "params": []})
                    e["class"] = d.get("class_name")
                    lvl = _ival(f.get("Element.m_assocLevelId"))
                    if lvl and lvl != "-1":
                        e["level_id"] = lvl
                    for k, v in f.items():
                        if k.endswith(_NAME_KEYS) and isinstance(v, dict) and v.get("text"):
                            e.setdefault("name", v["text"])
                        if k.endswith("AttributesId") or k.endswith(".m_typeId"):
                            t = _ival(v)
                            if t and t != "-1":
                                e.setdefault("type_id", t)
                    if e["class"] == "Level":
                        t = f.get("DatumPlane.m_text")
                        if isinstance(t, dict) and t.get("text"):
                            names[str(d["owner"])] = t["text"]
            elif row == "parameter":
                e = elems.setdefault(str(d["owner"]), {"id": str(d["owner"]), "params": []})
                label = d.get("builtin_label") or d.get("builtin_parameter") or d.get("parameter_id")
                val = _scalar((d.get("fields") or {}))
                if val is None:
                    rec = (d.get("fields") or {}).get("record") or {}
                    for k, v in rec.items():
                        if k.endswith(".m_value"):
                            val = _scalar(v)
                e["params"].append((str(label), val, d.get("storage")))
    if saved_year:
        notes.append(f"saved with Revit {saved_year}")
    return list(elems.values()), names, notes


def read_glb_quantities(path: Path) -> Dict[str, Dict[str, float]]:
    """Per Revit element id: mesh volume (m3), surface area (m2) and bounding box (m) from native_graph.glb."""
    data = Path(path).read_bytes()
    if data[:4] != b"glTF":
        raise TableError(f"{path.name}: not a GLB file")
    jl = struct.unpack("<I", data[12:16])[0]
    gltf = json.loads(data[20:20 + jl])
    off = 20 + jl
    bl = struct.unpack("<I", data[off:off + 4])[0]
    blob = data[off + 8: off + 8 + bl]

    def accessor(i: int):
        a = gltf["accessors"][i]
        bv = gltf["bufferViews"][a["bufferView"]]
        start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        ct = {5126: ("f", 4), 5125: ("I", 4), 5123: ("H", 2), 5121: ("B", 1)}[a["componentType"]]
        nc = {"SCALAR": 1, "VEC3": 3, "VEC2": 2, "VEC4": 4}[a["type"]]
        stride = bv.get("byteStride") or ct[1] * nc
        out = []
        for k in range(a["count"]):
            out.append(struct.unpack_from("<" + ct[0] * nc, blob, start + k * stride))
        return out

    res: Dict[str, Dict[str, float]] = {}
    for node in gltf.get("nodes", []):
        eid = (node.get("extras") or {}).get("element_id")
        if eid is None or "mesh" not in node:
            continue
        mat = node.get("matrix") or [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        vol = area = 0.0
        mn = [math.inf] * 3
        mx = [-math.inf] * 3
        for prim in gltf["meshes"][node["mesh"]]["primitives"]:
            pos = [(mat[0] * x + mat[4] * y + mat[8] * z + mat[12],
                    mat[1] * x + mat[5] * y + mat[9] * z + mat[13],
                    mat[2] * x + mat[6] * y + mat[10] * z + mat[14])
                   for x, y, z in accessor(prim["attributes"]["POSITION"])]
            idx = [t[0] for t in accessor(prim["indices"])] if "indices" in prim else list(range(len(pos)))
            for p in pos:
                for k in range(3):
                    mn[k] = min(mn[k], p[k])
                    mx[k] = max(mx[k], p[k])
            for t in range(0, len(idx) - 2, 3):
                a, b, c = pos[idx[t]], pos[idx[t + 1]], pos[idx[t + 2]]
                vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                        + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
                ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
                vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
                cx, cy, cz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
                area += 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)
        r = res.setdefault(str(eid), {"volume": 0.0, "area": 0.0, "min": mn, "max": mx})
        if r["min"] is not mn:                    # element split over several nodes
            r["min"] = [min(a, b) for a, b in zip(r["min"], mn)]
            r["max"] = [max(a, b) for a, b in zip(r["max"], mx)]
        r["volume"] += vol
        r["area"] += area
    return res


def _is_type_class(c: Optional[str]) -> bool:
    return bool(c) and (c.endswith(("Type", "Symbol", "Surrogate")) or c in ("Family", "FamilyBase"))


def rvt_rows(folder: Path, use_ifc: bool = True, use_glb: bool = True, include_all: bool = False,
             qualified: bool = False) -> Table:
    folder = Path(folder)
    props = folder / "properties.jsonl" if folder.is_dir() else folder
    if folder.is_file():
        folder = folder.parent
    if not props.exists():
        raise TableError(f"{folder}: no properties.jsonl (run RVTconverter.exe with --properties)")
    elems, level_names, notes = read_rvt_properties(props)
    glb = {}
    if use_glb and (folder / "native_graph.glb").exists():
        glb = read_glb_quantities(folder / "native_graph.glb")
    ifc_by_eid: Dict[str, Dict[str, Any]] = {}
    ifc_file = folder / "native_graph.ifc"
    kind = "rvt"
    if use_ifc and ifc_file.exists():
        model = ifcmodel.from_step(ifc_file)
        for r in ifc_rows(model, include_all=True, qualified=qualified):
            if r.get("ElementId") is not None:
                ifc_by_eid[str(r["ElementId"])] = r
        kind = "rvt+ifc"
    else:
        notes.append("native_graph.ifc not found: Category/Family/Type names are not available. "
                     "Run RVTconverter.exe with --properties --ifc for them.")
    rows: List[Dict[str, Any]] = []
    for e in elems:
        eid = e["id"]
        cid = e.get("category_id", "-1")
        has_geo = eid in glb
        if not include_all and cid == "-1" and not has_geo and eid not in ifc_by_eid:
            continue
        base = ifc_by_eid.get(eid)
        if not include_all and not base and not has_geo and _is_type_class(e.get("class")):
            continue
        row: Dict[str, Any] = {}
        if base:
            row.update(base)
            row["ID"] = int(eid) if eid.lstrip("-").isdigit() else eid
        else:
            row["ID"] = int(eid) if eid.lstrip("-").isdigit() else eid
            row["ElementId"] = row["ID"]
            if cid != "-1":
                row["Category Id"] = int(cid) if cid.lstrip("-").isdigit() else cid
                code = ost_code(cid, None)
                if code:
                    row["Category"] = code
                    row["Category Name"] = code[4:]
            if e.get("class"):
                row["Revit Class"] = e["class"]
            if e.get("type_id"):
                row["Type Id"] = int(e["type_id"])
            if e.get("name"):
                row["Name"] = e["name"]
            lv = level_names.get(e.get("level_id", ""))
            if lv:
                row["Level"] = lv
        row["On the standard 3D View"] = bool(has_geo or base)
        if e.get("class") and "Revit Class" not in row:
            row["Revit Class"] = e["class"]
        if e.get("name") and "Name" not in row:
            row["Name"] = e["name"]
        have = set(row)
        unit_note = False
        for label, val, storage in e["params"]:
            if val is None or label in have or label in row:
                continue
            if isinstance(val, str) and val == "":
                continue
            row[label] = val
            if storage == "ParamValueDouble":
                unit_note = True
        if unit_note and not base:
            row["Parameter Units"] = "Revit internal units (lengths in feet)"
        g = glb.get(eid)
        if g:
            row["Mesh Volume"] = _round(g["volume"])
            row["Mesh Area"] = _round(g["area"])
            dims = [g["max"][k] - g["min"][k] for k in range(3)]
            # GLB is Y-up: Revit X = glTF X, Revit Y = glTF Z, Revit Z (up) = glTF Y
            row["BBox X"], row["BBox Y"], row["BBox Z"] = (_round(dims[0]), _round(dims[2]), _round(dims[1]))
            srcs = []
            if "Volume" not in row:
                row["Volume"] = _round(abs(g["volume"]))
                srcs.append("Volume=glb-mesh")
            if "Area" not in row:
                row["Area"] = _round(g["area"])
                srcs.append("Area=glb-mesh")
            if srcs:
                row["Quantity Source"] = "; ".join(filter(None, [row.get("Quantity Source"), "; ".join(srcs)]))
        rows.append(row)
    if glb:
        notes.append("Volume/Area from the GLB are tessellation values in metres; they equal the Revit "
                     "values only for closed, watertight meshes.")
    notes.append("Parameter values come from the saved graph: no formula evaluation, no unit formatting.")
    return _finish(rows, notes, kind, str(folder))


# --------------------------------------------------------------------------- DWG

_DWG_SKIP = {"BLOCK", "ENDBLK", "SEQEND", "VERTEX_PFACE", "VERTEX_PFACE_FACE", "VERTEX_2D", "VERTEX_3D",
             "VERTEX_MESH"}
_DWG_DROP = {"generation", "type_name_source", "kind", "reason", "native_coverage", "coverage_legacy",
             "raw_sha256", "decoded_sources", "decoded_by", "evidence_tier", "owner_origin",
             "layer_handle", "layer_reason", "metadata", "metadata_coverage", "metadata_reason",
             "unknown_fields", "parameters", "type_code", "owner_block_handle", "block_link_reason",
             "annotation", "annotation_coverage", "annotation_reason", "hatch_boundary",
             "hatch_boundary_coverage", "linetype_handle", "dim_style_handle", "status",
             "coordinate_space", "entity_mode"}


_DWG_DROP_PREFIX = ("parameters.", "metadata.", "annotation.", "hatch_boundary", "unknown_fields")


def _jl(v: Any) -> Any:
    if isinstance(v, str):
        try:
            return json.loads(v)
        except ValueError:
            return None
    return v


def _num_or_none(v: Any) -> Optional[float]:
    n = _num(v)
    return n


def _bulge_len(p: Tuple[float, float], q: Tuple[float, float], b: float) -> float:
    d = math.hypot(q[0] - p[0], q[1] - p[1])
    if not b or d == 0:
        return d
    theta = 4 * math.atan(b)
    r = d / (2 * math.sin(theta / 2))
    return abs(r * theta)


def _poly_metrics(r: Dict[str, Any]) -> Tuple[Optional[float], Optional[float], bool]:
    """(length, area, exact) of a polyline row; area only for closed polylines without bulges."""
    pts = _jl(r.get("vertices_json"))
    if not isinstance(pts, list) or len(pts) < 2:
        return None, None, False
    bulges = _jl(r.get("bulges_json")) or []
    closed = str(r.get("closed")).lower() in ("true", "1")
    xy = [(float(p[0]), float(p[1])) for p in pts]
    n = len(xy)
    segs = n if closed else n - 1
    length = 0.0
    for i in range(segs):
        b = float(bulges[i]) if i < len(bulges) and bulges[i] else 0.0
        length += _bulge_len(xy[i], xy[(i + 1) % n], b)
    area = None
    if closed and not any(bulges):
        area = abs(sum(xy[i][0] * xy[(i + 1) % n][1] - xy[(i + 1) % n][0] * xy[i][1] for i in range(n))) / 2
    return length, area, True


def dwg_rows(path: Path, include_all: bool = False) -> Table:
    p = Path(path)
    files = [p]
    if p.is_dir():
        def tables(d: Path) -> List[Path]:
            return [x for x in d.iterdir() if x.is_file() and x.suffix.lower() in (".jsonl", ".csv", ".xlsx")]
        files = tables(p)
        if not files:                    # dwg2excel writes one sub-folder per drawing
            for sub in sorted(d for d in p.iterdir() if d.is_dir()):
                files = tables(sub)
                if files:
                    break
        pref = {".jsonl": 0, ".csv": 1, ".xlsx": 2}
        files.sort(key=lambda x: (pref[x.suffix.lower()], x.name))
        files = files[:1] if files else []
    if not files:
        raise TableError(f"{path}: no CAD Drawing to Excel table (.jsonl/.csv/.xlsx) found")
    raw = read_file(files[0])
    if not raw or "handle" not in raw[0]:
        raise TableError(f"{files[0].name}: not a CAD Drawing to Excel table (no 'handle' column)")
    rows: List[Dict[str, Any]] = []
    for r in raw:
        t = r.get("type_name")
        if not include_all:
            if is_empty(r.get("layer_name")) and is_empty(r.get("owner_block_name")):
                continue
            if t in _DWG_SKIP:
                continue
        row: Dict[str, Any] = {}
        row["ID"] = r["handle"]
        cat = t or (f"UNKNOWN_{r.get('type_code')}" if not is_empty(r.get("type_code")) else "UNKNOWN")
        row["Category"] = cat
        row["Category Name"] = cat
        blk = r.get("block_name") if t == "INSERT" else None
        row["Type Name"] = blk or cat
        row["Type"] = row["Type Name"]
        txt = r.get("text_plain") or r.get("text_raw")
        if not is_empty(txt):
            row["Name"] = txt
        ob = r.get("owner_block_name")
        if not is_empty(ob):
            row["Level"] = str(ob).lstrip("*")
        row["On the standard 3D View"] = (str(ob).lower() == "*model_space")
        if not is_empty(r.get("layer_name")):
            row["Layer"] = r["layer_name"]
        length = area = perim = None
        x, y, z = (_num_or_none(r.get(k)) for k in ("x", "y", "z"))
        if t == "LINE":
            x2, y2, z2 = (_num_or_none(r.get(k)) for k in ("x2", "y2", "z2"))
            if None not in (x, y, z, x2, y2, z2):
                length = math.sqrt((x2 - x) ** 2 + (y2 - y) ** 2 + (z2 - z) ** 2)
        elif t == "CIRCLE" and _num_or_none(r.get("radius")) is not None:
            rad = _num_or_none(r.get("radius"))
            perim = 2 * math.pi * rad
            length = perim
            area = math.pi * rad * rad
        elif t == "ARC" and _num_or_none(r.get("radius")) is not None:
            a0, a1 = _num_or_none(r.get("start_angle_rad")), _num_or_none(r.get("end_angle_rad"))
            if a0 is not None and a1 is not None:
                sweep = (a1 - a0) % (2 * math.pi)
                length = _num_or_none(r.get("radius")) * sweep
        elif t in ("LWPOLYLINE", "POLYLINE", "POLYLINE_2D", "POLYLINE_3D"):
            ln, ar, ok = _poly_metrics(r)
            if ok:
                length, area = ln, ar
                if str(r.get("closed")).lower() in ("true", "1"):
                    perim = ln
        elif t == "HATCH" and _num_or_none(r.get("hatch_area")) is not None:
            area = _num_or_none(r.get("hatch_area"))
        srcs = []
        for col, v in (("Length", length), ("Perimeter", perim), ("Area", area)):
            if v is not None:
                row[col] = _round(v)
                srcs.append(col)
        if srcs:
            row["Quantity Source"] = "geometry"
        row["Coverage"] = r.get("coverage")
        for k, v in r.items():
            if k in _DWG_DROP or k in ("handle", "type_name", "layer_name", "owner_block_name", "coverage") \
                    or k in row or is_empty(v):
                continue
            if k == "text_plain" or k.startswith(_DWG_DROP_PREFIX):
                continue
            row[k] = v
        rows.append(row)
    notes = ["Lengths/areas are in drawing units; arcs/polylines with bulges use exact arc lengths; "
             "areas only for circles, closed polylines without bulges and HATCH with a stored area.",
             "Rows with Coverage other than DECODED are envelope-only records (no geometry)."]
    return _finish(rows, notes, "dwg", str(files[0]))


# --------------------------------------------------------------------------- entry point

def detect_kind(path: Path) -> str:
    p = Path(path)
    if not p.exists():
        raise TableError(f"path not found: {path}")
    if p.is_file():
        if p.name == "properties.jsonl":
            return "rvt"
        if p.suffix.lower() == ".ifc":
            return "ifc-step"
        if p.suffix.lower() in (".jsonl", ".ndjson", ".sqlite", ".sqlite3", ".db", ".xlsx"):
            if ifcmodel.is_ifc_excel(p):
                return "ifc-excel"
        return "dwg"
    if (p / "properties.jsonl").exists():
        return "rvt"
    if any((p / n).exists() for n in ("data.jsonl", "data.sqlite", "drawing.xlsx")):
        return "ifc-excel"
    subs = [d for d in p.iterdir() if d.is_dir() and (d / "data.jsonl").exists()]
    if subs:
        return "ifc-excel"
    ifcs = sorted(p.glob("*.ifc"))
    if ifcs:
        return "ifc-step"
    return "dwg"


def build_table(path: str, kind: Optional[str] = None, include_all: bool = False, qualified: bool = False,
                use_ifc: bool = True, use_glb: bool = True) -> Table:
    p = Path(path)
    k = kind or detect_kind(p)
    if k == "rvt":
        return rvt_rows(p, use_ifc=use_ifc, use_glb=use_glb, include_all=include_all, qualified=qualified)
    if k in ("ifc", "ifc-excel", "ifc-step"):
        if k == "ifc-step" or (k == "ifc" and p.suffix.lower() == ".ifc"):
            src = p if p.is_file() else sorted(p.glob("*.ifc"))[0]
            model = ifcmodel.from_step(src)
            kk = "ifc-step"
        else:
            model = ifcmodel.from_ifc_excel(p)
            kk = "ifc-excel"
        rows = ifc_rows(model, include_all=include_all, qualified=qualified)
        notes = [f"IFC schema {model.schema}" if model.schema else "IFC"]
        notes.append("Units are the IFC project units (normally metres) as stored; no unit conversion.")
        return _finish(rows, notes, kk, str(p))
    if k == "dwg":
        return dwg_rows(p, include_all=include_all)
    raise TableError(f"unknown input kind {k!r}")


# --------------------------------------------------------------------------- writers

def write_csv(t: Table, path: str, delimiter: str = ",") -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=delimiter)
        w.writerow(t.columns)
        for r in t.rows:
            w.writerow([r.get(c, "") if r.get(c) is not None else "" for c in t.columns])


def write_xlsx(t: Table, path: str, sheet: str = "Project_Data") -> None:
    """Sheet name Project_Data is the one the old exports used."""
    from openpyxl import Workbook
    from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
    from openpyxl.utils import get_column_letter
    from .xlsxutil import style_header, autosize

    wb = Workbook(write_only=False)
    ws = wb.active
    ws.title = sheet
    ws.append(t.columns)
    for r in t.rows:
        ws.append([_xl(r.get(c)) for c in t.columns])
    style_header(ws, 1, len(t.columns))
    ws.freeze_panes = "A2"
    if t.rows:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(t.columns))}{len(t.rows) + 1}"
    autosize(ws)
    info = wb.create_sheet("Info")
    info.append(["Source", t.source])
    info.append(["Input kind", t.kind])
    info.append(["Elements", len(t.rows)])
    info.append(["Columns", len(t.columns)])
    for n in t.notes:
        info.append(["Note", n])
    info.column_dimensions["A"].width = 14
    info.column_dimensions["B"].width = 110
    wb.save(path)


def _xl(v: Any) -> Any:
    from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
    if isinstance(v, str):
        v = ILLEGAL_CHARACTERS_RE.sub("", v)
        if len(v) > 32000:
            v = v[:32000]
    return v
