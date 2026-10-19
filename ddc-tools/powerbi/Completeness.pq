// Completeness: for every column, how many elements have a value (share in percent).
// On very wide tables (thousands of columns) this takes a while; filter the list if needed.
let
    Source = Elements,
    Total = Table.RowCount(Source),
    Rows = List.Transform(Table.ColumnNames(Source), (c) =>
        let Filled = List.Count(List.Select(Table.Column(Source, c), each _ <> null and _ <> ""))
        in [Column = c, Filled = Filled, Total = Total, Percent = if Total = 0 then 0 else Filled / Total]),
    Result = Table.FromRecords(Rows, type table [Column = text, Filled = Int64.Type, Total = Int64.Type, Percent = Percentage.Type])
in
    Result
