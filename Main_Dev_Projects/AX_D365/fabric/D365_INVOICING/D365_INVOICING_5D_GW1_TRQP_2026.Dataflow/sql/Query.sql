-- Made by: Hazzard
-- D365 shipped invoice lines since 2026-01-01 with delivery address (Riverton C79)
SELECT
    'D365'                                          AS DATA_BASE,
    'C79'                                           AS ORGANIZATION_CODE,
    'RIVERTON'                                     AS ORGANIZATION_NAME,
    'HVAC'                                          AS DIVISION,
    so_line_v3.DELIVERYADDRESSNAME                  AS CUSTOMER_NAME,
    so_line.CUSTACCOUNT                             AS CUSTOMER_NUMBER,
    so_line.SALESID                                 AS ORDER_NUMBER,
    so_line.LINENUM                                 AS ORDER_LINE_NUMBER,
    so_header.PURCHORDERFORMNUM                     AS CUST_PO_NUMBER,
    packing_slip.BILLOFLADINGID                     AS [BILL OF LADING ID],
    packing_slip.CTSSHIPMENTID                      AS DELIVERY_NUMBER,
    so_line.ITEMID                                  AS ITEM_NUMBER,
    item.DESCRIPTION                                AS DESCRIPTION,
    packing_line.QTY                                AS QUANTITY,
    bill_of_lading.TRAILERNUMBER                    AS WAYBILL_AIRBILL,
    so_line.SALESPRICE * packing_line.QTY           AS SALESPRICE,
    packing_line.VALUEMST                           AS AMOUNT,
    so_line_v3.DELIVERYADDRESSSTATEID               AS [SHIPPING STATE],
    bill_of_lading.CARRIERNAME                      AS FREIGHT_CARRIER_CODE,
    so_line.MCACUSTSHIPDATEREQUESTED                AS REQUEST_DATE,
    so_line.SHIPPINGDATEREQUESTED                   AS SCHEDULE_SHIP_DATE,
    CAST(load_line.CREATEDATETIME AS DATE)          AS RELEASE_TO_WAREHOUSE_DATE,
    FORMAT(load_line.CREATEDATETIME, 'HH:mm:ss')    AS RELEASE_TO_WAREHOUSE_TIME,
    packing_line.DELIVERYDATE                       AS SHIP_CONFIRM_DATE,
    CAST(packing_line.CREATEDATETIME AS DATE)       AS ACTUAL_SHIPMENT_DATE,
    FORMAT(packing_line.CREATEDATETIME, 'HH:mm:ss') AS ACTUAL_SHIPMENT_TIME,
    CASE WHEN so_line.MCACUSTSHIPDATEREQUESTED > packing_line.CREATEDATETIME THEN 'YES' ELSE 'NO' END
                                                    AS [MEET REQ. SHIP DATE],
    CASE WHEN so_line.SHIPPINGDATEREQUESTED > packing_line.CREATEDATETIME THEN 'YES' ELSE 'NO' END
                                                    AS [MEET SCHED. SHIP DATE],
    so_header.DLVREASON                             AS [DELIVERY REASON],
    delivery_address.STREET                         AS [DELIVERY_STREET],
    delivery_address.CITY                           AS [DELIVERY_CITY],
    delivery_address.STATE                          AS [DELIVERY_STATE],
    delivery_address.ZIPCODE                        AS [DELIVERY_ZIPCODE],
    delivery_address.COUNTRYREGIONID                AS [DELIVERY_COUNTRY],
    FORMAT(GETDATE(), 'yyyy-MM-dd')                 AS EXECUTION_DATE,
    FORMAT(GETDATE(), 'HH:mm:ss')                   AS EXECUTION_TIME
FROM SALESLINE                       so_line
INNER JOIN CUSTPACKINGSLIPTRANS      packing_line
    ON  packing_line.SALESID        = so_line.SALESID
    AND packing_line.INVENTTRANSID  = so_line.INVENTTRANSID
INNER JOIN CUSTPACKINGSLIPJOUR       packing_slip
    ON  packing_slip.PACKINGSLIPID  = packing_line.PACKINGSLIPID
-- INVENTDIM and CUSTTABLE add no columns: they only keep lines that have both
INNER JOIN INVENTDIM                 inventory_dim
    ON  inventory_dim.INVENTDIMID   = so_line.INVENTDIMID
INNER JOIN CUSTTABLE                 customer
    ON  customer.ACCOUNTNUM         = so_line.CUSTACCOUNT
INNER JOIN SALESLINEV3               so_line_v3
    ON  so_line_v3.INVENTORYLOTID   = so_line.INVENTTRANSID
INNER JOIN INVENTTABLE               item
    ON  item.ITEMID                 = so_line.ITEMID
INNER JOIN WHSLOADLINE               load_line
    ON  load_line.INVENTTRANSID        = so_line.INVENTTRANSID
    AND load_line.SHIPMENTID           = packing_slip.CTSSHIPMENTID
INNER JOIN SALESTABLE                so_header
    ON  so_header.SALESID           = so_line.SALESID
-- Was FULL JOIN: the INNER JOINs on so_line already made it a LEFT JOIN
LEFT JOIN WHSBILLOFLADING            bill_of_lading
    ON  bill_of_lading.BILLOFLADINGID = packing_slip.BILLOFLADINGID
LEFT JOIN LOGISTICSPOSTALADDRESS     delivery_address
    ON  delivery_address.RECID      = so_header.DELIVERYPOSTALADDRESS
WHERE CAST(packing_line.CREATEDATETIME AS DATE) BETWEEN '2026-01-01' AND CAST(GETDATE() AS DATE);
