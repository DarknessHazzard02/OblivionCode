-- Made by: Hazzard
-- Active locations of warehouses RVT-MS and RVT-RET (Riverton C79) with no positive on-hand stock
SELECT
    'D365'                          AS DATA_BASE,
    'C79'                           AS ORG_CODE,
    'RIVERTON'                     AS ORG_NAME,
    'HVAC'                          AS DIVISION,
    FORMAT(GETDATE(), 'MM-dd-yyyy') AS EXECUTION_DATE,
    FORMAT(GETDATE(), 'HH:mm:ss')   AS EXECUTION_TIME,
    wms_location.INVENTLOCATIONID   AS [Warehouse],
    wms_location.WMSLOCATIONID      AS [Location]
FROM SIWMSLOCATIONSTAGING wms_location
INNER JOIN INVENTLOCATION warehouse
    ON  warehouse.WAREHOUSEID = wms_location.INVENTLOCATIONID
WHERE wms_location.OUTPUTBLOCKINGCAUSEID <> 'INACTIVE'
  AND wms_location.INPUTBLOCKINGCAUSEID  <> 'INACTIVE'
  AND UPPER(wms_location.INVENTLOCATIONID) IN ('RVT-MS', 'RVT-RET')
  AND NOT EXISTS (
      SELECT 1
      FROM SIINVENTDIMSTAGING inventory_dim
      INNER JOIN SIINVENTSUMSTAGING inventory_sum
          ON  inventory_sum.INVENTDIMID = inventory_dim.INVENTDIMID
      WHERE inventory_dim.WMSLOCATIONID    = wms_location.WMSLOCATIONID
        AND inventory_dim.INVENTLOCATIONID = wms_location.INVENTLOCATIONID
        AND inventory_sum.PhysicalInvent > 0
  )
