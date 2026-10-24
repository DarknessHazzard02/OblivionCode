SELECT
    -- Made by: Hazzard
    -- Open, approved PO shipments for orgs C71, C74 and C75, one row per distribution
    po_header.segment1                         AS PO_NUM,
    po_header.authorization_status             AS AUTHORIZATION_STATUS,
    vendor.segment1                            AS VENDOR_NUM,
    vendor.vendor_name                         AS VENDOR_NAME,
    vendor_site.vendor_site_code               AS VENDOR_SITE_CODE,
    ship_to_org.organization_code              AS ORGANIZATION_CODE,
    ship_to_org.organization_name              AS ORG,
    po_shipment.ship_to_location_id            AS SHIP_TO_LOCATION_ID,
    ship_to_location.location_code             AS LOCATION_CODE,
    NVL2(po_line.item_id, item_master.description, po_line.item_description)
                                               AS DESCRIPTION,
    po_line.line_num                           AS LINE_NUM,
    item_master.segment1                       AS ITEM_NUM,
    po_distribution.quantity_ordered           AS QUANTITY,
    po_distribution.quantity_delivered         AS QUANTITY_RECEIVED,
    po_distribution.quantity_cancelled         AS QUANTITY_CANCELLED,
    po_distribution.quantity_ordered
        - NVL(po_distribution.quantity_cancelled, 0)
        - NVL(po_distribution.quantity_delivered, 0)
                                               AS QUANTITY_BALANCE,
    po_line.unit_meas_lookup_code              AS UNIT_MEAS_LOOKUP_CODE,
    CASE
        WHEN po_header.creation_date BETWEEN DATE '1970-01-01' AND DATE '2100-01-01'
        THEN po_header.creation_date
    END                                        AS CREATION_DATE,
    CASE
        WHEN po_shipment.need_by_date BETWEEN DATE '1970-01-01' AND DATE '2100-01-01'
        THEN po_shipment.need_by_date
    END                                        AS NEED_BY_DATE
FROM apps.po_headers_all                    po_header
INNER JOIN apps.po_lines_all                po_line
    ON  po_line.po_header_id            = po_header.po_header_id
INNER JOIN apps.po_line_locations_all       po_shipment
    ON  po_shipment.po_line_id          = po_line.po_line_id
    AND po_shipment.po_header_id        = po_line.po_header_id
INNER JOIN apps.po_distributions_all        po_distribution
    ON  po_distribution.po_line_id      = po_line.po_line_id
    AND po_distribution.line_location_id = po_shipment.line_location_id
INNER JOIN apps.org_organization_definitions ship_to_org
    ON  ship_to_org.organization_id     = po_shipment.ship_to_organization_id
INNER JOIN apps.po_vendor_sites_all         vendor_site
    ON  vendor_site.vendor_site_id      = po_header.vendor_site_id
    AND vendor_site.org_id              = po_header.org_id
INNER JOIN apps.po_vendors                  vendor
    ON  vendor.vendor_id                = po_header.vendor_id
LEFT JOIN apps.mtl_system_items             item_master
    ON  item_master.inventory_item_id   = po_line.item_id
    AND item_master.organization_id     = po_shipment.ship_to_organization_id
LEFT JOIN apps.hr_locations                 ship_to_location
    ON  ship_to_location.location_id    = po_shipment.ship_to_location_id
WHERE po_header.authorization_status = 'APPROVED'
  AND po_shipment.closed_code = 'OPEN'
  AND NVL(po_shipment.cancel_flag, 'N') <> 'Y'
  AND ship_to_org.organization_code IN ('C71', 'C74', 'C75')
