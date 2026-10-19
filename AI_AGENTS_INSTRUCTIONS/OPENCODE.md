# Opencode Instructions for CAD2DATA Repository

## Repository Overview

**CAD2DATA Pipeline** - tools and workflow templates for construction data automation, designed to be integrated into any solution via CLI. Workflows and scripts are MIT-licensed; the DDC converters are proprietary previews distributed via GitHub Releases.

## Core Concept

Convert proprietary CAD/BIM files to open formats:
- `.rvt` -> GLB, JSON/JSONL properties, IFC4 (experimental)
- IFC -> XLSX, JSONL, SQLite
- `.dwg` -> XLSX, CSV, JSONL, DXF, SVG

**No vendor lock-in. No Autodesk licence required on the conversion machine. Offline processing.**

## Converters

| Tool | Input | Output |
|------|-------|--------|
| DDC RVT Converter 0.6.8 (`cli\RVTconverter.exe`) | `.rvt`, `.rfa` saved by Autodesk® Revit® 2019-2027 | `<stem>.converted/`: `native_graph.glb`, `summary.json`, `report.json`; with `--properties` also `properties.jsonl`, `property_scopes.jsonl`; with `--ifc` also `native_graph.ifc` (IFC4, experimental) |
| DDC RVT-to-IFC 0.6.8 | `.rvt`, `.rfa` | Same engine and CLI, IFC defaults |
| DDC IFC to Excel 0.3.1-preview | IFC2x3 / IFC4 (SPF, IFCZIP) | `drawing.xlsx`, `data.jsonl`, `data.sqlite`, `result.json` |
| DDC CAD drawing (.dwg) to Excel 0.4.1 (`cli\dwg2excel.exe`) | `.dwg` | `.xlsx`, `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json`, `REPORT.txt` |
| DDC Data Viewer 0.1.1 (free) | XLSX / CSV / JSONL / Parquet (+ GLB / DAE) | Viewer |

All are **previews** (quality not fully qualified): check the reports they write. DGN conversion is discontinued. Download: <https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases> (suggested folders `C:\DDC\RVT-Converter\`, `C:\DDC\IFC-to-Excel\`, `C:\DDC\DWG-to-Excel\`).

## CLI Examples

```bash
# .rvt -> GLB + summary/report (+ element properties)
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out" --properties

# .rvt -> IFC4 (experimental)
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" --ifc --ifc-profile coordination --ifc-units m

# IFC -> Excel + JSONL + SQLite
cd C:\DDC\IFC-to-Excel
runtime\python.exe sources\ifc-excel\converter.py "C:\Models\Model.ifc" --output "C:\Out\Model"

# .dwg -> Excel + CSV + JSONL + DXF + SVG
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Projects\Plan.dwg" -o "C:\Out" --json

# RVT exit codes: 0 ok, 2 written with gaps / bad args, 1 failure
```

## Output Formats

| Format | Description |
|--------|-------------|
| **XLSX / CSV** | Tables |
| **JSONL / SQLite** | Properties and tables |
| **GLB** | 3D model (`native_graph.glb`) |
| **IFC** | IFC4, experimental |
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

# Convert (exit code 0 ok, 2 written with gaps, 1 failure)
r = subprocess.run([r"C:\DDC\RVT-Converter\cli\RVTconverter.exe", "model.rvt", "-o", "out", "--properties"])
print("exit code:", r.returncode)

# Analyze
df = pd.read_json("out/model.converted/properties.jsonl", lines=True)
```

### PowerShell
```powershell
Get-ChildItem "*.rvt" | ForEach-Object {
    & "C:\DDC\RVT-Converter\cli\RVTconverter.exe" $_.FullName -o "C:\Out" --properties
}
```

### Node.js
```javascript
const { execSync } = require('child_process');
execSync('C:\\DDC\\RVT-Converter\\cli\\RVTconverter.exe "model.rvt" -o out --properties');
```

## Best Practices

1. Check the exit code and read `report.json` / `REPORT.txt` / `result.json` after every run
2. Use `--properties` for RVT when element parameters are needed
3. Treat output as preview quality; validate before downstream processing
4. Use n8n workflows for complex automation

## For Code Generation

When generating code for this repository:
- Use CLI calls with subprocess/execSync
- Parse XLSX/JSONL with pandas/openpyxl
- Generate HTML reports for visualization
- Follow existing n8n workflow patterns

---

*Workflows, scripts, and documentation are MIT-licensed. The DDC converter binaries are proprietary previews (see LICENSE-PROPRIETARY).*
