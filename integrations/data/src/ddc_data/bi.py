"""Star schema for BI tools: fact_elements + dim_category/level/type/material (+ bridge)."""
from __future__ import annotations

import json
import os
import re

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .frame import Frame, load

UNKNOWN = "(unassigned)"
SEP = "\x1f"
MEASURES = ["Length", "Width", "Height", "Perimeter", "Area", "Volume", "NetArea", "GrossArea",
            "NetSideArea", "GrossSideArea", "NetVolume", "GrossVolume", "NetSurfaceArea", "Depth",
            "CrossSectionArea"]
ATTRS = ["GlobalId", "UniqueId", "IfcClass", "Workset", "Phase Created", "Phase Demolished", "Design Option",
         "Mark", "Type Mark"]
PRIMARY_MATERIAL = ["Material", "Structural Material", "Exterior Material", "Door Material", "Frame Material",
                    "Interior Material"]
TABLES = ["fact_elements", "dim_category", "dim_level", "dim_type", "dim_material", "bridge_element_material"]
RELATIONS = [("fact_elements", "category_key", "dim_category"), ("fact_elements", "level_key", "dim_level"),
             ("fact_elements", "type_key", "dim_type"), ("fact_elements", "material_key", "dim_material"),
             ("dim_type", "category_key", "dim_category"),
             ("bridge_element_material", "element_key", "fact_elements"),
             ("bridge_element_material", "material_key", "dim_material")]


def _snake(s: str) -> str:
    s = s.replace("²", "2").replace("³", "3")
    return re.sub(r"[^0-9a-zA-Z]+", "_", s).strip("_").lower() or "col"


def _blank(s: pd.Series) -> pd.Series:
    return s.isna() | (s.astype("string").str.strip() == "").fillna(True)


def _key(series: pd.Series):
    """Dense integer keys from 1 (sorted); 0 is the unassigned member."""
    s = series.astype("object").where(~_blank(series), None)
    m = {v: i + 1 for i, v in enumerate(sorted({v for v in s if v is not None}, key=str))}
    return s.map(lambda v: m.get(v, 0)).astype("int64"), m


def build(fr: Frame) -> dict:
    df = fr.df.reset_index(drop=True)
    n = len(df)
    ids = (df["ElementId"] if "ElementId" in df.columns else pd.Series(range(1, n + 1))).astype("int64")
    cat_key, cat_map = _key(df["Category"])
    lvl_key, lvl_map = _key(df["Level"])
    cat = df["Category"].astype("object").where(~_blank(df["Category"]), UNKNOWN).astype(str)
    fam = df["Family"].astype("object").where(~_blank(df["Family"]), "").astype(str)
    typ = df["Type Name"].astype("object").where(~_blank(df["Type Name"]), "").astype(str)
    comb = (cat + SEP + fam + SEP + typ).where((fam != "") | (typ != ""), None)
    type_key, type_map = _key(comb)

    mat_cols = [c for c in df.columns if c == "Material" or c.endswith(" Material")]
    prim_cols = [c for c in PRIMARY_MATERIAL if c in df.columns] + [c for c in mat_cols if c not in PRIMARY_MATERIAL]
    prim = pd.Series([None] * n, dtype="object")
    for c in prim_cols:
        prim = prim.where(~_blank(prim), df[c].astype("object"))
    all_mats = sorted({str(v).strip() for c in mat_cols for v in df[c][~_blank(df[c])]})
    mat_map = {v: i + 1 for i, v in enumerate(all_mats)}
    mat_key = prim.map(lambda v: mat_map.get(str(v).strip(), 0) if v is not None and v == v else 0).astype("int64")

    dim_cat = pd.DataFrame({"category_key": [0] + list(cat_map.values()), "category": [UNKNOWN] + list(cat_map)})
    if "IfcClass" in df.columns:
        ifc = df.groupby(cat_key)["IfcClass"].agg(lambda s: next((x for x in s if isinstance(x, str)), None))
        dim_cat["ifc_class"] = dim_cat["category_key"].map(ifc.to_dict())
    else:
        dim_cat["ifc_class"] = None
    dim_lvl = pd.DataFrame({"level_key": [0] + list(lvl_map.values()), "level": [UNKNOWN] + list(lvl_map)})
    rows = [(0, 0, "", "")]
    for c, k in type_map.items():
        cc, f, t = c.split(SEP)
        rows.append((k, cat_map.get(cc, 0), f, t))
    dim_type = pd.DataFrame(rows, columns=["type_key", "category_key", "family", "type_name"])
    dim_mat = pd.DataFrame({"material_key": [0] + list(mat_map.values()), "material": [UNKNOWN] + list(mat_map)})

    fact = pd.DataFrame({"element_key": ids, "category_key": cat_key, "level_key": lvl_key,
                         "type_key": type_key, "material_key": mat_key})
    for a in ATTRS:
        if a in df.columns:
            fact[_snake(a)] = df[a]
    for m in MEASURES:
        if m in df.columns:
            u = fr.units.get(m)
            fact[_snake(m) + (f"_{_snake(u)}" if u else "")] = pd.to_numeric(df[m], errors="coerce")
    parts = []
    for c in mat_cols:
        ok = ~_blank(df[c])
        parts.append(pd.DataFrame({"element_key": ids[ok].values,
                                   "material_key": [mat_map[str(v).strip()] for v in df[c][ok]],
                                   "role": c}))
    br = pd.concat(parts, ignore_index=True).drop_duplicates() if parts else pd.DataFrame(
        {"element_key": pd.Series([], dtype="int64"), "material_key": pd.Series([], dtype="int64"),
         "role": pd.Series([], dtype="object")})
    return {"fact_elements": fact, "dim_category": dim_cat, "dim_level": dim_lvl, "dim_type": dim_type,
            "dim_material": dim_mat, "bridge_element_material": br}


def write(tables: dict, out_dir: str) -> list:
    os.makedirs(os.path.join(out_dir, "csv"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "parquet"), exist_ok=True)
    files = []
    for name, df in tables.items():
        p = os.path.join(out_dir, "csv", name + ".csv")
        df.to_csv(p, index=False, encoding="utf-8")
        q = os.path.join(out_dir, "parquet", name + ".parquet")
        pq.write_table(pa.Table.from_pandas(df, preserve_index=False), q, compression="zstd")
        files += [p, q]
    with open(os.path.join(out_dir, "relationships.json"), "w", encoding="utf-8") as f:
        json.dump([{"from": a, "to": b, "key": c} for a, c, b in RELATIONS], f, indent=1)
    return files


def check(out_dir: str, fmt: str = "parquet") -> dict:
    """Load the dataset into DuckDB; count orphan keys per relationship and fact rows lost by joins."""
    import duckdb

    con = duckdb.connect()
    for name in TABLES:
        p = os.path.join(out_dir, fmt, f"{name}.{fmt}").replace("\\", "/")
        src = f"read_parquet('{p}')" if fmt == "parquet" else f"read_csv('{p}', header=true)"
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM {src}")
    res = {}
    for a, col, b in RELATIONS:
        dkey = "element_key" if b == "fact_elements" else col
        res[f"{a}.{col}->{b}"] = con.execute(
            f"SELECT count(*) FROM {a} x WHERE x.{col} IS NULL OR TRY_CAST(x.{col} AS BIGINT) NOT IN (SELECT TRY_CAST({dkey} AS BIGINT) FROM {b})"
        ).fetchone()[0]
    res["dup_keys"] = sum(con.execute(f"SELECT count(*)-count(DISTINCT {k}) FROM {t}").fetchone()[0]
                          for t, k in [("fact_elements", "element_key"), ("dim_category", "category_key"),
                                       ("dim_level", "level_key"), ("dim_type", "type_key"),
                                       ("dim_material", "material_key")])
    res["fact_rows"] = con.execute("SELECT count(*) FROM fact_elements").fetchone()[0]
    res["joined_rows"] = con.execute(
        "SELECT count(*) FROM fact_elements f JOIN dim_category USING(category_key) JOIN dim_level USING(level_key) "
        "JOIN dim_type USING(type_key) JOIN dim_material USING(material_key)").fetchone()[0]
    res["ok"] = all(v == 0 for k, v in res.items() if "->" in k or k == "dup_keys") \
        and res["fact_rows"] == res["joined_rows"]
    con.close()
    return res


def export(src: str, out_dir: str) -> dict:
    from .bi_assets import write_assets

    tables = build(load(src))
    write(tables, out_dir)
    write_assets(out_dir, tables)
    return {k: len(v) for k, v in tables.items()}
