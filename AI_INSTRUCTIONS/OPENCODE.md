# Opencode Instructions for CAD2DATA Repository

## Repository Overview

This is the **CAD2DATA Pipeline** repository - open-source tools for construction data automation. All tools are designed to be integrated into any solution.

## Core Concept

Extract structured data from CAD/BIM files:
- Revit (.rvt) -> JSON/CSV
- IFC (.ifc) -> JSON/CSV
- DWG (.dwg) -> JSON/CSV
- DGN (.dgn) -> IFC/DWG/JSON

## Folder Structure

```
DDC_CONVERTER_DGN/     - Bentley DGN format converter
DDC_CONVERTER_DWG/     - AutoCAD DWG extractor
DDC_CONVERTER_IFC/     - IFC parser and analyzer
DDC_CONVERTER_REVIT/   - Revit data extractor
DDC_CONVERTER_Revit2IFC/ - Revit to IFC converter
DDC_Update_Revit_from_Excel/ - Sync Excel data to Revit
n8n_*.json             - Ready automation workflows
```

## Philosophy

Read `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` in this folder - it explains why data-driven approach matters in construction.

## Integration Capabilities

### As Libraries
Import converters into your Python/C# projects

### As CLI Tools
Execute converters from command line in batch mode

### As n8n Nodes
Use JSON workflow templates for visual automation

### As API Endpoints
Wrap converters with FastAPI/Flask for web services

## Supported Workflows

1. **Format Conversion**: DGN -> IFC, Revit -> IFC
2. **Data Extraction**: Properties, quantities, schedules
3. **Validation**: Check compliance, find errors
4. **QTO (Quantity Take-Off)**: Automated measurements
5. **Classification**: AI-assisted element classification
6. **Reporting**: Generate HTML/Excel reports

## Sample Code

```python
# Extract IFC quantities
from DDC_CONVERTER_IFC import IfcParser

parser = IfcParser("building.ifc")
quantities = parser.get_quantities()
for element in quantities:
    print(f"{element['type']}: {element['area']} m2")
```

## n8n Workflows Available

| File | Purpose |
|------|---------|
| n8n_1_* | Simple conversion |
| n8n_2_* | Advanced settings |
| n8n_3_* | Batch processing |
| n8n_4_* | Validation |
| n8n_5_* | AI Classification |
| n8n_6_* | Cost Estimation |
| n8n_7_* | CO2 Footprint |
| n8n_8_* | Phase extraction |
| n8n_9_* | QTO Reports |

## Best Practices

1. Use IFC as interchange format when possible
2. Validate data before processing
3. Keep original files unchanged
4. Document transformations
5. Use structured output (JSON preferred)

## For Code Generation

When generating code for this repository:
- Follow existing code patterns
- Use consistent naming conventions
- Add error handling
- Support batch processing
- Output structured data

---

*All tools are open-source and can be freely integrated into your solutions.*
