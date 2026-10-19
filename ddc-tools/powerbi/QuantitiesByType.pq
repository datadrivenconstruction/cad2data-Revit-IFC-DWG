// QuantitiesByType: element count and sums of the quantity columns per Category / TypeName / Level.
// Values are summed as exported (no unit conversion). Text that is not a number counts as empty.
let
    Source = Elements,
    Keys = {"Category", "TypeName", "Level"},
    Ensure = List.Accumulate(Keys, Source, (t, k) =>
        if List.Contains(Table.ColumnNames(t), k) then t else Table.AddColumn(t, k, each null, type text)),
    QtyNames = {"Length", "Width", "Height", "Thickness", "Perimeter", "Area", "Volume",
                "NetArea", "GrossArea", "NetVolume", "GrossVolume", "NetSideArea", "GrossSideArea", "Weight"},
    QtyCols = List.Select(Table.ColumnNames(Ensure), (c) =>
        List.Contains(List.Transform(QtyNames, Text.Lower), Text.Lower(c))),
    AsNumbers = Table.TransformColumns(
        Ensure,
        List.Transform(QtyCols, (c) => {c, (v) =>
            try (if v is number then v else Number.From(Text.Replace(Text.From(v), ",", "."), "en-US")) otherwise null,
            type nullable number})
    ),
    Aggs = {{"Count", each Table.RowCount(_), Int64.Type}}
        & List.Transform(QtyCols, (c) => {c, (g) => List.Sum(Table.Column(g, c)), type nullable number}),
    Grouped = Table.Group(AsNumbers, Keys, Aggs)
in
    Grouped
