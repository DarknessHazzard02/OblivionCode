-- Made by: Hazzard
-- D365 shipped sales order lines (packing slips) with customer, BOL, trailer, carrier, amounts and on-time flags
SELECT
    'D365'                                      AS DATA_BASE,
    'C79'                                       AS ORG_CODE,
    'RIVERTON'                                 AS ORG_NAME,
    'HVAC'                                      AS DIVISION,
    FORMAT(GETDATE(), 'MM-dd-yyyy')             AS EXECUTION_DATE,
    FORMAT(GETDATE(), 'HH:mm:ss')               AS EXECUTION_TIME,
    inventory_dim.INVENTSITEID                  AS [Warehouse],
    customer.CUSTOMERGROUPID                    AS [Division2],
    so_line_v3.DELIVERYADDRESSNAME              AS [Customer Name],
    so_line.CUSTACCOUNT                         AS [Customer Number],
    so_line.SALESID                             AS [Sales Order],
    so_line.LINENUM                             AS [Line Number],
    so_header.PURCHORDERFORMNUM                 AS [Purchase Order],
    packing_slip.BILLOFLADINGID                 AS [Bill of Lading ID],
    packing_slip.CTSSHIPMENTID                  AS [Shipment ID],
    so_line.ITEMID                              AS [Item Number],
    item.DESCRIPTION                            AS [Item Description],
    packing_line.QTY                            AS [Shipped Qty],
    bill_of_lading.TRAILERNUMBER                AS [Trailer ID],
    so_line.SALESPRICE * packing_line.QTY       AS [Sales Price],
    packing_line.VALUEMST                       AS [Sales Amount with Discount],
    so_line_v3.DELIVERYADDRESSSTATEID           AS [Shipping State],
    bill_of_lading.CARRIERNAME                  AS [Carrier Name],
    so_line.MCACUSTSHIPDATEREQUESTED            AS [Requested Ship Date],
    so_line.SHIPPINGDATEREQUESTED               AS [Scheduled Shipping Date],
    load_line.CREATEDATETIME                    AS [Released Date],
    packing_line.DELIVERYDATE                   AS [Confirmed Date],
    packing_line.CREATEDATETIME                 AS [Actual Ship Date],
    CASE WHEN so_line.MCACUSTSHIPDATEREQUESTED > packing_line.CREATEDATETIME THEN 'YES' ELSE 'NO' END
                                                AS [Meet Req. Ship Date],
    CASE WHEN so_line.SHIPPINGDATEREQUESTED > packing_line.CREATEDATETIME THEN 'YES' ELSE 'NO' END
                                                AS [Meet Sched. Ship Date],
    so_header.DLVREASON                         AS [Delivery Reason]
FROM SALESLINE                      so_line
INNER JOIN CUSTPACKINGSLIPTRANS     packing_line
    ON  packing_line.SALESID        = so_line.SALESID
    AND packing_line.INVENTTRANSID  = so_line.INVENTTRANSID
INNER JOIN CUSTPACKINGSLIPJOUR      packing_slip
    ON  packing_slip.PACKINGSLIPID  = packing_line.PACKINGSLIPID
INNER JOIN INVENTDIM                inventory_dim
    ON  inventory_dim.INVENTDIMID   = so_line.INVENTDIMID
INNER JOIN CUSTTABLE                customer
    ON  customer.CUSTOMERACCOUNT    = so_line.CUSTACCOUNT
INNER JOIN SalesOrderLineV3Staging  so_line_v3
    ON  so_line_v3.INVENTORYLOTID   = so_line.INVENTTRANSID
INNER JOIN INVENTTABLE              item
    ON  item.ITEMID                 = so_line_v3.ITEMNUMBER
INNER JOIN WHSLOADLINE              load_line
    ON  load_line.INVENTTRANSID     = so_line.INVENTTRANSID
    AND load_line.SHIPMENTID        = packing_slip.CTSSHIPMENTID
INNER JOIN SALESTABLE               so_header
    ON  so_header.SALESID           = so_line.SALESID
-- Was FULL JOIN: the INNER JOINs on so_line already made it a LEFT JOIN
LEFT JOIN WHSBILLOFLADING           bill_of_lading
    ON  bill_of_lading.BILLOFLADINGID = packing_slip.BILLOFLADINGID;
