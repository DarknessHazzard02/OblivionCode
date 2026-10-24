// Made by: Hazzard
// Loads Lakehouse table D365_WAREHOUSE_PROD_SHIPMENT from D365 (D365_EXPORT_PRD) through the ODBC gateway
shared Odbc = let
    D365Source = Odbc.Query("dsn=D365_EXPORT_PRD", "@@sql:sql/Odbc.sql@@"),
    TypedColumns = Table.TransformColumnTypes(D365Source, {{"EXECUTION_DATE", type date}}),
    RenamedColumns = Table.RenameColumns(TypedColumns, {{"Division", "Division2"}})
in
    RenamedColumns;
