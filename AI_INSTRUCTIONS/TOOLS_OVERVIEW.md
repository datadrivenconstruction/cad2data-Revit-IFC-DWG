# CAD2DATA Tools Overview

## Introduction

This document provides a comprehensive overview of all tools in the CAD2DATA repository. All tools are open-source (MIT) and can be integrated into any solution.

**Key features:**
- No Autodesk or CAD licenses required
- Offline processing
- CLI interfaces for automation
- Output to open formats (XLSX, DAE, IFC, PDF, HTML)

---

## Converters

### RvtExporter.exe - Revit Data Extractor

**Location**: `DDC_CONVERTER_REVIT/datadrivenlibs/RvtExporter.exe`

**Purpose**: Extract data and geometry from Autodesk Revit files

**Input**: `.rvt`, `.rfa` (Revit 2015-2026)

**Output**:
- XLSX database (elements as rows, properties as columns)
- DAE (Collada 3D geometry with element IDs matching XLSX)
- PDF (sheets/drawings)
- Revit Schedules

**CLI Syntax**:
```bash
RvtExporter.exe <input.rvt> [output.dae] [output.xlsx] [export_mode] [options]

# Export modes:
#   basic    - 309 categories
#   standard - 724 categories
#   complete - 1209 categories (all)
#   custom   - user-defined categories from .txt file

# Options:
#   bbox       - Include element bounding boxes in XLSX
#   room       - Include ToRoom/FromRoom data
#   schedule   - Export all Revit schedules
#   sheets2pdf - Export all sheets to PDF
#   -no-xlsx   - Disable XLSX export
#   -no-collada - Disable DAE export
```

**Examples**:
```bash
# Basic conversion (XLSX + DAE)
RvtExporter.exe "C:\Projects\Building.rvt"

# Full export with all options
RvtExporter.exe "C:\Projects\Building.rvt" complete bbox schedule sheets2pdf

# XLSX only (no 3D geometry)
RvtExporter.exe "C:\Projects\Building.rvt" -no-collada

# Custom categories
RvtExporter.exe "C:\Projects\Building.rvt" custom "C:\Config\my_categories.txt"
```

---

### RVT2IFCconverter.exe - Revit to IFC Converter

**Location**: `DDC_CONVERTER_Revit2IFC/datadrivenlibs/RVT2IFCconverter.exe`

**Purpose**: Convert Revit files to IFC format

**Input**: `.rvt`, `.rfa`

**Output**: IFC2x3, IFC4, IFC4.3, IFCXML, IFCZIP, HDF5

**CLI Syntax**:
```bash
RVT2IFCconverter.exe <input.rvt> [output.ifc] [preset=name] [config="..."] [key=value]

# Presets: standard, extended, custom
```

**Examples**:
```bash
# Standard IFC export
RVT2IFCconverter.exe "C:\Projects\Building.rvt"

# Extended export with more detail
RVT2IFCconverter.exe "C:\Projects\Building.rvt" preset=extended

# Custom output path
RVT2IFCconverter.exe "C:\Projects\Building.rvt" "D:\Output\model.ifc"

# Custom configuration
RVT2IFCconverter.exe "C:\Projects\Building.rvt" config="ExportBaseQuantities=true; SitePlacement=Shared"
```

---

### IfcExporter.exe - IFC Data Extractor

**Location**: `DDC_CONVERTER_IFC/datadrivenlibs/IfcExporter.exe`

**Purpose**: Extract data and geometry from IFC files

**Input**: `.ifc` (IFC2x3, IFC4, IFC4x1, IFC4x3)

**Output**:
- XLSX database
- DAE (Collada 3D geometry)

**CLI Syntax**:
```bash
IfcExporter.exe <input.ifc>
```

**Example**:
```bash
IfcExporter.exe "C:\Projects\Model.ifc"
```

---

### DwgExporter.exe - DWG Data Extractor

**Location**: `DDC_CONVERTER_DWG/datadrivenlibs/DwgExporter.exe`

**Purpose**: Extract data from AutoCAD DWG files

**Input**: `.dwg` (AutoCAD 1983-2026)

**Output**:
- XLSX database
- PDF drawings

**CLI Syntax**:
```bash
DwgExporter.exe <input.dwg>
```

**Example**:
```bash
DwgExporter.exe "C:\Projects\Plan.dwg"
```

---

### DgnExporter.exe - DGN Data Extractor

**Location**: `DDC_CONVERTER_DGN/datadrivenlibs/DgnExporter.exe`

**Purpose**: Extract data from Bentley MicroStation DGN files

**Input**: `.dgn` (MicroStation V7, V8)

**Output**: XLSX database

**CLI Syntax**:
```bash
DgnExporter.exe <input.dgn>
```

**Example**:
```bash
DgnExporter.exe "C:\Projects\Bridge.dgn"
```

---

## Excel to Revit Update Tool

**Location**: `DDC_Update_Revit_from_Excel/`

**Purpose**: Sync data from Excel back to Revit

**Workflow**: Revit -> Excel -> Transform -> Excel -> Revit

---

## n8n Workflows

### 1. Basic Conversion
**File**: `n8n_1_Revit_IFC_DWG_Conversation_simple.json`

Simple file conversion for Revit, IFC, DWG, DGN.

### 2. Advanced Settings
**File**: `n8n_2_All_Settings_Revit_IFC_DWG_Conversation_simple.json`

Configurable export modes (basic/standard/complete) and options (bbox, schedule, sheets2pdf).

### 3. Batch Processing
**File**: `n8n_3_CAD-BIM-Batch-Converter-Pipeline.json`

Batch conversion with validation, metrics tracking, and HTML report generation.

### 4. BIM Validation
**Files**:
- `n8n_4_Validation_CAD_BIM_Revit_IFC_DWG.json`
- `n8n_4_DDC_BIM_Requirements_Table_for_Revit_IFC_DWG.xlsx`

Validate CAD/BIM data against predefined rules, generate color-coded Excel reports.

### 5. AI Classification
**File**: `n8n_5_CAD_BIM_Automatic_Classification_with_LLM_and_RAG.json`

AI-powered element classification using LLM and RAG. Supports any classification system (Omniclass, Uniclass, custom).

### 6. Cost Estimation
**File**: `n8n_6_Construction_Price_Estimation_with_LLM_for_Revt_and_IFC.json`

Automated cost estimation with AI classification, market prices, and reports.

### 7. Carbon Footprint
**File**: `n8n_7_Carbon_Footprint_CO2_Estimator_for_Revit and_IFC.json`

Calculate embodied carbon emissions (A1-A3 lifecycle stages).

### 8. ETL for LLM
**File**: `n8n_8_Revit_IFC_DWG_Conversation_EXTRACT_Phase_with_Parse_XLSX.json`

Data preparation for LLM-based automation tasks.

### 9. QTO Reports
**File**: `n8n_9_CAD_BIM_Quantity_TakeOff_HTML_Report_Generator.json`

Generate interactive HTML quantity take-off reports.

---

## Output Format Details

### XLSX (Excel Database)

Structure: Elements as rows, properties as columns

```
| ElementId | Category | Type Name | Area | Volume | Material | Level | ... |
|-----------|----------|-----------|------|--------|----------|-------|-----|
| 123456    | Walls    | Basic Wall| 45.5 | 12.3   | Concrete | 01    | ... |
```

### DAE (Collada 3D Geometry)

- Standard 3D format viewable in any 3D viewer
- Element IDs match XLSX for data linking
- Includes materials and textures

### IFC (Industry Foundation Classes)

Supported versions:
- IFC2x3
- IFC4
- IFC4.3
- IFCXML
- IFCZIP
- HDF5

### PDF

- Sheets and drawings from Revit/DWG
- Preserves layout and annotations

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
    r"C:\DDC\RvtExporter.exe",
    r"C:\Projects\Building.rvt",
    "complete", "bbox", "schedule"
], capture_output=True, text=True)
```

### PowerShell (batch)
```powershell
Get-ChildItem "C:\Projects\*.rvt" | ForEach-Object {
    & "C:\DDC\RvtExporter.exe" $_.FullName complete bbox
}
```

### Node.js
```javascript
const { execSync } = require('child_process');
execSync('C:\\DDC\\RvtExporter.exe "C:\\Projects\\Building.rvt" complete bbox');
```

### n8n (Execute Command node)
```javascript
C:\DDC\RvtExporter.exe "{{ $json.filePath }}" complete bbox
```

---

## Prerequisites

**For v17+**: Install Microsoft Visual C++ Redistributable 2015-2022 (x64)

---

## Documentation

- **Book**: `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` (in AI_INSTRUCTIONS folder)
- **PDF Guide**: `GuideBook_DataDrivenConstruction_Book_2ndEdition_ArtemBoiko_2025_en-US.pdf`
- **Sample Data**: `Sample_Projects/` folder

---

## License

MIT License - free to use, modify, and distribute.

---

*All tools are designed to be building blocks for construction automation.*
