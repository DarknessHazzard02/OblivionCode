SELECT DISTINCT
    -- Made by: Hazzard
    -- Source: SO HOLDS-Book1 / Shipment Status. Pick status of open order lines in operating unit 166
    TO_CHAR(so_header_all.order_number) || '|' || TO_CHAR(so_line.line_number) || '.' || TO_CHAR(so_line.shipment_number)
                                                       AS Order_line_shipment,
    TO_CHAR(so_header_all.order_number)                AS order_number,
    TO_CHAR(so_line.line_number) || '.' || TO_CHAR(so_line.shipment_number)
                                                       AS Line_shipment2,
    so_line.schedule_status,
    so_line.status,
    pick_status_lookup.meaning                         AS pick_status,
    so_line.actual_shipment_date
FROM apps.oe_bv_order_lines              so_line
INNER JOIN apps.oe_order_lines_all      so_line_all
    ON  so_line_all.line_id                  = so_line.line_id
INNER JOIN apps.oe_order_headers_all    so_header_all
    ON  so_header_all.header_id              = so_line_all.header_id
    AND so_header_all.org_id                 = so_line_all.org_id
INNER JOIN apps.wsh_delivery_details    delivery_detail
    ON  delivery_detail.source_line_id       = so_line_all.line_id
    AND delivery_detail.source_header_id     = so_header_all.header_id
    AND delivery_detail.org_id               = so_header_all.org_id
    AND delivery_detail.source_code          = 'OE'
INNER JOIN apps.wsh_delivery_assignments delivery_assignment
    ON  delivery_assignment.delivery_detail_id = delivery_detail.delivery_detail_id
INNER JOIN apps.wsh_new_deliveries      delivery
    ON  delivery.delivery_id                 = delivery_assignment.delivery_id
INNER JOIN apps.fnd_lookup_values       pick_status_lookup
    ON  pick_status_lookup.lookup_code       = delivery_detail.released_status
    AND pick_status_lookup.lookup_type       = 'PICK_STATUS'
    AND pick_status_lookup.view_application_id = 665
    AND pick_status_lookup.language          = 'US'
WHERE so_header_all.org_id = 101
  AND so_line_all.line_category_code = 'ORDER'
  AND so_line.status <> 'Closed'
  AND (so_line.actual_shipment_date IS NULL
       OR so_line.actual_shipment_date >= DATE '2018-11-30')
