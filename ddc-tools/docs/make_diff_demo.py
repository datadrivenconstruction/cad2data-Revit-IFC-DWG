"""Make two versions of a small synthetic RVT-style output for the ddc diff demo (README picture).

    python make_diff_demo.py DEMO_A DEMO_B

Base: tests/data/rvt_converted/properties.jsonl (synthetic, RVT Converter layout). Its wall 1001 is cloned
into eight walls that form a room with a partition; a box per wall is written as native_graph.glb (the
converter's node layout: extras.element_id, one node per element). Version B: wall 1004 is taller (stored
height and mesh), wall 1006 is deleted, wall 1009 is new (and lower). Not a model of anything real.
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tests"))
from _glbutil import write_boxes  # noqa: E402

# id: (x, z, length, along) in metres, wall thickness 0.2, height 3 (glTF Y up)
WALLS = {1001: (0, 0, 8, "x"), 1002: (0, 6, 8, "x"), 1003: (0, 0, 6, "z"), 1004: (8, 0, 6, "z"),
         1005: (3, 0, 6, "z"), 1006: (3, 3, 3, "x"), 1007: (0, 3, 3, "x"), 1008: (5, 4.5, 3, "x")}


def set_first_number(obj, new):
    if isinstance(obj, dict):
        if "number" in obj:
            obj["number"] = new
            return True
        return any(set_first_number(v, new) for v in obj.values())
    if isinstance(obj, list):
        return any(set_first_number(v, new) for v in obj)
    return False


def box(eid, spec, height=3.0):
    x, z, ln, along = spec
    return (eid, (x, 0, z), (ln, height, 0.2) if along == "x" else (0.2, height, ln))


def write(dst, ids, heights=None):
    heights = heights or {}
    dst.mkdir(parents=True)
    base = [json.loads(l) for l in (HERE.parent / "tests/data/rvt_converted/properties.jsonl").read_text(encoding="utf-8").splitlines()]
    out = [d for d in base if str(d.get("owner")) != "1001" and str(d.get("owner")) != "1002"]
    wall = [d for d in base if str(d.get("owner")) == "1001"]
    for i in ids:
        for d in wall:
            e = json.loads(json.dumps(d).replace('"1001"', f'"{i}"'))
            if i in heights and e.get("row") == "parameter" and e.get("builtin_label") == "Unconnected Height":
                set_first_number(e["fields"], heights[i] / 0.3048)
            out.append(e)
    (dst / "properties.jsonl").write_text("\n".join(json.dumps(d) for d in out) + "\n", encoding="utf-8")
    boxes = [box(i, WALLS[i], heights.get(i, 3.0)) for i in ids]
    write_boxes(dst / "native_graph.glb", boxes)


def main(a, b):
    ids = sorted(WALLS)
    write(Path(a), ids)
    new = [i for i in ids if i != 1006] + [1009]
    WALLS[1009] = (5, 1.5, 3, "x")
    write(Path(b), new, heights={1004: 4.5, 1009: 2.4})


if __name__ == "__main__":
    main(*sys.argv[1:3])
