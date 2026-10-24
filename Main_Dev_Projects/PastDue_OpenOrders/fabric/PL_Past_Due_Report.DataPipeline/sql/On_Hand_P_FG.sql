SELECT
    -- Made by: Hazzard
    -- Source: HOLDS-Book1 / On-Hand P FG. Item type P on hand in FG subinventories of C orgs (except C71, C77, CZ9)
    onhand_balance.organization_code,
    onhand_balance.xxct_item_number,
    CAST(SUM(onhand_balance.onhand_quantity) AS NUMBER(28,10)) AS Onhand,
    SYSDATE                                                    AS EXTRACT_DATE,
    onhand_balance.subinventory_name,
    org_item.item_type,
    org_item.inventory_item_status_code
FROM apps.inv_bv_onhand_balances          onhand_balance
INNER JOIN apps.inv_bv_organization_items org_item
    ON  org_item.inventory_item_id = onhand_balance.inventory_item_id
    AND org_item.organization_id   = onhand_balance.organization_id
WHERE onhand_balance.organization_code LIKE 'C%'
  AND onhand_balance.organization_code NOT IN ('C77', 'CZ9', 'C71')
  AND org_item.organization_code LIKE 'C%'
  AND org_item.organization_code NOT IN ('C77', 'CZ9', 'C71')
  AND onhand_balance.subinventory_name LIKE 'FG%'
  AND onhand_balance.subinventory_name NOT IN ('RWK', 'RMA', 'RGA')
  AND org_item.item_type = 'P'
  AND org_item.inventory_item_status_code <> 'Obsolete'
GROUP BY
    org_item.item_type,
    onhand_balance.organization_code,
    onhand_balance.subinventory_name,
    onhand_balance.xxct_item_number,
    org_item.inventory_item_status_code
