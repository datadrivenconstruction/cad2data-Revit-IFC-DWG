# DDC IFC to Excel 2.0 (portable, Windows x64)

Reads IFC2x3 / IFC4 (STEP and IFCZIP) and writes `drawing.xlsx`,
`data.jsonl`, `data.sqlite`, `result.json`. IFCXML is not supported. Version: `MANIFEST.json`.
Everything needed is in the package; nothing else has to be installed.
Licence: DDC EULA, <https://datadrivenconstruction.io/term-of-use-and-eula/>; third-party notices in `SOURCES.json`.

> **Licence: free for non-commercial use only.** Commercial use of the DDC converters requires a licence on
> request: [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io). Commercial use means use by or
> for a business or organisation, in paid work or services (including processing files for clients), in
> revenue-generating projects, or inside a product, service or SaaS offered to others. Personal learning,
> research, teaching and non-profit evaluation are non-commercial. Terms: [EULA](../../EULA.md) and
> [LICENSE-PROPRIETARY](../../LICENSE-PROPRIETARY). The MIT-licensed `ddc-tools` and the documentation are a separate, open-source licence.

## Desktop app

Double-click `IFC to Excel.exe` (or `Start IFC to Excel.cmd`), choose IFC file(s) and an output folder.

## Command line (scripts, n8n, notebooks)

```bat
runtime\python.exe sources\ifc-excel\converter.py "C:\Models\Building.ifc" --output "C:\Out"
```

Writes a sub-folder `<name>-<hash>` into the output folder and prints one JSON line
(`status`, `folder`, `data`, `errors`). Exit code 0 = converted (with the limits listed in the report).

## Flat table for scripts

`--output` is required and the result is a folder. A flat table (one row per element, sheet `Project_Data`) is rebuilt from `data.jsonl` / `data.sqlite` / `drawing.xlsx` by `ddc table` (folder `ddc-tools` of this repository); `ddc convert model.ifc` runs this converter and then `ddc table`.

## Updating

Replace the folder contents (keep this `README.md`) with the new portable zip.
All versions: <https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases>

Autodesk® and Revit® are trademarks of Autodesk, Inc. DDC is not affiliated with, endorsed by or
certified by Autodesk. File-format names (RVT, RFA, DWG, DXF) identify file formats only.
