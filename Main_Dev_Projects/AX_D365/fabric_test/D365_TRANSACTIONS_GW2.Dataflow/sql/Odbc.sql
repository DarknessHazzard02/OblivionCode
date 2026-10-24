-- Made by: Hazzard
-- D365 inventory transactions with reference category name, status, quantity, cost and dimensions
WITH reference_category (category_id, category_name) AS (
    SELECT category_id, category_name
    FROM (VALUES
        (0, 'Sales'), (1, 'WHSWarehouseOrder'), (2, 'Production'), (3, 'Purch'),
        (4, 'InventTransaction'), (5, 'InventLossProfit'), (6, 'InventTransfer'), (7, 'SummedUp'),
        (8, 'ProdLine'), (9, 'BOMLine'), (10, 'BOMMain'), (11, 'WMSOrder'),
        (12, 'Project'), (13, 'InventCounting'), (14, 'WMSTransport'), (15, 'QuarantineOrder'),
        (16, 'WHSWarehouseReceipt'), (17, 'WHSWarehouseInventoryAdjustment'), (18, 'WHSWarehouseInventoryBlocking'),
        (19, 'WHSOutboundShipmentOrder'), (20, 'Asset'), (21, 'TransferOrderShip'), (22, 'TransferOrderReceive'),
        (23, 'TransferOrderScrap'), (24, 'SalesQuotation'), (25, 'QualityOrder'), (26, 'Blocking'),
        (27, 'KanbanJobProcess'), (28, 'KanbanJobTransferReceipt'), (29, 'KanbanJobTransferIssue'),
        (30, 'KanbanJobPickingList'), (31, 'KanbanJobWIP'), (32, 'KanbanEmptied'),
        (33, 'ConsignmentReplenishmentOrder'), (34, 'InventOwnershipChange'), (35, 'WHSInboundShipmentOrder'),
        (36, 'WHSEWOutboundShipmentOrderUpdate'), (100, 'PmfProdCoBy'), (101, 'ProdRelease_RU'),
        (102, 'FixedAssets_RU'), (103, 'Assembling_JP'), (110, 'ITMGIT'), (150, 'Statement'),
        (201, 'WHSWork'), (202, 'WHSQuarantine'), (203, 'WHSContainer'), (204, 'WHSOrderCommittedReservation'),
        (205, 'InventTransArchive'), (206, 'WHSInventTransArchiveOnlyAffectsLocationAndBelow'),
        (207, 'WHSWarehouseOrderReservation')
    ) AS category_list (category_id, category_name)
)
SELECT
    'D365'                                  AS DATA_BASE,
    'C79'                                   AS ORG_CODE,
    'RIVERTON'                             AS ORG_NAME,
    'HVAC'                                  AS DIVISION,
    FORMAT(GETDATE(), 'MM-dd-yyyy')         AS EXECUTION_DATE,
    FORMAT(GETDATE(), 'HH:mm:ss')           AS EXECUTION_TIME,
    inventory_trans.ITEMID                  AS [Item Number],
    inventory_trans.DATEPHYSICAL            AS [Physical Date],
    inventory_trans.DATEFINANCIAL           AS [Financial Date],
    COALESCE(category.category_name, CAST(trans_origin.REFERENCECATEGORY AS VARCHAR(20)))
                                            AS [Category],
    trans_origin.REFERENCEID                AS [Number],
    inventory_trans.STATUSRECEIPT           AS [Receipt],
    inventory_trans.STATUSISSUE             AS [Issue],
    inventory_trans.QTY                     AS [Quantity],
    inventory_trans.COSTAMOUNTPHYSICAL      AS [Cost Amount],
    inventory_dim.INVENTSITEID              AS [Site],
    inventory_dim.INVENTLOCATIONID          AS [Warehouse],
    inventory_dim.INVENTBATCHID             AS [Batch Number],
    inventory_dim.WMSLOCATIONID             AS [Location],
    inventory_dim.INVENTSTATUSID            AS [Inventory Status],
    inventory_dim.LICENSEPLATEID            AS [License Plate]
FROM SIInventTransStaging               inventory_trans
INNER JOIN SIInventTransOriginStaging   trans_origin
    ON  trans_origin.RECORDID       = inventory_trans.INVENTTRANSORIGIN
INNER JOIN InventDim                    inventory_dim
    ON  inventory_dim.INVENTDIMID   = inventory_trans.INVENTDIMID
LEFT JOIN reference_category            category
    ON  category.category_id        = trans_origin.REFERENCECATEGORY;
