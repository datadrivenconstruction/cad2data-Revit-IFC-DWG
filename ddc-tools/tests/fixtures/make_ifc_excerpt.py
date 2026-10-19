"""Cut a small excerpt out of a real DDC IFC to Excel output folder (data.jsonl, data.sqlite,
drawing.xlsx) while keeping the records byte-for-byte as the converter wrote them.

    python make_ifc_excerpt.py <output folder of IFC to Excel> <target folder>

The committed excerpt comes from Sample_Projects/Ifc2x3_Duplex_Architecture.ifc of this repository,
converted with DDC IFC to Excel 0.3.1-preview (release v2026.10.0).
"""
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook, load_workbook

KEEP = {  # IFC class -> how many objects to keep
    "IfcProject": 1, "IfcSite": 1, "IfcBuilding": 1, "IfcBuildingStorey": 4, "IfcWallStandardCase": 6,
    "IfcWall": 1, "IfcDoor": 4, "IfcWindow": 3, "IfcSpace": 3, "IfcSlab": 2, "IfcRoof": 1,
    "IfcFurnishingElement": 3, "IfcBeam": 1,
}
TABLES = ["Objects", "Properties", "Quantities", "SpatialLinks", "TypeLinks", "Relations"]


def main(src, dst):
    src, dst = Path(src), Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(f"file:{(src / 'data.sqlite').as_posix()}?mode=ro", uri=True)
    recs = defaultdict(list)
    for t, o, js in con.execute("select table_name, ordinal, record_json from records order by table_name, ordinal"):
        if t in TABLES:
            recs[t].append((o, js, json.loads(js)))
    objs = {r["ID"]: r for _, _, r in recs["Objects"]}
    keep, left = set(), dict(KEEP)
    for _, _, r in recs["Objects"]:
        if not r["IsType"] and left.get(r["Category"], 0) > 0:
            keep.add(r["ID"])
            left[r["Category"]] -= 1
    # openings that cut the kept walls (the host decides the storey)
    n_open = 0
    for _, _, r in recs["Relations"]:
        a = r["attributes"]
        if r["ifc_class"] == "IfcRelVoidsElement" and n_open < 3:
            host, op = str((a.get("RelatingBuildingElement") or {}).get("ref")), str((a.get("RelatedOpeningElement") or {}).get("ref"))
            if host in keep and op in objs:
                keep.add(op)
                n_open += 1
    # pull in what the kept objects point to: types and every storey / space parent
    for _, _, l in recs["TypeLinks"]:
        if l["owner_step_id"] in keep:
            keep.add(l["type_step_id"])
    sel = {t: [] for t in TABLES}
    for t in TABLES:
        for o, js, r in recs[t]:
            if t == "Objects":
                ok = r["ID"] in keep
            elif t in ("Properties", "Quantities"):
                ok = r["owner_step_id"] in keep
            elif t == "SpatialLinks":
                ok = r["child_step_id"] in keep and r["parent_step_id"] in keep
            elif t == "TypeLinks":
                ok = r["owner_step_id"] in keep and r["type_step_id"] in keep
            else:  # Relations: voids between kept objects only
                a = r["attributes"]
                ok = (r["ifc_class"] == "IfcRelVoidsElement"
                      and str((a.get("RelatingBuildingElement") or {}).get("ref")) in keep
                      and str((a.get("RelatedOpeningElement") or {}).get("ref")) in keep)
            if ok:
                sel[t].append((o, js, r))
    with open(dst / "data.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for t in TABLES:
            for o, js, r in sel[t]:
                f.write(json.dumps({"table": t, "ordinal": o, "record": r}, ensure_ascii=False, separators=(",", ":")) + "\n")
    db = dst / "data.sqlite"
    if db.exists():
        db.unlink()
    out = sqlite3.connect(db)
    out.execute("CREATE TABLE records(table_name TEXT NOT NULL, ordinal INTEGER NOT NULL, record_json TEXT NOT NULL, "
                "PRIMARY KEY(table_name,ordinal))")
    out.executemany("insert into records values (?,?,?)", [(t, o, js) for t in TABLES for o, js, _ in sel[t]])
    out.commit()
    out.close()
    # xlsx: same rows, copied from the converter's own sheets
    wb_in = load_workbook(src / "drawing.xlsx", read_only=True)
    wb = Workbook()
    wb.remove(wb.active)
    for t in TABLES:
        ws_in = wb_in[t]
        it = ws_in.iter_rows(values_only=True)
        header = next(it)
        ws = wb.create_sheet(t)
        ws.append(list(header))
        want = {(t, o) for o, _, _ in sel[t]}
        # sheets carry the same row order as the table, so zip by position
        for (o, _, _), row in zip(recs[t], it):
            if (t, o) in want:
                ws.append(list(row))
    wb.save(dst / "drawing.xlsx")
    print({t: len(v) for t, v in sel.items()})


if __name__ == "__main__":
    main(*sys.argv[1:3])
