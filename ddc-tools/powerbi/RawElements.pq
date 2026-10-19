// RawElements: reads every export file of one format from ExportFolder and stacks them.
// Works offline, no Python. Auxiliary files (geometry_index, property_scopes, manifests) are skipped.
let
    Exts = {".xlsx", ".csv", ".jsonl"},
    Order = List.Distinct({"." & Text.Lower(PreferredFormat)} & Exts),
    AllFiles = Table.SelectRows(
        Folder.Files(ExportFolder),
        each List.Contains(Exts, Text.Lower([Extension]))
            and not Text.StartsWith([Name], "~$")
            and not Text.Contains(Text.Lower([Name]), "geometry_index")
            and not Text.Contains(Text.Lower([Name]), "property_scopes")
            and not Text.Contains(Text.Lower([Name]), "manifest")
    ),
    Chosen = List.First(
        List.Select(Order, (e) => not Table.IsEmpty(Table.SelectRows(AllFiles, each Text.Lower([Extension]) = e))),
        null
    ),
    Files = if Chosen = null then error "No .xlsx, .csv or .jsonl export files found in ExportFolder" else
        Table.SelectRows(AllFiles, each Text.Lower([Extension]) = Chosen),
    ReadOne = (content as binary, ext as text) as table =>
        if ext = ".csv" then
            Table.PromoteHeaders(
                Csv.Document(content, [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
                [PromoteAllScalars = true]
            )
        else if ext = ".xlsx" then
            Excel.Workbook(content, true, true){0}[Data]
        else
            let
                Lines = Lines.FromBinary(content, null, null, 65001),
                NonEmpty = List.Select(Lines, each Text.Trim(_) <> ""),
                Records = List.Transform(NonEmpty, each Json.Document(_))
            in
                Table.FromRecords(Records, null, MissingField.UseNull),
    WithTables = Table.AddColumn(Files, "Data", each ReadOne([Content], Text.Lower([Extension]))),
    Tagged = Table.AddColumn(WithTables, "T", (row) => Table.AddColumn(row[Data], "SourceFile", (r) => row[Name])),
    Combined = Table.Combine(Tagged[T])
in
    Combined
