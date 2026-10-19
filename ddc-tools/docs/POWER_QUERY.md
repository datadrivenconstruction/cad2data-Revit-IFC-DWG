# Power BI and Excel: read an export folder with Power Query

No Python, no account, nothing leaves your machine. Works on a folder with `.xlsx`, `.csv` or `.jsonl`
files written by the DDC converters (several models in one folder are stacked, column `SourceFile` tells
them apart).

Status: the M code was written and checked for structure only (see `tests/test_kit.py`); it has not been
run in Power BI Desktop or Excel in the environment where it was authored. If a step fails, open an issue
with the error text and your Power BI / Excel version.

## Power BI Desktop

1. Home > Transform data > Manage Parameters > New Parameter. Create two text parameters:
   `ExportFolder` (path to your folder, for example `C:\DDC\exports\MyProject`) and `PreferredFormat`
   (`xlsx`, `csv` or `jsonl`). The files `powerbi/ExportFolder.pq` and `powerbi/PreferredFormat.pq`
   show the exact definition if you prefer to paste it into a blank query.
2. For each of `RawElements`, `Elements`, `QuantitiesByType`, `Completeness`, in this order:
   Home > New Source > Blank Query > Advanced Editor, paste the content of the `.pq` file, Done,
   rename the query to the file name (without `.pq`).
3. Right-click `RawElements` and untick Enable load (it is only an intermediate step).
4. Close & Apply. In the model, add the measures from `powerbi/measures.dax`.
5. Suggested pages: elements per category (bar), volume by level (column), data completeness (table with
   data bars on `Percent`), slicers on `Category` and `Level`.
6. New conversion? Replace the files in the folder and press Refresh. To share the report, save it as a
   template: File > Export > Power BI template (`.pbit`); the folder parameter is asked on open.

## Excel (Microsoft 365, 2019 or later with Power Query)

1. Open `excel/DDC_Excel_Kit.xlsx`, sheet `Config`, type your folder into `ExportFolder`.
2. Data > Get Data > From Other Sources > Blank Query > Advanced Editor. Paste the code from sheet `Queries`
   (column C), top to bottom, naming each query as in column A.
3. Load `Elements`, `QuantitiesByType` and `Completeness` as tables; keep the rest as connection only.
4. Insert a PivotTable on `QuantitiesByType` (Rows: Category, Values: Count, Volume, Area).
5. Data > Refresh All after a new conversion. Save as `.xltx` to reuse the setup as a template.

## Column names

`Elements.pq` maps common names to `ElementId`, `GlobalId`, `Category`, `TypeName`, `Level`. If your export
uses other names, add them to the alias lists in the `Role(...)` lines. `QuantitiesByType.pq` sums the
columns named in its `QtyNames` list; add yours there. Values are summed as exported, without unit conversion.

Excel and Power BI are trademarks of Microsoft Corporation; used only to say what the files work with.
