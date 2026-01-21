# CAD2DATA Tools Overview

## Introduction

This document provides a comprehensive overview of all tools available in the CAD2DATA repository. Each tool is open-source and can be integrated into any solution.

## Converters

### DDC_CONVERTER_DGN

**Purpose**: Convert Bentley MicroStation DGN files to open formats

**Input**: .dgn (V7, V8)

**Output**: .ifc, .dwg

**Components**:
- `DDC_Community_DGN_converter.exe` - Main GUI application
- `DgnExporter.exe` - Command-line exporter
- `datadrivenlibs/` - Required libraries

**Usage**:
```cmd
DDC_Community_DGN_converter.exe
# or CLI:
DgnExporter.exe input.dgn output.ifc
```

---

### DDC_CONVERTER_DWG

**Purpose**: Extract data from AutoCAD DWG files

**Input**: .dwg (2000-2025 versions)

**Output**: JSON, CSV

**Capabilities**:
- Layer information
- Block attributes
- Text content
- Geometry data
- Custom properties

---

### DDC_CONVERTER_IFC

**Purpose**: Parse and analyze IFC (Industry Foundation Classes) files

**Input**: .ifc (IFC2x3, IFC4, IFC4x3)

**Output**: JSON, CSV

**Capabilities**:
- Property extraction
- Quantity calculation
- Spatial structure analysis
- Material information
- Classification data

---

### DDC_CONVERTER_REVIT

**Purpose**: Extract data from Autodesk Revit files

**Input**: .rvt

**Output**: JSON, CSV, Excel

**Capabilities**:
- Parameter export
- Schedule extraction
- Family information
- Room data
- Geometry properties

**Note**: Requires Revit installation for full functionality

---

### DDC_CONVERTER_Revit2IFC

**Purpose**: Convert Revit files to IFC format

**Input**: .rvt

**Output**: .ifc

**Features**:
- Configurable export settings
- Property mapping
- Classification support
- Geometry options

---

### DDC_Update_Revit_from_Excel

**Purpose**: Sync data from Excel to Revit

**Input**: Excel (.xlsx), Revit (.rvt)

**Output**: Updated Revit file

**Use Cases**:
- Bulk parameter updates
- Cost data import
- Specification updates
- Property synchronization

---

## n8n Workflows

### n8n_1_Revit_IFC_DWG_Conversation_simple.json
Basic conversion workflow for single files.

### n8n_2_All_Settings_Revit_IFC_DWG_Conversation_simple.json
Advanced conversion with configurable settings.

### n8n_3_CAD-BIM-Batch-Converter-Pipeline.json
Batch processing pipeline for multiple files.

### n8n_4_Validation_CAD_BIM_Revit_IFC_DWG.json
Validation workflow with requirements from Excel.
- Accompanying file: `n8n_4_DDC_BIM_Requirements_Table_for_Revit_IFC_DWG.xlsx`

### n8n_5_CAD_BIM_Automatic_Classification_with_LLM_and_RAG.json
AI-powered element classification using LLM and RAG.

### n8n_6_Construction_Price_Estimation_with_LLM_for_Revt_and_IFC.json
Automated cost estimation using AI.

### n8n_7_Carbon_Footprint_CO2_Estimator_for_Revit_and_IFC.json
Carbon footprint calculation for sustainability analysis.

### n8n_8_Revit_IFC_DWG_Conversation_EXTRACT_Phase_with_Parse_XLSX.json
Phase-based extraction with Excel parsing.

### n8n_9_CAD_BIM_Quantity_TakeOff_HTML_Report_Generator.json
Generate HTML reports for quantity take-off.

---

## Sample Projects

Located in `Sample_Projects/` folder. Contains test files for:
- IFC models
- Revit projects
- DWG drawings
- DGN files

---

## Integration Guide

### Command Line
```bash
# Process single file
./converter input.ifc --output result.json

# Batch processing
./converter --batch ./input_folder --output ./output_folder
```

### Python Integration
```python
from DDC_CONVERTER_IFC import IfcParser

parser = IfcParser("model.ifc")
data = parser.extract_all()
```

### n8n Integration
1. Import JSON workflow into n8n
2. Configure input/output paths
3. Set up triggers (manual, schedule, webhook)
4. Execute workflow

### REST API (Custom)
```python
from fastapi import FastAPI
from DDC_CONVERTER_IFC import IfcParser

app = FastAPI()

@app.post("/api/parse/ifc")
async def parse_ifc(file: UploadFile):
    parser = IfcParser(file.file)
    return parser.extract_all()
```

---

## Output Formats

### JSON Structure
```json
{
  "metadata": {
    "source_file": "building.ifc",
    "format_version": "IFC4",
    "processed_at": "2024-01-15T10:30:00Z"
  },
  "elements": [...],
  "summary": {...}
}
```

### CSV Structure
```csv
id,type,name,area,volume,material
123,IfcWall,Basic Wall,45.5,12.3,Concrete
```

---

## Documentation

- Main book: `DATA_DRIVEN_CONSTRUCTION_BOOK.txt`
- PDF Guide: `GuideBook_DataDrivenConstruction_Book_2ndEdition_ArtemBoiko_2025_en-US.pdf`
- Per-tool READMEs in each folder

---

## License

MIT License - free to use, modify, and distribute.

---

*All tools are designed to be building blocks for construction automation.*
