"""Power BI (Power Query M) and Tableau connection assets written next to the dataset."""
from __future__ import annotations

import os

import pandas as pd

from .bi import RELATIONS

_M_TYPE = {"i": "Int64.Type", "f": "type number", "b": "type logical", "O": "type text"}


def _mtype(dtype) -> str:
    return _M_TYPE.get(dtype.kind, "type text")


def power_query_m(tables: dict) -> str:
    out = ["// DDC star schema loader. In Power BI Desktop: Home > Transform data > New Source > Blank Query >",
           "// Advanced Editor, paste this file, set DataFolder below, then Close & Apply.",
           "// Each table also exists as its own query; this one returns all of them as a record.",
           "let",
           '    DataFolder = "C:\\path\\to\\bi\\csv\\",']
    names = []
    for name, df in tables.items():
        cols = ", ".join(f'{{"{c}", {_mtype(df[c].dtype)}}}' for c in df.columns)
        out += [f'    {name}_raw = Csv.Document(File.Contents(DataFolder & "{name}.csv"), '
                f'[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
                f"    {name} = Table.TransformColumnTypes(Table.PromoteHeaders({name}_raw, [PromoteAllScalars=true]), {{{cols}}}, \"en-US\"),"]
        names.append(name)
    rec = ", ".join(f"{n} = {n}" for n in names)
    out += [f"    Result = [{rec}]", "in", "    Result"]
    return "\n".join(out) + "\n"


def per_table_m(tables: dict) -> str:
    """One query per table, for users who prefer to add them individually."""
    blocks = []
    for name, df in tables.items():
        cols = ", ".join(f'{{"{c}", {_mtype(df[c].dtype)}}}' for c in df.columns)
        blocks.append(f"// ---- query: {name}\nlet\n    DataFolder = \"C:\\path\\to\\bi\\csv\\\",\n"
                      f"    Source = Csv.Document(File.Contents(DataFolder & \"{name}.csv\"), "
                      f"[Delimiter=\",\", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n"
                      f"    Typed = Table.TransformColumnTypes(Table.PromoteHeaders(Source, [PromoteAllScalars=true]), "
                      f"{{{cols}}}, \"en-US\")\nin\n    Typed\n")
    return "\n".join(blocks)


def _rel_lines():
    lines = []
    for a, c, b in RELATIONS:
        k = "element_key" if b == "fact_elements" else c
        lines.append(f"- {a}[{c}] many-to-one {b}[{k}]")
    return "\n".join(lines)


POWERBI_MD = """# Power BI

1. Open Power BI Desktop > Home > Transform data > New Source > Blank Query > Advanced Editor.
2. Paste `DDC_StarSchema.pq`, or use `DDC_tables.pq` (one query per table; paste each block into its own blank query).
   Set `DataFolder` to the absolute path of the `csv` folder (keep the trailing backslash).
3. Close & Apply. Model view > Manage relationships (Power BI usually detects them from the key names;
   otherwise create them):
{rel}
   Direction: single (dimension filters fact). Set the key columns to "Don't summarize".
4. Key 0 in every dimension is the "(unassigned)" member, so every fact row has a matching dimension row.
5. Measures to start with (DAX):
   `Volume m3 = SUM(fact_elements[volume_m3])`, `Area m2 = SUM(fact_elements[area_m2])`,
   `Elements = COUNTROWS(fact_elements)`.
   Column names carry the unit (`_m`, `_m2`, `_m3`).

Parquet instead of CSV: Get data > Parquet, pick the files in the `parquet` folder (same table and column names).
"""

TABLEAU_MD = """# Tableau (no extract tooling needed)

CSV connection:
1. Connect > To a File > Text file > `csv/fact_elements.csv`.
2. Drag `dim_category.csv`, `dim_level.csv`, `dim_type.csv`, `dim_material.csv` onto the canvas; in each
   relationship use the key column of the same name (category_key, level_key, type_key, material_key).
   Use Relationships (the default noodle), not physical joins, so unused dimensions do not multiply rows.
3. `dim_type.category_key` links types to categories; `bridge_element_material.csv` (element_key, material_key, role)
   holds every material parameter of an element for many-to-many material analysis.
4. Set `*_key` and `element_key` fields to Dimension / Discrete; units are in the column names.

Parquet: Tableau 2023.1+ reads the files in `parquet/` through Connect > More > Parquet (or via DuckDB ODBC).
No .hyper or .tds is shipped; the connection above is reproducible from the CSVs alone.
"""


def write_assets(out_dir: str, tables: dict) -> None:
    pb = os.path.join(out_dir, "powerbi")
    os.makedirs(pb, exist_ok=True)
    with open(os.path.join(pb, "DDC_StarSchema.pq"), "w", encoding="utf-8") as f:
        f.write(power_query_m(tables))
    with open(os.path.join(pb, "DDC_tables.pq"), "w", encoding="utf-8") as f:
        f.write(per_table_m(tables))
    with open(os.path.join(pb, "README.md"), "w", encoding="utf-8") as f:
        f.write(POWERBI_MD.format(rel=_rel_lines()))
    tb = os.path.join(out_dir, "tableau")
    os.makedirs(tb, exist_ok=True)
    with open(os.path.join(tb, "README.md"), "w", encoding="utf-8") as f:
        f.write(TABLEAU_MD)
