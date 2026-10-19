# AI Instructions for CAD2DATA Repository

## Overview

This folder contains instructions for AI coding assistants (Claude Code, Opencode, Google Antigravity, Cursor, Copilot, Windsurf, Aider, Cline, and others) to effectively work with the CAD2DATA pipeline repository.

## Purpose

The MIT-licensed parts of this repository (workflows, scripts, instructions) are **open source**; the DDC converter binaries are proprietary previews distributed through GitHub Releases. The repository is designed to be:
- Freely integrated into any solution
- Extended and customized by AI assistants
- Used as building blocks for construction automation workflows
- Called directly from CLI by AI assistants (the converters)

## Repository Philosophy

This repository follows the **Data-Driven Construction** approach as described in the book `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` located in this folder. The book serves as a **guiding beacon** for automation processes in construction companies.

## Key Principles

1. **Data as Foundation**: Construction data is the new oil - extract, transform, and utilize it effectively
2. **Open Formats**: Convert proprietary CAD/BIM to open formats (XLSX, CSV, JSONL, SQLite, GLB, IFC, HTML)
3. **No Vendor Lock-in**: Works offline; no Autodesk licence is required on the conversion machine and no cloud API is used
4. **Automation First**: Every repetitive task should be automated
5. **AI-Ready Pipelines**: Design workflows that can be enhanced by AI assistants

## Repository Structure

```
cad2data-Revit-IFC-DWG/
├── AI_AGENTS_INSTRUCTIONS/              # Instructions for AI assistants
├── DDC_WINDOWS_Converters/              # Windows folder (converters now via GitHub Releases)
│   └── DDC_Update_Revit_from_Excel/    # Add-in for Autodesk® Revit® (Excel to Revit sync)
├── DDC_LINUX_Converters/                # CWICR search packages (.deb), Qdrant, dashboard, worker
│   ├── ddc-qdrant/                     # Qdrant vector DB package
│   ├── ddc-cwicr-cli/                  # Semantic search CLI
│   └── ddc-cwicr-data/                 # Language data packages (9 languages)
├── DDC_n8n_Workflows&Pipelines/         # n8n automation workflows (9 workflows)
├── DDC_in_additon/                      # Additional utilities
└── Sample_Projects/                     # Test data
```

The converters themselves are distributed through GitHub Releases:
<https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases>

## Supported Input/Output Formats

### Converters (previews - quality not fully qualified)

| Tool | Input | Output |
|------|-------|--------|
| DDC RVT Converter 0.6.8 (`cli\RVTconverter.exe`) | `.rvt`, `.rfa` saved by Autodesk® Revit® 2019-2027 | `<stem>.converted/`: `native_graph.glb`, `summary.json`, `report.json`; with `--properties` also `properties.jsonl`, `property_scopes.jsonl`; with `--ifc` also `native_graph.ifc` (IFC4, experimental) |
| DDC RVT-to-IFC 0.6.8 | `.rvt`, `.rfa` | Same engine and CLI, IFC defaults |
| DDC IFC to Excel 0.3.1-preview | IFC2x3 / IFC4 (SPF, IFCZIP) | `drawing.xlsx`, `data.jsonl`, `data.sqlite`, `result.json` |
| DDC CAD drawing (.dwg) to Excel 0.4.1 (`cli\dwg2excel.exe`) | `.dwg` | `.xlsx`, `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json`, `REPORT.txt` |
| DDC Data Viewer 0.1.1 (free) | XLSX / CSV / JSONL / Parquet (+ GLB / DAE) | Viewer |

All are **previews** (quality not fully qualified): check the reports they write. DGN conversion is discontinued. Download: <https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases> (suggested folders `C:\DDC\RVT-Converter\`, `C:\DDC\IFC-to-Excel\`, `C:\DDC\DWG-to-Excel\`).

### Output Formats
| Format | Description | Produced By |
|--------|-------------|-------------|
| **GLB** | 3D model (`native_graph.glb`) | DDC RVT Converter |
| **XLSX / CSV** | Tables | DDC IFC to Excel, DDC CAD drawing (.dwg) to Excel |
| **JSONL / SQLite** | Properties and tables | DDC RVT Converter (`--properties`), DDC IFC to Excel |
| **IFC** | IFC4, experimental | DDC RVT Converter / RVT-to-IFC (`--ifc`) |
| **DXF / SVG** | Drawing geometry | DDC CAD drawing (.dwg) to Excel |
| **HTML** | Interactive reports with charts | n8n workflows |

## Available Instructions

- [INSTRUCTIONS.md](INSTRUCTIONS.md) - This file (general overview)
- [TOOLS_OVERVIEW.md](TOOLS_OVERVIEW.md) - Detailed tool descriptions and CLI syntax
- [CLAUDE.md](CLAUDE.md) - Claude Code specific instructions
- [OPENCODE.md](OPENCODE.md) - Opencode specific instructions
- [ANTIGRAVITY.md](ANTIGRAVITY.md) - Google Antigravity specific instructions
- [DATA_DRIVEN_CONSTRUCTION_BOOK.txt](DATA_DRIVEN_CONSTRUCTION_BOOK.txt) - The guiding book

## For AI Assistants

When working with this repository:

1. **Read the book** - `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` provides context for construction automation
2. **Use CLI tools directly** - The converters have command-line interfaces that AI can execute; read the report each tool writes
3. **Respect open formats** - Output to XLSX, CSV, JSONL, GLB, IFC, HTML
4. **Think data-first** - Extract structured data (DataFrames), not just geometry
5. **Automate workflows** - Use n8n JSON templates as starting points

## Quick CLI Examples

### Windows
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

Linux and macOS builds of the new converters are in preparation; the old Linux converter packages (`ddc-*converter`, `ddc-sdk-*`) are discontinued. DGN conversion is discontinued.

### Linux — DDC CWICR Semantic Search

```bash
# Install Qdrant vector database
sudo apt install ddc-qdrant

# Install language data (each ~1 GB of pre-computed embeddings)
sudo apt install ddc-cwicr-en  # English (CAD, Toronto)
sudo apt install ddc-cwicr-de  # German (EUR, Berlin)
sudo apt install ddc-cwicr-ru  # Russian (RUB, St. Petersburg)

# Install search CLI
sudo apt install ddc-cwicr-cli

# Search (keyword — no API key needed)
ddc-search --keyword "concrete foundation"

# Search (semantic — requires OpenAI API key)
export OPENAI_API_KEY=sk-...
ddc-search "reinforced concrete foundation"

# JSON output
ddc-search --json --limit 10 "floor tiles"
```

Available CWICR languages: `en`, `de`, `ru`, `fr`, `es`, `ar`, `zh`, `pt`, `hi` (55,719 work items per language)

## n8n Workflows - Visual Process Templates

The `n8n_*.json` files are **visual representations of process logic** - not the final solution, but a foundation that can be implemented in any language or application.

**Use these workflows as:**
- Reference architecture for building your own pipelines
- Visual documentation of data processing logic
- Starting point for Python, JavaScript, C#, or any other implementation
- Templates for integration into enterprise systems

### Available Process Templates

1. **Basic Conversion** - Simple file conversion logic
2. **Advanced Settings** - Configurable export options
3. **Batch Processing** - Multiple files with reporting
4. **Validation** - BIM data quality checks
5. **AI Classification** - LLM + RAG element classification
6. **Cost Estimation** - Price calculation with DDC CWICR database
7. **Carbon Footprint** - CO2 emissions calculation
8. **ETL for LLM** - Data preparation for AI tasks
9. **QTO Reports** - Quantity take-off report generation

**The logic shown in n8n can be reproduced in:** Python, JavaScript/Node.js, C#, Go, Rust, or any language that can call CLI tools and process XLSX/JSON.

## License

Workflows, scripts, and documentation are MIT-licensed (see LICENSE). The DDC converter binaries are proprietary (see LICENSE-PROPRIETARY and NOTICE).

---

*"If data is the new oil, we need to learn to define it, find it, mine it, refine it, to make it valuable."*
— Ralph Montague
