# Claude Code Instructions for CAD2DATA Repository

## About This Repository

You are working with the **CAD2DATA Pipeline** - a suite of tools and automation templates for extracting, converting, and validating construction data from `.rvt`, IFC, and `.dwg` files. The MIT-licensed parts (workflows, scripts, instructions) are open source; the DDC converter binaries are proprietary software distributed  GitHub Releases.

**Key advantage**: The converters have CLI interfaces that you can execute directly (DDC IFC to Excel, DDC CAD drawing (.dwg) to Excel, DDC RVT Converter).

## Quick Start

1. **Understand the context**: Read `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` in this folder
2. **Use CLI tools**: Execute converters directly from terminal
3. **Process outputs**: Work with XLSX, CSV, JSONL, SQLite, GLB, IFC, HTML files

## Converters & CLI Syntax

### Where to get the converters

The DDC converters are distributed as release packages (not stored in git):
<https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases>

Suggested unpack locations: `C:\DDC\RVT-Converter\`, `C:\DDC\IFC-to-Excel\`, `C:\DDC\DWG-to-Excel\`.
Always read the report each tool writes and verify results before relying on them.

### DDC RVT Converter 2.0 (and DDC RVT-to-IFC 2.0) - `.rvt` / `.rfa` files

Reads `.rvt` / `.rfa` files saved by Autodesk® Revit® 2019-2027. Desktop app `RVT Converter.exe` and CLI `cli\RVTconverter.exe` (DDC RVT-to-IFC has IFC defaults).

```bash
RVTconverter.exe "C:\Models\Project.rvt" [-o OUTDIR] [--properties] [--ifc] [--gltf] [--obj]
                 [--ifc-profile full|coordination|geometry|custom]
                 [--ifc-units m|mm]
                 [--ifc-origin internal|project-base-point|survey-point]
                 [--ifc-categories IDS]

# Examples:
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt"
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out" --properties
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" --ifc --ifc-profile coordination --ifc-units m
```

- Output folder: `<stem>.converted` (never overwrites an existing folder). Always contains `native_graph.glb` (3D model), `summary.json`, `report.json`.
- `--properties` adds `properties.jsonl` and `property_scopes.jsonl` (element properties, one JSON object per line).
- `--ifc` adds `native_graph.ifc` (IFC4.
- Exit codes: `0` ok, `2` written with gaps (or bad arguments), `1` failure. Check `report.json` on exit code 2.
- The desktop app also writes CSV tables and SQLite.

### DDC IFC to Excel 2.0 - `.ifc` / `.ifczip` files

Portable app. Reads IFC2x3 and IFC4 (STEP and IFCZIP).

```bash
runtime\python.exe sources\ifc-excel\converter.py model.ifc --output OUTDIR

# Example:
cd C:\DDC\IFC-to-Excel
runtime\python.exe sources\ifc-excel\converter.py "C:\Models\Model.ifc" --output "C:\Out\Model"
```

Output: `drawing.xlsx`, `data.jsonl`, `data.sqlite`, `result.json`.

### DDC CAD drawing (.dwg) to Excel 2.0 - `.dwg` files

Reads `.dwg` drawings.

```bash
dwg2excel.exe drawing.dwg -o OUTDIR [--json] [--no-dxf] [--no-svg] [--no-xlsx] [--language en|ru]

# Example:
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Projects\Plan.dwg" -o "C:\Out" --json
```

Output: one folder per drawing with `.xlsx`, `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json`, `REPORT.txt`. The report states how many records were decoded, refused, or unsupported - always read it before using the data.

### DDC Data Viewer 2.0 (free)

Desktop viewer for XLSX / CSV / JSONL / Parquet tables with linked GLB / DAE 3D models.

### Not available

DGN is not supported. Linux and macOS builds are coming soon.

### Linux — DDC CWICR Semantic Search

55,719 construction work items with costs across 9 languages, searchable via keyword or AI-powered semantic search.

```bash
# Install Qdrant vector database
sudo apt install ddc-qdrant

# Install language data (~1 GB each, pre-computed OpenAI embeddings)
sudo apt install ddc-cwicr-en  # English (CAD, Toronto)
sudo apt install ddc-cwicr-de  # German (EUR, Berlin)
sudo apt install ddc-cwicr-ru  # Russian (RUB, St. Petersburg)
# Available: en, de, ru, fr, es, ar, zh, pt, hi

# Install search CLI
sudo apt install ddc-cwicr-cli

# Keyword search (no API key needed)
ddc-search --keyword "concrete foundation"

# Semantic search (requires OpenAI API key)
export OPENAI_API_KEY=sk-...
ddc-search "reinforced concrete foundation"

# JSON output
ddc-search --json --limit 10 "floor tiles"
```

## Output Formats

| Format | Description | Produced by | Use Case |
|--------|-------------|-------------|----------|
| **GLB** | 3D model (`native_graph.glb`) | DDC RVT Converter | 3D visualization, web viewers, DDC Data Viewer |
| **JSONL / SQLite** | Element properties and tables | RVT Converter (`--properties`), IFC to Excel | Data analysis, pandas, databases |
| **XLSX / CSV** | Tables (elements as rows, properties as columns) | IFC to Excel, .dwg to Excel | Data analysis, pandas, databases |
| **IFC** | IFC4 (`native_graph.ifc`) | RVT Converter / RVT-to-IFC (`--ifc`) | Interoperability, BIM software |
| **DXF / SVG** | Drawing geometry | .dwg to Excel | CAD/vector tooling |
| **JSON reports** | `report.json`, `summary.json`, `result.json`, `REPORT.txt` | all | Quality control of every conversion |
| **HTML** | Interactive reports with charts | n8n workflows | Dashboards, sharing results |

## What You Can Do

### 1. Batch Processing
```python
import subprocess
from pathlib import Path

RVT_CLI = r"C:\DDC\RVT-Converter\cli\RVTconverter.exe"

def batch_convert_revit(folder, out_dir):
    for rvt in Path(folder).glob("*.rvt"):
        r = subprocess.run([RVT_CLI, str(rvt), "-o", out_dir, "--properties"])
        if r.returncode == 2:
            print(f"{rvt.name}: written with gaps, check report.json")
        elif r.returncode != 0:
            print(f"{rvt.name}: failed")
```

### 2. Data Analysis Pipeline
```python
import pandas as pd

# Properties written by RVTconverter.exe --properties (one JSON object per line)
df = pd.read_json("Project.converted/properties.jsonl", lines=True)
print(df.head())

# Table written by DDC IFC to Excel
df = pd.read_excel("Model/drawing.xlsx")
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
| Convert files | "Convert all .rvt files in C:\Projects with RVTconverter.exe --properties and summarise report.json" |
| Analyze data | "Read the converted tables and show wall types with total volumes" |
| Build pipeline | "Create a Python script: .rvt -> properties.jsonl -> cost report" |
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
2. **Check exit codes and reports** - `0` ok, `2` written with gaps, `1` failure; read `report.json` / `REPORT.txt` / `result.json`
3. **Verify results** - verify counts against the source before downstream use
4. **Use `--properties`** for RVT when you need element parameters
5. **Never overwrite** - the RVT converter writes `<stem>.converted` and never overwrites; choose a fresh `-o` folder for repeated runs

## What NOT To Do

- Don't modify original CAD files without explicit user consent
- Don't assume file paths - always verify with user
- Don't skip validation steps in production workflows
- Don't hardcode paths - use parameters
- Don't describe the converters as official, certified, or affiliated with Autodesk; they are independent software

## Resources

- Book: `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` (in this folder)
- n8n Workflows: `n8n_*.json` (in repository root)
- Sample Data: `Sample_Projects/` folder
- DDC CWICR Database: 55,719 work items for cost estimation

---

*"You don't need to write code yourself - just describe what you want, and AI will integrate DDC converters into your workflow."*
