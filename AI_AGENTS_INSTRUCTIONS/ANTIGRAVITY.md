# Google Antigravity Instructions for CAD2DATA Repository

## What Is This Repository?

**CAD2DATA Pipeline** - toolkit and workflow templates for converting and extracting data from construction files (`.rvt`, IFC, `.dwg`) to open formats (XLSX, CSV, JSONL, SQLite, GLB, IFC, HTML). Workflows and scripts are MIT-licensed; the DDC converters are proprietary software distributed  GitHub Releases.

## Key Value

- Transform proprietary CAD/BIM files into structured, analyzable data
- No vendor lock-in; no Autodesk licence required on the conversion machine
- The converters have CLI interfaces for direct execution
- Works offline

## Available Converters

| Tool | Input | Output |
|------|-------|--------|
| DDC RVT Converter 2.0 (`cli\RVTconverter.exe`) | `.rvt`, `.rfa` saved by Autodesk® Revit® 2019-2027 | `<stem>.converted/`: `native_graph.glb`, `summary.json`, `report.json`; with `--properties` also `properties.jsonl`, `property_scopes.jsonl`; with `--ifc` also `native_graph.ifc` (IFC4 |
| DDC RVT-to-IFC 2.0 | `.rvt`, `.rfa` | Same command line, IFC defaults |
| DDC IFC to Excel 2.0 | IFC2x3 / IFC4 (STEP, IFCZIP) | `drawing.xlsx`, `data.jsonl`, `data.sqlite`, `result.json` |
| DDC CAD drawing (.dwg) to Excel 2.0 (`cli\dwg2excel.exe`) | `.dwg` | `.xlsx`, `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json`, `REPORT.txt` |
| DDC Data Viewer 2.0 (free) | XLSX / CSV / JSONL / Parquet (+ GLB / DAE) | Viewer |

Check the reports each tool writes. DGN is not supported. Download: <https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases> (suggested folders `C:\DDC\RVT-Converter\`, `C:\DDC\IFC-to-Excel\`, `C:\DDC\DWG-to-Excel\`).

## CLI Syntax

```bash
# .rvt -> GLB + summary/report (+ element properties)
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out" --properties

# .rvt -> IFC4
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" --ifc --ifc-profile coordination --ifc-units m

# IFC -> Excel + JSONL + SQLite
cd C:\DDC\IFC-to-Excel
runtime\python.exe sources\ifc-excel\converter.py "C:\Models\Model.ifc" --output "C:\Out\Model"

# .dwg -> Excel + CSV + JSONL + DXF + SVG
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Projects\Plan.dwg" -o "C:\Out" --json

# RVT exit codes: 0 ok, 2 written with gaps / bad args, 1 failure
```

## Output Format Details

| Format | Description | Use Case |
|--------|-------------|----------|
| **XLSX / CSV** | Tables | BigQuery, pandas, databases |
| **JSONL / SQLite** | Properties and tables | pandas, databases |
| **GLB** | 3D model (`native_graph.glb`) | 3D viewers, web visualization |
| **IFC** | IFC4 | Interoperability, BIM tools |
| **HTML** | Interactive reports (n8n) | Dashboards, sharing |

## Google Cloud Integration Examples

### Cloud Storage + Converter
```python
from google.cloud import storage
import subprocess
import tempfile
from pathlib import Path

def process_revit_from_gcs(bucket_name, blob_name,
                           converter_path=r"C:\DDC\RVT-Converter\cli\RVTconverter.exe"):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    with tempfile.TemporaryDirectory() as tmpdir:
        local_file = f"{tmpdir}/{blob_name}"
        blob.download_to_filename(local_file)

        subprocess.run([converter_path, local_file, "-o", tmpdir, "--properties"])

        # Upload results
        for output_file in Path(tmpdir).glob("*.converted/*.jsonl"):
            result_blob = bucket.blob(f"results/{output_file.name}")
            result_blob.upload_from_filename(str(output_file))
```

### BigQuery Integration
```python
from google.cloud import bigquery
import pandas as pd

def load_bim_data_to_bigquery(xlsx_path, table_id):
    client = bigquery.Client()
    df = pd.read_excel(xlsx_path)

    job = client.load_table_from_dataframe(df, table_id)
    job.result()

    return f"Loaded {len(df)} rows to {table_id}"
```

### Vertex AI Classification
```python
from vertexai.generative_models import GenerativeModel
import pandas as pd

def classify_bim_elements(xlsx_path):
    model = GenerativeModel("gemini-pro")
    df = pd.read_excel(xlsx_path)

    elements = df[["Category", "Type Name", "Area", "Volume"]].head(20).to_dict()

    prompt = f"""
    Classify these construction elements according to Omniclass:
    {elements}
    Return JSON with element_id and omniclass_code.
    """

    response = model.generate_content(prompt)
    return response.text
```

## n8n Workflows - Process Logic Templates

The `n8n_*.json` files are **visual representations of process logic** - use them as reference architecture for building solutions in any language or Google Cloud services.

| # | Process Logic |
|---|---------------|
| 1 | Basic conversion flow |
| 2 | Advanced settings handling |
| 3 | Batch processing + reporting |
| 4 | BIM validation rules |
| 5 | AI classification (LLM + RAG) |
| 6 | Cost estimation with DDC CWICR |
| 7 | Carbon footprint calculation |
| 8 | ETL for LLM preparation |
| 9 | QTO report generation |

**Implement this logic in:** Python + Cloud Functions, Vertex AI Pipelines, BigQuery workflows, or any GCP service.

## DDC CWICR Database

The repository integrates with **DDC CWICR** - open construction cost database:
- 55,719 work items
- 27,672 resources
- 9 languages
- Pre-computed OpenAI embeddings for semantic search
- Qdrant vector database ready

## Guiding Philosophy

See `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` - explains data-driven approach to construction automation.

## Best Practices

1. Check exit codes (RVT: 0 ok, 2 written with gaps, 1 failure) and read `report.json` / `REPORT.txt` / `result.json`
2. Use `--properties` for RVT when element parameters are needed
3. Verify converter output and read its report before downstream use
4. Stream large files to Cloud Storage
5. Use BigQuery for analytics, Vertex AI for classification tasks

## License

Workflows, scripts, and documentation are MIT-licensed and can be freely integrated into Google Cloud workflows, Vertex AI pipelines, or any other solution. The DDC converter binaries are proprietary (see LICENSE-PROPRIETARY).

---

*Data-Driven Construction: transforming buildings into structured information.*
