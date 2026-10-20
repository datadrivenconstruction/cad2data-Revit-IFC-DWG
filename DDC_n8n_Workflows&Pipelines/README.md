# n8n workflows

Nine workflows (conversion, batch pipeline, validation, AI classification, cost and CO2 estimation, ETL and QTO
report). They use the flat table `<name>_rvt.xlsx` (sheet `Project_Data`) and a 3D model next to the input, produced from the output of the converters in
[`DDC_WINDOWS_Converters/`](../DDC_WINDOWS_Converters/).

## How the port works

The new converters write other things (a saved parameter graph, entity tables, drawing records). The free tool
[`ddc-tools`](../ddc-tools/README.md) rebuilds the old flat table from them:

    ddc convert "C:\Models\Project.rvt" --converters "C:\DDC\cad2data-Revit-IFC-DWG\DDC_WINDOWS_Converters"

runs the right converter (`RVTconverter.exe --properties --ifc`, the IFC to Excel runtime, or `dwg2excel.exe`) and writes
`Project_rvt.xlsx` / `_ifc.xlsx` / `_dwg.xlsx` next to the model, sheet `Project_Data`, with the old columns
(`ID`, `Category` as `OST_Walls` for Revit and the IFC class for IFC, `Family`, `Type Name`, `Level`, `Length`, `Area`,
`Volume`, `On the standard 3D View`, one column per parameter). The column mapping is documented in the
[ddc-tools README](../ddc-tools/README.md#ddc-table). Everything after the conversion step of the workflows
(reading the XLSX, grouping, AI steps, reports) is unchanged.

**One-time setup:** `pip install "C:\DDC\cad2data-Revit-IFC-DWG\ddc-tools"` (Python 3.9+) and set two variables in the
setup node of the workflow: `path_to_ddc` (`ddc`, or the full path to `ddc.exe`) and `path_to_converters` (the folder
`DDC_WINDOWS_Converters` of this repository). The sample file paths are placeholders in `C:\DDC\Models\`.

## Status

| Workflow | What changed | Checked |
|---|---|---|
| n8n_1 | Execute Command runs `ddc convert`. | Command built from the node values and run on a Revit sample: converter folder and `_rvt.xlsx` written. |
| n8n_2 | Form and variables replaced by the options of the new RVT converter (`--properties`, `--ifc`, `--gltf`, `--obj`, `--neutral`, `--timings`, IFC profile, unit, categories). Runs the converter, then `ddc table`. The old modes `basic/standard/complete`, `bbox`, `schedule`, `sheets2pdf`, `-no-xlsx`, `-no-collada` do not exist any more. | Command expression evaluated and run. The form itself was not opened in n8n. |
| n8n_3 | Batch pipeline: `ddc convert` per file, DAE checks replaced by GLB checks (GLB exists for RVT only; IFC and DWG are checked by their XLSX), new options note. | Code nodes run in Node.js with sample data (paths, success logic, HTML report); command evaluated. |
| n8n_4 | Conversion step as n8n_1; the validation code reads the table unchanged. | Validation code run on a table built from a Revit sample with a rules workbook. |
| n8n_5, n8n_6, n8n_7 | Conversion step as n8n_1. The "On the standard 3D View" filter works on the new column of the same name. In n8n_7 three references to a renamed node were fixed. | Commands evaluated, all code nodes syntax-checked, node references checked. **The AI steps (OpenAI, Anthropic, Grok, OpenRouter) were not run:** they need your credentials. |
| n8n_8 | Conversion step as n8n_1. | Command evaluated and run. |
| n8n_9 | Conversion step as n8n_1; the column names lost the old ` : String` / ` : Double` / ` : Boolean` suffixes (`Category`, `Type Name`, `Volume`). Walls are filtered with `OST_Walls`, so this workflow is for Revit files; for IFC use the class `IfcWallStandardCase` / `IfcWall`. | Command evaluated and run; code syntax-checked. |

No workflow was run inside an n8n instance (none is installed here); the checks above exercise the commands, the code
nodes and the node references outside n8n. Report anything that behaves differently in your n8n version.

## What is different in the data

* `Volume`, `Area`, `Length` of a Revit element come from the converter's IFC quantities, else from the GLB mesh (`Quantity Source`
  says which); they are not Revit's own formula values. Without `--ifc` there are no category, family or type names.
* The old `bbox` columns (`BoundingBoxMin_X` ... in feet) are not produced; n8n_5 contains the code for them, it stays inactive.
  The table has `BBox X/Y/Z` in metres for RVT elements with a mesh.
* Schedules and sheet PDFs (`schedule`, `sheets2pdf`) have no equivalent; DGN is not supported.
* A 3D model is the GLB (`<name>.converted\native_graph.glb`) of the RVT converter, not a DAE. View it in
  [`DDC_Data_Viewer`](../DDC_WINDOWS_Converters/DDC_Data_Viewer/).
