"""Make "version 2" of a real RVT Converter output folder for the ddc diff demo (README screenshots).

    RVTconverter.exe Sample_R24.rvt -o R24 --properties --ifc
    python make_diff_demo.py R24 R24_v2

Sample_R24.rvt is the DDC sample of this repository (DDC_Update_Revit_from_Excel/Samples). The copy is
edited the way a designer edits a model between two issues: wall 2567 gets taller (stored height
and a 25 % taller mesh), wall 2646 is deleted, a new wall 9100 appears (a copy of wall 2606 moved by 3 m)
properties.jsonl and native_graph.glb are rewritten; native_graph.ifc is copied unchanged.
"""
import json
import shutil
import struct
import sys
from pathlib import Path


def set_first_number(obj, new):
    if isinstance(obj, dict):
        if "number" in obj:
            obj["number"] = new
            return True
        return any(set_first_number(v, new) for v in obj.values())
    if isinstance(obj, list):
        return any(set_first_number(v, new) for v in obj)
    return False


def edit_glb(src, dst, drop, scale_y, clone_from, clone_id, dx):
    d = Path(src).read_bytes()
    jl = struct.unpack("<I", d[12:16])[0]
    g = json.loads(d[20:20 + jl])
    off = 20 + jl
    bl = struct.unpack("<I", d[off:off + 4])[0]
    blob = d[off + 8: off + 8 + bl]
    nodes = []
    for n in g["nodes"]:
        eid = n["extras"]["element_id"]
        if eid == drop:
            continue
        if eid in scale_y:                       # glTF is Y-up, the matrix is column-major
            m = n["matrix"]
            m[9] *= scale_y[eid]
        nodes.append(n)
        if eid == clone_from:
            c = json.loads(json.dumps(n))
            c["extras"]["element_id"] = clone_id
            c["name"] = f"element_{clone_id}"
            c["matrix"][12] += dx
            nodes.append(c)
    g["nodes"] = nodes
    g["scenes"][0]["nodes"] = list(range(len(nodes)))
    js = json.dumps(g, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    total = 12 + 8 + len(js) + 8 + len(blob)
    Path(dst).write_bytes(b"glTF" + struct.pack("<II", 2, total) + struct.pack("<I", len(js)) + b"JSON" + js
                          + struct.pack("<I", len(blob)) + b"BIN\x00" + blob)


def main(src, dst):
    src, dst = Path(src), Path(dst)
    dst.mkdir(parents=True)
    shutil.copy(src / "native_graph.ifc", dst / "native_graph.ifc")
    out = []
    for ln in (src / "properties.jsonl").read_text(encoding="utf-8").splitlines():
        d = json.loads(ln)
        owner = str(d.get("owner"))
        if owner == "2646":
            continue
        if owner == "2567" and d.get("row") == "parameter" and d.get("builtin_label") == "Unconnected Height":
            set_first_number(d["fields"], 17.0)
        out.append(ln if owner != "2567" or d.get("builtin_label") != "Unconnected Height" else json.dumps(d))
        if owner == "2606":
            out.append(json.dumps(json.loads(json.dumps(d).replace('"2606"', '"9100"'))))
    (dst / "properties.jsonl").write_text("\n".join(out) + "\n", encoding="utf-8")
    edit_glb(src / "native_graph.glb", dst / "native_graph.glb", drop=2646, scale_y={2567: 1.25},
             clone_from=2606, clone_id=9100, dx=3.0)


if __name__ == "__main__":
    main(*sys.argv[1:3])
