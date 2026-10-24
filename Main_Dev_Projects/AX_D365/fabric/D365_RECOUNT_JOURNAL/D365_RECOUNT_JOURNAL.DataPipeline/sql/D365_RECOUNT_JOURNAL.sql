-- Made by: Hazzard
-- D365 recount journal lines (journal name RECOUNT) with counted vs on-hand and cost (Riverton C79)
SELECT
    'D365'                              AS DATA_BASE,
    'C79'                               AS ORG_CODE,
    'RIVERTON'                         AS ORG_NAME,
    'HVAC'                              AS DIVISION,
    FORMAT(GETDATE(), 'MM-dd-yyyy')     AS EXECUTION_DATE,
    FORMAT(GETDATE(), 'HH:mm:ss')       AS EXECUTION_TIME,
    count_line.COUNTINGDATE             AS [Date],
    count_line.ITEMNUMBER               AS [Item Number],
    released_product.ITEMNUMBER         AS [Product Name],
    count_line.INVENTORYSITEID          AS [Site],
    count_line.INVENTORYSITEID          AS [Warehouse],
    count_line.WAREHOUSELOCATIONID      AS [LOCATION],
    count_line.ITEMBATCHNUMBER          AS [Batch Number],
    count_line.ONHANDQUANTITY           AS [On-Hand],
    count_line.COUNTEDQUANTITY          AS [Counted],
    count_line.ADJUSTMENTQUANTITY       AS [Quantity Adjustment],
    count_line.WORKERPERSONNELNUMBER    AS [Worker],
    count_line.LICENSEPLATENUMBER       AS [License Plate Number],
    count_line.CostPrice                AS [Cost Price],
    count_line.CostAmount               AS [Cost Amount]
FROM InventInventoryCountingJournalHeaderStaging     count_header
INNER JOIN InventInventoryCountingJournalLineStaging count_line
    ON  count_line.JOURNALNUMBER   = count_header.JOURNALNUMBER
INNER JOIN EcoResReleasedProductV2Staging            released_product
    ON  released_product.ITEMID    = count_line.ITEMNUMBER
WHERE count_header.JOURNALNAMEID = 'RECOUNT';
