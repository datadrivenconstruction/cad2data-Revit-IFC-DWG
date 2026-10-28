# DDC IFC to Excel 2.0.0 (portable, Windows x64)

Reads IFC2x3 / IFC4 (STEP and IFCZIP) and writes `Name.xlsx` and
`result.json`. IFCXML is not supported. Version: `MANIFEST.json`.
**Download:** [DDC-IFC-to-Excel-2.0.0-portable.zip](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v2026.10.0/DDC-IFC-to-Excel-2.0.0-portable.zip) (release [v2026.10.0](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.0); SHA-256 in `MANIFEST.json`). This folder holds only the pointer; unzip the package anywhere.
Everything needed is in the package; nothing else has to be installed.
Licence: DDC EULA, <https://datadrivenconstruction.io/term-of-use-and-eula/>; third-party notices in the `licenses` folder of the package.

> **Licence: free for non-commercial use only.** Commercial use of the DDC converters requires a licence on
> request: [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io). Commercial use means use by or
> for a business or organisation, in paid work or services (including processing files for clients), in
> revenue-generating projects, or inside a product, service or SaaS offered to others. Personal learning,
> research, teaching and non-profit evaluation are non-commercial. Terms: [EULA](../../EULA.md) and
> [LICENSE-PROPRIETARY](../../LICENSE-PROPRIETARY). The MIT-licensed `ddc-tools` and the documentation are a separate, open-source licence.

## Desktop app

Unzip the release package and double-click `IFC to Excel.exe`, choose IFC file(s) and an output folder.

## Command line (scripts, n8n, notebooks)

```bat
"IFC to Excel.exe" "C:\Models\Building.ifc" --output "C:\Out"
```

Writes a sub-folder per model into the output folder and prints one JSON line
(`status`, `folder`, `data`). Exit code 0 = converted (with the limits listed in `result.json`).

## Flat table for scripts

`--output` is required and the result is a folder. A flat table (one row per element, sheet `Project_Data`) is rebuilt from the converter output by `ddc table` (folder `ddc-tools` of this repository); `ddc convert model.ifc` runs this converter and then `ddc table`.

## Updating

Download the newer portable zip and unzip it over the old folder.
All versions: <https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases>

See Trademarks in the main README.
