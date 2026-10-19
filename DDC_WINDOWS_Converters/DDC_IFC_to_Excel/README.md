# DDC IFC to Excel (portable, Windows x64, preview)

Own IFC reader (no IfcOpenShell). Reads IFC2x3 / IFC4 (SPF and IFCZIP) and writes `drawing.xlsx`,
`data.jsonl`, `data.sqlite`, `result.json`. IFCXML is not supported. Version: `MANIFEST.json`.
A Python runtime is bundled in `runtime\`; nothing else has to be installed.
Licence: DDC EULA, <https://datadrivenconstruction.io/term-of-use-and-eula/>; third-party notices in `SOURCES.json`.

## Desktop app

Double-click `IFC to Excel.exe` (or `Start IFC to Excel.cmd`), choose IFC file(s) and an output folder.

## Command line (scripts, n8n, notebooks)

```bat
runtime\python.exe sources\ifc-excel\converter.py "C:\Models\Building.ifc" --output "C:\Out"
```

Writes a sub-folder `<name>-<hash>` into the output folder and prints one JSON line
(`status`, `folder`, `data`, `errors`). Exit code 0 = converted (with the limits listed in the report).
This is a Python entry point, not a stable CLI contract; it may change between previews.

## Migrating from the retired `IfcExporter.exe`

The call shape differs: `--output` is required and the result is a folder, not `<name>_ifc.xlsx` beside
the input. Steps that read the old XLSX/DAE names must be adapted; DAE is no longer produced.

## Updating

Replace the folder contents (keep this `README.md`) with the new portable zip.
All versions: <https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases>

Autodesk® and Revit® are trademarks of Autodesk, Inc. DDC is not affiliated with, endorsed by or
certified by Autodesk. File-format names (RVT, RFA, DWG, DXF) identify file formats only.
