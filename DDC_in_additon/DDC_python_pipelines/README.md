# Python notebooks

The notebooks were written for the retired 18.x converters (`<name>_rvt.xlsx`, `.dae`). They are ported to the converters in
[`DDC_WINDOWS_Converters/`](../../DDC_WINDOWS_Converters/): a model goes through the converter and then through
[`ddc table`](../../ddc-tools/README.md#ddc-table), which rebuilds the flat table (sheet `Project_Data`, columns `ID`, `Category`,
`Type Name`, `Level`, `Length`, `Area`, `Volume`, ...). The analysis cells work on that table.

Every notebook starts with `REPO = Path(os.environ.get("DDC_REPO", r"C:\DDC\cad2data-Revit-IFC-DWG"))`: set it to where you cloned
this repository (or install the tool once: `pip install "<repo>\ddc-tools"`). Paths of your own files are variables at the top; the
environment variables `DDC_RVT`, `DDC_MODEL`, `DDC_BATCH` and `DDC_OUT` override them. Requirements: `pandas`, `matplotlib`,
`openpyxl`; `fpdf2` (notebooks 3 and 7) and `missingno` (notebook 4) are installed with pip.

| Notebook | Status |
|---|---|
| 1 Conversion of a single Revit project | Ported. Runs `RVTconverter.exe --properties --ifc`, builds `<name>_rvt.xlsx`, sums `Volume` by `Type Name`. |
| 2 Batch conversion Revit / IFC | Ported. Converts every `.rvt` and `.ifc` of a folder to `<path>\converted\<name>_rvt|_ifc` and writes the tables `<name>_rvt.xlsx` / `_ifc.xlsx`. |
| 3 Example of data processing | Ported. Input: `.ifc` file (default: the open Duplex sample of this repository), `.rvt` or `.dwg`. Categories work for both `OST_` codes and IFC classes. |
| 4 Dataframe from Revit / IFC | Ported, same input as 3. |
| 5 Batch processing, charts | Ported. Convert a folder, then a bar chart per table. |
| 6 Quick QTO for all files in a folder | Ported. Converts the models to CSV tables, then grouped sums per `Type Name` with element ids. |
| 7 Batch processing, JPEG and PDF | Ported. Converts a folder, then pie / bar charts and a PDF report per table. |

Run on 2026-10-19 with `jupyter nbconvert --execute`: notebooks 3 and 4 on the open IFC sample (`Sample_Projects`), notebooks 1, 2, 5, 6, 7
on a folder that held that IFC sample and a small Revit sample; all cells ran without errors. The committed notebooks have their
outputs cleared. Differences to the old results: `Volume` / `Area` of Revit elements come from the converter's IFC quantities or the
GLB mesh, not from Revit's own values; the old `.dae` is replaced by the GLB; DGN is not supported.

Converter folders and command lines: `DDC_WINDOWS_Converters/README.md`.
