"""Load an element table into pandas with clean column names and a unit map."""
from __future__ import annotations

import os

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .categories import canonical_series
from .xlsxio import read_table, split_unit


class Frame:
    def __init__(self, df: pd.DataFrame, units: dict, source: str = ""):
        self.df, self.units, self.source = df, units, source


def from_arrow(tab: pa.Table, source: str = "") -> Frame:
    df = tab.to_pandas()
    ren, units, seen = {}, {}, set()
    for f in tab.schema:
        base, unit = split_unit(f.name)
        md = f.metadata or {}
        if b"unit" in md:
            unit = md[b"unit"].decode()
            base = md.get(b"ddc_base_name", base.encode()).decode()
        n, k = base, 1
        while n in seen:
            k += 1
            n = f"{base} [{k}]"
        seen.add(n)
        ren[f.name] = n
        if unit:
            units[n] = unit
    df = df.rename(columns=ren)
    for c in ("Category", "Level", "Family", "Type Name"):
        if c not in df.columns:
            df[c] = None
    df["CategoryEn"] = canonical_series(df["Category"])
    return Frame(df, units, source)


def load(path: str, sheet: str = "Elements") -> Frame:
    if os.path.isdir(path):
        p = os.path.join(path, sheet + ".parquet")
        tab = pq.read_table(p if os.path.exists(p) else path)
    elif path.lower().endswith(".parquet"):
        tab = pq.read_table(path)
    else:
        tab = read_table(path, sheet)
    return from_arrow(tab, os.path.basename(path.rstrip("/\\")))
