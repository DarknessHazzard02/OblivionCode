// Made by: Hazzard
// Loads Lakehouse table D365_INVOICING from D365 (D365_EXPORT_PRD) through the ODBC gateway
shared Query = let
    D365Source = Odbc.Query("dsn=D365_EXPORT_PRD", "@@sql:sql/Query.sql@@"),
    TypedColumns = Table.TransformColumnTypes(D365Source, {{"ORDER_LINE_NUMBER", type number}, {"QUANTITY", type number}, {"SALESPRICE", type number}, {"AMOUNT", type number}}),
    DateOnlyColumns = Table.TransformColumns(TypedColumns, {{"REQUEST_DATE", each DateTime.Date(_), type nullable date}, {"SCHEDULE_SHIP_DATE", each DateTime.Date(_), type nullable date}, {"SHIP_CONFIRM_DATE", each DateTime.Date(_), type nullable date}}),
    TypedColumns2 = Table.TransformColumnTypes(DateOnlyColumns, {{"RELEASE_TO_WAREHOUSE_DATE", type date}, {"ACTUAL_SHIPMENT_DATE", type date}, {"EXECUTION_DATE", type date}})
in
    TypedColumns2;
