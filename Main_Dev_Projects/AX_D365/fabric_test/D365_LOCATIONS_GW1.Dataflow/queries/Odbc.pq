// Made by: Hazzard
// Loads Lakehouse table D365_LOCATIONS from D365 (D365_EXPORT_PRD) through the ODBC gateway
shared Odbc = let
    D365Source = Odbc.Query("dsn=D365_EXPORT_PRD", "@@sql:sql/Odbc.sql@@"),
    FilteredRows = Table.SelectRows(D365Source, each ([Site] = "RVT-MS")),
    TypedColumns = Table.TransformColumnTypes(FilteredRows, {{"EXECUTION_DATE", type date}})
in
    TypedColumns;
