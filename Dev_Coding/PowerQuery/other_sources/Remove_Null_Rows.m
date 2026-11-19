// Made by: Hazzard
// Other Sources: Remove blank or null rows from critical columns

let
    Source = Excel.CurrentWorkbook(){[Name="Table1"]}[Content],
    FilteredRows = Table.SelectRows(Source, each [CustomerID] <> null and [CustomerID] <> "")
in
    FilteredRows
