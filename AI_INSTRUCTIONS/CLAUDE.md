# Claude Code Instructions for CAD2DATA Repository

## About This Repository

You are working with the **CAD2DATA Pipeline** - a comprehensive suite of open-source tools for extracting, converting, and validating construction data from Revit, IFC, DWG, and DGN files.

## Quick Start

1. **Understand the context**: Read `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` in this folder
2. **Know the tools**: Each `DDC_CONVERTER_*` folder contains standalone converters
3. **Use n8n workflows**: JSON files in root are ready-to-use automation templates

## What You Can Do

### Extend Converters
```bash
# Example: Add new IFC entity support
DDC_CONVERTER_IFC/  # Python/C# based IFC parser
```

### Create New Pipelines
```bash
# Use existing n8n templates as reference
n8n_3_CAD-BIM-Batch-Converter-Pipeline.json
```

### Build Integrations
- All tools output JSON/CSV - easy to integrate
- APIs can be wrapped around converters
- Docker containers can be created

## Key Commands

```bash
# DGN Converter (Windows)
DDC_CONVERTER_DGN/DDC_Community_DGN_converter.exe

# IFC Parser
python DDC_CONVERTER_IFC/ifc_parser.py <file.ifc>

# DWG Extractor
DDC_CONVERTER_DWG/dwg_extractor.exe <file.dwg>
```

## Data Flow Principle

```
[CAD/BIM File] -> [DDC Converter] -> [Structured JSON/CSV] -> [Analysis/Report]
```

## Integration Patterns

### Pattern 1: Batch Processing
```python
import subprocess
import json
from pathlib import Path

def process_ifc_batch(folder):
    results = []
    for ifc_file in Path(folder).glob("*.ifc"):
        output = subprocess.run(
            ["python", "DDC_CONVERTER_IFC/ifc_parser.py", str(ifc_file)],
            capture_output=True
        )
        results.append(json.loads(output.stdout))
    return results
```

### Pattern 2: API Wrapper
```python
from fastapi import FastAPI, UploadFile
from DDC_CONVERTER_IFC import parse_ifc

app = FastAPI()

@app.post("/parse/ifc")
async def parse_ifc_endpoint(file: UploadFile):
    content = await file.read()
    return parse_ifc(content)
```

### Pattern 3: n8n Integration
Use existing n8n workflow JSONs as templates for custom automation.

## Best Practices

1. **Always validate output** - Use DDC validation workflows
2. **Preserve metadata** - Include source file info in output
3. **Handle large files** - Stream processing for big models
4. **Log everything** - Maintain audit trail for compliance

## What NOT To Do

- Don't modify original CAD files without explicit user consent
- Don't skip validation steps
- Don't ignore IFC schema versions
- Don't hardcode file paths

## Resources

- Book: `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` (in this folder)
- n8n Workflows: `n8n_*.json` (in root)
- Sample Data: `Sample_Projects/` folder

## Example Tasks Claude Code Can Help With

1. "Create a Python script to extract all door quantities from IFC files"
2. "Build a validation workflow that checks if all walls have fire rating"
3. "Generate a cost estimation report from Revit schedules"
4. "Convert DGN files to IFC with proper classification"
5. "Create a dashboard for tracking BIM model quality"

---

*Remember: Data-Driven Construction is about transforming raw geometry into actionable information.*
