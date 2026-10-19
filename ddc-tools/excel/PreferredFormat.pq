// Excel: read from the Config sheet ("PreferredFormat": xlsx, csv or jsonl).
let
    Value = Excel.CurrentWorkbook(){[Name = "Config"]}[Content],
    Row = Table.SelectRows(Value, each [Setting] = "PreferredFormat"){0}[Value]
in
    Row
