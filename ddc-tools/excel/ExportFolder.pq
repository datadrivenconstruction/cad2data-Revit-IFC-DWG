// Excel: the folder is read from the Config sheet (cell next to "ExportFolder"), so there is nothing to edit here.
let
    Value = Excel.CurrentWorkbook(){[Name = "Config"]}[Content],
    Row = Table.SelectRows(Value, each [Setting] = "ExportFolder"){0}[Value]
in
    Row
