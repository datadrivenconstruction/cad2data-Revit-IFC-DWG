# Opencode Instructions for CAD2DATA Repository

## Repository Overview

**CAD2DATA Pipeline** - open-source tools for construction data automation. All tools are designed to be integrated into any solution via CLI.

## Core Concept

Convert proprietary CAD/BIM files to open formats:
- Revit (.rvt) -> XLSX, DAE, PDF, IFC
- IFC (.ifc) -> XLSX, DAE
- DWG (.dwg) -> XLSX, PDF
- DGN (.dgn) -> XLSX

**No vendor lock-in. No licenses required. Offline processing.**

## Converters

| Converter | Input | Output |
|-----------|-------|--------|
| RvtExporter.exe | .rvt, .rfa (2015-2026) | XLSX + DAE + PDF + Schedules |
| RVT2IFCconverter.exe | .rvt, .rfa | IFC2x3, IFC4, IFC4.3, IFCXML, IFCZIP, HDF5 |
| IfcExporter.exe | .ifc (2x3, 4, 4x1, 4x3) | XLSX + DAE |
| DwgExporter.exe | .dwg (1983-2026) | XLSX + PDF |
| DgnExporter.exe | .dgn (V7, V8) | XLSX |

## CLI Examples

```bash
# Revit to Excel + 3D
RvtExporter.exe "model.rvt"

# Revit with all options
RvtExporter.exe "model.rvt" complete bbox schedule sheets2pdf

# Revit to IFC
RVT2IFCconverter.exe "model.rvt"

# IFC to Excel + 3D
IfcExporter.exe "model.ifc"

# DWG to Excel + PDF
DwgExporter.exe "drawing.dwg"

# DGN to Excel
DgnExporter.exe "design.dgn"
```

## Output Formats

| Format | Description |
|--------|-------------|
| **XLSX** | Excel database - elements as rows, properties as columns |
| **DAE** | Collada 3D geometry with element IDs matching XLSX |
| **PDF** | Drawings and sheets |
| **IFC** | Open BIM standard (multiple versions) |
| **HTML** | Interactive reports (via n8n workflows) |

## Philosophy

Read `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` in this folder - explains data-driven approach to construction automation.

## n8n Workflows - Process Logic Templates

The `n8n_*.json` files are **visual representations of process logic** - a foundation that can be implemented in any language or application.

| # | Process Logic |
|---|---------------|
| 1 | Basic conversion flow |
| 2 | Advanced settings handling |
| 3 | Batch processing + reporting |
| 4 | BIM validation rules |
| 5 | AI classification (LLM + RAG) |
| 6 | Cost estimation pipeline |
| 7 | Carbon footprint calculation |
| 8 | ETL for LLM preparation |
| 9 | QTO report generation |

**Implement this logic in:** Python, JavaScript, C#, Go, Rust, or any language that can call CLI and process XLSX/JSON.

## Integration Patterns

### Python
```python
import subprocess
import pandas as pd

# Convert
subprocess.run(["RvtExporter.exe", "model.rvt", "complete", "bbox"])

# Analyze
df = pd.read_excel("model_Elements.xlsx")
summary = df.groupby("Category")["Volume"].sum()
```

### PowerShell
```powershell
Get-ChildItem "*.rvt" | ForEach-Object {
    & "RvtExporter.exe" $_.FullName complete bbox
}
```

### Node.js
```javascript
const { execSync } = require('child_process');
execSync('RvtExporter.exe "model.rvt" complete bbox');
```

## Best Practices

1. Use `complete` mode for full data extraction (1209 categories)
2. Enable `bbox` for spatial analysis
3. Validate XLSX output before downstream processing
4. DAE element IDs match XLSX for data linking
5. Use n8n workflows for complex automation

## For Code Generation

When generating code for this repository:
- Use CLI calls with subprocess/execSync
- Parse XLSX with pandas/openpyxl
- Generate HTML reports for visualization
- Follow existing n8n workflow patterns

---

*All tools are open-source (MIT) and can be freely integrated into your solutions.*
