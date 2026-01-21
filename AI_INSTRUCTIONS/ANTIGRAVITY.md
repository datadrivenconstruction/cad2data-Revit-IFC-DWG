# Google Antigravity Instructions for CAD2DATA Repository

## What Is This Repository?

**CAD2DATA Pipeline** - open-source toolkit for converting and extracting data from construction files (Revit, IFC, DWG, DGN).

## Key Value

Transform proprietary CAD/BIM files into structured, analyzable data formats (JSON, CSV).

## Available Converters

| Tool | Input | Output | Use Case |
|------|-------|--------|----------|
| DDC_CONVERTER_DGN | .dgn | .ifc, .dwg | Legacy CAD conversion |
| DDC_CONVERTER_DWG | .dwg | JSON, CSV | DWG data extraction |
| DDC_CONVERTER_IFC | .ifc | JSON, CSV | IFC analysis |
| DDC_CONVERTER_REVIT | .rvt | JSON, CSV | Revit data export |
| DDC_CONVERTER_Revit2IFC | .rvt | .ifc | Revit to IFC |

## Guiding Philosophy

See `DATA_DRIVEN_CONSTRUCTION_BOOK.txt` - explains data-driven approach to construction automation.

## Integration Points

### Google Cloud Integration
```python
from google.cloud import storage
from DDC_CONVERTER_IFC import parse_ifc

def process_ifc_from_gcs(bucket_name, blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    content = blob.download_as_bytes()
    result = parse_ifc(content)

    # Upload result
    result_blob = bucket.blob(f"results/{blob_name}.json")
    result_blob.upload_from_string(json.dumps(result))
    return result
```

### BigQuery Integration
```python
from google.cloud import bigquery
import json

def upload_ifc_data_to_bigquery(ifc_data, table_id):
    client = bigquery.Client()
    table = client.get_table(table_id)

    rows = [
        {"element_type": elem["type"], "quantity": elem["quantity"]}
        for elem in ifc_data["elements"]
    ]

    errors = client.insert_rows_json(table, rows)
    return errors
```

### Vertex AI Integration
```python
from vertexai.generative_models import GenerativeModel

def classify_elements_with_ai(ifc_data):
    model = GenerativeModel("gemini-pro")

    prompt = f"""
    Classify the following construction elements according to UniClass:
    {json.dumps(ifc_data['elements'][:10])}
    """

    response = model.generate_content(prompt)
    return response.text
```

## n8n Workflows

Pre-built automation workflows in `n8n_*.json`:
- Batch conversion
- Validation
- AI Classification
- Cost Estimation
- Carbon Footprint calculation
- QTO Reports

## Common Tasks

1. **Extract quantities from IFC**
2. **Validate BIM model compliance**
3. **Generate cost estimates**
4. **Calculate carbon footprint**
5. **Create QTO reports**

## Data Schema

All converters output consistent JSON:
```json
{
  "source_file": "building.ifc",
  "format": "IFC4",
  "elements": [
    {
      "id": "2O2Fr$t4X7Zf8NOew3FL3",
      "type": "IfcWall",
      "name": "Basic Wall",
      "properties": {...},
      "quantities": {...}
    }
  ],
  "summary": {
    "total_elements": 1234,
    "by_type": {...}
  }
}
```

## Best Practices

1. Use streaming for large files
2. Validate IFC schema before processing
3. Cache results in Cloud Storage
4. Use BigQuery for analytics
5. Apply AI for classification tasks

## Open Source License

All tools are open-source. Can be freely integrated into Google Cloud workflows, Vertex AI pipelines, or any other solution.

---

*Data-Driven Construction: transforming buildings into structured information.*
