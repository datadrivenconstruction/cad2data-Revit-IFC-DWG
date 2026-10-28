"""Minimal GLB reader/writer (numpy only)."""
from __future__ import annotations
import json
import struct
from dataclasses import dataclass
import numpy as np

_CT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}
_NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


@dataclass
class Mesh:
    verts: np.ndarray  # (N,3) world space, metres, Y-up (as in the GLB scene)
    tris: np.ndarray   # (M,3) int

    def bbox(self):
        return self.verts.min(0), self.verts.max(0)

    def volume(self) -> float:
        """Absolute signed volume (exact for closed meshes)."""
        if not len(self.tris):
            return 0.0
        a, b, c = (self.verts[self.tris[:, i]].astype(np.float64) for i in range(3))
        return abs(float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum()) / 6.0)


def read_glb(path):
    d = open(path, "rb").read()
    if d[:4] != b"glTF":
        raise ValueError("not a GLB: %s" % path)
    off, j, binc = 12, None, b""
    while off < len(d):
        ln, ty = struct.unpack("<II", d[off:off + 8])
        body = d[off + 8:off + 8 + ln]
        if ty == 0x4E4F534A:
            j = json.loads(body)
        elif ty == 0x004E4942:
            binc = body
        off += 8 + ln
    return j, binc


def _acc(j, binc, i):
    a = j["accessors"][i]
    bv = j["bufferViews"][a["bufferView"]]
    dt, nc = _CT[a["componentType"]], _NC[a["type"]]
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride")
    isz = np.dtype(dt).itemsize * nc
    if stride and stride != isz:
        raw = np.frombuffer(binc, np.uint8, count=stride * a["count"], offset=base).reshape(a["count"], stride)
        arr = np.ascontiguousarray(raw[:, :isz]).view(dt)
    else:
        arr = np.frombuffer(binc, dt, count=a["count"] * nc, offset=base)
    return arr.reshape(a["count"], nc) if nc > 1 else arr


def _local(n):
    if "matrix" in n:
        return np.array(n["matrix"], np.float64).reshape(4, 4).T
    m = np.eye(4)
    if "scale" in n:
        m = np.diag(list(n["scale"]) + [1.0]) @ m
    if "rotation" in n:
        x, y, z, w = n["rotation"]
        r = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        rm = np.eye(4)
        rm[:3, :3] = r
        m = rm @ m
    if "translation" in n:
        t = np.eye(4)
        t[:3, 3] = n["translation"]
        m = t @ m
    return m


def element_meshes(path) -> dict:
    """element_id -> world-space Mesh (all primitives of the element merged)."""
    j, binc = read_glb(path)
    out: dict = {}
    nodes = j.get("nodes", [])

    def walk(i, parent):
        n = nodes[i]
        m = parent @ _local(n)
        if "mesh" in n:
            eid = (n.get("extras") or {}).get("element_id")
            if eid is None:
                tail = n.get("name", "").split("_")[-1]
                eid = int(tail) if tail.isdigit() else None
            if eid is not None:
                for p in j["meshes"][n["mesh"]]["primitives"]:
                    if p.get("mode", 4) != 4 or "indices" not in p:
                        continue
                    v = _acc(j, binc, p["attributes"]["POSITION"]).astype(np.float64)
                    w = v @ m[:3, :3].T + m[:3, 3]
                    out.setdefault(int(eid), []).append(
                        (w, _acc(j, binc, p["indices"]).reshape(-1, 3).astype(np.int64)))
        for c in n.get("children", []):
            walk(c, m)

    for r in j["scenes"][j.get("scene", 0)]["nodes"]:
        walk(r, np.eye(4))
    res = {}
    for eid, parts in out.items():
        vs, ts, o = [], [], 0
        for w, t in parts:
            vs.append(w)
            ts.append(t + o)
            o += len(w)
        res[eid] = Mesh(np.vstack(vs), np.vstack(ts))
    return res


def write_colored_glb(path, items):
    """items: list of (name, Mesh, (r,g,b,a)); one node per item."""
    chunks, views, accs, meshes, nodes, mats, matidx = [], [], [], [], [], [], {}
    off = 0

    def add(buf, target):
        nonlocal off
        pad = (-off) % 4
        if pad:
            chunks.append(b"\0" * pad)
            off += pad
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(buf), "target": target})
        chunks.append(buf)
        off += len(buf)
        return len(views) - 1

    for name, mesh, col in items:
        if not len(mesh.tris):
            continue
        key = tuple(col)
        if key not in matidx:
            matidx[key] = len(mats)
            mats.append({"pbrMetallicRoughness": {"baseColorFactor": list(col), "metallicFactor": 0.0,
                                                  "roughnessFactor": 0.9},
                         "alphaMode": "BLEND" if col[3] < 1 else "OPAQUE", "doubleSided": True})
        v = mesh.verts.astype("<f4")
        i = mesh.tris.astype("<u4").ravel()
        va = len(accs)
        accs.append({"bufferView": add(v.tobytes(), 34962), "componentType": 5126, "count": len(v),
                     "type": "VEC3", "min": v.min(0).tolist(), "max": v.max(0).tolist()})
        accs.append({"bufferView": add(i.tobytes(), 34963), "componentType": 5125, "count": len(i),
                     "type": "SCALAR"})
        meshes.append({"primitives": [{"attributes": {"POSITION": va}, "indices": va + 1,
                                       "material": matidx[key]}]})
        nodes.append({"name": name, "mesh": len(meshes) - 1})
    js = {"asset": {"version": "2.0", "generator": "ddc-qa"}, "scene": 0,
          "scenes": [{"nodes": list(range(len(nodes)))}], "nodes": nodes, "meshes": meshes,
          "materials": mats, "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": off}]}
    jb = json.dumps(js, separators=(",", ":")).encode()
    jb += b" " * ((-len(jb)) % 4)
    bb = b"".join(chunks)
    bb += b"\0" * ((-len(bb)) % 4)
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(jb) + 8 + len(bb)))
        f.write(struct.pack("<II", len(jb), 0x4E4F534A))
        f.write(jb)
        f.write(struct.pack("<II", len(bb), 0x004E4942))
        f.write(bb)
