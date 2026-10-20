# DDC CAD drawing (.dwg) to Excel 2.0 (portable, Windows x64)

Reads `.dwg` drawings. Per drawing writes `.xlsx`, `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json`,
`REPORT.txt` including counts of decoded / skipped / unsupported records. Version: `MANIFEST.json`.
Licence: `EULA.txt`. Desktop app: `DWG to Excel.exe`.

## Command line

```bat
cli\dwg2excel.exe "C:\Drawings\plan.dwg" --output "C:\Out"
cli\dwg2excel.exe a.dwg b.dwg --output "C:\Out" --json --no-svg
```

A new sub-folder per drawing is created in the output folder. `--json` prints one JSON line per file.
See `cli\dwg2excel.exe --help` (`--no-dxf`, `--no-svg`, `--no-xlsx`, `--timeout`, `--memory-limit-mb`).

## Flat table for scripts

A flat table (one row per entity) can be built from the `.jsonl` / `.csv` by `ddc table` (folder `ddc-tools` of this repository); `ddc convert drawing.dwg` runs this converter and then `ddc table`.

## Updating

Replace the folder contents (keep this `README.md`) with the new portable zip.
Releases: [https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases)

Autodesk® and Revit® are trademarks of Autodesk, Inc. DDC is not affiliated with, endorsed by or certified by Autodesk. File-format names (RVT, RFA, DWG, DXF) identify file formats only.
