# DDC Windows Converters — Proprietary Software

> **The DDC binaries are NOT MIT-licensed.**
> They are proprietary software licensed under the
> DataDrivenConstruction Proprietary Software License and the
> DataDrivenConstruction Terms of Use and EULA at
> <https://datadrivenconstruction.io/term-of-use-and-eula/>.
>
> See [LICENSE-PROPRIETARY.txt](./LICENSE-PROPRIETARY.txt) and
> [EULA.txt](./EULA.txt) in this folder, and [NOTICE](../NOTICE)
> at the repository root, for the full terms.

## Converters in this folder

Each sub-folder is a ready-to-run **portable** build for Windows x64 (unpack nothing, just use it).
Installers (`Setup.exe`) and zip packages of every version are on the
[Releases page](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases).
Current release: [v2026.10.0](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.0).

| Product | Version | Folder (portable) | Installer / zip in the release | What it does |
|---|---|---|---|---|
| DDC RVT Converter | 0.6.9 | [`DDC_RVT_Converter/`](./DDC_RVT_Converter/) | [Setup](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v2026.10.0/DDC-RVT-Converter-0.6.9-Setup.exe) / [zip](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v2026.10.0/DDC-RVT-Converter-0.6.9-portable.zip) | Reads `.rvt` / `.rfa` files saved by Autodesk® Revit® 2019–2027. Writes GLB, JSON summary/report, optional property tables and experimental IFC4. Desktop app `RVT Converter.exe` and CLI `cli\RVTconverter.exe`. |
| DDC RVT-to-IFC | 0.6.9 | [`DDC_RVT_to_IFC/`](./DDC_RVT_to_IFC/) | [Setup](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v2026.10.0/DDC-RVT-to-IFC-0.6.9-Setup.exe) / [zip](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v2026.10.0/DDC-RVT-to-IFC-0.6.9-portable.zip) | Same engine and CLI as DDC RVT Converter; the desktop app exports IFC by default. |
| DDC IFC to Excel | 0.3.1-preview | [`DDC_IFC_to_Excel/`](./DDC_IFC_to_Excel/) | [zip](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v2026.10.0/DDC-IFC-to-Excel-0.3.1-preview-portable.zip) (no Setup yet) | Own IFC reader (IFC2x3 / IFC4, SPF and IFCZIP). Writes `drawing.xlsx`, `data.jsonl`, `data.sqlite`, `result.json`. |
| DDC CAD drawing (.dwg) to Excel | 0.4.1 | [`DDC_DWG_to_Excel/`](./DDC_DWG_to_Excel/) | [Setup](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v2026.10.0/DDC-DWG-to-Excel-0.4.1-Setup.exe) / [zip](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v2026.10.0/DDC-DWG-to-Excel-0.4.1-portable.zip) | Own `.dwg` decoder. Writes `.xlsx`, `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json`, `REPORT.txt`. |
| DDC Data Viewer | 0.1.2 | [`DDC_Data_Viewer/`](./DDC_Data_Viewer/) | [Setup](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v2026.10.0/DDC-Data-Viewer-0.1.2-Setup.exe) / [zip](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v2026.10.0/DDC-Data-Viewer-0.1.2-portable.zip) | Free desktop viewer for XLSX / CSV / JSONL / Parquet tables with linked GLB / DAE 3D models. |
| DDC Excel add-in | 2026.10.0 preview | [`DDC_Excel_Addin/`](./DDC_Excel_Addin/) | [zip](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v2026.10.0/DDC-Excel-AddIn-2026.10.0-unsigned.zip) (not code-signed) | Excel add-in: imports RVT, IFC and DWG as tables through the converters above (downloaded on first use, SHA-256 checked). Documentation only in this folder. |
| DDC Excel to Revit (add-in) | — | [`DDC_Update_Revit_from_Excel/`](./DDC_Update_Revit_from_Excel/) | distributed separately | Add-in for Autodesk® Revit®: round-trip updates from tabular data into a Revit model. Documentation and samples only. |

**Status: the converters are previews.** Quality has not been fully qualified. Check the
`report.json` / `REPORT.txt` / `result.json` files that each tool writes, and verify results on your
own data before relying on them. MicroStation DGN conversion is discontinued (there is no own DGN reader).

## Quick start

1. Clone or download this repository (or just the sub-folder you need). Keep the product folder intact.
2. Run a converter from the command line (from this folder):

```bat
:: Revit file -> GLB + JSON in "Project.converted" beside the input
DDC_RVT_Converter\cli\RVTconverter.exe "C:\Models\Project.rvt"

:: IFC file -> Excel / JSONL / SQLite
DDC_IFC_to_Excel\runtime\python.exe DDC_IFC_to_Excel\sources\ifc-excel\converter.py "C:\Models\Building.ifc" --output "C:\Out"

:: DWG file -> Excel / CSV / DXF / SVG
DDC_DWG_to_Excel\cli\dwg2excel.exe "C:\Drawings\plan.dwg" --output "C:\Out"
```

3. Or double-click the desktop app in the product folder (`RVT Converter.exe`, `Revit to IFC.exe`,
   `IFC to Excel.exe`, `DWG to Excel.exe`, `DDC Data Viewer.exe`).

Every product folder has its own `README.md` with more CLI examples.
The n8n workflows and Jupyter notebooks in this repository use these paths
(see [DDC_n8n_Workflows&Pipelines](../DDC_n8n_Workflows&Pipelines/) and
[DDC_in_additon](../DDC_in_additon/)).

## Updating a product

Each product folder holds exactly the contents of the portable zip of one release, plus a
version-neutral `README.md`. A new version replaces the folder contents; the folder name and paths do not change.
The version is stored in `MANIFEST.json` inside each folder.

## Files too large for git

GitHub rejects files above 100 MB and Git LFS is not used. Every file here is below that limit
(the largest, the RVT desktop app, is about 78 MB). If a future build exceeds ~95 MB, only the
release package will carry it and the product folder will say so in its `README.md`.

## How the binaries relate to the MIT-licensed parts of the repo

The repository's MIT-licensed n8n workflows, AI agent instructions, Python utilities, and samples
orchestrate the converters via subprocess calls. You may freely study, modify, and redistribute the
MIT-licensed orchestration files; you may NOT redistribute the DDC binaries without a separate
commercial licence.

Third-party components of each package are listed in its `licenses/` or `THIRD_PARTY_NOTICES` files.

## Trademarks

Autodesk®, Revit®, AutoCAD®, and Navisworks® are registered trademarks or trademarks of Autodesk,
Inc., and/or its subsidiaries and/or affiliates in the USA and/or other countries. MicroStation® is
a registered trademark of Bentley Systems, Incorporated. IFC and buildingSMART® are trademarks of
buildingSMART International Ltd. All other trademarks belong to their respective owners. File-format
names (RVT, RFA, DWG, DXF, DGN) are used only to identify file formats.

DataDrivenConstruction is not affiliated with, endorsed by, sponsored by, or certified by Autodesk,
Inc. or Bentley Systems, Incorporated. DDC products are independent software developed for
interoperability. They do not contain or use Autodesk software, SDKs (including the Revit API or
RealDWG), or Autodesk source code. See also [TRADEMARK.md](../TRADEMARK.md).

## Export control

Classified EAR99 under U.S. Export Administration Regulations (15 CFR Parts 730-774) and subject to
EU Regulation 2021/821 and the German Außenwirtschaftsgesetz. Do not export to jurisdictions subject
to comprehensive U.S. or EU sanctions, or to sanctioned persons. See [NOTICE](../NOTICE) for details.

## Contact

All enquiries (general, commercial licensing, security, privacy):
**info@datadrivenconstruction.io**
