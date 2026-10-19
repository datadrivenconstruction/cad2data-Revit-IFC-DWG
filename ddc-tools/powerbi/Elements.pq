// Elements: RawElements with common column roles renamed to ElementId, GlobalId, Category, TypeName, Level.
// If your export uses other column names, add them to the alias lists below.
let
    Source = RawElements,
    Role = (t as table, aliases as list, newName as text) as table =>
        let
            Cols = Table.ColumnNames(t),
            Hits = List.RemoveNulls(List.Transform(
                aliases,
                (a) => List.First(List.Select(Cols, (c) => Text.Lower(c) = Text.Lower(a)), null)
            )),
            Hit = List.First(Hits, null)
        in
            if Hit = null or Hit = newName or List.Contains(Cols, newName) then t
            else Table.RenameColumns(t, {{Hit, newName}}),
    A = Role(Source, {"ElementId", "Element Id", "native_id", "Id", "ObjectId"}, "ElementId"),
    B = Role(A, {"GlobalId", "Global Id", "IfcGUID", "UniqueId", "unique_id", "Guid"}, "GlobalId"),
    C = Role(B, {"Category", "IfcClass", "IfcType", "Entity", "source_class", "Class"}, "Category"),
    D = Role(C, {"Type Name", "TypeName", "Family and Type", "ObjectType", "Type"}, "TypeName"),
    E = Role(D, {"Level", "Base Constraint", "Reference Level", "BuildingStorey", "Storey", "Floor"}, "Level")
in
    E
