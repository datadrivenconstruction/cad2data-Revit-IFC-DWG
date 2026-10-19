# n8n workflows

All nine workflows start a converter with an **Execute Command** node as `"<converter>" "<model file>"`.
That call shape is still valid for the new converters. The default converter path in every workflow is now

    C:\DDC\cad2data-Revit-IFC-DWG\DDC_WINDOWS_Converters\DDC_RVT_Converter\cli\RVTconverter.exe

(change it to where you cloned this repository; the sample file paths are placeholders in `C:\DDC\Models\`).

## What is NOT ported yet

The workflows were written for the retired 18.x converters, which wrote `<name>_rvt.xlsx` (sheet `Project_Data`)
and `<name>_rvt.dae` next to the input. The new RVT converter writes a folder `<name>.converted`
(`native_graph.glb`, `summary.json`, `report.json`, and with `--properties` also `properties.jsonl`).
So the paths are updated, but the steps after the conversion node still look for the old XLSX/DAE:

| Workflow | Status |
|---|---|
| n8n_1, n8n_2 | Converter call works for RVT with the new path. `n8n_2` builds the old output arguments (`.xlsx`, `.dae`, `bbox`, ...), which the new CLI does not accept: use `-o <new folder>` instead. |
| n8n_3 | Passes the old positional output arguments, which the new CLI refuses. Needs the same change, plus the verification step (looks for `.xlsx` / `.dae`). |
| n8n_4 - n8n_9 | Converter call works; the parsing steps expect the old XLSX and must be adapted to `properties.jsonl` (RVT) or `drawing.xlsx` (IFC, via `DDC_IFC_to_Excel`). |

IFC and DWG: use `DDC_IFC_to_Excel` and `DDC_DWG_to_Excel` (see their `README.md` for the command lines).
