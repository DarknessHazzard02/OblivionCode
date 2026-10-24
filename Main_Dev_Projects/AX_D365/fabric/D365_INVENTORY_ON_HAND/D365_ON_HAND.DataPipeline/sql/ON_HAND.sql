-- Made by: Hazzard
-- Current D365 on-hand inventory for Riverton (C79) with site, warehouse, batch, weights and cost
SELECT
    'D365'                                        AS DATA_BASE,
    'C79'                                         AS ORG_CODE,
    'RIVERTON'                                   AS ORG_NAME,
    'HVAC'                                        AS DIVISION,
    CAST(GETDATE() AS date)                       AS EXECUTION_DATE,
    FORMAT(GETDATE(), 'HH:mm:ss')                 AS EXECUTION_TIME,
    'Finished good'                               AS ITEM_TYPE,
    inventory_sum.ITEMID                          AS ITEM_NUMBER,
    item_table.DESCRIPTION                        AS DESCRIPTION,
    item_table.CTSPRODUCTLINE                     AS PRODUCT_LINE,
    released_product.NAMEALIAS                    AS PRODUCT_NUMBER,
    released_product.SEARCHNAME                   AS SEARCH_NAME,
    unit_weight.weight                            AS WEIGHT,
    inventory_dim.INVENTSITEID                    AS SITE,
    inventory_dim.INVENTLOCATIONID                AS WAREHOUSE,
    inventory_dim.INVENTBATCHID                   AS BATCH_NUMBER,
    inventory_dim.WMSLOCATIONID                   AS LOCATION,
    inventory_dim.INVENTSTATUSID                  AS STATUS,
    inventory_dim.LICENSEPLATEID                  AS LPN,
    inventory_sum.PHYSICALINVENT                  AS PHYSICAL_INVENTORY,
    unit_weight.weight * inventory_sum.PHYSICALINVENT
                                                  AS [Total Weight],
    inventory_sum.RESERVPHYSICAL                  AS [Physical Reserved],
    inventory_sum.AVAILPHYSICAL                   AS [Available Physical],
    inventory_sum.ONORDER                         AS [On Order],
    inventory_sum.RESERVORDERED                   AS [Ordered Reserve],
    available.avail_total + inventory_sum.ONORDER AS [Available for Reservation],
    available.avail_total                         AS [Avail Total],
    released_product.SALESUNITSYMBOL              AS INVENTORY_UNIT,
    inventory_sum.CTSInTransit,
    item_cost.price                               AS ITEM_COST,
    item_cost.price * inventory_sum.PostedQty     AS TOTAL_COST
FROM InventSum                                   inventory_sum
INNER JOIN EcoResReleasedProductV2Staging         released_product
    ON  released_product.ITEMID     = inventory_sum.ITEMID
INNER JOIN SIInventDimStaging                     inventory_dim
    ON  inventory_dim.INVENTDIMID   = inventory_sum.INVENTDIMID
LEFT JOIN INVENTTABLE                             item_table
    ON  item_table.ITEMID           = inventory_sum.ITEMID
CROSS APPLY (
    SELECT released_product.NETPRODUCTWEIGHT + released_product.TAREPRODUCTWEIGHT AS weight
) unit_weight
CROSS APPLY (
    SELECT inventory_sum.PHYSICALINVENT - inventory_sum.RESERVPHYSICAL + inventory_sum.ORDERED
         - inventory_sum.ONORDER - inventory_sum.RESERVORDERED AS avail_total
) available
CROSS APPLY (
    -- Scalar subquery on purpose: more than one cost row per item must fail, not duplicate rows
    SELECT (
        SELECT module_cost.Price
        FROM SIInventTableModuleStaging module_cost
        WHERE module_cost.ITEMID     = released_product.ITEMID
          AND module_cost.MODULETYPE = 0
    ) AS price
) item_cost
WHERE inventory_sum.PostedQty > 0;
