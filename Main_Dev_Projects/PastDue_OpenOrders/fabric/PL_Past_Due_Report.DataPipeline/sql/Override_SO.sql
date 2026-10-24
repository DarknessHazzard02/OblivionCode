WITH
    -- Made by: Hazzard
    -- Source: Override / Override SO. Open external SO lines with ATP date override, by EMC production line
    item_production_line AS (
        SELECT
            item_category.inventory_item_id,
            item_category.organization_id,
            MAX(category.segment1 || '.' || category.segment2) AS production_line
        FROM apps.mtl_item_categories      item_category
        INNER JOIN apps.mtl_categories     category
            ON  category.category_id         = item_category.category_id
        INNER JOIN apps.mtl_category_sets  category_set
            ON  category_set.category_set_id = item_category.category_set_id
        WHERE category_set.category_set_name = 'EMC Production Line'
        GROUP BY
            item_category.inventory_item_id,
            item_category.organization_id
    ),
    c_org_item AS (
        SELECT
            item_master.inventory_item_id,
            item_master.organization_id,
            item_master.segment1          AS item_name,
            org_parameter.organization_code,
            item_line.production_line
        FROM apps.mtl_system_items        item_master
        INNER JOIN apps.mtl_parameters    org_parameter
            ON  org_parameter.organization_id = item_master.organization_id
        LEFT JOIN item_production_line    item_line
            ON  item_line.inventory_item_id   = item_master.inventory_item_id
            AND item_line.organization_id     = item_master.organization_id
        WHERE org_parameter.organization_code LIKE 'C%'
    )
SELECT
    so_header.order_number                                        AS order_number,
    TO_CHAR(so_line.line_number) || '.' || TO_CHAR(SUM(so_line.shipment_number))
                                                                  AS line_number,
    CAST(SUM(so_line.ordered_quantity) AS NUMBER(28,10))          AS ordered_quantity_sum,
    so_line.status                                                AS status,
    so_header.customer                                            AS customer,
    so_line.override_atp_date_code                                AS override_atp_date_code,
    so_line.request_date                                          AS request_date,
    so_line.schedule_ship_date                                    AS schedule_ship_date,
    org_item.production_line                                      AS production_line,
    org_item.organization_code                                    AS organization_code,
    org_item.item_name                                            AS item_name
FROM apps.oe_bv_order_lines          so_line
INNER JOIN apps.oe_bv_order_headers  so_header
    ON  so_header.header_id         = so_line.header_id
INNER JOIN c_org_item               org_item
    ON  org_item.inventory_item_id  = so_line.ordered_item_id
    AND org_item.organization_id    = so_line.ship_from_org_id
WHERE so_line.override_atp_date_code = 'Y'
  AND NVL(so_header.customer, ' ') NOT LIKE '%Internal%'
  AND NVL(so_header.customer, ' ') NOT LIKE '%CONTOSO DYNAMICS INVENTORY TRANSFER ACCNT%'
  AND NVL(so_line.status, ' ') NOT LIKE '%Closed%'
  AND NVL(so_line.status, ' ') NOT LIKE '%Cancelled%'
GROUP BY
    so_header.customer,
    so_header.order_number,
    so_line.request_date,
    so_line.schedule_ship_date,
    so_line.status,
    so_line.override_atp_date_code,
    org_item.item_name,
    org_item.organization_code,
    org_item.production_line,
    so_line.line_number
