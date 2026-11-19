// FreeCodeCamp: Power Query (M Language)
// Transformation: Parse dates, trim whitespace, uppercase status

let
    Source = Csv.Document(File.Contents("C:\Data\raw_orders.csv"), [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders, {{"OrderID", Int64.Type}, {"OrderDate", type date}, {"Amount", type number}, {"Status", type text}}),
    TrimmedText = Table.TransformColumns(ChangedType, {{"Status", Text.Trim, type text}}),
    UppercasedStatus = Table.TransformColumns(TrimmedText, {{"Status", Text.Upper, type text}})
in
    UppercasedStatus
