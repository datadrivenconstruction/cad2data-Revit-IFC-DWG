# ddc-data

Post-processing for the converter's xlsx output (sheet `Elements`, hidden `_ddc_base`): Parquet/DuckDB export,
report templates, and a BI star schema. It reads files only; the converter engine is untouched.
If `ddc-converter` is installed, a `.rvt`/`.rfa` path can be given instead of an xlsx and is converted first.

```
pip install -e integrations/data          # pyarrow, duckdb, openpyxl, pandas, pyyaml (all permissive licences)
ddc-data to-parquet model.xlsx [--by-category] [--out DIR]
ddc-data to-duckdb  model.xlsx [--by-category] [--out FILE]
ddc-data report     model.xlsx -t quantity_takeoff [--format xlsx,html] [--out PREFIX]
ddc-data report --list
ddc-data to-bi      model.xlsx --out DIR      # writes the dataset and checks key integrity
ddc-data bi-check   DIR [--format csv]
ddc-data bench      model.xlsx                # read time and size vs xlsx
```

## Parquet and DuckDB

One table per visible sheet (`Elements`), plus `ddc_meta` (key/value from `_ddc_base`) and `ddc_units`
(table, column, base_name, unit). `--include-base` also exports the `_ddc_base` mirror.

- `ElementId` is `int64`; numeric columns are `float64`; everything else is text. A column mixing numbers and
  text stays text.
- The header keeps its unit, `Area (m²)`, and each field carries `unit` and `ddc_base_name` in its Arrow
  metadata (`m`, `m²`, `m³`, `internal units` = feet, ...).
- `--by-category` writes a hive-partitioned dataset `Elements/Category=<name>/` (Parquet) or one extra table
  `Elements__<category>` per category (DuckDB). Missing categories go to `(none)`.

## Report templates

Built-in: `quantity_takeoff` (count, length, area, volume by category, level, category+level, type),
`room_schedule`, `door_window_schedule`, `wall_types_summary`, `parameter_fill_rate`.
Output is a formatted xlsx (header style, frozen header, filters, number formats, totals row, Summary sheet)
and a self-contained HTML file.

Category names are localized in Revit files. Templates should filter on the virtual column `CategoryEn`, which maps
common English, German, French, Spanish, Italian, Russian, Portuguese, Dutch and Polish names to the English
one (`Walls`, `Doors`, `Windows`, `Rooms`, `Floors`, ...); unknown names pass through unchanged.

### Custom template format (YAML or JSON)

```yaml
name: Wall volume by level and type     # shown in the report
description: free text
filters:                                 # all must match; applied before grouping
  - {column: CategoryEn, in: [Walls]}
  - {column: Volume, gt: 0}
group_by: [Level, Type Name]             # omit for a flat list
aggregates:                              # fn: sum mean min max median count nunique first
  - {fn: count, as: Walls}               # count without a column = rows
  - {column: Volume, fn: sum, as: Volume}
having: [{column: Volume, gt: 1}]        # filters on the aggregated result
columns: [ElementId, {column: Mark, as: Tag}]   # flat lists: select, order and rename
sort: [Level, -Volume]                   # leading - = descending
convert: {Volume: ft3, Length: ft}       # unit conversion on output columns
limit: 20
totals: true                             # default: on when group_by is set
```

- Column names are the headers without the unit: `Area`, `Volume`, `Length`, `Type Name`, `Level`, `Category`,
  `Family`, plus any parameter column. Units come from the header and are shown in the output header.
- Filter operators: `eq ne in not_in gt ge lt le contains matches` (case-insensitive substring / regex),
  `notnull isnull`. A filter on a column that does not exist matches nothing (negative tests match everything);
  columns missing from `group_by`, `aggregates` or `columns` are skipped and listed in a note under the table.
- Units for `convert`: `m mm cm ft in yd`, squared/cubed forms (`m2`, `ft3`, `m²`), `L`; `internal units` count as feet.
- Several tables in one report: put `sections:` (a list of the keys above, each with its own `title`) under the
  shared `filters`. `kind: fill_rate` turns a section into a per-category parameter fill-rate table.

Examples in `examples/`: `wall_volume_imperial.yaml` (group, aggregate, convert), `fire_rated_doors.json`
(flat list, rename), `floors_and_ceilings.yaml` (two sections, having, limit).
Run: `ddc-data report model.xlsx --template examples/wall_volume_imperial.yaml`.

## BI star schema

`ddc-data to-bi model.xlsx --out DIR` writes `csv/` and `parquet/` with the same tables:

| table | key | content |
|---|---|---|
| `fact_elements` | `element_key` (= ElementId) | FKs `category_key`, `level_key`, `type_key`, `material_key`; measures with units in the name (`volume_m3`, `area_m2`, `length_m`, ...); GlobalId, UniqueId, IfcClass, workset, phases, marks |
| `dim_category` | `category_key` | category, ifc_class |
| `dim_level` | `level_key` | level |
| `dim_type` | `type_key` | category_key, family, type_name |
| `dim_material` | `material_key` | material |
| `bridge_element_material` | element_key + material_key + role | every `* Material` parameter of an element |

Key 0 in every dimension is `(unassigned)`, so each fact row joins to every dimension. `bi-check` loads the
dataset into DuckDB and counts orphan keys, duplicate keys and rows lost by the joins; `to-bi` runs it and exits 1
on any failure. Also written: `relationships.json`, `powerbi/` (`DDC_StarSchema.pq` Power Query M script,
`DDC_tables.pq`, README with relationships and starter measures) and `tableau/README.md` (CSV connection guide;
no .hyper or .tds is generated).

## Tests and tools

`pytest integrations/data` (synthetic workbooks: unicode names, empty and missing categories, missing columns,
localized categories, old-version column sets, mixed types, orphan detection).
`tools/validate_truth.py` compares template totals with Revit truth dumps; `tools/run_matrix.py` runs bench,
all templates and the BI check over converted files.
