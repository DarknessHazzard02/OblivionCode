-- Made by: Hazzard
-- D365 warehouse locations of all sites (Riverton C79) with aisle, rack, level and zone
SELECT
    'D365'                          AS DATA_BASE,
    'C79'                           AS ORG_CODE,
    'RIVERTON'                     AS ORG_NAME,
    'HVAC'                          AS DIVISION,
    FORMAT(GETDATE(), 'MM-dd-yyyy') AS EXECUTION_DATE,
    FORMAT(GETDATE(), 'HH:mm:ss')   AS EXECUTION_TIME,
    wms_location.WMSLOCATIONID      AS [Location],
    wms_location.AISLEID            AS [Aisle],
    wms_location.RACK               AS [Rack],
    wms_location.LEVEL_             AS [Level],
    wms_location.POSITION           AS [Position],
    wms_location.INVENTLOCATIONID   AS [Site],
    wms_location.ADDITIONALZONE1    AS [Zone],
    wms_location.SORTCODE           AS [Sort Code]
FROM SIWMSLocationStaging wms_location;
