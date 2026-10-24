-- Made by: Hazzard
-- D365 open sales orders (status 1) with total amount including markup, holds, sales taker and document status
WITH document_status (status_id, status_name) AS (
    SELECT status_id, status_name
    FROM (VALUES
        (0, 'None'), (1, 'Quotation'), (2, 'PurchaseOrder'), (3, 'Confirmation'), (4, 'PickingList'),
        (5, 'PackingSlip'), (6, 'ReceiptsList'), (7, 'Invoice'), (8, 'ApproveJournal'), (9, 'ProjectInvoice'),
        (10, 'ProjectPackingSlip'), (11, 'CRMQuotation'), (12, 'Lost'), (13, 'Cancelled'), (14, 'FreeTextInvoice'),
        (15, 'RFQ'), (16, 'RFQAccept'), (17, 'RFQReject'), (18, 'PurchReq'), (19, 'RFQReSend'), (20, 'Note'),
        (21, 'ProjectPickingList'), (22, 'ITMGoodsInTransitReceive'), (23, 'RevRecRevenueCancelation'),
        (24, 'RevRecDeferredRevenueInvoice'), (30, 'ConfirmationRequest'), (101, 'Invoice4Paym_RU'),
        (102, 'Facture_RU'), (103, 'PlSAD'), (105, 'FreeTextInvoice4Paym_RU'), (150, 'DeliverySlip_BR'),
        (219, 'InvoiceRegistration_IN'), (220, 'BillOfEntry_IN'), (221, 'ShippingBill_IN'),
        (222, 'DeliverySlipProject_BR')
    ) AS status_list (status_id, status_name)
)
SELECT
    'D365'                                  AS DATA_BASE,
    'C79'                                   AS ORG_CODE,
    'RIVERTON'                             AS ORG_NAME,
    'HVAC'                                  AS DIVISION,
    FORMAT(GETDATE(), 'MM-dd-yyyy')         AS EXECUTION_DATE,
    FORMAT(GETDATE(), 'HH:mm:ss')           AS EXECUTION_TIME,
    so_header.RECORDID,
    so_line.SALESID                         AS [Sales Order],
    so_header.CUSTACCOUNT                   AS [Customer Account],
    so_header.SALESNAME                     AS [Customer Name],
    so_header.INVOICEACCOUNT                AS [Invoice Account],
    customer.MCACITY                        AS [City],
    customer.MCASTATE                       AS [State/Province],
    -- Markup category: 0 = fixed amount, 1 = per unit, 2 = percent of line amount
    CASE markup.MARKUPCATEGORY
        WHEN 0 THEN SUM(so_line.LINEAMOUNT) + markup.VALUE
        WHEN 1 THEN SUM(so_line.LINEAMOUNT) + markup.VALUE * SUM(so_line.SALESQTY)
        WHEN 2 THEN SUM(so_line.LINEAMOUNT) + ABS(markup.VALUE) * SUM(so_line.LINEAMOUNT) / 100
        ELSE SUM(so_line.LINEAMOUNT)
    END                                     AS [Total Amount],
    so_header.MCAHOLDREASONCODE             AS [Hold Reason Code],
    so_header.SHIPPINGDATEREQUESTED         AS [Expected Shipping Date],
    hold_comment.HOLDCOMMENTS               AS [Hold Comment],
    CASE so_header.RELEASESTATUS
        WHEN 0 THEN 'OPEN'
        WHEN 1 THEN 'PARTIALLY RELEASED'
        WHEN 2 THEN 'RELEASED'
        ELSE CAST(so_header.RELEASESTATUS AS VARCHAR(10))
    END                                     AS [Release Status],
    sales_taker.Name                        AS [Sales Taker],
    COALESCE(document_status.status_name, CAST(so_header.DOCUMENTSTATUS AS VARCHAR(10)))
                                            AS [Document Status]
FROM SISalesTableStaging                          so_header
INNER JOIN SISalesLineStaging                     so_line
    ON  so_line.SALESID             = so_header.SALESID
INNER JOIN CustTable                              customer
    ON  customer.ACCOUNTNUM         = so_header.CUSTACCOUNT
-- The three joins below were FULL OUTER JOIN: the WHERE on so_header already made them LEFT JOIN
LEFT JOIN BusinessDocumentMarkupTransactionStaging markup
    ON  markup.TransRecId           = so_header.RECORDID
LEFT JOIN SIHoldReasonCommentsStaging             hold_comment
    ON  hold_comment.RECORDID       = so_header.SIHOLDCOMMENTS
LEFT JOIN HcmWorkerBaseStaging                    sales_taker
    ON  sales_taker.RECID           = so_header.WORKERSALESTAKER
LEFT JOIN document_status
    ON  document_status.status_id   = so_header.DOCUMENTSTATUS
WHERE so_header.SALESSTATUS = 1
GROUP BY
    so_line.SALESID,
    so_header.CUSTACCOUNT,
    so_header.SALESNAME,
    so_header.INVOICEACCOUNT,
    customer.MCACITY,
    customer.MCASTATE,
    markup.MARKUPCATEGORY,
    markup.VALUE,
    so_header.MCAHOLDREASONCODE,
    so_header.RECORDID,
    so_header.SHIPPINGDATEREQUESTED,
    hold_comment.HOLDCOMMENTS,
    sales_taker.Name,
    so_header.RELEASESTATUS,
    so_header.DOCUMENTSTATUS,
    document_status.status_name;
