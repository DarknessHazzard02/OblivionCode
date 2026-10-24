-- Made by: Hazzard
-- Test: D365 sales invoice lines May-June 2026 in the Oracle AR invoicing layout (77 columns, unused ones as NULL)
SELECT
    'D365'                                              AS DATA_BASE,
    invoice_line.INVOICEID                              AS INVOICE_NUMBER,
    so_line.LINENUM                                     AS LINE_NUMBER,
    NULL                                                AS ORG_NAME,
    NULL                                                AS DIVISION,
    so_line.LINEAMOUNT                                  AS ACCTD_AMOUNT,
    ABS(SUM(inventory_trans.QTY))                       AS QUANTITY,
    NULL                                                AS LINE_TYPE,
    so_line.SALESPRICE                                  AS UNIT_SELLING_PRICE,
    so_line.LINEAMOUNT                                  AS EXTENDED_AMOUNT,
    so_line.SALESID                                     AS ORDER_NUMBER,
    so_line.SALESTYPE                                   AS ORDER_TYPE,
    so_line.LINENUM                                     AS ORDER_LINE_NUMBER,
    so_line.MCAITEMALTID                                AS ORDERED_ITEM,
    NULL                                                AS TRX_TYPE_NAME,
    invoice_line.INVOICEDATE                            AS GL_DATE,
    invoice_line.INVOICEDATE                            AS TRX_DATE,
    NULL                                                AS GL_ACCOUNT,
    YEAR(invoice_line.INVOICEDATE)                      AS GL_YEAR,
    MONTH(invoice_line.INVOICEDATE)                     AS GL_MONTH,
    so_header.PURCHORDERFORMNUM                         AS CUST_PO_NUMBER,
    invoice_line.INVOICEDATE                            AS INVOICE_DATE,
    NULL AS SEGMENT1, NULL AS SEGMENT2, NULL AS SEGMENT3, NULL AS SEGMENT4,
    NULL AS SEGMENT5, NULL AS SEGMENT6, NULL AS SEGMENT7,
    NULL                                                AS PERIOD_NAME,
    DATEPART(QUARTER, invoice_line.INVOICEDATE)         AS FISCAL_QTR,
    MONTH(invoice_line.INVOICEDATE)                     AS FISCAL_MON,
    UPPER(LEFT(DATENAME(MONTH, invoice_line.INVOICEDATE), 3))
                                                        AS CAL_MONTH,
    NULL                                                AS EFFECTIVE_PERIOD_NUM,
    so_header.SALESNAME                                 AS CUSTOMER_NAME,
    NULL                                                AS INVENTORY_ITEM_ID,
    bill_of_lading.SHIPMENTID                           AS DELIVERY_NUMBER,
    so_line.CUSTACCOUNT                                 AS CUSTOMER_NUMBER,
    so_line.ITEMID                                      AS ITEM_NUMBER,
    NULL                                                AS ITEM_ID,
    NULL                                                AS ITEM_DESCRIPTION,
    invoice_line.INVENTTRANSID                          AS LINE_ID,
    NULL                                                AS CODE_COMBINATION_ID,
    inventory_dim.INVENTSITEID                          AS ORGANIZATION_CODE,
    NULL                                                AS ORGANIZATION_ID,
    NULL                                                AS CUSTOMER_TRX_ID,
    NULL                                                AS INTERFACE_HEADER_ATTRIBUTE6,
    invoice_line.INVENTTRANSID                          AS INTERFACE_LINE_ATTRIBUTE6,
    NULL                                                AS SITE_USE_ID,
    NULL                                                AS KEY_CUST,
    NULL                                                AS NEW_CUST,
    NULL                                                AS BATCH_SOURCE_ID,
    inventory_dim.INVENTSITEID                          AS PARTY_SITE_NUMBER,
    inventory_dim.INVENTSITEID                          AS SITE_NUMBER,
    NULL AS MARKET_MANAGER_DESCRIPTION, NULL AS MARKET_MANAGER,
    NULL AS SUB_MARKET_DESCRIPTION,     NULL AS SUB_MARKET,
    NULL AS MARKET_CLASS_DESCRIPTION,   NULL AS MARKET_CHANNEL,
    NULL AS MARKET_CHANNEL_DESCRIPTION, NULL AS MARKET_DIVISION,
    NULL AS MARKET_CLASS,               NULL AS HEADER_ID,
    NULL                                                AS FREIGHT_CARRIER_CODE,
    delivery_mode.TXT                                   AS SHIPPING_METHOD_CODE,
    packing_slip.BILLOFLADINGID                         AS WAYBILL_AIRBILL,
    NULL                                                AS INTERMEDIATE,
    CASE WHEN so_line.SALESTYPE = 3 THEN 'Sales Orders'
         ELSE CAST(so_line.SALESTYPE AS VARCHAR(50))
    END                                                 AS DELIVERY_TYPE,
    so_line.CREATEDDATETIME                             AS CREATION_DATE,
    NULL                                                AS HEADER_CREATION_DATE,
    NULL                                                AS SHIP_TO_ORG_ID,
    so_line.MCACUSTSHIPDATEREQUESTED                    AS REQUEST_DATE,
    so_line.SHIPPINGDATEREQUESTED                       AS SCHEDULE_SHIP_DATE,
    packing_slip.DELIVERYDATE                           AS ACTUAL_DEPARTURE_DATE,
    CONVERT(VARCHAR(10), GETDATE(), 23)                 AS EXECUTION_DATE,
    CONVERT(VARCHAR(8), GETDATE(), 108)                 AS EXECUTION_TIME
FROM CUSTINVOICETRANS               invoice_line
INNER JOIN SALESLINE                so_line
    ON  so_line.INVENTTRANSID           = invoice_line.INVENTTRANSID
INNER JOIN SALESTABLE               so_header
    ON  so_header.SALESID               = so_line.SALESID
INNER JOIN CUSTTABLE                customer
    ON  customer.ACCOUNTNUM             = so_line.CUSTACCOUNT
INNER JOIN INVENTDIM                inventory_dim
    ON  inventory_dim.INVENTDIMID       = so_line.INVENTDIMID
INNER JOIN SMMSALESDISTRICTSTAGING  sales_district
    ON  sales_district.DISTRICTID       = customer.SALESDISTRICTID
INNER JOIN DLVMODE                  delivery_mode
    ON  delivery_mode.CODE              = so_line.DLVMODE
INNER JOIN INVENTTRANSORIGIN        trans_origin
    ON  trans_origin.INVENTTRANSID      = invoice_line.INVENTTRANSID
INNER JOIN INVENTTRANS              inventory_trans
    ON  inventory_trans.INVOICEID       = invoice_line.INVOICEID
    AND inventory_trans.INVENTTRANSORIGIN = trans_origin.RECORDID
INNER JOIN CUSTPACKINGSLIPJOUR      packing_slip
    ON  packing_slip.PACKINGSLIPID      = inventory_trans.PACKINGSLIPID
INNER JOIN WHSBILLOFLADING          bill_of_lading
    ON  bill_of_lading.BILLOFLADINGID   = packing_slip.BILLOFLADINGID
WHERE trans_origin.REFERENCECATEGORY = 0            -- 0 = Sales
  AND invoice_line.INVOICEDATE >= '2026-05-01'
  AND invoice_line.INVOICEDATE <  '2026-07-01'
GROUP BY
    invoice_line.INVOICEID,
    so_line.LINENUM,
    so_line.LINEAMOUNT,
    so_line.SALESPRICE,
    so_line.SALESID,
    so_line.SALESTYPE,
    so_line.MCAITEMALTID,
    invoice_line.INVOICEDATE,
    so_header.PURCHORDERFORMNUM,
    so_header.SALESNAME,
    bill_of_lading.SHIPMENTID,
    so_line.CUSTACCOUNT,
    so_line.ITEMID,
    invoice_line.INVENTTRANSID,
    inventory_dim.INVENTSITEID,
    delivery_mode.TXT,
    packing_slip.BILLOFLADINGID,
    so_line.CREATEDDATETIME,
    so_line.MCACUSTSHIPDATEREQUESTED,
    so_line.SHIPPINGDATEREQUESTED,
    packing_slip.DELIVERYDATE;
