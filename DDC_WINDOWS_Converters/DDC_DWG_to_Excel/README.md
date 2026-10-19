# DDC CAD drawing (.dwg) to Excel (portable, Windows x64, preview)

Own `.dwg` decoder. Per drawing writes `.xlsx`, `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json`,
`REPORT.txt` including counts of decoded / refused / unsupported records. Version: `MANIFEST.json`.
Licence: `EULA.txt`. Desktop app: `DWG to Excel.exe`.

## Command line

```bat
cli\dwg2excel.exe "C:\Drawings\plan.dwg" --output "C:\Out"
cli\dwg2excel.exe a.dwg b.dwg --output "C:\Out" --json --no-svg
```

A new sub-folder per drawing is created in the output folder. `--json` prints one JSON line per file.
See `cli\dwg2excel.exe --help` (`--no-dxf`, `--no-svg`, `--no-xlsx`, `--timeout`, `--memory-limit-mb`).

## Migrating from the retired `DwgExporter.exe`

Same idea (file in, tables out) but different arguments and result names; DGN is discontinued.
Steps that read old `<name>_dwg.xlsx` / `.dae` must be adapted.

## Updating

Replace the folder contents (keep this `README.md`) with the new portable zip.
Releases: [https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases)

Autodesk® and Revit® are trademarks of Autodesk, Inc. DDC is not affiliated with, endorsed by or certified by Autodesk. File-format names (RVT, RFA, DWG, DXF) identify file formats only.
