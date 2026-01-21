# AI Instructions for CAD2DATA Repository

## Overview

This folder contains instructions for AI coding assistants (Claude Code, Opencode, Google Antigravity, Cursor, Copilot, Windsurf, Aider, Cline, and others) to effectively work with the CAD2DATA pipeline repository.

## Purpose

All tools in this repository are **open-source** and designed to be:
- Freely integrated into any solution
- Extended and customized by AI assistants
- Used as building blocks for construction automation workflows
- Called directly from CLI by AI assistants

## Repository Philosophy

This repository follows the **Data-Driven Construction** approach as described in the book `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` located in this folder. The book serves as a **guiding beacon** for automation processes in construction companies.

## Key Principles

1. **Data as Foundation**: Construction data is the new oil - extract, transform, and utilize it effectively
2. **Open Formats**: Convert proprietary CAD/BIM to open formats (XLSX, DAE, IFC, CSV, HTML, PDF)
3. **No Vendor Lock-in**: Works offline without Autodesk licenses or cloud APIs
4. **Automation First**: Every repetitive task should be automated
5. **AI-Ready Pipelines**: Design workflows that can be enhanced by AI assistants

## Repository Structure

```
cad2data-Revit-IFC-DWG-DGN-pipeline/
├── AI_INSTRUCTIONS/              # Instructions for AI assistants
├── DDC_CONVERTER_DGN/            # DGN converter (DgnExporter.exe)
├── DDC_CONVERTER_DWG/            # DWG converter (DwgExporter.exe)
├── DDC_CONVERTER_IFC/            # IFC converter (IfcExporter.exe)
├── DDC_CONVERTER_REVIT/          # Revit converter (RvtExporter.exe)
├── DDC_CONVERTER_Revit2IFC/      # Revit to IFC (RVT2IFCconverter.exe)
├── DDC_Update_Revit_from_Excel/  # Excel to Revit sync
├── DDC_in_additon/               # Additional utilities
├── Sample_Projects/              # Test data
└── n8n_*.json                    # n8n automation workflows (9 workflows)
```

## Supported Input/Output Formats

### Input Formats
| Format | Versions | Converter |
|--------|----------|-----------|
| Revit (.rvt, .rfa) | 2015-2026 | RvtExporter.exe, RVT2IFCconverter.exe |
| IFC (.ifc) | IFC2x3, IFC4, IFC4x1, IFC4x3 | IfcExporter.exe |
| AutoCAD (.dwg) | 1983-2026 | DwgExporter.exe |
| MicroStation (.dgn) | V7, V8 | DgnExporter.exe |

### Output Formats
| Format | Description | Produced By |
|--------|-------------|-------------|
| **XLSX** | Excel database (elements as rows, properties as columns) | All converters |
| **DAE** | Collada 3D geometry with element IDs matching XLSX | RvtExporter, IfcExporter |
| **PDF** | Drawings and sheets | RvtExporter, DwgExporter |
| **IFC** | IFC2x3, IFC4, IFC4.3, IFCXML, IFCZIP, HDF5 | RVT2IFCconverter |
| **HTML** | Interactive reports with charts | n8n workflows |
| **CSV** | Simple tabular data | Post-processing |

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
2. **Use CLI tools directly** - All converters have command-line interfaces that AI can execute
3. **Respect open formats** - Output to XLSX, DAE, IFC, HTML, PDF
4. **Think data-first** - Extract structured data (DataFrames), not just geometry
5. **Automate workflows** - Use n8n JSON templates as starting points

## Quick CLI Examples

```bash
# Convert Revit to XLSX + DAE
RvtExporter.exe "C:\Projects\Building.rvt"

# Convert Revit with all options
RvtExporter.exe "C:\Projects\Building.rvt" complete bbox schedule sheets2pdf

# Convert Revit to IFC
RVT2IFCconverter.exe "C:\Projects\Building.rvt"

# Convert IFC to XLSX + DAE
IfcExporter.exe "C:\Projects\Model.ifc"

# Convert DWG to XLSX + PDF
DwgExporter.exe "C:\Projects\Plan.dwg"

# Convert DGN to XLSX
DgnExporter.exe "C:\Projects\Bridge.dgn"
```

## n8n Workflows (9 ready-to-use)

1. **Basic Conversion** - Simple file conversion
2. **Advanced Settings** - Configurable export options
3. **Batch Processing** - Multiple files with HTML reports
4. **Validation** - BIM data quality checks
5. **AI Classification** - LLM + RAG element classification
6. **Cost Estimation** - Price calculation with DDC CWICR database
7. **Carbon Footprint** - CO2 emissions calculation
8. **ETL for LLM** - Data preparation for AI tasks
9. **QTO Reports** - Quantity take-off HTML reports

## License

All tools are open-source (MIT). See LICENSE file for details.

---

*"If data is the new oil, we need to learn to define it, find it, mine it, refine it, to make it valuable."*
— Ralph Montague
