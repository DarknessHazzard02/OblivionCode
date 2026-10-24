SELECT
    -- Made by: Hazzard
    -- Source: IN_TRANSIT / Sheet1. Shipment and receiving supply heading to C and D orgs (except C77, CZ9)
    inventory_supply.to_organization_code,
    TRIM(inventory_supply.xxct_item_number)                     AS xxct_item_number,
    CAST(SUM(inventory_supply.quantity) AS NUMBER(28,10))        AS quantity_sum,
    inventory_supply.expected_delivery_date,
    inventory_supply.supply_type_code
FROM apps.inv_bv_inventory_supplies inventory_supply
WHERE inventory_supply.supply_type_code IN ('SHIPMENT', 'RECEIVING')
  AND TRIM(inventory_supply.xxct_item_number) IS NOT NULL
  AND (inventory_supply.to_organization_code LIKE 'C%'
       OR inventory_supply.to_organization_code LIKE 'D%')
  AND inventory_supply.to_organization_code NOT IN ('C77', 'CZ9')
GROUP BY
    inventory_supply.to_organization_code,
    TRIM(inventory_supply.xxct_item_number),
    inventory_supply.expected_delivery_date,
    inventory_supply.supply_type_code
ORDER BY
    inventory_supply.to_organization_code,
    TRIM(inventory_supply.xxct_item_number),
    inventory_supply.expected_delivery_date,
    inventory_supply.supply_type_code
