# CAD2DATA Tools Overview

## Introduction

This document gives an overview of the tools in the CAD2DATA repository. The workflows, scripts, and documentation are MIT-licensed. The DDC converter binaries are proprietary software (see LICENSE-PROPRIETARY) distributed through GitHub Releases.

**Key features:**
- No Autodesk or CAD licence is required on the conversion machine
- Offline processing
- CLI interfaces for automation
- Output to open formats (XLSX, CSV, JSONL, SQLite, GLB, IFC, HTML)

**Status:** the converters below are previews. Quality is not fully qualified; every tool writes a report (`report.json`, `REPORT.txt`, `result.json`) that you should read before relying on the data.

---

## Where to get the converters

<https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases>

Suggested unpack folders: `C:\DDC\RVT-Converter\`, `C:\DDC\IFC-to-Excel\`, `C:\DDC\DWG-to-Excel\`.
Third-party components are listed in `THIRD_PARTY_NOTICES` inside each release package.

| Product | Version | Platform |
|---------|---------|----------|
| DDC RVT Converter | 0.6.8 | Windows (desktop app + CLI) |
| DDC RVT-to-IFC | 0.6.8 | Windows (desktop app, same engine and CLI) |
| DDC IFC to Excel | 0.3.1-preview | Windows (portable Python app) |
| DDC CAD drawing (.dwg) to Excel | 0.4.1 | Windows (CLI) |
| DDC Data Viewer | 0.1.1 (free) | Desktop (Tauri) |

Linux and macOS builds of the new converters are in preparation. The old Linux converter packages (`ddc-*converter`, `ddc-sdk-*`) are discontinued. MicroStation DGN conversion is discontinued (no own DGN reader).

---

## Converters

### DDC RVT Converter (and DDC RVT-to-IFC)

**Executables**: desktop app `RVT Converter.exe`, CLI `cli\RVTconverter.exe`

**Purpose**: Extract geometry and data from files created in Autodesk® Revit®

**Input**: `.rvt`, `.rfa` saved by Autodesk® Revit® 2019-2027

**Output** (folder `<stem>.converted`, never overwrites an existing folder):
- `native_graph.glb` - 3D model
- `summary.json`, `report.json` - summary and quality report
- with `--properties`: `properties.jsonl`, `property_scopes.jsonl`
- with `--ifc`: `native_graph.ifc` (IFC4, experimental)
- the desktop app also writes CSV tables and SQLite

**CLI Syntax**:
```bash
RVTconverter.exe "C:\Models\Project.rvt" [-o OUTDIR] [--properties] [--ifc] [--gltf] [--obj]
                 [--ifc-profile full|coordination|geometry|custom]
                 [--ifc-units m|mm]
                 [--ifc-origin internal|project-base-point|survey-point]
                 [--ifc-categories IDS]
```

**Exit codes**: `0` ok, `2` written with gaps (or bad arguments), `1` failure.

**Examples**:
```bash
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt"
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out" --properties
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" --ifc --ifc-profile coordination --ifc-units m --ifc-origin project-base-point
```

DDC RVT-to-IFC is a desktop app built on the same engine and CLI with IFC export as the default.

---

### DDC IFC to Excel

**Purpose**: Extract data from IFC files (portable Python app with its own IFC reader; no IfcOpenShell at runtime)

**Input**: IFC2x3 and IFC4, SPF and IFCZIP

**Output**: `drawing.xlsx`, `data.jsonl`, `data.sqlite`, `result.json`

**CLI Syntax**:
```bash
runtime\python.exe sources\ifc-excel\converter.py model.ifc --output OUTDIR
```

**Example**:
```bash
cd C:\DDC\IFC-to-Excel
runtime\python.exe sources\ifc-excel\converter.py "C:\Models\Model.ifc" --output "C:\Out\Model"
```

---

### DDC CAD drawing (.dwg) to Excel

**Purpose**: Extract data from `.dwg` drawings with an own `.dwg` decoder

**Input**: `.dwg`

**Output** (one folder per drawing): `.xlsx`, `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json`, `REPORT.txt`. The report states how many records were decoded, refused, or unsupported.

**CLI Syntax**:
```bash
dwg2excel.exe drawing.dwg -o OUTDIR [--json] [--no-dxf] [--no-svg] [--no-xlsx] [--language en|ru]
```

**Example**:
```bash
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Projects\Plan.dwg" -o "C:\Out" --json
```

---

### DDC Data Viewer

Free desktop viewer (Tauri) that opens XLSX / CSV / JSONL / Parquet tables with linked GLB / DAE 3D models.

---

## DDC CWICR — Semantic Search for Construction Work Items (Linux)

**Install**: APT packages (`ddc-qdrant`, `ddc-cwicr-cli`, `ddc-cwicr-{lang}`)

**Purpose**: Search 55,719 construction work items with costs and resources using keyword or semantic (AI-powered) search across 9 languages.

**Available languages**: `en` (CAD), `de` (EUR), `ru` (RUB), `fr` (EUR), `es` (EUR), `ar` (AED), `zh` (CNY), `pt` (BRL), `hi` (INR)

**Installation**:
```bash
# Qdrant vector database (runs as systemd service on port 6333)
sudo apt install ddc-qdrant

# Language data (each ~1 GB of pre-computed OpenAI embeddings)
sudo apt install ddc-cwicr-en ddc-cwicr-de ddc-cwicr-ru

# Search CLI
sudo apt install ddc-cwicr-cli
```

**CLI Usage**:
```bash
# Keyword search (no API key needed)
ddc-search --keyword "concrete foundation"

# Semantic search (requires OpenAI API key)
export OPENAI_API_KEY=sk-...
ddc-search "reinforced concrete foundation"

# JSON output with limit
ddc-search --json --limit 10 "floor tiles"

# Search in specific language
ddc-search --collection ddc_cwicr_de "Stahlbetonfundament"

# List installed collections
ddc-search --list
```

**Dependencies**:
| Package | Depends On |
|---------|-----------|
| `ddc-qdrant` | `libc6 (>= 2.31)`, `libssl3 \| libssl1.1`, `curl` |
| `ddc-cwicr-cli` | `python3 (>= 3.8)`, `ddc-qdrant` |
| `ddc-cwicr-{lang}` | `ddc-qdrant`, `curl` |

---

## Excel to Revit Update Tool

**Location**: `DDC_WINDOWS_Converters/DDC_Update_Revit_from_Excel/`

**Purpose**: An add-in for Autodesk® Revit® that syncs data from Excel back to the model. Its MSI installers were removed from git for legal reasons and are distributed separately.

**Workflow**: Revit -> Excel -> Transform -> Excel -> Revit

---

## n8n Workflows - Process Logic Templates

The `n8n_*.json` files are **visual representations of process logic** - not the final solution, but a foundation that can be implemented in any language or application.

**Use these workflows as:**
- Reference architecture for building your own pipelines
- Visual documentation of data processing logic
- Starting point for Python, JavaScript, C#, Go, or any implementation
- Templates for integration into enterprise systems

### 1. Basic Conversion
**File**: `n8n_1_Revit_IFC_DWG_Conversation_simple.json`

**Logic**: Simple file conversion flow for Revit, IFC, DWG files.

### 2. Advanced Settings
**File**: `n8n_2_All_Settings_Revit_IFC_DWG_Conversation_simple.json`

**Logic**: Configurable export modes (basic/standard/complete) and options handling.

### 3. Batch Processing
**File**: `n8n_3_CAD-BIM-Batch-Converter-Pipeline.json`

**Logic**: Batch conversion with validation, metrics tracking, and report generation.

### 4. BIM Validation
**Files**:
- `n8n_4_Validation_CAD_BIM_Revit_IFC_DWG.json`
- `n8n_4_DDC_BIM_Requirements_Table_for_Revit_IFC_DWG.xlsx`

**Logic**: Validate CAD/BIM data against predefined rules, generate color-coded reports.

### 5. AI Classification
**File**: `n8n_5_CAD_BIM_Automatic_Classification_with_LLM_and_RAG.json`

**Logic**: AI-powered element classification using LLM and RAG. Supports any classification system.

### 6. Cost Estimation
**File**: `n8n_6_Construction_Price_Estimation_with_LLM_for_Revt_and_IFC.json`

**Logic**: Cost estimation pipeline with AI classification and market prices.

### 7. Carbon Footprint
**File**: `n8n_7_Carbon_Footprint_CO2_Estimator_for_Revit and_IFC.json`

**Logic**: Calculate embodied carbon emissions (A1-A3 lifecycle stages).

### 8. ETL for LLM
**File**: `n8n_8_Revit_IFC_DWG_Conversation_EXTRACT_Phase_with_Parse_XLSX.json`

**Logic**: Data preparation and transformation for LLM-based automation.

### 9. QTO Reports
**File**: `n8n_9_CAD_BIM_Quantity_TakeOff_HTML_Report_Generator.json`

**Logic**: Generate quantity take-off reports with aggregation and visualization.

**The logic shown in n8n can be reproduced in:** Python, JavaScript/Node.js, C#, Go, Rust, or any language that can call CLI tools and process XLSX/JSON.

---

## Output Format Details

### XLSX / CSV (tables)

Structure: elements (or drawing entities) as rows, properties as columns

```
| ElementId | Category | Type Name | Area | Volume | Material | Level | ... |
|-----------|----------|-----------|------|--------|----------|-------|-----|
| 123456    | Walls    | Basic Wall| 45.5 | 12.3   | Concrete | 01    | ... |
```

Written by DDC IFC to Excel and DDC CAD drawing (.dwg) to Excel (the exact columns depend on the source).

### JSONL / SQLite

- One JSON object per line (`properties.jsonl`, `data.jsonl`)
- `data.sqlite` from DDC IFC to Excel; the RVT desktop app also writes SQLite

### GLB (3D model)

- `native_graph.glb` from DDC RVT Converter
- Opens in any glTF viewer and in DDC Data Viewer

### IFC

- `native_graph.ifc` from DDC RVT Converter / RVT-to-IFC (`--ifc`): IFC4, experimental

### DXF / SVG

- Drawing geometry written by DDC CAD drawing (.dwg) to Excel

### HTML

- Interactive reports with charts
- Generated by n8n workflows
- Self-contained, shareable

---

## Integration Examples

### Python (subprocess)
```python
import subprocess
result = subprocess.run([
    r"C:\DDC\RVT-Converter\cli\RVTconverter.exe",
    r"C:\Projects\Building.rvt",
    "-o", r"C:\Out", "--properties"
], capture_output=True, text=True)
# result.returncode: 0 ok, 2 written with gaps, 1 failure
```

### PowerShell (batch)
```powershell
Get-ChildItem "C:\Projects\*.rvt" | ForEach-Object {
    & "C:\DDC\RVT-Converter\cli\RVTconverter.exe" $_.FullName -o "C:\Out" --properties
}
```

### Node.js
```javascript
const { execSync } = require('child_process');
execSync('C:\\DDC\\RVT-Converter\\cli\\RVTconverter.exe "C:\\Projects\\Building.rvt" -o "C:\\Out" --properties');
```

### n8n (Execute Command node)
```javascript
C:\DDC\RVT-Converter\cli\RVTconverter.exe "{{ $json.filePath }}" -o "C:\Out" --properties
```

---

## Prerequisites

**Windows**: unpack the release packages to the suggested folders. See the README inside each package for runtime requirements.

**Linux**: only the CWICR packages (`ddc-qdrant`, `ddc-cwicr-cli`, `ddc-cwicr-{lang}`) are available; they require Ubuntu 20.04+ / Debian 11+ (amd64).

---

## Documentation

- **Book**: `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` (in AI_AGENTS_INSTRUCTIONS folder)
- **PDF Guide**: `GuideBook_DataDrivenConstruction_Book_2ndEdition_ArtemBoiko_2025_en-US.pdf`
- **Sample Data**: `Sample_Projects/` folder

---

## License

Workflows, scripts, and documentation: MIT License. DDC converter binaries: proprietary (see LICENSE-PROPRIETARY and NOTICE).

---

*Building blocks for construction automation.*
