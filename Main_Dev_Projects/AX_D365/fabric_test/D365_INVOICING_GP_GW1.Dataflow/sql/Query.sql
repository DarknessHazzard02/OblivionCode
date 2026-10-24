-- Made by: Hazzard
-- D365 gross-profit invoicing report: item invoice lines + free-text invoices (account 40100100) + charges per invoice
DECLARE @StartDate DATE = '2015-04-01';
DECLARE @EndDate   DATE = '2026-01-28';   -- Fixed end date: invoices after it are not loaded

WITH
-- Revenue posted to account 40100100, per ledger voucher
ledger_revenue AS (
    SELECT
        gl_entry.SUBLEDGERVOUCHER                          AS ledger_voucher,
        SUM(ABS(gl_entry.ACCOUNTINGCURRENCYAMOUNT))        AS sum_abs_amount,
        ABS(SUM(gl_entry.ACCOUNTINGCURRENCYAMOUNT))        AS abs_sum_amount
    FROM GeneralJournalAccountEntryStaging gl_entry
    INNER JOIN MainAccountStaging          main_account
        ON  main_account.MAINACCOUNTRECID = gl_entry.MAINACCOUNT
    WHERE main_account.MAINACCOUNTID = '40100100'
    GROUP BY gl_entry.SUBLEDGERVOUCHER
),
-- Item line amount per invoice
invoice_line_total AS (
    SELECT
        invoice_line.INVOICEID                             AS invoice_id,
        SUM(ABS(invoice_line.LineAmount))                  AS sum_abs_amount,
        ABS(SUM(invoice_line.LineAmount))                  AS abs_sum_amount
    FROM SICustInvoiceTransStaging invoice_line
    GROUP BY invoice_line.INVOICEID
)

/* ==========================================================
   1. Item invoice lines
   ========================================================== */
SELECT
    ''                                                     AS [Division],
    so_header.INVENTLOCATIONID                             AS [ORGANISATION],
    ''                                                     AS [Group],
    customer.SALESSUBSEGMENTID                             AS [REPORTING MASTER CLASS],
    ''                                                     AS [Market Close Code],
    customer.SALESSEGMENTID                                AS [MARKET CLASS],
    ''                                                     AS [Market Channel Code],
    customer.SALESSUBSEGMENTID                             AS [MARKET CHANNEL],
    0                                                      AS [SUB MARKET CODE],
    0                                                      AS [SUB MARKET],
    customer.CTSMARKETMANAGER                              AS [MARKET MANAGER CODE],
    (SELECT district.DISTRICTDESCRIPTION FROM smmSalesDistrictStaging district
     WHERE district.DISTRICTID = customer.CTSMARKETMANAGER) AS [Market Manager],
    (SELECT district.DISTRICTDESCRIPTION FROM smmSalesDistrictStaging district
     WHERE district.DISTRICTID = customer.SALESDISTRICTID)  AS [SALES PERSON],
    so_header.CUSTACCOUNT                                  AS [CUSTOMER NUMBER],
    customer.NAMEALIAS                                     AS [CUSTOMER NAME],
    (SELECT TOP 1 CAST(address.CITY AS VARCHAR(100)) FROM SILogisticsPostalAddressStaging address
     WHERE address.RECORDID = so_header.DELIVERYPOSTALADDRESS)
    + ', ' +
    (SELECT TOP 1 CAST(address.STATE AS VARCHAR(100)) FROM SILogisticsPostalAddressStaging address
     WHERE address.RECORDID = so_header.DELIVERYPOSTALADDRESS) AS [LOCATION],
    so_header.SALESID                                      AS [ORDER NUMBER],
    so_line.LINENUM                                        AS [ORDER LINE NUMBER],
    ''                                                     AS [Order Transaction Type],
    so_header.SALESTYPE                                    AS [ORDER LINE TYPE],
    invoice_header.INVOICEDATE                             AS [INVOICE DATE],
    invoice_header.INVOICEID                               AS [INVOICE NUMBER],
    invoice_line.LINENUM                                   AS [INVOICE LINE NUMBER],
    so_header.SALESTYPE                                    AS [Trx Type Name],
    ''                                                     AS [Trx Line Type],
    ''                                                     AS [Prod Type],
    (SELECT product.CTSPRODUCTLINE FROM EcoResReleasedProductV2Staging product
     WHERE product.ITEMID = invoice_line.ITEMID)           AS [Product Line],
    ''                                                     AS [Product Line2],
    ''                                                     AS [Mod Product Line],
    ''                                                     AS [Mod Product Line2],
    so_line.MCAITEMALTID                                   AS [Ordered Item],
    so_line.ITEMID                                         AS [ITEM NUMBER],
    (SELECT product.DESCRIPTION FROM EcoResReleasedProductV2Staging product
     WHERE product.ITEMID = invoice_line.ITEMID)           AS [Item Description],
    CAST(invoice_line.QTY AS DECIMAL(18, 2))               AS [Qty],
    CAST(so_line.SALESPRICE AS DECIMAL(18, 2))             AS [Unit Selling Price],
    CAST(invoice_line.LINEAMOUNT AS DECIMAL(18, 2))
      + CAST(invoice_line.LINEAMOUNTTAX AS DECIMAL(18, 2)) AS [Sales],
    posted_cost.amount / invoice_line.QTY                  AS [Costs (ea)],
    posted_cost.amount                                     AS [Costs],
    ''                                                     AS [Preferred Plantof Manufacture],
    ''                                                     AS [Discount Symbol],
    ''                                                     AS [Catalog Number],
    0 AS [FCQty],    0 AS [FCSales],    0 AS [FCCost],    0 AS [FCMargin],
    0 AS [Open Qty], 0 AS [Open Sales], 0 AS [Open Cost],
    0 AS [PDQty],    0 AS [PDSales],    0 AS [PDCost],
    0 AS [Credit Ck], 0 AS [Sales Ck],  0 AS [GPChk],
    CAST(invoice_line.LINEAMOUNT AS DECIMAL(18, 2))
      + CAST(invoice_line.LINEAMOUNTTAX AS DECIMAL(18, 2)) AS [Subtotal],
    -- Header discount, charges and tax are carried on invoice line 1 only
    CASE WHEN invoice_line.LINENUM = 1
         THEN invoice_header.SUMLINEDISC + invoice_header.ENDDISC
         ELSE invoice_header.SUMLINEDISC
    END                                                    AS [Discount],
    CASE WHEN invoice_line.LINENUM = 1
         THEN CAST(invoice_header.SumMarkup AS DECIMAL(18, 2))
         ELSE 0.00
    END                                                    AS [Charges],
    CAST(CASE WHEN invoice_line.LINENUM = 1 THEN invoice_header.SUMTAX ELSE 0 END AS DECIMAL(18, 2))
                                                           AS [Tax Amount],
    CAST(invoice_line.LINEAMOUNTMST AS DECIMAL(18, 2))     AS [Sales Ledger Amt],
    CAST(invoice_line.LINEAMOUNT AS DECIMAL(18, 2))
      + CAST(invoice_line.LINEAMOUNTTAX AS DECIMAL(18, 2))
      - CAST(invoice_line.LINEAMOUNTMST AS DECIMAL(18, 2)) AS [Difference between Sales Amt & Sales Ledger Amt],
    so_header.PURCHORDERFORMNUM                            AS [Customer PO number],
    (SELECT TOP 1 chain.CHAINID FROM smmBusRelChainGroup chain
     WHERE chain.CHAINID = customer.CHAINID)               AS [Chain],
    (SELECT TOP 1 chain.DESCRIPTION FROM smmBusRelChainGroup chain
     WHERE chain.CHAINID = customer.CHAINID)               AS [Chain Description]
FROM SICustInvoiceTransStaging      invoice_line
INNER JOIN SICustInvoiceJourStaging invoice_header
    ON  invoice_header.INVOICEID    = invoice_line.INVOICEID
INNER JOIN SISalesTableStaging      so_header
    ON  so_header.SALESID           = invoice_header.SALESID
INNER JOIN CustCustomerV3Staging    customer
    ON  customer.ACCOUNTNUM         = so_header.CUSTACCOUNT
INNER JOIN SISalesLineStaging       so_line
    ON  so_line.INVENTTRANSID       = invoice_line.INVENTTRANSID
-- Posted cost of the invoiced inventory transactions (one aggregate row per invoice line)
OUTER APPLY (
    SELECT -(SUM(CAST(inventory_trans.COSTAMOUNTPOSTED AS DECIMAL(18, 2)))) AS amount
    FROM SIInventTransStaging              inventory_trans
    INNER JOIN SIInventTransOriginStaging  trans_origin
        ON  trans_origin.RECORDID = inventory_trans.INVENTTRANSORIGIN
    WHERE inventory_trans.QTY <> 0
      AND inventory_trans.PACKINGSLIPRETURNED = 0
      AND inventory_trans.STATUSRECEIPT <= 1
      AND inventory_trans.STATUSISSUE <= 1
      AND inventory_trans.INVOICEID    = invoice_line.INVOICEID
      AND trans_origin.INVENTTRANSID   = invoice_line.INVENTTRANSID
) posted_cost
WHERE invoice_header.SALESID <> ''
  AND invoice_header.INVOICEDATE BETWEEN @StartDate AND @EndDate

UNION ALL

/* ==========================================================
   2. Free-text invoice lines posted to account 40100100
   ========================================================== */
SELECT
    ''                                                     AS [Division],
    customer.INVENTLOCATION                                AS [ORGANISATION],
    ''                                                     AS [Group],
    customer.SALESSUBSEGMENTID                             AS [REPORTING MASTER CLASS],
    ''                                                     AS [Market Close Code],
    customer.SALESSEGMENTID                                AS [MARKET CLASS],
    ''                                                     AS [Market Channel Code],
    customer.SALESSUBSEGMENTID                             AS [MARKET CHANNEL],
    0                                                      AS [SUB MARKET CODE],
    0                                                      AS [SUB MARKET],
    customer.CTSMARKETMANAGER                              AS [MARKET MANAGER CODE],
    (SELECT district.DISTRICTDESCRIPTION FROM smmSalesDistrictStaging district
     WHERE district.DISTRICTID = customer.CTSMARKETMANAGER) AS [Market Manager],
    (SELECT district.DISTRICTDESCRIPTION FROM smmSalesDistrictStaging district
     WHERE district.DISTRICTID = customer.SALESDISTRICTID)  AS [SALES PERSON],
    customer.ACCOUNTNUM                                    AS [CUSTOMER NUMBER],
    customer.NAMEALIAS                                     AS [CUSTOMER NAME],
    ''                                                     AS [LOCATION],
    ''                                                     AS [ORDER NUMBER],
    free_text_line.LINENUM                                 AS [ORDER LINE NUMBER],
    ''                                                     AS [Order Transaction Type],
    ''                                                     AS [ORDER LINE TYPE],
    free_text_header.INVOICEDATE                           AS [INVOICE DATE],
    free_text_header.INVOICEID                             AS [INVOICE NUMBER],
    0                                                      AS [INVOICE LINE NUMBER],
    ''                                                     AS [Trx Type Name],
    ''                                                     AS [Trx Line Type],
    ''                                                     AS [Prod Type],
    ''                                                     AS [Product Line],
    ''                                                     AS [Product Line2],
    ''                                                     AS [Mod Product Line],
    ''                                                     AS [Mod Product Line2],
    ''                                                     AS [Ordered Item],
    ''                                                     AS [ITEM NUMBER],
    ''                                                     AS [Item Description],
    CAST(free_text_line.QUANTITY AS DECIMAL(18, 2))        AS [Qty],
    CAST(free_text_line.UNITPRICE AS DECIMAL(18, 2))       AS [Unit Selling Price],
    CAST(free_text_line.AMOUNTCUR AS DECIMAL(18, 2))       AS [Sales],
    0.00                                                   AS [Costs (ea)],
    0.00                                                   AS [Costs],
    ''                                                     AS [Preferred Plantof Manufacture],
    ''                                                     AS [Discount Symbol],
    ''                                                     AS [Catalog Number],
    0 AS [FCQty],    0 AS [FCSales],    0 AS [FCCost],    0 AS [FCMargin],
    0 AS [Open Qty], 0 AS [Open Sales], 0 AS [Open Cost],
    0 AS [PDQty],    0 AS [PDSales],    0 AS [PDCost],
    0 AS [Credit Ck], 0 AS [Sales Ck],  0 AS [GPChk],
    0.00                                                   AS [Subtotal],
    0.00                                                   AS [Discount],
    0.00                                                   AS [Charges],
    0.00                                                   AS [Tax Amount],
    CAST(free_text_line.AMOUNTCUR AS DECIMAL(18, 2))       AS [Sales Ledger Amt],
    0.00                                                   AS [Difference between Sales Amt & Sales Ledger Amt],
    ''                                                     AS [Customer PO number],
    ''                                                     AS [Chain],
    ''                                                     AS [Chain Description]
FROM SICustInvoiceLineStaging                         free_text_line
INNER JOIN SICustInvoiceTableStaging                  free_text_header
    ON  free_text_header.RECORDID       = free_text_line.PARENTRECID
INNER JOIN SIDimensionAttributeValueCombinationStaging ledger_dimension
    ON  ledger_dimension.RECORDID       = free_text_line.LEDGERDIMENSION
INNER JOIN MainAccountStaging                         main_account
    ON  main_account.MAINACCOUNTID      = ledger_dimension.DISPLAYVALUE
INNER JOIN CustCustomerV3Staging                      customer
    ON  customer.ACCOUNTNUM             = free_text_header.ORDERACCOUNT
WHERE main_account.MAINACCOUNTID = '40100100'
  AND free_text_header.INVOICEDATE BETWEEN @StartDate AND @EndDate

UNION ALL

/* ==========================================================
   3. Charges: ledger revenue not explained by item lines, one row per invoice
   ========================================================== */
SELECT
    ''                                                     AS [Division],
    invoice_header.INVENTLOCATIONID                        AS [ORGANISATION],
    ''                                                     AS [Group],
    customer.SALESSUBSEGMENTID                             AS [REPORTING MASTER CLASS],
    ''                                                     AS [Market Close Code],
    customer.SALESSEGMENTID                                AS [MARKET CLASS],
    ''                                                     AS [Market Channel Code],
    customer.SALESSUBSEGMENTID                             AS [MARKET CHANNEL],
    0                                                      AS [SUB MARKET CODE],
    0                                                      AS [SUB MARKET],
    customer.CTSMARKETMANAGER                              AS [MARKET MANAGER CODE],
    market_manager.DISTRICTDESCRIPTION                     AS [Market Manager],
    sales_person.DISTRICTDESCRIPTION                       AS [SALES PERSON],
    so_header.CUSTACCOUNT                                  AS [CUSTOMER NUMBER],
    customer.NAMEALIAS                                     AS [CUSTOMER NAME],
    CAST(delivery_address.CITY AS VARCHAR(100)) + ', ' + CAST(delivery_address.STATE AS VARCHAR(100))
                                                           AS [LOCATION],
    so_header.SALESID                                      AS [ORDER NUMBER],
    0                                                      AS [ORDER LINE NUMBER],
    ''                                                     AS [Order Transaction Type],
    so_header.SALESTYPE                                    AS [ORDER LINE TYPE],
    invoice_header.INVOICEDATE                             AS [INVOICE DATE],
    invoice_header.INVOICEID                               AS [INVOICE NUMBER],
    0                                                      AS [INVOICE LINE NUMBER],
    so_header.SALESTYPE                                    AS [Trx Type Name],
    ''                                                     AS [Trx Line Type],
    ''                                                     AS [Prod Type],
    ''                                                     AS [Product Line],
    ''                                                     AS [Product Line2],
    ''                                                     AS [Mod Product Line],
    ''                                                     AS [Mod Product Line2],
    ''                                                     AS [Ordered Item],
    'CHARGES'                                              AS [ITEM NUMBER],
    ''                                                     AS [Item Description],
    NULL                                                   AS [Qty],
    NULL                                                   AS [Unit Selling Price],
    0.00                                                   AS [Sales],
    0.00                                                   AS [Costs (ea)],
    0.00                                                   AS [Costs],
    ''                                                     AS [Preferred Plantof Manufacture],
    ''                                                     AS [Discount Symbol],
    ''                                                     AS [Catalog Number],
    0 AS [FCQty],    0 AS [FCSales],    0 AS [FCCost],    0 AS [FCMargin],
    0 AS [Open Qty], 0 AS [Open Sales], 0 AS [Open Cost],
    0 AS [PDQty],    0 AS [PDSales],    0 AS [PDCost],
    0 AS [Credit Ck], 0 AS [Sales Ck],  0 AS [GPChk],
    0.00                                                   AS [Subtotal],
    0.00                                                   AS [Discount],
    0.00                                                   AS [Charges],
    0.00                                                   AS [Tax Amount],
    -- Sales type 4 (return order) keeps the charge positive, everything else is negative
    CASE WHEN so_header.SalesType = 4
         THEN  ABS(ledger.sum_abs_amount - lines.sum_abs_amount)
         ELSE -ABS(ledger.sum_abs_amount - lines.sum_abs_amount)
    END                                                    AS [Sales Ledger Amt],
    ABS(lines.sum_abs_amount - ledger.sum_abs_amount)      AS [Difference between Sales Amt & Sales Ledger Amt],
    ''                                                     AS [Customer PO number],
    ''                                                     AS [Chain],
    ''                                                     AS [Chain Description]
FROM SICustInvoiceTransStaging           invoice_line
INNER JOIN SICustInvoiceJourStaging      invoice_header
    ON  invoice_header.INVOICEID         = invoice_line.INVOICEID
INNER JOIN SISalesTableStaging           so_header
    ON  so_header.SALESID                = invoice_header.SALESID
INNER JOIN CustCustomerV3Staging         customer
    ON  customer.ACCOUNTNUM              = so_header.CUSTACCOUNT
INNER JOIN SISalesLineStaging            so_line
    ON  so_line.INVENTTRANSID            = invoice_line.INVENTTRANSID
LEFT JOIN smmSalesDistrictStaging        market_manager
    ON  market_manager.DISTRICTID        = customer.CTSMARKETMANAGER
LEFT JOIN smmSalesDistrictStaging        sales_person
    ON  sales_person.DISTRICTID          = customer.SALESDISTRICTID
LEFT JOIN SILogisticsPostalAddressStaging delivery_address
    ON  delivery_address.RECORDID        = so_header.DELIVERYPOSTALADDRESS
LEFT JOIN ledger_revenue                 ledger
    ON  ledger.ledger_voucher            = invoice_header.LEDGERVOUCHER
LEFT JOIN invoice_line_total             lines
    ON  lines.invoice_id                 = invoice_header.INVOICEID
WHERE invoice_header.SALESID <> ''
  AND invoice_header.INVOICEDATE BETWEEN @StartDate AND @EndDate
  AND invoice_line.LINENUM = 1
GROUP BY
    invoice_header.INVENTLOCATIONID,
    customer.SALESSUBSEGMENTID,
    customer.SALESSEGMENTID,
    customer.CTSMARKETMANAGER,
    market_manager.DISTRICTDESCRIPTION,
    sales_person.DISTRICTDESCRIPTION,
    so_header.CUSTACCOUNT,
    customer.NAMEALIAS,
    delivery_address.CITY,
    delivery_address.STATE,
    so_header.SALESID,
    so_header.SALESTYPE,
    invoice_header.INVOICEDATE,
    invoice_header.INVOICEID,
    invoice_header.SALESTYPE,
    invoice_header.LEDGERVOUCHER,
    ledger.sum_abs_amount,
    ledger.abs_sum_amount,
    lines.sum_abs_amount,
    lines.abs_sum_amount
HAVING ledger.abs_sum_amount - lines.abs_sum_amount <> 0;
