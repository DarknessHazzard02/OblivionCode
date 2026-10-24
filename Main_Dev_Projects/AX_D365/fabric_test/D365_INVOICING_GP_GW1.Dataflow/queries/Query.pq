// Made by: Hazzard
// Loads Lakehouse table D365_INVOICING_GP from D365 (D365_EXPORT_PRD) through the ODBC gateway
shared Query = let
    D365Source = Odbc.Query("dsn=D365_EXPORT_PRD", "@@sql:sql/Query.sql@@")
in
    D365Source;
