# Claude Code Instructions for CAD2DATA Repository

## About This Repository

You are working with the **CAD2DATA Pipeline** - a comprehensive suite of open-source tools for extracting, converting, and validating construction data from Revit, IFC, DWG, and DGN files.

**Key advantage**: All converters have CLI interfaces that you can execute directly.

## Quick Start

1. **Understand the context**: Read `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` in this folder
2. **Use CLI tools**: Execute converters directly from terminal
3. **Process outputs**: Work with XLSX, DAE, IFC, HTML, PDF files

## Converters & CLI Syntax

### RvtExporter.exe - Revit to XLSX/DAE/PDF

```bash
RvtExporter.exe <input.rvt> [output.dae] [output.xlsx] [export_mode] [options]

# Export modes: basic (309 categories), standard (724), complete (1209), custom
# Options: bbox, room, schedule, sheets2pdf, -no-xlsx, -no-collada

# Examples:
RvtExporter.exe "C:\Projects\Building.rvt"
RvtExporter.exe "C:\Projects\Building.rvt" complete bbox schedule sheets2pdf
RvtExporter.exe "C:\Projects\Building.rvt" -no-collada  # XLSX only
```

### RVT2IFCconverter.exe - Revit to IFC

```bash
RVT2IFCconverter.exe <input.rvt> [output.ifc] [preset=name] [config="..."]

# Presets: standard, extended, custom
# Output: IFC2x3, IFC4, IFC4.3, IFCXML, IFCZIP, HDF5

# Examples:
RVT2IFCconverter.exe "C:\Projects\Building.rvt"
RVT2IFCconverter.exe "C:\Projects\Building.rvt" preset=extended
RVT2IFCconverter.exe "C:\Projects\Building.rvt" config="ExportBaseQuantities=true"
```

### IfcExporter.exe - IFC to XLSX/DAE

```bash
IfcExporter.exe <input.ifc>

# Supports: IFC2x3, IFC4, IFC4x1, IFC4x3
# Output: XLSX database + DAE geometry

# Example:
IfcExporter.exe "C:\Projects\Model.ifc"
```

### DwgExporter.exe - DWG to XLSX/PDF

```bash
DwgExporter.exe <input.dwg>

# Supports: AutoCAD 1983-2026
# Output: XLSX database + PDF drawings

# Example:
DwgExporter.exe "C:\Projects\Plan.dwg"
```

### DgnExporter.exe - DGN to XLSX

```bash
DgnExporter.exe <input.dgn>

# Supports: MicroStation V7, V8
# Output: XLSX database

# Example:
DgnExporter.exe "C:\Projects\Bridge.dgn"
```

## Output Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| **XLSX** | Excel with elements as rows, properties as columns | Data analysis, pandas, databases |
| **DAE** | Collada 3D geometry with element IDs matching XLSX | 3D visualization, web viewers |
| **IFC** | Open BIM standard (multiple versions) | Interoperability, BIM software |
| **PDF** | Drawings and sheets from Revit/DWG | Documentation, printing |
| **HTML** | Interactive reports with charts | Dashboards, sharing results |

## What You Can Do

### 1. Batch Processing
```python
import subprocess
from pathlib import Path

def batch_convert_revit(folder, converter_path):
    for rvt in Path(folder).glob("*.rvt"):
        subprocess.run([converter_path, str(rvt), "complete", "bbox"])
```

### 2. Data Analysis Pipeline
```python
import pandas as pd

# After conversion, analyze XLSX
df = pd.read_excel("Building_Elements.xlsx")
walls = df[df["Category"] == "Walls"]
print(f"Total wall area: {walls['Area'].sum()} m2")
```

### 3. Build Automation Workflows
Use n8n JSON templates as starting points:
- `n8n_3_CAD-BIM-Batch-Converter-Pipeline.json` - batch processing
- `n8n_4_Validation_CAD_BIM_Revit_IFC_DWG.json` - data validation
- `n8n_5_CAD_BIM_Automatic_Classification_with_LLM_and_RAG.json` - AI classification

### 4. Create Reports
```python
# Generate cost/quantity reports from converted data
import pandas as pd

df = pd.read_excel("output.xlsx")
summary = df.groupby("Type Name").agg({
    "Volume": "sum",
    "Area": "sum",
    "Count": "count"
})
summary.to_html("report.html")
```

## Example Prompts for Claude Code

| Task | Prompt Example |
|------|----------------|
| Convert files | "Convert all .rvt files in C:\Projects to Excel with bounding boxes" |
| Analyze data | "Read the XLSX and show wall types with total volumes" |
| Build pipeline | "Create a Python script: Revit -> Excel -> cost report" |
| Validate BIM | "Check parameter fill rate and generate quality report" |
| Cost estimation | "Calculate material costs from the extracted quantities" |

## n8n Workflows - Process Logic Templates

The `n8n_*.json` files are **visual representations of process logic** - use them as reference architecture for building your own solutions in any language.

| # | File | Process Logic |
|---|------|---------------|
| 1 | n8n_1_*.json | Basic conversion flow |
| 2 | n8n_2_*.json | Advanced settings handling |
| 3 | n8n_3_*.json | Batch processing + reporting |
| 4 | n8n_4_*.json | BIM validation rules |
| 5 | n8n_5_*.json | AI classification (LLM + RAG) |
| 6 | n8n_6_*.json | Cost estimation pipeline |
| 7 | n8n_7_*.json | Carbon footprint calculation |
| 8 | n8n_8_*.json | ETL for LLM preparation |
| 9 | n8n_9_*.json | QTO report generation |

**You can implement this logic in:** Python, JavaScript, C#, Go, or any language.

## Best Practices

1. **Always use CLI** - Direct execution is faster than scripting wrappers
2. **Use complete mode** - Extracts all 1209 Revit categories
3. **Enable bbox** - Bounding boxes are useful for spatial analysis
4. **Check outputs** - Verify XLSX has expected data before processing
5. **Preserve IDs** - DAE element IDs match XLSX for data linking

## What NOT To Do

- Don't modify original CAD files without explicit user consent
- Don't assume file paths - always verify with user
- Don't skip validation steps in production workflows
- Don't hardcode paths - use parameters

## Resources

- Book: `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` (in this folder)
- n8n Workflows: `n8n_*.json` (in repository root)
- Sample Data: `Sample_Projects/` folder
- DDC CWICR Database: 55,719 work items for cost estimation

---

*"You don't need to write code yourself - just describe what you want, and AI will integrate DDC converters into your workflow."*
