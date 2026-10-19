# DDC free tools

Three small, free, offline tools for the tables written by the DDC converters (RVT, IFC, DWG to
XLSX, CSV, JSONL, SQLite or JSON). Your data stays on your machine: no upload, no account, no cloud.

| Tool | What it does |
|---|---|
| `ddc check` | Rule-based data quality check (required parameters, regex, uniqueness, ranges, allowed values). Traffic-light XLSX, JSON, exit code for CI. |
| `ddc convert` | Runs the right DDC converter for a `.rvt` / `.ifc` / `.dwg` file and then `ddc table`: one command from model to the flat table. |
| `ddc table` | Builds the flat one-row-per-element table (the old `*_rvt.xlsx` layout: ID, Category, Type Name, Level, Volume, ...) from RVT, IFC and DWG converter output. |
| `ddc qto` | Quantity summary by category, type and level (count, length, area, volume, whichever the export has) with warnings about gaps. |
| Power BI and Excel kit | Power Query (M) scripts and an Excel workbook that read a whole export folder. No Python needed. |

Python 3.9+, dependencies: `openpyxl` and `PyYAML` (both permissive licences). MIT licence, see the
[repository licence](../LICENSE) for the scope.

## Install

```bash
cd ddc-tools
pip install .          # gives the `ddc` command
# or run without installing:  PYTHONPATH=src python -m ddc_tools --help
```

## What the tools read

A **folder** with converter output or a single file: `.xlsx` (first sheet, or `--sheet`), `.csv`,
`.jsonl` (nested objects are flattened to `Pset.Property` columns), `.json` (list of objects) and
`.sqlite` (table `elements`, else the widest table, or `--table`). If a folder holds several formats,
the first present is used in this order: sqlite, jsonl, xlsx, csv, json (`--format xlsx` forces one).
Helper files such as `geometry_index.jsonl` or `*manifest*` are skipped.

### Converter outputs (no manual mapping)

* **DDC IFC to Excel** writes a relational model (`Objects`, `Properties`, `Quantities`, `SpatialLinks`,
  `TypeLinks` in `drawing.xlsx`, `data.jsonl` or `data.sqlite`). The tools join it into one row per object:
  `ElementId` (STEP id), `GlobalId`, `Category` (IFC class), `Name`, `TypeName` (from the type
  relation, else `ObjectType`), `Level` (storey by containment or aggregation; an opening takes the
  storey of its host wall, Revit-style `Level` properties are the fallback) and one column per property or
  quantity named `<Set>.<Property>`, for example `Pset_WallCommon.FireRating`. Stored `IfcElementQuantity`
  values and length, area and volume measures of property sets count as quantities (property sets of
  types, `PSet_Revit_Type_*`, are not summed). Type objects themselves are not rows.
* **DDC RVT Converter** `--properties` writes `properties.jsonl` (saved graphs). The tools read it as one
  row per element with its stored parameters by label (`Mark`, `Comments`, `Length`, ...). This output has
  numeric category ids instead of names (`Category` shows the id), no level or type columns, and no
  calculated quantities, so `ddc qto` gives counts and whatever stored values exist, with warnings.
  Values are in the model's internal units.
* **DWG to Excel** tables are plain sheets, CSV or JSONL and are read as they are.

Columns of other tables are found by common names, case-insensitive:

| Role | Recognised names |
|---|---|
| ElementId | `ElementId`, `Element Id`, `native_id`, `Id` |
| GlobalId | `GlobalId`, `IfcGUID`, `UniqueId`, `unique_id` |
| Category | `Category`, `IfcClass`, `source_class`, `Entity` |
| Type | `Type Name`, `Family and Type`, `ObjectType`, `Type` |
| Level | `Level`, `Base Constraint`, `BuildingStorey`, `Storey` |

Override them in the rules file (`columns:`). Quantity columns: `Length`, `Width`, `Height`,
`Thickness`, `Perimeter`, `Area`, `Volume`, `NetArea`, `GrossVolume` and similar, also inside
`Qto_...` style names. Units are used as exported and never converted.

## `ddc check`

```bash
ddc check export_folder --rules examples/rules_basic.yaml --xlsx report.xlsx --json report.json
echo $?    # 0 = pass, 1 = failing rules, 2 = bad input or rules file
```

![Traffic-light summary](docs/check_summary.png)

*Real run on the IFC Duplex sample of this repository, converted by DDC IFC to Excel 0.3.1-preview
(`examples/rules_ifc.yaml`). The picture is drawn from the cell contents of the generated XLSX
(`docs/render_xlsx_png.py`), not a screenshot of Excel. The door fire ratings in that model hold the
placeholder text "Fire Rating", which the rule `IFC-DOOR-FIRE-VALUE` flags.*

Rules file (YAML):

```yaml
name: Handover basics
rules:
  - id: WALL-FIRE
    title: Walls must have a Fire Rating
    where: { category: Walls }       # glob on category / type / level, or category_regex ...
    check: required                  # required | not_empty | pattern | unique | range | enum
    param: Fire Rating               # or params: [A, B]
  - id: MARK-FORMAT
    severity: warning                # error (default) | warning | info
    check: pattern
    param: Mark
    regex: 'W-\d{3}'                 # must match the whole value
  - { id: MARK-UNIQUE, check: unique, param: Mark, scope: Level }   # unique per level
  - { id: WIDTH, check: range, param: Width, min: 0.1, max: 0.5 }
  - { id: FIRE, check: enum, param: Fire Rating, values: ["EI 30", "EI 60"] }
```

Semantics:

* `required`: the parameter must exist in the export and be non-empty. A missing column fails every
  matching element. `not_empty`: same, but a missing column makes the rule `SKIP`.
* `pattern`, `range`, `enum`, `unique` ignore empty values (use `required` for those).
* Status per rule: `PASS`, `FAIL` (failures with severity error), `WARN`, `INFO`, `SKIP` (nothing matched).
* Exit code `1` if any rule is `FAIL`; with `--fail-on warning` also for `WARN`.
* `Details` sheet lists every failing element with `ElementId`, `GlobalId`, category, type, level,
  parameter, value and message (up to 5000 per rule; the sheet says when truncated).

CI example:

```yaml
- run: ddc check out/model --rules rules.yaml --xlsx check.xlsx --json check.json
- uses: actions/upload-artifact@v4
  if: always()
  with: { name: data-check, path: "check.*" }
```

`examples/rules_ifc.yaml` works on the IFC to Excel output as it is. A short parameter name such as
`FireRating` matches every property set that has it and the first non-empty value counts; use
`Pset_DoorCommon.FireRating` to be specific.

## `ddc convert`

One command from model file to table. It calls the converters' own command lines and then `ddc table`:

| Model | Command that is run |
|---|---|
| `.rvt`, `.rfa` | `DDC_RVT_Converter\cli\RVTconverter.exe MODEL -o WORK --properties --ifc` |
| `.ifc` | `DDC_IFC_to_Excel\runtime\python.exe sources\ifc-excel\converter.py MODEL --output WORK` |
| `.dwg` | `DDC_DWG_to_Excel\cli\dwg2excel.exe MODEL --output WORK --json --no-svg --no-dxf --no-xlsx` |

```bash
ddc convert "C:\Models\Project.rvt"                 # -> C:\Models\Project_rvt.xlsx (+ Project.converted\)
ddc convert Building.ifc --xlsx out\Building.xlsx --csv out\Building.csv
ddc convert plan.dwg --json                          # one JSON line with the paths, for n8n and scripts
```

The converters are looked up in `--converters DIR`, then `$DDC_CONVERTERS`, then the `DDC_WINDOWS_Converters`
folder of the repository this tool sits in. A finished `WORK` folder that is newer than the model is reused;
`--force` converts again and renames the old folder (`.old-<time>`), nothing is deleted. RVT converter exit
code 2 (written with reported gaps) is accepted, the gaps are in `report.json` / `summary.json` of `WORK`.

## `ddc table`

The current converters do not write the flat per-element sheet the 18.x converters did (`<name>_rvt.xlsx`,
sheet `Project_Data`). `ddc table` rebuilds it, so spreadsheets, notebooks and n8n steps written for that
layout keep working.

```bash
# RVT: convert with properties (+ IFC for names), then build the table
RVTconverter.exe Project.rvt -o out\Project --properties --ifc
ddc table out\Project --xlsx Project_rvt.xlsx

# IFC: DDC IFC to Excel output (folder, data.jsonl, data.sqlite or drawing.xlsx) or a plain .ifc file
ddc table out\Building-440646b4da26 --xlsx Building_ifc.xlsx --csv Building_ifc.csv
ddc table Building.ifc --xlsx Building_ifc.xlsx

# DWG: the .jsonl / .csv / .xlsx that dwg2excel.exe writes
ddc table out\plan --xlsx plan_dwg.xlsx
```

Options: `--csv`, `--jsonl` (more outputs), `--all` (keep rows normally dropped), `--qualified` (name IFC
parameter columns `Pset.Property`), `--no-ifc` / `--no-glb` (RVT: ignore `native_graph.ifc` /
`native_graph.glb`), `--kind` (force the input kind), `--columns` (print the mapping below). The XLSX has the
sheet `Project_Data` (as in the old files) and a sheet `Info` with source, counts and notes.

What each input gives:

* **RVT `<name>.converted`** (`--properties`): every element with a real category or a mesh, with `ElementId`,
  `Revit Class`, `Category Id`, the stored `Level`, `Type Id` and every stored parameter as a column. The
  saved graph holds no category, family or type names. With `--ifc` as well (`native_graph.ifc`), the same
  rows get `Category`, `Family`, `Type Name`, `Level`, `Material`, GUIDs and the metric parameter values. With
  `native_graph.glb` present, `Mesh Volume`, `Mesh Area` and `BBox X/Y/Z` (metres, Z up) are added and fill
  `Volume` / `Area` when nothing better exists. Without `--ifc`, double-valued parameters are in Revit internal
  units (feet); the column `Parameter Units` says so.
* **IFC**: products (types, project/site/building/storey and openings are left out unless `--all`). `Level` is
  the containing storey, `Type Name` the linked type object, `Material` the associated materials. Parameters
  from all property sets become columns named by the property; when two sets use the same name with different
  values the second one is called `Pset.Property`. Values are as stored (IFC project units).
* **DWG**: drawing objects (layer, entity type, block name, text, position); blocks, vertices and table records
  are left out. `Coverage` repeats the converter's status; `ENVELOPE_ONLY` rows carry no geometry.

### Column mapping

| Column | Meaning | RVT | IFC | DWG |
|---|---|---|---|---|
| `ID` | Row key, the same value type as the old exports | ElementId | STEP id (or Revit ElementId in a Revit IFC) | handle |
| `ElementId` | Revit element id | ElementId | Revit_Identity.ElementId if present | - |
| `GlobalId` | Global unique id | IFC GlobalId when native_graph.ifc is present | IfcRoot.GlobalId | - |
| `Category` | Old-style category code | OST_ code from the category id (OST_Walls) | IFC class (IfcWall) or the Revit category in a Revit IFC | entity type (LINE, INSERT, ...) |
| `Category Name` | Readable category | Revit_Identity.CategoryName | Revit category if present, else the IFC class without Ifc | entity type |
| `IfcClass` | IFC entity class | from native_graph.ifc | IfcRoot class | - |
| `Revit Class` | Revit element class | root object class (SWall, FamilyInstance) | Revit_Identity.Class | - |
| `Family` | Family name | Revit_Identity.FamilyName | Revit_Identity.FamilyName, else first part of 'Family:Type:Id' names | - |
| `Type Name` | Type name | Revit_Identity.TypeName | type object name, else Revit_Identity.TypeName, else middle part of 'Family:Type:Id' | block name for INSERT |
| `Type` | Same as Type Name (the old exports had both columns) | Type Name | Type Name | Type Name |
| `Family and Type` | Family: Type | Family and Type names joined | same | - |
| `Type Id` | Type element id | root object type reference | Revit_Identity.TypeId | - |
| `Name` | Element name | first name-like stored text | IfcRoot.Name | text of TEXT/MTEXT |
| `Level` | Level / storey / layout | associated level name | Revit_Identity.LevelName, else the containing IfcBuildingStorey | owner block (Model_Space, Paper_Space) |
| `Material` | Material names joined by '; ' | - | IfcRelAssociatesMaterial | - |
| `Length` | Length | - | see Quantity rules | LINE, ARC, CIRCLE, ELLIPSE, polyline length |
| `Width` | Width | - | see Quantity rules | - |
| `Height` | Height | - | see Quantity rules | - |
| `Perimeter` | Perimeter | - | see Quantity rules | closed polyline / circle |
| `Area` | Area | mesh surface area (m2) from the GLB | see Quantity rules | circle, closed polyline (no bulges) |
| `Volume` | Volume | mesh volume (m3) from the GLB, not Revit's Volume | see Quantity rules | - |
| `Quantity Source` | Where Length..Volume came from | glb-mesh | property:Set.Name or quantity:Set.Name | geometry |
| `Layer` | Drawing layer | - | - | layer_name |
| `On the standard 3D View` | True when the element is part of the exported model (the old exports had a Revit view flag of this name) | True when the element has a mesh in native_graph.glb or a product in native_graph.ifc | True for every product row | True for model space, False for paper space and blocks |

Quantity rules (columns `Length`, `Width`, `Height`, `Perimeter`, `Area`, `Volume`): for every element the
properties are searched first, then the quantity sets (`Qto_*`), by these names in order:
`Length` = Length, NominalLength; `Width` = Width, NominalWidth, Thickness; `Height` = Height, NominalHeight,
Unconnected Height; `Perimeter`; `Area` = Area, NetArea, NetSideArea, GrossArea, GrossSideArea,
NetFootprintArea, GrossFootprintArea; `Volume` = Volume, NetVolume, GrossVolume. Instance values win over type
values. `Quantity Source` records where each number came from. Nothing is computed or converted except mesh
quantities (RVT, from the GLB) and DWG geometry.

Every other column is a parameter: its name is the parameter name, values keep their stored type. `ddc check`
and `ddc qto` read the result directly (`ddc qto Project_rvt.xlsx`).

Limits, stated plainly: for RVT the table follows what the saved graph stores, which has no formula
evaluation and no unit formatting; mesh volumes equal Revit's `Volume` only for closed meshes. The IFC table
is only as good as the property and quantity sets in the file. Category codes (`OST_Walls`) come from a
short list of certain ids and otherwise from the category name.

## `ddc qto`

```bash
ddc qto export_folder --xlsx qto.xlsx
ddc qto model.xlsx --category "Wall*" --quantities Area,Volume --json qto.json
# IFC to Excel output of the Duplex sample, walls, slabs and coverings only
ddc qto Duplex.converted --category "IfcWall*" --category IfcSlab --category IfcCovering     --quantities "PSet_Revit_Dimensions.Length,PSet_Revit_Dimensions.Area,PSet_Revit_Dimensions.Volume" --xlsx qto.xlsx
```

![QTO by type](docs/qto_by_type.png)

*Same run, walls, slabs and coverings of the Duplex model; quantities as stored in the IFC.*

Workbook sheets: `Read me`, `By Category`, `By Type`, `By Level`, `Detail` (category + type + level),
`Warnings`. Every table has filters, a frozen header and a `SUBTOTAL` total row that follows the filter.

Warnings cover: missing id, category, type or level columns; elements without a level or type
(grouped as `(none)`); non-numeric values; categories with no quantities at all; quantities missing
or zero for part of a category; repeated element ids; quantity columns without any number.
`--strict` turns warnings into exit code 1.

Sums use only elements that have a numeric value. Treat the result as a data summary: check units and
completeness before it goes into a bill of quantities, and compare against your authoring tool.

## Power BI and Excel

Folder `powerbi/` holds Power Query (M) scripts: `RawElements` (reads every `.xlsx`, `.csv` or `.jsonl`
of the folder), `Elements` (standard column names), `QuantitiesByType`, `Completeness`, plus `measures.dax`.
`excel/DDC_Excel_Kit.xlsx` carries the same code with a `Config` sheet for the folder path.
Steps: [docs/POWER_QUERY.md](docs/POWER_QUERY.md).

A ready `.pbit` is not included: it can only be produced reliably with Power BI Desktop, and the
scripts were written without access to it, so please report anything that does not load on your
version. SQLite is not read by Power Query directly; use the xlsx, csv or jsonl files.

## Tests

```bash
pip install pytest openpyxl pyyaml
python -m pytest -q          # run inside ddc-tools/
```

Tests use a tiny synthetic table (`examples/make_sample.py`) and an excerpt of a real IFC to Excel run
(`tests/fixtures/`, see its README; the RVT fixture keeps the real row layout with invented values).
Regenerate the synthetic sample with `python examples/make_sample.py examples/data/sample_export`.

## Notes

Excel and Power BI are trademarks of Microsoft Corporation. Autodesk, Revit and AutoCAD are
trademarks of Autodesk, Inc.; IFC and buildingSMART are trademarks of buildingSMART International.
Format names are used only to say which files are read. These tools are independent software and are
not affiliated with, endorsed by or certified by those companies. See [../TRADEMARK.md](../TRADEMARK.md).
