# Test data for `ddc table`

Trimmed real converter output, a handful of elements each:

* `ifc_excel/data.jsonl` - DDC IFC to Excel 0.3.1-preview run on `Sample_Projects/Ifc2x3_Duplex_Architecture.ifc`
  (open sample): 19 objects with their property sets, types, storeys and materials.
* `rvt_converted/properties.jsonl`, `native_graph.ifc` - RVT Converter 0.6.8 (`--properties --ifc`) run on
  `DDC_Update_Revit_from_Excel/Samples/Sample_R24.rvt` (DDC sample): two walls, the wall type, the level, one
  phase; the IFC keeps the header, the units and the entities of the first two walls.
* `dwg/sample.jsonl` - DWG to Excel 0.4.1 run on `sample_AC1027.dwg` from the ACadSharp test files (MIT):
  20 records (lines, polylines, circle, arc, text, insert, hatch, one envelope-only record).

No Autodesk sample models are used. Local paths were removed from the metadata.
