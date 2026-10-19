"""Tiny GLB writer for tests: cubes laid out like native_graph.glb of the RVT Converter
(flat nodes, ``extras.element_id``, a matrix per node, Revit feet to metres, Z up to Y up)."""
import json
import struct
from pathlib import Path

QUADS = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def write_cubes(path, cubes, scale=0.3048, extras_key="element_id", name_prefix="element_"):
    """cubes: list of (element id, edge in feet, x offset in feet)."""
    pos_blob, idx_blob = b"", b""
    views, accessors, meshes, nodes = [], [], [], []
    for n, (eid, edge, dx) in enumerate(cubes):
        v = [(x, y, z) for x in (0, edge) for y in (0, edge) for z in (0, edge)]
        idx = []
        for a, b, c, d in QUADS:
            idx += [a, b, c, a, c, d]
        p = b"".join(struct.pack("<3f", *q) for q in v)
        i = b"".join(struct.pack("<H", k) for k in idx)
        i += b"\x00" * (-len(i) % 4)
        views.append({"buffer": 0, "byteOffset": len(pos_blob) + 0, "byteLength": len(p), "_p": True})
        pos_blob += p
        views.append({"buffer": 0, "byteOffset": -1 - len(idx_blob), "byteLength": len(i)})
        idx_blob += i
        accessors.append({"bufferView": 2 * n, "componentType": 5126, "count": 8, "type": "VEC3"})
        accessors.append({"bufferView": 2 * n + 1, "componentType": 5123, "count": len(idx), "type": "SCALAR"})
        meshes.append({"primitives": [{"attributes": {"POSITION": 2 * n}, "indices": 2 * n + 1, "material": 0, "mode": 4}]})
        nodes.append({"name": f"{name_prefix}{eid}", "mesh": n, "extras": {extras_key: eid},
                      "matrix": [scale, 0, 0, 0, 0, 0, -scale, 0, 0, scale, 0, 0, dx * scale, 0, 0, 1]})
    for v in views:                       # all positions first, then all indices
        if v.pop("_p", False):
            continue
        v["byteOffset"] = len(pos_blob) + (-1 - v["byteOffset"])
    blob = pos_blob + idx_blob
    g = {"asset": {"version": "2.0", "generator": "test"}, "buffers": [{"byteLength": len(blob)}],
         "bufferViews": views, "accessors": accessors, "meshes": meshes, "nodes": nodes,
         "materials": [{"name": "orig", "pbrMetallicRoughness": {"baseColorFactor": [0.5, 0.5, 0.5, 1]}}],
         "scenes": [{"nodes": list(range(len(nodes)))}], "scene": 0}
    js = json.dumps(g).encode()
    js += b" " * (-len(js) % 4)
    total = 12 + 8 + len(js) + 8 + len(blob)
    Path(path).write_bytes(b"glTF" + struct.pack("<II", 2, total) + struct.pack("<I", len(js)) + b"JSON" + js
                           + struct.pack("<I", len(blob)) + b"BIN\x00" + blob)


def write_boxes(path, boxes, extras_key="element_id", name_prefix="element_"):
    """boxes: list of (element id, (x, y, z) corner, (sx, sy, sz) size) in metres, glTF axes (Y up)."""
    pos_blob, idx_blob = b"", b""
    views, accessors, meshes, nodes = [], [], [], []
    idx = []
    for a, b, c, d in QUADS:
        idx += [a, b, c, a, c, d]
    i_bytes = b"".join(struct.pack("<H", k) for k in idx)
    i_bytes += b"\x00" * (-len(i_bytes) % 4)
    # one shared unit-cube mesh, every box is a node with a scale + translation matrix
    v = [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
    p = b"".join(struct.pack("<3f", *q) for q in v)
    views = [{"buffer": 0, "byteOffset": 0, "byteLength": len(p)},
             {"buffer": 0, "byteOffset": len(p), "byteLength": len(i_bytes)}]
    accessors = [{"bufferView": 0, "componentType": 5126, "count": 8, "type": "VEC3"},
                 {"bufferView": 1, "componentType": 5123, "count": len(idx), "type": "SCALAR"}]
    meshes = [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1, "material": 0, "mode": 4}]}]
    for eid, (x, y, z), (sx, sy, sz) in boxes:
        nodes.append({"name": f"{name_prefix}{eid}", "mesh": 0, "extras": {extras_key: eid},
                      "matrix": [sx, 0, 0, 0, 0, sy, 0, 0, 0, 0, sz, 0, x, y, z, 1]})
    blob = p + i_bytes
    g = {"asset": {"version": "2.0", "generator": "test"}, "buffers": [{"byteLength": len(blob)}],
         "bufferViews": views, "accessors": accessors, "meshes": meshes, "nodes": nodes,
         "materials": [{"name": "orig", "pbrMetallicRoughness": {"baseColorFactor": [0.6, 0.6, 0.65, 1]}}],
         "scenes": [{"nodes": list(range(len(nodes)))}], "scene": 0}
    js = json.dumps(g).encode()
    js += b" " * (-len(js) % 4)
    total = 12 + 8 + len(js) + 8 + len(blob)
    Path(path).write_bytes(b"glTF" + struct.pack("<II", 2, total) + struct.pack("<I", len(js)) + b"JSON" + js
                           + struct.pack("<I", len(blob)) + b"BIN\x00" + blob)
