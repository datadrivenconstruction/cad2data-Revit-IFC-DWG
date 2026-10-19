"""Generate a tiny synthetic export (xlsx, csv, jsonl, sqlite) with deliberate defects.

Not a real model: the values are invented for demos and tests.
    python make_sample.py data/sample_export
"""
import csv
import json
import sqlite3
import sys
from pathlib import Path

HEADER = ["ElementId", "GlobalId", "Category", "Type Name", "Level", "Mark", "Fire Rating",
          "Length", "Width", "Area", "Volume"]


def rows():
    out = []
    n = 1000

    def add(cat, typ, lvl, mark, fire, length, width, area, volume):
        nonlocal n
        n += 1
        out.append([str(n), f"3Xk{n:05d}AAAAAAAAAAAAAA", cat, typ, lvl, mark, fire, length, width, area, volume])

    for lvl, k in (("Level 1", 0), ("Level 2", 1)):
        add("Walls", "Basic Wall: Generic - 200mm", lvl, f"W-{1 + k * 3:03d}", "EI 60", 5.0, 0.2, 14.0, 2.8)
        add("Walls", "Basic Wall: Generic - 200mm", lvl, f"W-{2 + k * 3:03d}", "EI 60", 3.5, 0.2, 9.8, 1.96)
        add("Walls", "Basic Wall: Exterior - 300mm", lvl, f"W-{3 + k * 3:03d}", None, 8.0, 0.3, 22.4, 6.72)
        add("Doors", "Single-Flush: 0915 x 2134mm", lvl, f"D-{1 + k:03d}", "EI 30", None, 0.915, 1.95, None)
        add("Windows", "Fixed: 1200 x 1500mm", lvl, f"WIN-{1 + k:03d}", None, None, 1.2, 1.8, None)
        add("Floors", "Floor: Concrete 250mm", lvl, None, None, None, 0.25, 48.0, 12.0)
    # defects
    add("Walls", "Basic Wall: Generic - 200mm", "Level 2", "W-001", "EI 60", 4.0, 0.2, 11.2, 2.24)   # duplicate mark
    add("Walls", "Basic Wall: Generic - 200mm", "Level 1", "wall7", "EI 60", 2.0, 0.2, 5.6, 0)       # bad mark, zero volume
    add("Walls", "Basic Wall: Partition - 100mm", None, "W-009", "EI 30", 3.0, 1.5, 8.4, 0.84)       # no level, width out of range
    add("Columns", "Concrete-Rectangular: 300 x 300", "Level 1", "C-001", "R 90", 3.0, None, None, 0.27)
    add("Columns", "Concrete-Rectangular: 300 x 300", "Level 2", "C-002", "R 90", 3.0, None, None, "n/a")
    add("Generic Models", "Placeholder", "Level 1", None, None, None, None, None, None)
    return out


def write_all(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    data = rows()
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Elements"
    ws.append(HEADER)
    for r in data:
        ws.append(r)
    wb.save(folder / "sample_model.xlsx")
    with open(folder / "sample_model.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows([["" if v is None else v for v in r] for r in data])
    with open(folder / "sample_model.jsonl", "w", encoding="utf-8") as f:
        for r in data:
            f.write(json.dumps({h: v for h, v in zip(HEADER, r)}, ensure_ascii=False) + "\n")
    db = folder / "sample_model.sqlite"
    if db.exists():
        db.unlink()
    con = sqlite3.connect(db)
    con.execute("create table elements (" + ",".join(f'"{h}"' for h in HEADER) + ")")
    con.executemany("insert into elements values (" + ",".join("?" * len(HEADER)) + ")", data)
    con.commit()
    con.close()


if __name__ == "__main__":
    write_all(sys.argv[1] if len(sys.argv) > 1 else "data/sample_export")
