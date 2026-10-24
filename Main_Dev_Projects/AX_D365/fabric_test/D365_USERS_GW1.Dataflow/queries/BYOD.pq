// Made by: Hazzard
// Loads Lakehouse table D365_USERS from D365 (D365_EXPORT_PRD) through the ODBC gateway
shared BYOD = let
    D365Source = Odbc.Query("dsn=D365_EXPORT_PRD", "@@sql:sql/BYOD.sql@@"),
    TypedColumns = Table.TransformColumnTypes(D365Source, {{"EXECUTION_DATE", type date}, {"RECORDID", type text}})
in
    TypedColumns;
