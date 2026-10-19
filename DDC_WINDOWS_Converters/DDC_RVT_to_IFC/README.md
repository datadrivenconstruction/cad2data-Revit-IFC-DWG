# DDC RVT to IFC (portable, Windows x64)

Reads `.rvt` / `.rfa` files saved by Autodesk® Revit® and writes IFC export through the desktop app; the CLI is the same engine as in DDC RVT Converter.
Preview quality: always check `report.json` and `summary.json` next to the result.
The exact version is in `MANIFEST.json` in this folder. Licence: `EULA.txt`.

## Layout

```
DDC_RVT_to_IFC\
  Revit to IFC.exe              desktop app
  cli\RVTconverter.exe          command line (use this from scripts, n8n, notebooks)
  MANIFEST.json, licenses\, EULA.txt, README.html
```

Keep the whole folder together. Installer and zip of every version: [Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases).

## Command line

```bat
:: model -> GLB + summary.json + report.json in <name>.converted beside the input
cli\RVTconverter.exe "C:\Models\Project.rvt"

:: choose the output folder (it must not exist yet) and also write IFC4
cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out\Project" --ifc

:: property table (properties.jsonl), glTF, OBJ
cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out\Project2" --properties --gltf --obj
```

`cli\RVTconverter.exe --help` lists all options (IFC profiles, units, origin, category and phase filters).
Exit codes: 0 written, 2 written with reported gaps or invalid arguments, 1 failure.

## Migrating from the retired 18.x `RvtExporter.exe`

- Same call shape: `converter "model.rvt"`. Point your script to `cli\RVTconverter.exe`.
- Different output: a folder `<name>.converted` (GLB, JSON, optional `properties.jsonl`) instead of
  `<name>_rvt.xlsx` + `<name>_rvt.dae`. The old positional output arguments and `bbox` / `complete` /
  `sheets` style switches do not exist. The old flat table is rebuilt by `ddc convert` / `ddc table` (folder `ddc-tools` of this repository); the 3D model is the GLB.

## Updating

This folder is replaced as a whole by a newer release: delete the folder contents except this
`README.md`, then copy the contents of the new portable zip into it.

Autodesk® and Revit® are trademarks of Autodesk, Inc. DDC is not affiliated with, endorsed by or certified by Autodesk. File-format names (RVT, RFA, DWG, DXF) identify file formats only.
