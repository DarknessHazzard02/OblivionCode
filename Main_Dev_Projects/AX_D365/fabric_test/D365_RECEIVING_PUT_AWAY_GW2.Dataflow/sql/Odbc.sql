-- Made by: Hazzard
-- D365 closed purchase-order put-away work lines with delivery, batch, LPN, timestamps and user
SELECT
    'D365'                                          AS DATA_BASE,
    'C79'                                           AS ORG_CODE,
    'RIVERTON'                                     AS ORG_NAME,
    'HVAC'                                          AS DIVISION,
    FORMAT(GETDATE(), 'MM-dd-yyyy')                 AS EXECUTION_DATE,
    FORMAT(GETDATE(), 'HH:mm:ss')                   AS EXECUTION_TIME,
    work_staging.SIDELIVERYNUMBER                   AS [DELIVERY NUMBER],
    work_line.SOURCEORDERNUMBER                     AS [PURCHASE ORDER NUMBER],
    work_line.WAREHOUSEWORKID                       AS [WORK ID],
    work_line.ITEMNUMBER                            AS [ITEM NUMBER],
    work_line.WORKQUANTITY                          AS [QUANTITY],
    CASE work_line.WAREHOUSEWORKSTATUS
        WHEN 0 THEN 'OPEN'
        WHEN 1 THEN 'IN PROCESS'
        WHEN 2 THEN 'PENDING REVIEW'
        WHEN 3 THEN 'SKIPPED'
        WHEN 4 THEN 'CLOSED'
        WHEN 5 THEN 'CANCELLED'
        WHEN 6 THEN 'COMBINED'
        ELSE CAST(work_line.WAREHOUSEWORKSTATUS AS VARCHAR(10))
    END                                             AS [WORK ID STATUS],
    work_line.WAREHOUSELOCATIONID                   AS [LOCATION],
    inventory_dim.INVENTBATCHID                     AS [BATCH NUMBER],
    inventory_dim.LICENSEPLATEID                    AS [LICENSE PLATE],
    work_line.WAREHOUSEWORKPROCESSINGSTARTDATETIME  AS [WORK IN PROCESS],
    work_line.WAREHOUSEWORKCLOSEDDATETIME           AS [CLOSED WORK],
    work_user.USERNAME                              AS [NAME OF USER]
FROM WHSWORKLINE                         work_line
INNER JOIN WHSWORKTABLE                  work_header
    ON  work_header.WAREHOUSEWORKID      = work_line.WAREHOUSEWORKID
INNER JOIN SIWHSWorkTableStaging         work_staging
    ON  work_staging.WORKID              = work_line.WAREHOUSEWORKID
INNER JOIN SIWHSWorkInventTransStaging   work_trans
    ON  work_trans.WORKID                = work_line.WAREHOUSEWORKID
    AND work_trans.LINENUM               = work_line.WORKLINENUMBER
INNER JOIN SIInventTransOriginStaging    trans_origin
    ON  trans_origin.INVENTTRANSID       = work_trans.INVENTTRANSIDFROM
INNER JOIN SIInventTransStaging          inventory_trans
    ON  inventory_trans.INVENTTRANSORIGIN = trans_origin.RECORDID
INNER JOIN InventDim                     inventory_dim
    ON  inventory_dim.INVENTDIMID        = inventory_trans.INVENTDIMID
INNER JOIN SIWHSWORKUSERSTAGING          work_user
    ON  work_user.USERID                 = work_line.PROCESSINGWAREHOUSEMOBILEDEVICEUSERID
WHERE work_line.WORKQUANTITY > 0
  AND work_line.WAREHOUSEWORKCLOSEDDATETIME <> '1900-01-01 00:00:00'
  AND work_line.WAREHOUSEWORKTYPE = 2               -- 2 = Purchase order work
  AND work_header.WAREHOUSEWORKORDERTYPE = 1        -- 1 = Purchase order
ORDER BY work_line.WAREHOUSEWORKPROCESSINGSTARTDATETIME DESC;
