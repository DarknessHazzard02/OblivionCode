// Made by: Hazzard
// Cleans the source export and keeps rows with a plant
let
    Source = Csv.Document(File.Contents(FilePath), [Delimiter = ",", Encoding = 65001]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    CleanedHeaders = Table.TransformColumnNames(PromotedHeaders, Text.Trim),
    RemovedColumns = Table.SelectColumns(CleanedHeaders, {"Plant", "Material", "OnHand"}),
    FilteredRows = Table.SelectRows(RemovedColumns, each [Plant] <> null and [Plant] <> ""),
    ChangedTypes = Table.TransformColumnTypes(FilteredRows, {{"OnHand", type number}})
in
    ChangedTypes
