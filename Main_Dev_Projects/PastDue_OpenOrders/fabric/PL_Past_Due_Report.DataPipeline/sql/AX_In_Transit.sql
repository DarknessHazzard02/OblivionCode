SELECT
    -- Made by: Hazzard
    -- Source: HOLDS-Book1 / AX In Transit. On-hand FG and P-FG in transit org CZ9, by subinventory
    onhand_balance.organization_code,
    onhand_balance.xxct_item_number,
    CAST(SUM(onhand_balance.onhand_quantity) AS NUMBER(28,10)) AS Onhand,
    SYSDATE                                                    AS EXTRACT_DATE,
    org_item.item_type,
    onhand_balance.subinventory_name,
    org_item.inventory_item_status_code
FROM apps.inv_bv_onhand_balances          onhand_balance
INNER JOIN apps.inv_bv_organization_items org_item
    ON  org_item.inventory_item_id = onhand_balance.inventory_item_id
    AND org_item.organization_id   = onhand_balance.organization_id
WHERE onhand_balance.organization_code = 'CZ9'
  AND org_item.organization_code = 'CZ9'
  AND org_item.item_type IN ('FG', 'P-FG')
  AND org_item.inventory_item_status_code <> 'Obsolete'
  AND onhand_balance.subinventory_name NOT IN ('RWK', 'RGA', 'RMA')
GROUP BY
    org_item.item_type,
    onhand_balance.organization_code,
    onhand_balance.subinventory_name,
    onhand_balance.xxct_item_number,
    org_item.inventory_item_status_code
