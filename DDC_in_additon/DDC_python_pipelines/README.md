# Python notebooks

| Notebook | Status |
|---|---|
| 1 Conversion of a single Revit project | Conversion cell ported to `DDC_WINDOWS_Converters/DDC_RVT_Converter/cli/RVTconverter.exe`. Later cells still read the old `*_rvt.xlsx` and need to be adapted to `properties.jsonl`. |
| 2 Batch conversion Revit / IFC | Ported and tested: RVT via `RVTconverter.exe --properties`, IFC via `DDC_IFC_to_Excel`. Results go to `<path>\converted\`. |
| 3, 4, 6 | Analytics on the old XLSX layout; not ported. |
| 5, 7 | Conversion cell still uses the retired `RvtExporter.exe` / `IfcExporter.exe` and the old XLSX layout; marked as not ported. |

Converter folders and command lines: `DDC_WINDOWS_Converters/README.md`.
