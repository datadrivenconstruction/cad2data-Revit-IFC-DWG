"""xlsx -> Parquet / DuckDB with typed columns; units kept in field metadata."""
from __future__ import annotations

import os
import re

import pyarrow as pa
import pyarrow.compute
import pyarrow.dataset as ds
import pyarrow.parquet as pq

from .xlsxio import Workbook, read_workbook

PART_COL = "Category"
NONE_LABEL = "(none)"


def _safe(name: str) -> str:
    return re.sub(r"[^\w\-. ]+", "_", name, flags=re.UNICODE).strip() or "sheet"


def _meta_table(wb: Workbook, source: str) -> pa.Table:
    items = dict(wb.meta)
    items["source_file"] = os.path.basename(source)
    return pa.table({"key": list(items), "value": list(items.values())})


def units_table(tables: dict[str, pa.Table]) -> pa.Table:
    rows = []
    for t, tab in tables.items():
        for f in tab.schema:
            md = f.metadata or {}
            rows.append((t, f.name, md.get(b"ddc_base_name", f.name.encode()).decode(),
                         md.get(b"unit", b"").decode() or None))
    return pa.table({k: [r[i] for r in rows] for i, k in enumerate(["table", "column", "base_name", "unit"])})


def _with_partition(tab: pa.Table) -> pa.Table:
    i = tab.schema.get_field_index(PART_COL)
    col = tab.column(i).cast(pa.string()).fill_null(NONE_LABEL)
    return tab.set_column(i, tab.schema.field(i), col)


def to_parquet(xlsx: str, out_dir: str, by_category: bool = False, include_base: bool = False,
               compression: str = "zstd") -> list[str]:
    wb = read_workbook(xlsx, include_base)
    os.makedirs(out_dir, exist_ok=True)
    written = []

    def put(tab: pa.Table, name: str):
        p = os.path.join(out_dir, name + ".parquet")
        pq.write_table(tab, p, compression=compression)
        written.append(p)

    for sheet, tab in wb.tables.items():
        if tab.num_columns == 0:
            continue
        if by_category and PART_COL in tab.column_names:
            d = os.path.join(out_dir, _safe(sheet))
            ds.write_dataset(_with_partition(tab), d, format="parquet", partitioning=[PART_COL],
                             partitioning_flavor="hive", existing_data_behavior="overwrite_or_ignore",
                             basename_template="part-{i}.parquet",
                             file_options=ds.ParquetFileFormat().make_write_options(compression=compression))
            written.append(d)
        else:
            put(tab, _safe(sheet))
    put(_meta_table(wb, xlsx), "ddc_meta")
    put(units_table(wb.tables), "ddc_units")
    return written


def to_duckdb(xlsx: str, db_path: str, by_category: bool = False, include_base: bool = False) -> dict[str, int]:
    import duckdb

    wb = read_workbook(xlsx, include_base)
    con = duckdb.connect(db_path)
    counts: dict[str, int] = {}
    try:
        def create(name: str, tab: pa.Table):
            con.register("_t", tab)
            con.execute(f'CREATE OR REPLACE TABLE "{name}" AS SELECT * FROM _t')
            con.unregister("_t")
            counts[name] = tab.num_rows

        for sheet, tab in wb.tables.items():
            if tab.num_columns == 0:
                continue
            create(sheet, tab)
            if by_category and PART_COL in tab.column_names:
                tab = _with_partition(tab)
                cats = sorted(set(tab.column(PART_COL).to_pylist()))
                used: set[str] = set()
                for c in cats:
                    slug = re.sub(r"\W+", "_", c, flags=re.UNICODE).strip("_").lower() or "none"
                    n, k = f"{sheet}__{slug}", 1
                    while n in used:
                        k += 1
                        n = f"{sheet}__{slug}_{k}"
                    used.add(n)
                    mask = pa.compute.equal(tab.column(PART_COL), pa.scalar(c))
                    create(n, tab.filter(mask))
        create("ddc_meta", _meta_table(wb, xlsx))
        create("ddc_units", units_table(wb.tables))
    finally:
        con.close()
    return counts
