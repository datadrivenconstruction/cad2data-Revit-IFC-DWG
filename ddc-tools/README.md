# DDC free tools

Small, free, offline tools for the tables written by the DDC converters (RVT, IFC, DWG to
XLSX, CSV, JSONL, SQLite or JSON). Your data stays on your machine: no upload, no account, no cloud.

| Tool | What it does |
|---|---|
| `ddc check` | Rule-based data quality check (required parameters, regex, uniqueness, ranges, allowed values). Traffic-light XLSX, JSON, exit code for CI. |
| `ddc convert` | Runs the right DDC converter for a `.rvt` / `.ifc` / `.dwg` file and then `ddc table`: one command from model to the flat table. |
| `ddc table` | Builds the flat one-row-per-element table (the old `*_rvt.xlsx` layout: ID, Category, Type Name, Level, Volume, ...) from RVT, IFC and DWG converter output. |
| `ddc diff` | Compares two exports of a model (RVT, IFC, DWG outputs): added / removed / modified, old to new per property and quantity, changelog XLSX, JSON, GLB coloured by status, exit code for CI. |
| `ddc bcf` | Turns `ddc check` / `ddc diff` findings into BCF 2.1 / 3.0 issue files and tabulates any BCF into XLSX. |
| `ddc qto` | Quantity summary by category, type and level (count, length, area, volume, whichever the export has) with warnings about gaps. |
| Power BI and Excel kit | Power Query (M) scripts and an Excel workbook that read a whole export folder. No Python needed. |

Python 3.9+, dependencies: `openpyxl` and `PyYAML` (both permissive licences). MIT licence, see the
[repository licence](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/blob/main/LICENSE) for the scope.

## Install

```bash
pip install ddc-tools        # gives the `ddc` command
ddc --version
# from a source checkout:  cd ddc-tools && pip install .
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
* **CAD Drawing to Excel** tables are plain sheets, CSV or JSONL and are read as they are.

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

![Traffic-light summary](https://raw.githubusercontent.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/main/ddc-tools/docs/check_summary.png)

*Real run on the IFC Duplex sample of this repository, converted by DDC IFC to Excel 2.0
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
| `.dwg` | `DDC_CAD_Drawing_to_Excel\cli\dwg2excel.exe MODEL --output WORK --json --no-svg --no-dxf --no-xlsx` |

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

The converters write JSONL / CSV / GLB. `ddc table` builds the flat per-element sheet (`<name>_rvt.xlsx`,
sheet `Project_Data`), so spreadsheets, notebooks and n8n steps that expect that layout work with the converter output.

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

## `ddc diff`

What changed between two issues of a model? Both sides are read with the same adapters as `ddc table`
(RVT `properties.jsonl` folder, DDC IFC to Excel output or a plain `.ifc`, CAD Drawing to Excel table), so A and B can be
folders or files in any supported format.

```bash
ddc diff Duplex_v1 Duplex_v2 --xlsx changes.xlsx --json changes.json
ddc diff R24 R24_v2 --glb diff.glb --bcf issues.bcf        # RVT outputs with native_graph.glb
ddc diff A B --fail-on removed,modified                    # CI: exit code 1 only for these statuses
```

```
24 -> 24 elements, matched by key:GlobalId: 2 added, 2 removed, 4 modified, 18 unchanged (4 property, 7 quantity, 1 attribute changes)
```

**Matching.** By a key column: `GlobalId`, `UniqueId`, `ElementId` or `ID`, the first that is present in both
versions with enough coverage and overlap (or `--key COLUMN`). Elements left over on both sides are then matched by a
fingerprint (category, type, level, quantities and all properties, without names and ids); only an exact one-to-one
match counts, and those elements are reported as unchanged with `matched_by = fingerprint`. Statuses: `added`
(only in B), `removed` (only in A), `modified`, `unchanged`. Ids that are not the key (STEP ids, regenerated
GlobalIds) are not counted as changes; a warning says how many differ.

**Changes** are listed per field with old value, new value and, for numbers, delta and percent. Kinds: `quantity`
(Length, Width, Height, Perimeter, Area, Volume, mesh volume/area, bounding box, `Pset` quantities), `attribute`
(category, type, name, level, material, layer) and `property` (everything else). Numbers are equal within
`--tolerance` (relative, default 1e-6); `--ignore GLOB` skips columns.

![Summary sheet](https://raw.githubusercontent.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/main/ddc-tools/docs/diff_summary.png)

![Changelog sheet](https://raw.githubusercontent.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/main/ddc-tools/docs/diff_changelog.png)

The XLSX has sheets `Summary`, `Changelog` (one row per change, status colours), `Elements`, `By category` and
`Quantities` (totals per category in A and B). The JSON holds the same data plus the key diagnostics; unchanged
elements are left out unless `--include-unchanged`.

**Exit code** (`--fail-on`, default `added,removed,modified`): 0 = none of the listed statuses occurs, 1 = at least one
occurs, 2 = error. `--fail-on none` always gives 0 when the comparison ran.

**GLB.** `--glb out.glb` writes the GLB of version B with every material replaced by a status material
(added green, modified orange, unchanged translucent grey; `--glb-unchanged keep|hide`) and copies the geometry of
removed elements from the GLB of A in red. GLBs are taken from `native_graph.glb` / `model.glb` next to the inputs or
from `--glb-a` / `--glb-b`. A node is linked to an element like in the DDC Data Viewer: by `extras.element_id`,
`extras.global_id` or a trailing id of the node name; children inherit the status of their parent. The IFC to Excel
output has no GLB, so for IFC pass one with `--glb-b`. Without any GLB the option only prints a warning.

![GLB coloured by status](https://raw.githubusercontent.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/main/ddc-tools/docs/diff_glb.png)

*The picture is a drawing of the output GLB made by `docs/render_glb_png.py`. The input is a small synthetic RVT-style output
from `docs/make_diff_demo.py` (eight box walls): one wall taller (orange), one deleted (red), one added (green).*

Limits, stated plainly: for RVT the table follows what the saved graph stores, which has no formula
evaluation and no unit formatting; mesh volumes equal Revit's `Volume` only for closed meshes. The IFC table
is only as good as the property and quantity sets in the file. Category codes (`OST_Walls`) come from a
short list of certain ids and otherwise from the category name.

## `ddc diff`

What changed between two issues of a model? Both sides are read with the same adapters as `ddc table`
(RVT `properties.jsonl` folder, DDC IFC to Excel output or a plain `.ifc`, CAD Drawing to Excel table), so A and B can be
folders or files in any supported format.

```bash
ddc diff Duplex_v1 Duplex_v2 --xlsx changes.xlsx --json changes.json
ddc diff R24 R24_v2 --glb diff.glb --bcf issues.bcf        # RVT outputs with native_graph.glb
ddc diff A B --fail-on removed,modified                    # CI: exit code 1 only for these statuses
```

```
24 -> 24 elements, matched by key:GlobalId: 2 added, 2 removed, 4 modified, 18 unchanged (4 property, 7 quantity, 1 attribute changes)
```

**Matching.** By a key column: `GlobalId`, `UniqueId`, `ElementId` or `ID`, the first that is present in both
versions with enough coverage and overlap (or `--key COLUMN`). Elements left over on both sides are then matched by a
fingerprint (category, type, level, quantities and all properties, without names and ids); only an exact one-to-one
match counts, and those elements are reported as unchanged with `matched_by = fingerprint`. Statuses: `added`
(only in B), `removed` (only in A), `modified`, `unchanged`. Ids that are not the key (STEP ids, regenerated
GlobalIds) are not counted as changes; a warning says how many differ.

**Changes** are listed per field with old value, new value and, for numbers, delta and percent. Kinds: `quantity`
(Length, Width, Height, Perimeter, Area, Volume, mesh volume/area, bounding box, `Pset` quantities), `attribute`
(category, type, name, level, material, layer) and `property` (everything else). Numbers are equal within
`--tolerance` (relative, default 1e-6); `--ignore GLOB` skips columns.

![Summary sheet](https://raw.githubusercontent.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/main/ddc-tools/docs/diff_summary.png)

![Changelog sheet](https://raw.githubusercontent.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/main/ddc-tools/docs/diff_changelog.png)

The XLSX has sheets `Summary`, `Changelog` (one row per change, status colours), `Elements`, `By category` and
`Quantities` (totals per category in A and B). The JSON holds the same data plus the key diagnostics; unchanged
elements are left out unless `--include-unchanged`.

**Exit code** (`--fail-on`, default `added,removed,modified`): 0 = none of the listed statuses occurs, 1 = at least one
occurs, 2 = error. `--fail-on none` always gives 0 when the comparison ran.

**GLB.** `--glb out.glb` writes the GLB of version B with every material replaced by a status material
(added green, modified orange, unchanged translucent grey; `--glb-unchanged keep|hide`) and copies the geometry of
removed elements from the GLB of A in red. GLBs are taken from `native_graph.glb` / `model.glb` next to the inputs or
from `--glb-a` / `--glb-b`. A node is linked to an element like in the DDC Data Viewer: by `extras.element_id`,
`extras.global_id` or a trailing id of the node name; children inherit the status of their parent. The IFC to Excel
output has no GLB, so for IFC pass one with `--glb-b`. Without any GLB the option only prints a warning.

![GLB coloured by status](https://raw.githubusercontent.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/main/ddc-tools/docs/diff_glb.png)

*The picture is a drawing of the output GLB made by `docs/render_glb_png.py` from a real RVT Converter run on
a Revit sample model (your own `.rvt` file works the same) and an edited copy (`docs/make_diff_demo.py`): one wall taller, one deleted, one added.*

Limits, stated plainly: Revit ElementIds can change when a model is re-created and IFC STEP ids change on every
export, so prefer `GlobalId`; a fingerprint cannot tell identical elements apart if they only moved; the RVT output has
no placement, so a moved element of unchanged size shows as unchanged unless the GLB-derived columns differ;
comparing outputs of different converters or Revit versions produces many attribute changes.

## `ddc bcf`

[BCF](https://technical.buildingsmart.org/standards/bcf/) is an open issue exchange format of buildingSMART
International. `ddc bcf` writes BCF-XML 2.1 or 3.0 zip files and reads them back; it was written from the
published specification and schemas and the files are validated against the official XSD in the tests. No
certification of any kind is claimed.

```bash
ddc check Model --rules rules.yaml --json check.json --bcf check.bcf       # shortcut
ddc diff A B --json diff.json --bcf diff.bcf --bcf-version 3.0              # shortcut
ddc bcf export check.json -o check.bcf --version 2.1 --per-element          # from a saved report
ddc bcf read check.bcf --xlsx bcf_summary.xlsx                              # any BCF 2.0 / 2.1 / 3.0
```

* One topic per rule (check) or per status and category (diff); `--per-element` gives one topic per element.
  Title, description with examples and old to new values, priority (error = High), labels, status `Open`.
* Each topic has a viewpoint with the affected components: `IfcGuid` when the element has an IFC GlobalId, otherwise
  `AuthoringToolId` (ElementId or table id) with `OriginatingSystem`. Diff viewpoints colour the components by status.
  At most `--max-components` (1000) are selected per viewpoint; the description says how many were left out.
* No snapshot. No camera in 2.1 unless `--camera x,y,z,dx,dy,dz`; the 3.0 schema requires a camera in every
  viewpoint, so 3.0 files carry a neutral default one that viewers replace when they zoom to the selection.
* `ddc bcf read` writes `Summary`, `Topics`, `Comments` and `Components` sheets (and `--json`). Files with a
  DOCTYPE or entity declaration are refused.

![BCF topics](https://raw.githubusercontent.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/main/ddc-tools/docs/bcf_topics.png)

The buildingSMART XSD files are licensed CC BY-ND 4.0, not a permissive licence, so they are not part of this
repository; the tests download them on demand (set `DDC_BCF_XSD_DIR` to reuse a folder) and skip when `lxml` or the
network is missing.

## `ddc qto`

```bash
ddc qto export_folder --xlsx qto.xlsx
ddc qto model.xlsx --category "Wall*" --quantities Area,Volume --json qto.json
# IFC to Excel output of the Duplex sample, walls, slabs and coverings only
ddc qto Duplex.converted --category "IfcWall*" --category IfcSlab --category IfcCovering     --quantities "PSet_Revit_Dimensions.Length,PSet_Revit_Dimensions.Area,PSet_Revit_Dimensions.Volume" --xlsx qto.xlsx
```

![QTO by type](https://raw.githubusercontent.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/main/ddc-tools/docs/qto_by_type.png)

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
Steps: [docs/POWER_QUERY.md](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/blob/main/ddc-tools/docs/POWER_QUERY.md).

A ready `.pbit` is not included: it can only be produced reliably with Power BI Desktop, and the
scripts were written without access to it, so please report anything that does not load on your
version. SQLite is not read by Power Query directly; use the xlsx, csv or jsonl files.

## Tests

```bash
pip install pytest openpyxl pyyaml lxml   # lxml: BCF schema validation (tests skip without it)
python -m pytest -q          # run inside ddc-tools/
```

Tests use a tiny synthetic table (`examples/make_sample.py`) and an excerpt of a real IFC to Excel run
(`tests/fixtures/`, see its README; the RVT fixture keeps the real row layout with invented values).
Regenerate the synthetic sample with `python examples/make_sample.py examples/data/sample_export`.

## Notes

Excel and Power BI are trademarks of Microsoft Corporation. Autodesk, Revit and AutoCAD are
trademarks of Autodesk, Inc.; IFC, BCF and buildingSMART are trademarks of buildingSMART International.
Format names are used only to say which files are read. These tools are independent software and are
not affiliated with, endorsed by or certified by those companies. See [../TRADEMARK.md](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/blob/main/TRADEMARK.md).
