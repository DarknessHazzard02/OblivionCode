-- Made by: Hazzard
-- D365 released item master with dimensions, weight, cost and product line
SELECT
    item.DEFINITIONGROUP                                  AS DATA_BASE,
    item.ITEMID                                           AS ITEM_NUMBER,
    item.DESCRIPTION,
    item.NAMEALIAS,
    item.PRODUCTGROUPID,
    item.VALUEABCCODE                                     AS ABC,
    item.GROSSDEPTH,
    item.GROSSPRODUCTHEIGHT,
    item.GROSSPRODUCTWIDTH,
    item.PRODUCTVOLUME,
    item.NETPRODUCTWEIGHT,
    item.PRODUCTCOVERAGEGROUPID,
    item.UNITCOST,
    item.UNITCOSTDATE,
    item.UNITCOSTQUANTITY,
    item.INVENTORYUNITSYMBOL,
    item.WILLTOTALSALESDISCOUNTCALCULATIONINCLUDEPRODUCT,
    item.FIRSTPRODUCTFILTERCODE,
    item.CTSPRODUCTLINE,
    item.MCALEGACYSTATUS,
    item.CREATEDDATETIME                                  AS CREATION_DATE,
    item.MODIFIEDDATETIME                                 AS LAST_UPDATE_DATE
FROM InventTable item;
