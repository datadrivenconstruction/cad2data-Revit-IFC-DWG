"""Colour a GLB by change status (``ddc diff --glb``).

The GLB of the converters carries the element identity on its nodes (RVT Converter: ``extras.element_id``,
node name ``element_<id>``; other exporters also write ``extras.global_id``). A node is linked to a
diff element the way the DDC Data Viewer links geometry to table rows: by the element key first
(ids, GlobalId), then by a trailing ``:<id>`` / ``_<id>`` of the node name. Nodes below a linked node
inherit its status.

Output: the GLB of version B with every material replaced by a status material
(added green, modified orange, unchanged translucent grey) and, when version A has a GLB too, the
geometry of the removed elements copied in from A in red. Nothing but materials and the appended
nodes/buffer data is changed; geometry, transforms and node names stay as they were.
"""
from __future__ import annotations

import copy
import json
import re
import struct
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .diff import ID_COLUMNS, STATUS_COLORS

_GUID_KEYS = ("global_id", "globalId", "GlobalId", "ifc_guid", "IfcGuid", "guid", "unique_id", "UniqueId")
_ID_KEYS = ("element_id", "elementId", "ElementId", "id", "step_id", "handle")
GHOST_ALPHA = 0.25
IDENT = [1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0]


class GlbError(Exception):
    pass


# ------------------------------------------------------------------------------------------- GLB io

def read_glb(path: Path) -> Tuple[Dict[str, Any], bytes]:
    data = Path(path).read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise GlbError(f"{Path(path).name}: not a GLB file")
    total = struct.unpack("<I", data[8:12])[0]
    pos, gltf, blob = 12, None, b""
    while pos + 8 <= min(len(data), total):
        ln, kind = struct.unpack("<II", data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + ln]
        if kind == 0x4E4F534A:
            gltf = json.loads(chunk.decode("utf-8"))
        elif kind == 0x004E4942 and not blob:
            blob = bytes(chunk)
        pos += 8 + ln + (-ln % 4)
    if gltf is None:
        raise GlbError(f"{Path(path).name}: no JSON chunk")
    for b in gltf.get("buffers", []):
        if "uri" in b:
            raise GlbError(f"{Path(path).name}: external or data-URI buffers are not supported")
    return gltf, blob


def write_glb(path: Path, gltf: Dict[str, Any], blob: bytes) -> None:
    js = json.dumps(gltf, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    js += b" " * (-len(js) % 4)
    blob = blob + b"\0" * (-len(blob) % 4)
    total = 12 + 8 + len(js) + (8 + len(blob) if blob else 0)
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        if blob:
            f.write(struct.pack("<II", len(blob), 0x004E4942) + blob)


# ------------------------------------------------------------------------------------------- matrices

def _mul(a: List[float], b: List[float]) -> List[float]:
    """Column-major 4x4: a * b."""
    return [sum(a[k * 4 + r] * b[c * 4 + k] for k in range(4)) for c in range(4) for r in range(4)]


def _local(node: Dict[str, Any]) -> List[float]:
    if "matrix" in node:
        return [float(x) for x in node["matrix"]]
    t = node.get("translation", [0, 0, 0])
    q = node.get("rotation", [0, 0, 0, 1])
    s = node.get("scale", [1, 1, 1])
    x, y, z, w = q
    r = [1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w), 0,
         2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w), 0,
         2 * (x * z + y * w), 2 * (y * z - x * w), 1 - 2 * (x * x + y * y), 0, 0, 0, 0, 1]
    for c in range(3):
        for k in range(3):
            r[c * 4 + k] *= s[c]
    r[12], r[13], r[14] = t
    return r


# ------------------------------------------------------------------------------------------- linking

def _tail(s: str) -> Optional[str]:
    m = re.search(r"(?:[:_#\[ ])(\d{1,20})\]?$", s.strip())
    return m.group(1) if m else None


def build_lookup(result: Dict[str, Any], side: str) -> Dict[str, str]:
    """Status by id token. side "b": the ids of version B (added, modified, unchanged);
    side "a": the ids of version A (removed, modified, unchanged)."""
    out: Dict[str, str] = {}
    for e in result["elements"]:
        if (side == "b") == (e["status"] == "removed") or (side == "a" and e["status"] == "added"):
            continue
        for col in ID_COLUMNS:
            v = e[side].get(col)
            if v:
                out.setdefault(str(v), e["status"])
    return out


def node_tokens(node: Dict[str, Any]) -> List[str]:
    ex = node.get("extras") or {}
    toks: List[str] = []
    for k in _GUID_KEYS + _ID_KEYS:
        v = ex.get(k)
        if isinstance(v, (str, int)) and not isinstance(v, bool) and str(v) != "":
            toks.append(str(v))
    name = node.get("name")
    if isinstance(name, str) and name:
        t = _tail(name)
        if t:
            toks.append(t)
        toks.append(name)
    return toks


def _lookup(node: Dict[str, Any], table: Dict[str, str]) -> Optional[str]:
    for t in node_tokens(node):
        if t in table:
            return table[t]
    return None


# ------------------------------------------------------------------------------------------- colouring

def status_material(status: str) -> Dict[str, Any]:
    r, g, b = STATUS_COLORS[status]
    ghost = status == "unchanged"
    m: Dict[str, Any] = {
        "name": f"ddc-diff {status}",
        "pbrMetallicRoughness": {"baseColorFactor": [round(r / 255, 4), round(g / 255, 4), round(b / 255, 4),
                                                     GHOST_ALPHA if ghost else 1.0],
                                 "metallicFactor": 0.0, "roughnessFactor": 0.9},
        "doubleSided": True, "extras": {"ddc_diff_status": status},
    }
    if ghost:
        m["alphaMode"] = "BLEND"
    return m


def colorize(glb_b: Optional[str], glb_a: Optional[str], result: Dict[str, Any], out: str,
             unchanged: str = "ghost") -> Dict[str, Any]:
    """Write the status-coloured GLB to ``out``. ``unchanged``: ghost (translucent grey), keep (opaque grey), hide."""
    if unchanged not in ("ghost", "keep", "hide"):
        raise GlbError("unchanged must be ghost, keep or hide")
    base_path = glb_b or glb_a
    if not base_path:
        raise GlbError("no GLB to colour")
    gltf, blob = read_glb(Path(base_path))
    base_is_b = bool(glb_b)
    cur = build_lookup(result, "b" if base_is_b else "a")
    gone = {k: v for k, v in build_lookup(result, "a").items() if v == "removed"}
    stats = {"base": Path(base_path).name, "base_version": "B" if base_is_b else "A",
             "linked": 0, "unlinked": 0, "added": 0, "modified": 0, "unchanged": 0, "removed": 0,
             "removed_missing_geometry": 0}

    # materials: index by status; unlinked nodes look like unchanged ones
    mats: List[Dict[str, Any]] = []
    mat_idx: Dict[str, int] = {}

    def mat(status: str) -> int:
        st = "unchanged" if status == "unlinked" else status
        if st == "unchanged" and unchanged == "keep":
            st = "unchanged_opaque"
        if st not in mat_idx:
            m = status_material("unchanged" if st == "unchanged_opaque" else st)
            if st == "unchanged_opaque":
                m.pop("alphaMode", None)
                m["pbrMetallicRoughness"]["baseColorFactor"][3] = 1.0
            mat_idx[st] = len(mats)
            mats.append(m)
        return mat_idx[st]

    old_meshes = gltf.get("meshes", [])
    new_meshes: List[Dict[str, Any]] = []
    mesh_cache: Dict[Tuple[int, int], int] = {}

    def recolored(mesh_i: int, mi: int) -> int:
        key = (mesh_i, mi)
        if key not in mesh_cache:
            m = copy.deepcopy(old_meshes[mesh_i])
            for p in m.get("primitives", []):
                p["material"] = mi
            mesh_cache[key] = len(new_meshes)
            new_meshes.append(m)
        return mesh_cache[key]

    nodes = gltf.get("nodes", [])
    scenes = gltf.get("scenes", [])
    roots = scenes[gltf.get("scene", 0)].get("nodes", []) if scenes else list(range(len(nodes)))
    seen = set()

    def walk(i: int, inherited: Optional[str], hide_list: List[int]) -> None:
        if i in seen:
            return
        seen.add(i)
        n = nodes[i]
        st = _lookup(n, cur)
        status = st or inherited
        if "mesh" in n:
            if status is None:
                stats["unlinked"] += 1
                use = "unlinked"
            else:
                stats["linked"] += 1
                stats[status if status in stats else "unchanged"] += 1
                use = status
            if use in ("unchanged", "unlinked") and unchanged == "hide":
                del n["mesh"]
            else:
                n["mesh"] = recolored(n["mesh"], mat(use))
                n.setdefault("extras", {})["ddc_diff_status"] = "unchanged" if use == "unlinked" else use
        for c in n.get("children", []):
            walk(c, status, hide_list)

    for r in roots:
        walk(r, None, [])

    # removed elements: copy their geometry from version A into the version-B file
    if base_is_b and glb_a:
        try:
            ga, ba = read_glb(Path(glb_a))
        except GlbError as e:
            raise GlbError(f"GLB of version A: {e}")
        ok = _append_removed(gltf, blob, ga, ba, gone, new_meshes, mat("removed"), stats)
        blob = ok
    elif base_is_b and any(e["status"] == "removed" for e in result["elements"]):
        stats["removed_missing_geometry"] = sum(1 for e in result["elements"] if e["status"] == "removed")

    gltf["meshes"] = new_meshes
    gltf["materials"] = mats
    for k in ("textures", "images", "samplers"):
        gltf.pop(k, None)
    gltf.setdefault("asset", {"version": "2.0"})
    gltf["asset"].setdefault("extras", {})["ddc_diff"] = {
        "tool": "ddc diff", "legend": {s: "#%02X%02X%02X" % STATUS_COLORS[s] for s in STATUS_COLORS},
        "summary": {k: result["summary"][k] for k in ("added", "removed", "modified", "unchanged")}}
    gltf["asset"]["generator"] = (gltf["asset"].get("generator", "") + " + ddc diff").strip()
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    write_glb(Path(out), gltf, blob)
    return stats


def _append_removed(gltf: Dict[str, Any], blob: bytes, ga: Dict[str, Any], ba: bytes, gone: Dict[str, str],
                    new_meshes: List[Dict[str, Any]], mat_i: int, stats: Dict[str, Any]) -> bytes:
    """Copy the meshes of removed elements of A into gltf (buffer 0)."""
    a_nodes = ga.get("nodes", [])
    scenes = ga.get("scenes", [])
    roots = scenes[ga.get("scene", 0)].get("nodes", []) if scenes else list(range(len(a_nodes)))
    picks: List[Tuple[int, List[float], str]] = []   # (node index, world matrix, token)
    seen = set()

    def walk(i: int, parent: List[float], inherited: bool) -> None:
        if i in seen:
            return
        seen.add(i)
        n = a_nodes[i]
        world = _mul(parent, _local(n))
        hit = _lookup(n, gone) is not None
        take = hit or inherited
        if "mesh" in n and take:
            picks.append((i, world, n.get("name") or f"node{i}"))
        for c in n.get("children", []):
            walk(c, world, take)

    for r in roots:
        walk(r, IDENT, False)
    if not picks:
        return blob
    pad = b"\0" * (-len(blob) % 4)
    blob = blob + pad
    shift = len(blob)
    nbv, nacc = len(gltf.setdefault("bufferViews", [])), len(gltf.setdefault("accessors", []))
    for bv in ga.get("bufferViews", []):
        b = dict(bv)
        b["buffer"] = 0
        b["byteOffset"] = bv.get("byteOffset", 0) + shift
        gltf["bufferViews"].append(b)
    for acc in ga.get("accessors", []):
        a = copy.deepcopy(acc)
        if "bufferView" in a:
            a["bufferView"] += nbv
        if "sparse" in a:
            for part in ("indices", "values"):
                a["sparse"][part]["bufferView"] += nbv
        gltf["accessors"].append(a)
    blob = blob + ba
    gltf["buffers"] = [{"byteLength": len(blob)}]
    mesh_map: Dict[int, int] = {}
    root_nodes = gltf.setdefault("scenes", [{"nodes": []}])[gltf.get("scene", 0)].setdefault("nodes", [])
    for i, world, name in picks:
        src = a_nodes[i]["mesh"]
        if src not in mesh_map:
            m = copy.deepcopy(ga["meshes"][src])
            for p in m.get("primitives", []):
                p["material"] = mat_i
                p["attributes"] = {k: v + nacc for k, v in p.get("attributes", {}).items()}
                if "indices" in p:
                    p["indices"] += nacc
                for t in p.get("targets", []):
                    for k in list(t):
                        t[k] += nacc
            mesh_map[src] = len(new_meshes)
            new_meshes.append(m)
        node = {"name": name, "mesh": mesh_map[src], "matrix": world,
                "extras": dict(a_nodes[i].get("extras") or {}, ddc_diff_status="removed", ddc_diff_from="A")}
        gltf.setdefault("nodes", []).append(node)
        root_nodes.append(len(gltf["nodes"]) - 1)
        stats["removed"] += 1
    return blob
