<p align="center">
  <a href="README.md">English</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.fr.md">Français</a> •
  <a href="README.ru.md">Русский</a> •
  <a href="README.zh.md">中文</a> •
  <a href="README.ar.md">العربية</a>
</p>

<h1 align="center">cad2data — DDC converters for RVT, IFC and DWG files</h1>

<p align="center">
  <b>Turn CAD/BIM files into open, structured data — locally, offline, without CAD licences.</b><br>
  .rvt / .rfa → GLB · glTF · OBJ · IFC4 · JSONL/CSV &nbsp;|&nbsp; .ifc → Excel · JSONL · SQLite &nbsp;|&nbsp; .dwg → Excel · CSV · JSONL · DXF · SVG
</p>

<p align="center">
  <a href="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest"><img src="https://img.shields.io/github/v/release/datadrivenconstruction/cad2data-Revit-IFC-DWG?label=release" alt="Latest release"></a>
  <img src="https://img.shields.io/badge/input-.rvt%20.rfa%20.ifc%20.ifczip%20.dwg-blue" alt="Input formats">
  <img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.jsonl%20.glb%20.ifc%20.dxf%20.svg-green" alt="Output formats">
  <img src="https://img.shields.io/badge/platform-Windows%20x64%20%7C%20Linux%2FmacOS%20soon-lightgrey" alt="Windows x64; Linux and macOS coming soon">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT%20(workflows%2C%20docs)%20%2B%20freeware%20EULA%20(converters)-blue" alt="Licence"></a>
</p>

<p align="center">
  <img src="docs/images/data-viewer-3d-grouped.png" alt="DDC Data Viewer: table grouped by category and level with the linked 3D model" width="100%">
</p>

---

## What changed in October 2026

The converters in this repository were rebuilt on **DataDrivenConstruction's own file readers**.
They no longer depend on any third-party CAD SDK:

| Format | Reader | Implementation |
|---|---|---|
| `.rvt` / `.rfa` | DDC RVT reader | Rust, first-party code |
| `.ifc` / `.ifczip` | DDC IFC reader | Python, first-party code (no IfcOpenShell at runtime) |
| `.dwg` | DDC DWG reader | Python, first-party code |

What this means for you:

- **New binaries, new command lines.** The old `RvtExporter.exe`, `IfcExporter.exe`, `DwgExporter.exe`,
  `DgnExporter.exe` and `RVT2IFCconverter.exe` (generation 18.x) are retired and are no longer in the
  repository tree. The new converters are in [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) (portable, ready to run)
  and are also published as installers and packages on the
  [Releases page](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases).
- **DGN is discontinued** for now — there is no first-party DGN reader yet.
- **All new converters are previews.** Every run writes a machine-readable report with what was read,
  what was skipped and why. Please check it before relying on the output (see [Limitations](#limitations)).
- Older releases and the git history stay available for reference.

## Contents

- [Converters](#converters)
- [Screenshots](#screenshots)
- [Quick start](#quick-start)
- [Command line](#command-line)
- [Batch processing and automation](#batch-processing-and-automation)
- [DDC Data Viewer](#ddc-data-viewer)
- [Free tools: data check, quantity take-off, Power BI and Excel](#free-tools-data-check-quantity-take-off-power-bi-and-excel)
- [n8n workflows, notebooks and AI agents](#n8n-workflows-notebooks-and-ai-agents)
- [Limitations](#limitations)
- [Repository layout](#repository-layout)
- [Licensing](#licensing)
- [Trademarks](#trademarks)

## Converters

| Package | Version | Reads | Writes | Interface |
|---|---|---|---|---|
| **DDC RVT Converter** | 0.6.8 | `.rvt`, `.rfa` saved by Autodesk® Revit® 2019–2027 | GLB (default), glTF, OBJ, IFC4 (experimental), saved properties as JSONL; the desktop app also writes CSV tables and SQLite | Desktop app + `RVTconverter.exe` CLI |
| **DDC RVT to IFC** | 0.6.8 | `.rvt`, `.rfa` | IFC4 with property sets, quantities, classification, materials; profiles `full`, `coordination`, `geometry` | Desktop app (same CLI engine) |
| **DDC IFC to Excel** | 0.3.1 preview | IFC2x3 / IFC4 STEP files, `.ifczip` | `drawing.xlsx` (objects, properties, quantities), `data.jsonl`, `data.sqlite`, `result.json` | Desktop app + Python CLI (bundled runtime) |
| **DDC DWG to Excel** | 0.4.1 | `.dwg` drawings, R13–2018 format versions | `.xlsx` (Entities, Summary, Layers, Blocks), `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json` | Desktop app + `dwg2excel.exe` CLI |
| **DDC Data Viewer** | 0.1.2 | `.xlsx`, `.csv`, `.jsonl`, `.parquet` tables + `.glb` / `.dae` geometry | filtered views to XLSX / CSV | Desktop app (free) |

Every geometry node written by the RVT Converter keeps the native element id, so tables and 3D can be
joined by `ElementId`. All packages run fully offline on Windows 10/11 x64 and need no Autodesk
software, no Excel and no Python installation. Linux / macOS builds — coming soon.

## Screenshots

All screenshots below come from real runs of the packages in the current release. They use the
viewer's synthetic sample building and the open IFC sample in [`Sample_Projects/`](Sample_Projects/).

| | |
|---|---|
| ![Data Viewer: 3D selection linked to table rows](docs/images/data-viewer-3d-selection.png) | ![IFC to Excel output in the Data Viewer, grouped by IFC class](docs/images/ifc-to-excel-table.png) |
| **DDC Data Viewer** — a filter on *Structural Columns* highlights the linked elements in 3D; the summary panel sums area, volume and length. | **DDC IFC to Excel** — `drawing.xlsx` of the open Duplex IFC sample, grouped by IFC class (333 objects, 23 classes). |
| ![Command line runs of RVTconverter and IFC to Excel](docs/images/cli-rvt-ifc.png) | ![Data Viewer in dark theme with Russian interface](docs/images/data-viewer-dark-ru.png) |
| **Command line** — `RVTconverter.exe` writes GLB + IFC4 with a status line and report; IFC to Excel prints a JSON status (output abridged). | **Dark theme and localisation** — the viewer ships in English, German and Russian. |

## Quick start

1. Open the [latest release](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest)
   and download the package you need — a `*-Setup.exe` (per-user installer) or a `*-portable.zip`.
2. Verify the download against `SHA256SUMS.txt` from the same release:
   ```powershell
   Get-FileHash .\DDC-RVT-Converter-0.6.8-portable.zip -Algorithm SHA256
   ```
3. Unzip the portable package to a folder of your choice, for example `C:\DDC\RVT-Converter\`,
   `C:\DDC\IFC-to-Excel\`, `C:\DDC\DWG-to-Excel\`. Keep the folder structure as it is.
4. Start the desktop app (`RVT Converter.exe`, `IFC to Excel.exe`, `DWG to Excel.exe`), drop files or
   folders into the window and press *Convert* — or use the command line below.
5. Open the result in Excel, Python/pandas or the [DDC Data Viewer](#ddc-data-viewer).

The packages are not code-signed yet, so Windows SmartScreen may ask for confirmation on first start.

## Command line

The examples below were run with the binaries of the current release. Paths assume the portable
packages were unpacked to `C:\DDC\`.

### DDC RVT Converter — `RVTconverter.exe`

```powershell
# GLB + reports into "Project.converted" next to the input (existing folders are never overwritten)
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt"

# choose the output folder, add saved properties (JSONL) and an IFC4 file
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out\Project" --properties --ifc

# IFC for coordination: millimetres, survey point origin, only doors and windows
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" --ifc --ifc-profile coordination `
    --ifc-units mm --ifc-origin survey-point --ifc-categories Doors,Windows

# additional geometry formats
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Family.rfa" --gltf --obj
```

| Output | When | Content |
|---|---|---|
| `native_graph.glb` | always | 3D meshes, one node per element, named by ElementId |
| `summary.json`, `report.json` | always | status, counts, omissions and per-element diagnostics |
| `properties.jsonl`, `property_scopes.jsonl` (+ manifests) | `--properties` | saved parameters per element (one JSON object per line) |
| `native_graph.ifc`, `ifc.manifest.json`, `ifc.settings.json` | `--ifc` | IFC4 (tessellated geometry, property and quantity sets) |
| `native_graph.gltf` + `.bin`, `native_graph.obj` + `.mtl` | `--gltf`, `--obj` | same geometry as GLB; OBJ in metres, Y-up |

Exit codes: `0` written without reported gaps, `2` written with reported gaps (or invalid arguments),
`1` conversion or I/O failure. Run `RVTconverter.exe --help` for all IFC options
(`--ifc-config`, `--ifc-phase`, `--ifc-design-options`, `--ifc-exclude-categories`, …).

### DDC IFC to Excel

The portable package bundles its own Python runtime; the CLI is the converter module:

```powershell
C:\DDC\IFC-to-Excel\runtime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py `
    "C:\Models\Building.ifc" --output "C:\Out\Building"
```

The command prints one JSON line (`"status": "CONVERTED"`, `"CONVERTED_WITH_LIMITS"` or `"FAILED"`)
and creates a new sub-folder with `drawing.xlsx`, `data.jsonl`, `data.sqlite` and `result.json`.
`.ifczip` files are accepted directly.

### DDC DWG to Excel — `dwg2excel.exe`

```powershell
# one or more drawings; a new sub-folder per drawing
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"

# a whole folder: tables only, one JSON line per file for scripts
$dwg = (Get-ChildItem C:\Drawings -Filter *.dwg).FullName
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe @dwg -o C:\Out --no-dxf --no-svg --json
```

Each drawing folder contains `<name>.xlsx`, `<name>.csv`, `<name>.jsonl`, `<name>.dxf`, `<name>.svg`,
`report.json` and `REPORT.txt`. The console line reports how many records were decoded, refused or are
of a type the reader does not support yet. Other options: `--timeout`, `--memory-limit-mb`,
`--language en|ru`, `--version`.

## Batch processing and automation

**PowerShell — every RVT file in a folder tree:**

```powershell
$exe = "C:\DDC\RVT-Converter\cli\RVTconverter.exe"
Get-ChildItem "C:\Projects" -Recurse -Include *.rvt | ForEach-Object {
    & $exe $_.FullName -o (Join-Path "C:\Out" $_.BaseName) --properties --ifc
    "{0}: exit {1}" -f $_.Name, $LASTEXITCODE
}
```

**Python — load RVT properties and IFC tables with pandas:**

```python
import json, subprocess, pandas as pd

subprocess.run([r"C:\DDC\RVT-Converter\cli\RVTconverter.exe", r"C:\Models\Project.rvt",
                "-o", r"C:\Out\Project", "--properties"], check=False)
rows = [json.loads(line) for line in open(r"C:\Out\Project\properties.jsonl", encoding="utf-8")]
print(len(rows), "property records")

objects = pd.read_excel(r"C:\Out\Building\Building-<id>\drawing.xlsx", sheet_name="Objects")
print(objects.groupby("Category").size().sort_values(ascending=False))
```

**DWG in CI or bots:** `dwg2excel.exe --json` prints one JSON line per drawing; parse it to collect
status, output folder and decode statistics.

## DDC Data Viewer

A free desktop viewer for the converter output: virtualised grid for 100k+ rows, search, filters,
grouping with sums, column chooser, export of the current view to XLSX/CSV and a 3D panel that links
rows and elements both ways (GLB or DAE). English, German and Russian; light and dark theme.
Download `DDC-Data-Viewer-0.1.2-Setup.exe` or the portable zip from the release.

## Free tools: data check, model diff, BCF issues, quantity take-off, Power BI and Excel

[`ddc-tools/`](ddc-tools/) (Python 3.9+, MIT, offline) works on the tables the converters write
(XLSX, CSV, JSONL, SQLite, JSON):

- `ddc check` validates an export against YAML rules (required parameters, regex, uniqueness, ranges,
  allowed values) and writes a traffic-light XLSX with ElementId / GlobalId details, a JSON report and an
  exit code for CI.
- `ddc diff` compares two exports of a model (RVT, IFC or DWG converter output): added / removed / modified elements,
  old to new values per property and quantity, changelog XLSX, JSON, a GLB coloured by change status and an exit code for CI.
- `ddc bcf` writes the findings of `ddc check` and `ddc diff` as BCF 2.1 / 3.0 issue files (components by IFC GlobalId) and
  tabulates any BCF file into XLSX. BCF is an open buildingSMART format; no certification is claimed.
- `ddc qto` sums count, length, area and volume by category, type and level into a formatted XLSX and warns
  about missing or zero quantities.
- [`ddc-tools/powerbi/`](ddc-tools/powerbi/) and [`ddc-tools/excel/`](ddc-tools/excel/): Power Query scripts
  and an Excel workbook that read a whole export folder, no Python needed
  ([steps](ddc-tools/docs/POWER_QUERY.md)).

```bash
pip install ./ddc-tools
ddc check Project.converted --rules ddc-tools/examples/rules_basic.yaml --xlsx check.xlsx
ddc qto Project.converted --xlsx qto.xlsx
ddc diff Model_v1.converted Model_v2.converted --xlsx changes.xlsx --glb diff.glb --bcf changes.bcf
```

Excel and Power BI are trademarks of Microsoft Corporation, used only to say what the files work with.

## n8n workflows, notebooks and AI agents

- [`DDC_n8n_Workflows&Pipelines/`](DDC_n8n_Workflows&Pipelines/) — nine n8n workflows (conversion,
  batch validation, AI classification, cost and CO2 estimation, QTO reports).
- [`DDC_in_additon/DDC_python_pipelines/`](DDC_in_additon/DDC_python_pipelines/) — Jupyter notebooks for
  conversion, batch processing and analytics.

> **Status:** the workflows and notebooks were written for the retired 18.x command line (`RvtExporter.exe` producing XLSX +
> DAE). They are ported: they call the converters in [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) through `ddc convert` /
> `ddc table` (free tool [`ddc-tools/`](ddc-tools/)), which rebuilds the old flat table (`<name>_rvt.xlsx`, sheet `Project_Data`:
> `ID`, `Category`, `Type Name`, `Level`, `Volume`, ...) from `properties.jsonl` / IFC / DWG output; DAE is replaced by GLB.
> One-time setup: `pip install ddc-tools\`. The `README.md` next to the workflows and notebooks says what was checked and what is
> not covered (for example: the AI steps of n8n 5-7 need your credentials and were not run; schedules, sheet PDFs and DGN have no
> equivalent; Revit quantities come from IFC quantities or the GLB mesh, not from Revit's own values).

- [`AI_AGENTS_INSTRUCTIONS/`](AI_AGENTS_INSTRUCTIONS/) — ready context for coding agents
  (Claude Code, OpenCode, Antigravity and others) with the new command lines. Open the repository in your
  agent and ask, for example, *"convert every .rvt in C:\Projects to IFC and summarise the reports"*.
- [DDC Skills for AI agents](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction)
  — ready-made automations for construction data.

## Limitations

The converters are honest previews. Specifically:

- **RVT:** geometry completeness is not certified; textures are not exported; source colours are
  experimental; storage variants the reader does not understand are reported, not guessed. IFC export is
  tessellated IFC4 and is not schema-validated by the tool itself.
- **IFC:** IFCXML is not supported; computed properties and full source fidelity are not qualified;
  original records always remain in `data.jsonl` / `data.sqlite`.
- **DWG:** decoding coverage depends on the drawing: some object types (for example certain tables,
  multileaders, 3D solids, images) are reported as *unsupported* or *refused* instead of being exported
  incorrectly. Check `report.json` for every drawing.
- **DGN:** not supported in the current generation.
- **Platforms:** Windows 10/11 x64. **Linux / macOS — coming soon.**

Bug reports with a small example file are very welcome — please use
[GitHub Issues](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/issues) and do not attach
confidential models.

## Repository layout

| Path | Content |
|---|---|
| `docs/` | release notes, screenshots |
| `ddc-tools/` | free data check, model diff, BCF issues, quantity take-off, Power BI and Excel kit |
| `DDC_n8n_Workflows&Pipelines/` | n8n workflow JSON files |
| `DDC_in_additon/` | notebooks, presentations, images |
| `AI_AGENTS_INSTRUCTIONS/` | instructions for AI coding agents |
| `DDC_WINDOWS_Converters/` | portable Windows converters (RVT, RVT-to-IFC, IFC to Excel, DWG to Excel, Data Viewer), licence texts and the Excel → Revit add-in documentation; installers are on the Releases page |
| `DDC_LINUX_Converters/` | CWICR data packages, Qdrant packaging and telemetry dashboard |
| `Sample_Projects/` | open IFC sample files |

## Licensing

- **Workflows, notebooks, scripts, AI instructions and documentation** — [MIT License](LICENSE).
- **Converter packages** (Releases) — one free edition (no paid tier), free of charge for private and commercial use under the
  DataDrivenConstruction EULA shipped in each package (`EULA.txt`); see also
  [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) and [NOTICE](NOTICE). Third-party open-source components
  and their licences are listed in `licenses/` inside each package.
- Commercial redistribution, OEM or SaaS integration: [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io).

Security reports: see [SECURITY.md](SECURITY.md). Patents, trademarks and export control:
[PATENTS.md](PATENTS.md), [TRADEMARK.md](TRADEMARK.md), [EXPORT-COMPLIANCE.md](EXPORT-COMPLIANCE.md).

## Consulting and training

DataDrivenConstruction helps construction, engineering and technology companies automate CAD/BIM data
processing and build open ETL pipelines — workshops, consulting and prototypes on your real data.
Contact [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io) or visit
[datadrivenconstruction.io](https://datadrivenconstruction.io).

<p>
  <a href="https://x.com/datadrivenconst"><img src="https://img.shields.io/twitter/follow/datadrivenconst?logo=X&style=flat&color=%23f5f5f5" alt="Follow on X"></a>
  <a href="https://www.youtube.com/@datadrivenconstruction"><img src="https://img.shields.io/badge/YouTube-FF0000?logo=youtube&logoColor=white" alt="YouTube"></a>
  <a href="https://www.linkedin.com/company/78381569"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?logoColor=white" alt="LinkedIn"></a>
</p>

If these tools are useful to you, please star the repository to get notified about new releases.

## Trademarks

Autodesk®, Revit®, AutoCAD®, and Navisworks® are registered trademarks or trademarks of Autodesk, Inc.,
and/or its subsidiaries and/or affiliates in the USA and/or other countries. MicroStation® is a registered
trademark of Bentley Systems, Incorporated. IFC and buildingSMART® are trademarks of buildingSMART
International Ltd. All other trademarks belong to their respective owners. File-format names (RVT, RFA,
DWG, DXF, DGN) are used only to identify file formats.

DataDrivenConstruction is not affiliated with, endorsed by, sponsored by, or certified by Autodesk, Inc.
or Bentley Systems, Incorporated. DDC products are independent software developed for interoperability.
They do not contain or use Autodesk software, SDKs (including the Revit API or RealDWG), or Autodesk
source code.
