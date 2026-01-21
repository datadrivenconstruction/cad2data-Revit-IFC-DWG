# AI Instructions for CAD2DATA Repository

## Overview

This folder contains instructions for AI coding assistants (Claude Code, Opencode, Google Antigravity, and others) to effectively work with the CAD2DATA pipeline repository.

## Purpose

All tools in this repository are **open-source** and designed to be:
- Freely integrated into any solution
- Extended and customized by AI assistants
- Used as building blocks for construction automation workflows

## Repository Philosophy

This repository follows the **Data-Driven Construction** approach as described in the book `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` located in this folder. The book serves as a **guiding beacon** for automation processes in construction companies.

## Key Principles

1. **Data as Foundation**: Construction data is the new oil - extract, transform, and utilize it effectively
2. **Open Standards**: Prefer IFC, JSON, CSV over proprietary formats
3. **Automation First**: Every repetitive task should be automated
4. **AI-Ready Pipelines**: Design workflows that can be enhanced by AI assistants

## Repository Structure

```
cad2data-Revit-IFC-DWG-DGN-pipeline/
├── AI_INSTRUCTIONS/          # Instructions for AI assistants
├── DDC_CONVERTER_DGN/        # DGN to IFC/DWG converter
├── DDC_CONVERTER_DWG/        # DWG data extraction
├── DDC_CONVERTER_IFC/        # IFC data extraction
├── DDC_CONVERTER_REVIT/      # Revit data extraction
├── DDC_CONVERTER_Revit2IFC/  # Revit to IFC conversion
├── DDC_Update_Revit_from_Excel/ # Excel to Revit sync
├── DDC_in_additon/           # Additional utilities
├── Sample_Projects/          # Test data
└── n8n_*.json               # n8n automation workflows
```

## Available Instructions

- [INSTRUCTIONS.md](INSTRUCTIONS.md) - This file (general overview)
- [TOOLS_OVERVIEW.md](TOOLS_OVERVIEW.md) - Detailed tool descriptions
- [CLAUDE.md](CLAUDE.md) - Claude Code specific instructions
- [OPENCODE.md](OPENCODE.md) - Opencode specific instructions
- [ANTIGRAVITY.md](ANTIGRAVITY.md) - Google Antigravity specific instructions
- [DATA_DRIVEN_CONSTRUCTION_BOOK.txt](DATA_DRIVEN_CONSTRUCTION_BOOK.txt) - The guiding book

## For AI Assistants

When working with this repository:

1. **Read the book** - `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` provides context for construction automation
2. **Understand the tools** - Each DDC_CONVERTER_* folder has specific capabilities
3. **Respect open standards** - Prefer IFC format for interoperability
4. **Think data-first** - Extract structured data, not just geometry
5. **Automate workflows** - Use n8n JSON templates as starting points

## Supported Formats

| Format | Tool | Capabilities |
|--------|------|-------------|
| .rvt (Revit) | DDC_CONVERTER_REVIT | Extract properties, geometry, schedules |
| .ifc | DDC_CONVERTER_IFC | Parse IFC schema, extract quantities |
| .dwg | DDC_CONVERTER_DWG | Extract layers, blocks, attributes |
| .dgn | DDC_CONVERTER_DGN | Convert to IFC/DWG, extract data |

## License

All tools are open-source. See LICENSE file for details.

---

*"If data is the new oil, we need to learn to define it, find it, mine it, refine it, to make it valuable."*
— Ralph Montague
