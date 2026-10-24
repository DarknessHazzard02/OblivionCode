// Made by: Hazzard
// Loads Lakehouse table D365_ON_HAND from D365 (D365_EXPORT_PRD) through the ODBC gateway
shared Query = let
    D365Source = Odbc.Query("dsn=D365_EXPORT_PRD", "@@sql:sql/Query.sql@@"),
    TypedColumns = Table.TransformColumnTypes(D365Source, {{"EXECUTION_DATE", type date}})
in
    TypedColumns;
