-- Made by: Hazzard
-- D365 closed pick work lines (status 4) with shipment status, location, batch, LPN, pick times and picker
SELECT
    'D365'                                  AS DATA_BASE,
    'C79'                                   AS ORG_CODE,
    'RIVERTON'                             AS ORG_NAME,
    'HVAC'                                  AS DIVISION,
    FORMAT(GETDATE(), 'MM-dd-yyyy')         AS EXECUTION_DATE,
    FORMAT(GETDATE(), 'HH:mm:ss')           AS EXECUTION_TIME,
    work_line.SHIPMENTID                    AS [SHIPMENT],
    work_line.ORDERNUM                      AS [SALES ORDER],
    work_line.WORKID                        AS [WORK],
    work_line.ITEMID                        AS [ITEM NUMBER],
    work_line.QTYWORK                       AS QTY,
    CASE shipment.SHIPMENTSTATUS
        WHEN 0 THEN 'OPEN'
        WHEN 1 THEN 'WAVED'
        WHEN 2 THEN 'IN PROCESS'
        WHEN 4 THEN 'LOADED'
        WHEN 5 THEN 'SHIPPED'
        WHEN 6 THEN 'RECEIVED'
        ELSE 'UNKNOWN'
    END                                     AS [SHIPMENT STATUS],
    inventory_dim.INVENTSITEID              AS [SITE],
    inventory_dim.WMSLOCATIONID             AS [LOCATION],
    inventory_dim.INVENTBATCHID             AS [BATCH NUMBER],
    inventory_dim.INVENTLOCATIONID          AS [WAREHOUSE],
    inventory_dim.LICENSEPLATEID            AS [LICENSE PLATE],
    work_line.WORKINPROCESSUTCDATETIME      AS [START PICK TIME],
    work_line.WORKCLOSEDUTCDATETIME         AS [END PICK TIME],
    load_line.LOADCLOSEDUTCDATETIME         AS [LOAD CONFIRM DATE AND TIME],
    work_user.USERNAME                      AS [PICKER]
FROM SIWHSWORKLINE                 work_line
INNER JOIN WHSLOADLINE             load_line
    ON  load_line.RECORDID              = work_line.LOADLINEREFRECID
INNER JOIN SHIPMENTTABLE           shipment
    ON  shipment.SHIPMENTID             = work_line.SHIPMENTID
INNER JOIN WHSWORKINVENTTRANS      work_trans
    ON  work_trans.WORKID               = work_line.WORKID
    AND work_trans.LINENUM              = work_line.LINENUM
INNER JOIN INVENTTRANSORIGIN       trans_origin
    ON  trans_origin.INVENTTRANSID      = work_trans.InventTransIdFrom
INNER JOIN INVENTTRANS             inventory_trans
    ON  inventory_trans.INVENTTRANSORIGIN = trans_origin.RECORDID
INNER JOIN INVENTDIM               inventory_dim
    ON  inventory_dim.INVENTDIMID       = inventory_trans.INVENTDIMID
-- Was FULL OUTER JOIN: the WHERE on work_line already made it a LEFT JOIN
LEFT JOIN SIWHSWorkUserStaging     work_user
    ON  work_user.USERID                = work_line.USERID
WHERE work_line.QTYWORK > 0
  AND work_line.WORKSTATUS = 4;
