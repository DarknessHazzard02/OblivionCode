// Made by: Hazzard
// Loads Lakehouse table D365_ITEM_MASTER from D365 (D365_EXPORT_PRD) through the ODBC gateway
shared #"<query-id-22>" = let
    D365Source = Odbc.Query("dsn=D365_EXPORT_PRD", "@@sql:sql/query-id-22.sql@@")
in
    D365Source;
