# Google Antigravity Instructions for CAD2DATA Repository

## What Is This Repository?

**CAD2DATA Pipeline** - open-source toolkit for converting and extracting data from construction files (Revit, IFC, DWG, DGN) to open formats (XLSX, DAE, IFC, PDF, HTML).

## Key Value

- Transform proprietary CAD/BIM files into structured, analyzable data
- No vendor lock-in, no licenses required
- All tools have CLI interfaces for direct execution
- Works offline

## Available Converters

| Converter | Input | Output |
|-----------|-------|--------|
| RvtExporter.exe | Revit (.rvt, .rfa) 2015-2026 | XLSX + DAE + PDF + Schedules |
| RVT2IFCconverter.exe | Revit (.rvt, .rfa) | IFC2x3, IFC4, IFC4.3, IFCXML, IFCZIP, HDF5 |
| IfcExporter.exe | IFC (2x3, 4, 4x1, 4x3) | XLSX + DAE |
| DwgExporter.exe | AutoCAD (.dwg) 1983-2026 | XLSX + PDF |
| DgnExporter.exe | MicroStation (.dgn) V7, V8 | XLSX |

## CLI Syntax

```bash
# Revit to Excel + 3D geometry
RvtExporter.exe "building.rvt"
RvtExporter.exe "building.rvt" complete bbox schedule sheets2pdf

# Revit to IFC
RVT2IFCconverter.exe "building.rvt"
RVT2IFCconverter.exe "building.rvt" preset=extended

# IFC to Excel + 3D
IfcExporter.exe "model.ifc"

# DWG to Excel + PDF
DwgExporter.exe "plan.dwg"

# DGN to Excel
DgnExporter.exe "design.dgn"
```

## Output Format Details

| Format | Description | Use Case |
|--------|-------------|----------|
| **XLSX** | Elements as rows, properties as columns | BigQuery, pandas, databases |
| **DAE** | Collada 3D with element IDs matching XLSX | 3D viewers, web visualization |
| **IFC** | Open BIM standard | Interoperability, BIM tools |
| **PDF** | Drawings and sheets | Documentation |
| **HTML** | Interactive reports | Dashboards, sharing |

## Google Cloud Integration Examples

### Cloud Storage + Converter
```python
from google.cloud import storage
import subprocess
import tempfile

def process_revit_from_gcs(bucket_name, blob_name, converter_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    with tempfile.TemporaryDirectory() as tmpdir:
        local_file = f"{tmpdir}/{blob_name}"
        blob.download_to_filename(local_file)

        subprocess.run([converter_path, local_file, "complete", "bbox"])

        # Upload results
        for output_file in Path(tmpdir).glob("*.xlsx"):
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

## n8n Workflows (9 included)

| # | Purpose |
|---|---------|
| 1 | Basic conversion |
| 2 | Advanced settings |
| 3 | Batch processing with HTML reports |
| 4 | BIM validation |
| 5 | AI classification (LLM + RAG) |
| 6 | Cost estimation with DDC CWICR |
| 7 | Carbon footprint CO2 |
| 8 | ETL for LLM |
| 9 | QTO HTML reports |

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

1. Use `complete` mode for full extraction (1209 categories)
2. Enable `bbox` for spatial analysis
3. Stream large files to Cloud Storage
4. Use BigQuery for analytics
5. Apply Vertex AI for classification tasks

## License

All tools are open-source (MIT). Can be freely integrated into Google Cloud workflows, Vertex AI pipelines, or any other solution.

---

*Data-Driven Construction: transforming buildings into structured information.*
