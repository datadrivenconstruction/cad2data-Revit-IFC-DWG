"""Minimal read-only XLSX reader (stdlib only) for the converter element table."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile

_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def _col(ref: str) -> int:
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx(path, sheet: str | None = None):
    """Return (header, rows); rows are lists aligned to header. First visible sheet by default."""
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(_NS + "si"):
                shared.append("".join(t.text or "" for t in si.iter(_NS + "t")))
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        target = None
        for s in wb.iter(_NS + "sheet"):
            if (sheet is None and s.get("state") != "hidden") or s.get("name") == sheet:
                target = rels[s.get(_RNS + "id")]
                break
        if target is None:
            raise KeyError(f"sheet not found: {sheet or '(first visible)'}")
        target = target.lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        out = []
        for row in ET.fromstring(z.read(target)).iter(_NS + "row"):
            vals = []
            for c in row.iter(_NS + "c"):
                i = _col(c.get("r"))
                vals.extend([None] * (i - len(vals)))
                t, v = c.get("t"), c.find(_NS + "v")
                if t == "s" and v is not None:
                    x = shared[int(v.text)]
                elif t == "inlineStr":
                    x = "".join(e.text or "" for e in c.iter(_NS + "t"))
                elif v is None:
                    x = None
                elif t in ("str", "e"):
                    x = v.text
                elif t == "b":
                    x = v.text == "1"
                else:
                    f = float(v.text)
                    x = int(f) if re.fullmatch(r"-?\d+", v.text) else f
                vals.append(x)
            out.append(vals)
    if not out:
        return [], []
    header = [h if h is not None else "" for h in out[0]]
    rows = [r + [None] * (len(header) - len(r)) for r in out[1:]]
    return header, rows
