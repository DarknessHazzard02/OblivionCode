SELECT
    -- Made by: Hazzard
    -- Source: SO HOLDS-Book1 / Customer Pick Up. Open external SO shipments with customer pickup, by EMC production line
    TO_CHAR(so_header.order_number) || '|' || TO_CHAR(so_line.line_number) || '.' || TO_CHAR(so_line.shipment_number)
                                                               AS Order_line_shipment3,
    org_item.organization_code,
    so_header.order_number,
    TO_CHAR(so_line.line_number) || '.' || TO_CHAR(so_line.shipment_number)
                                                               AS Line_shipment3,
    so_line.schedule_ship_date,
    so_line_view.ordered_item,
    CAST(SUM(so_line.ordered_quantity) AS NUMBER(28,10))       AS ordered_quantity,
    so_line.status,
    so_line.shipping_method,
    so_header.customer,
    so_header.order_type,
    item_category.category_name,
    item_category.category_type_name
FROM apps.oe_order_lines_bv              so_line_view
INNER JOIN apps.oe_bv_order_headers          so_header
    ON  so_header.header_id            = so_line_view.header_id
INNER JOIN apps.oe_bv_order_lines            so_line
    ON  so_line.line_id                = so_line_view.line_id
    AND so_line.header_id              = so_line_view.header_id
    AND so_line.ordered_item_id        = so_line_view.inventory_item_id
    AND so_line.ship_from_org_id       = so_line_view.ship_from_org_id
INNER JOIN apps.inv_bv_organization_items    org_item
    ON  org_item.inventory_item_id     = so_line_view.inventory_item_id
    AND org_item.organization_id       = so_line_view.ship_from_org_id
INNER JOIN apps.inv_bv_item_category_asgns   item_category
    ON  item_category.inventory_item_id = org_item.inventory_item_id
    AND item_category.organization_id   = org_item.organization_id
WHERE item_category.category_type_name = 'EMC Production Line'
  AND org_item.organization_code NOT IN ('K61', 'K63', 'K64', 'TQA', 'TQB', 'TQC')
  AND so_line.shipping_method LIKE '%CUSTOMER PICKUP%'
  AND so_header.customer NOT LIKE '%Internal%'
  AND so_line.status NOT IN ('Closed', 'Cancelled')
GROUP BY
    so_header.order_number,
    so_line.line_number,
    so_line.shipment_number,
    item_category.category_type_name,
    so_header.customer,
    so_header.order_type,
    org_item.organization_code,
    so_line.schedule_ship_date,
    item_category.category_name,
    so_line.status,
    so_line_view.ordered_item,
    so_line.shipping_method
HAVING SUM(so_line.ordered_quantity) > 0
