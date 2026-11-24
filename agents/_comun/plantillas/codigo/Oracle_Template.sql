WITH
-- Made by: Hazzard
-- Open purchase order lines by need-by date (sin comentario antes de WITH y sin ; final)
po_line AS (
    SELECT pha.segment1           AS po_num,
           pla.line_num           AS line_num,
           msi.segment1           AS item_num,
           plla.quantity - NVL(plla.quantity_received, 0) AS open_qty,
           plla.need_by_date      AS need_by_date
    FROM   po_headers_all        pha
    JOIN   po_lines_all          pla  ON pla.po_header_id = pha.po_header_id
    JOIN   po_line_locations_all plla ON plla.po_line_id = pla.po_line_id
    JOIN   mtl_system_items_b    msi  ON msi.inventory_item_id = pla.item_id
                                     AND msi.organization_id = plla.ship_to_organization_id
    WHERE  NVL(plla.closed_code, 'OPEN') = 'OPEN'
)
SELECT po_num,
       line_num,
       item_num,
       open_qty,
       need_by_date
FROM   po_line
WHERE  open_qty > 0
ORDER  BY need_by_date
