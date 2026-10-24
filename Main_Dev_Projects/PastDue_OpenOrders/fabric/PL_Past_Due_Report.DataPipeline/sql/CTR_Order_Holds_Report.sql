WITH
-- Made by: Hazzard
-- Source: CTR_Order_Holds_Report. Unreleased holds on open CMS order lines (operating unit 166), one column per hold type
model_price_by_header AS (
    SELECT
        model_lines.header_id,
        SUM(model_lines.unit_selling_price) AS model_unit_selling_price
    FROM ont.oe_order_lines_all model_lines
    WHERE model_lines.item_type_code = 'MODEL'
    GROUP BY model_lines.header_id
),
credit_hold_sources AS (
    SELECT DISTINCT
        credit_sources.hold_source_id,
        credit_definitions.name AS hold_name
    FROM ont.oe_hold_sources_all credit_sources
    INNER JOIN ont.oe_hold_definitions credit_definitions
        ON credit_sources.hold_id = credit_definitions.hold_id
    WHERE INSTR(UPPER(credit_definitions.name), 'CREDIT') > 0
),
demand_class_lookup AS (
    SELECT DISTINCT
        lookup_values.lookup_code,
        lookup_values.meaning
    FROM applsys.fnd_lookup_values# lookup_values
    WHERE lookup_values.lookup_type = 'DEMAND_CLASS'
),
hold_entity_lookup AS (
    SELECT DISTINCT
        lookup_values.lookup_code,
        lookup_values.meaning
    FROM applsys.fnd_lookup_values# lookup_values
    WHERE lookup_values.lookup_type = 'HOLD_ENTITY_DESC'
      AND lookup_values.enabled_flag = 'Y'
),
base_hold_data AS (
    SELECT DISTINCT
        order_headers.header_id,
        order_lines.line_id,
        order_lines.line_number,
        order_lines.shipment_number,
        order_headers.order_number,
        organization_parameters.organization_code AS warehouse,
        order_types.name AS order_type,
        NVL(
            line_sales_representative.name,
            site_sales_representative.name
        ) AS salesperson,
        CAST(NULL AS VARCHAR2(240)) AS csr,
        CAST(NULL AS VARCHAR2(240)) AS market_manager,
        order_headers.cust_po_number,
        customer_accounts.account_number AS customer_number,
        SUBSTRB(customer_party.party_name, 1, 50) AS customer_name,
        demand_class.meaning AS demand_class,
        ship_to_site.attribute1 AS market_class,
        hold_definitions.name AS hold_type,
        NVL(hold_entity.meaning, hold_sources.hold_entity_code) AS hold_criteria,
        CASE WHEN order_holds.line_id IS NULL THEN 'HDR' ELSE 'LINE' END AS hold_level,
        TRUNC(hold_sources.hold_until_date) AS hold_until_date,
        TRUNC(NVL(order_lines.schedule_ship_date, order_lines.request_date)) AS schedule_request_date,
        TRUNC(order_lines.request_date) AS request_date,
        TRUNC(order_lines.schedule_ship_date) AS scheduled_ship_date,
        order_lines.ordered_quantity AS order_quantity,
        CASE
            WHEN order_lines.item_type_code = 'CONFIG'
                THEN model_prices.model_unit_selling_price
            ELSE order_lines.unit_selling_price
        END AS price_per_unit,
        inventory_items.segment1 AS item_number,
        CAST(NULL AS VARCHAR2(240)) AS product_line,
        ship_to_site.location AS ship_to_location,
        CASE WHEN credit_holds.hold_name IS NOT NULL THEN 'X' ELSE NULL END AS credit_hold,
        CASE
            WHEN hold_definitions.name IN (
                'CTR Price Approval Hold (CMS)',
                'CTR 1000 LB Ship Line Hold (CMS)',
                'CTR Freight Accumulation (CMS)'
            ) THEN 'X'
            ELSE NULL
        END AS marketing_hold,
        CASE
            WHEN hold_definitions.name IN (
                'CTR Test Apvl Customer (CMS)',
                'CTR Will Advise Address (CMS)',
                'CTR Need Address (CMS)',
                'CTR Hold Production (CMS)',
                'CTR Line Pick ' || CHR(38) || ' Ship Hold(CMS)',
                'CTR Order Hold (CMS)',
                'QUILL Process Hold (CMS)',
                'Quill Process Hold',
                'CTR Pend Hold (CMS)',
                'CTR Pend Hold(CMS)',
                'CTR Price Check Hold (CMS)'
            ) THEN 'X'
            ELSE NULL
        END AS customer_hold,
        CASE
            WHEN hold_definitions.name IN (
                'CTR Export Packing Req (CMS)',
                'CTR CIF Hold (CMS)'
            ) THEN 'X'
            ELSE NULL
        END AS export_hold,
        CASE
            WHEN hold_definitions.name IN (
                'CTR Test Apvl Engineering(CMS)',
                'CTR Item Status Hold (CMS)',
                'CTR Engineering Hold (CMS)'
            ) THEN 'X'
            ELSE NULL
        END AS engineering_hold,
        CAST(NULL AS VARCHAR2(1)) AS other_hold
    FROM ont.oe_order_headers_all order_headers
    INNER JOIN ont.oe_order_lines_all order_lines
        ON order_headers.header_id = order_lines.header_id
    INNER JOIN ont.oe_order_holds_all order_holds
        ON order_headers.header_id = order_holds.header_id
       AND (order_holds.line_id = order_lines.line_id OR order_holds.line_id IS NULL)
    INNER JOIN ont.oe_hold_sources_all hold_sources
        ON order_holds.hold_source_id = hold_sources.hold_source_id
    INNER JOIN ont.oe_hold_definitions hold_definitions
        ON hold_sources.hold_id = hold_definitions.hold_id
    INNER JOIN ont.oe_transaction_types_tl order_types
        ON order_headers.order_type_id = order_types.transaction_type_id
    INNER JOIN inv.mtl_parameters organization_parameters
        ON order_lines.ship_from_org_id = organization_parameters.organization_id
    INNER JOIN inv.mtl_system_items_b inventory_items
        ON order_lines.inventory_item_id = inventory_items.inventory_item_id
       AND organization_parameters.organization_id = inventory_items.organization_id
    INNER JOIN demand_class_lookup demand_class
        ON order_lines.demand_class_code = demand_class.lookup_code
    LEFT JOIN model_price_by_header model_prices
        ON order_headers.header_id = model_prices.header_id
    LEFT JOIN credit_hold_sources credit_holds
        ON order_holds.hold_source_id = credit_holds.hold_source_id
    LEFT JOIN ar.hz_cust_accounts customer_accounts
        ON order_headers.sold_to_org_id = customer_accounts.cust_account_id
    LEFT JOIN ar.hz_parties customer_party
        ON customer_accounts.party_id = customer_party.party_id
    LEFT JOIN ar.hz_cust_site_uses_all ship_to_site
        ON order_lines.ship_to_org_id = ship_to_site.site_use_id
    LEFT JOIN jtf.jtf_rs_salesreps line_sales_representative
        ON order_lines.salesrep_id = line_sales_representative.salesrep_id
    LEFT JOIN jtf.jtf_rs_salesreps site_sales_representative
        ON ship_to_site.primary_salesrep_id = site_sales_representative.salesrep_id
    LEFT JOIN hold_entity_lookup hold_entity
        ON hold_sources.hold_entity_code = hold_entity.lookup_code
    WHERE order_types.name NOT IN ('Order_Internal Sales_CMS', 'PRE_CONFIG_ONLY')
      AND INSTR(order_types.name, 'AMS') = 0
      AND INSTR(order_types.name, 'Invoice') = 0
      AND INSTR(order_types.name, 'Mixed') = 0
      AND INSTR(order_types.name, 'Sample') = 0
      AND order_lines.flow_status_code NOT IN ('CANCELLED', 'CLOSED')
      AND order_holds.creation_date IS NOT NULL
      AND order_lines.actual_shipment_date IS NULL
      AND order_lines.item_type_code IN ('STANDARD', 'CONFIG', 'OPTION')
      AND order_holds.released_flag = 'N'
      AND hold_sources.released_flag = 'N'
      AND CASE
              WHEN order_lines.item_type_code = 'CONFIG'
                  THEN model_prices.model_unit_selling_price
              ELSE order_lines.unit_selling_price
          END > 0
      AND NVL(order_lines.schedule_ship_date, order_lines.request_date) >= DATE '2026-01-01'
      AND NVL(order_lines.schedule_ship_date, order_lines.request_date) < DATE '2027-02-01'
      AND hold_definitions.name <> 'CTR RLM SALES ORDER HOLD (CMS)'
      AND order_headers.org_id = 101
),
hold_count_by_line AS (
    SELECT
        hold_rows.header_id,
        hold_rows.line_id,
        COUNT(DISTINCT hold_rows.hold_type) AS nbr_holds
    FROM base_hold_data hold_rows
    GROUP BY hold_rows.header_id, hold_rows.line_id
),
synchronized_hold_data AS (
    SELECT
        base_rows.warehouse,
        base_rows.order_number,
        TO_CHAR(base_rows.line_number) || '.' || TO_CHAR(NVL(base_rows.shipment_number, 1)) AS report_line_number,
        base_rows.order_type,
        base_rows.salesperson,
        base_rows.csr,
        base_rows.market_manager,
        base_rows.cust_po_number,
        base_rows.customer_number,
        base_rows.customer_name,
        base_rows.demand_class,
        base_rows.market_class,
        base_rows.hold_type,
        CASE WHEN line_counts.nbr_holds > 1 THEN 'Y' ELSE 'N' END AS multiple_holds,
        line_counts.nbr_holds,
        base_rows.hold_criteria,
        base_rows.hold_level,
        base_rows.hold_until_date,
        base_rows.schedule_request_date,
        base_rows.request_date,
        base_rows.scheduled_ship_date,
        base_rows.credit_hold,
        base_rows.marketing_hold,
        base_rows.customer_hold,
        base_rows.export_hold,
        base_rows.engineering_hold,
        base_rows.other_hold,
        base_rows.order_quantity,
        ROUND(base_rows.price_per_unit, 2) AS price_per_unit,
        ROUND(base_rows.order_quantity * base_rows.price_per_unit, 2) AS extended_price,
        base_rows.item_number,
        base_rows.product_line,
        base_rows.ship_to_location
    FROM base_hold_data base_rows
    INNER JOIN hold_count_by_line line_counts
        ON base_rows.header_id = line_counts.header_id
       AND base_rows.line_id = line_counts.line_id
)
SELECT DISTINCT
    warehouse AS "Warehouse",
    order_number AS "Order Number",
    report_line_number AS "Line Number",
    order_type AS "Order Type",
    salesperson AS "Salesperson",
    csr AS "CSR",
    market_manager AS "Market Manager",
    cust_po_number AS "Customer PO#",
    customer_number AS "Customer Number",
    customer_name AS "Customer Name",
    demand_class AS "Demand Class",
    market_class AS "Market Class",
    hold_type AS "Hold Type",
    multiple_holds AS "Multiple Holds",
    nbr_holds AS "Nbr Holds",
    hold_criteria AS "Hold Criteria",
    hold_level AS "Hold Level",
    hold_until_date AS "Hold Until Date",
    schedule_request_date AS "Schedule/Request Date",
    request_date AS "Request Date",
    scheduled_ship_date AS "Scheduled Ship Date",
    credit_hold AS "Credit Hold",
    marketing_hold AS "Marketing Hold",
    customer_hold AS "Customer Hold",
    export_hold AS "Export Hold",
    engineering_hold AS "Engineering Hold",
    other_hold AS "Other Hold",
    order_quantity AS "Order Quantity",
    price_per_unit AS "Price per Unit",
    extended_price AS "Extended Price",
    item_number AS "Item Number",
    product_line AS "Product Line",
    ship_to_location AS "Ship To Location",
    CASE WHEN hold_type = '3A7 Change Notification Hold' THEN 'X' ELSE NULL END AS "3A7 Change Notification Hold",
    CASE WHEN hold_type = 'Autocreate Config Exception' THEN 'X' ELSE NULL END AS "Autocreate Config Exception",
    CASE WHEN hold_type = 'Configurator Validation Hold' THEN 'X' ELSE NULL END AS "Configurator Validation Hold",
    CASE WHEN hold_type = 'Create Configuration Exception' THEN 'X' ELSE NULL END AS "Create Configuration Exception",
    CASE WHEN hold_type = 'Create Supply Exception' THEN 'X' ELSE NULL END AS "Create Supply Exception",
    CASE WHEN hold_type = 'Credit Card Auth Failure' THEN 'X' ELSE NULL END AS "Credit Card Auth Failure",
    CASE WHEN hold_type = 'Credit Card High Risk' THEN 'X' ELSE NULL END AS "Credit Card High Risk",
    CASE WHEN hold_type = 'Credit Check Failure' THEN 'X' ELSE NULL END AS "Credit Check Failure",
    CASE WHEN hold_type = 'DOO/O2C Change Management Hold' THEN 'X' ELSE NULL END AS "DOO/O2C Change Management Hold",
    CASE WHEN hold_type = 'Denied Parties Hold' THEN 'X' ELSE NULL END AS "Denied Parties Hold",
    CASE WHEN hold_type = 'CTR 1000 LB Ship Line Hold' THEN 'X' ELSE NULL END AS "CTR 1000 LB Ship Line Hold",
    CASE WHEN hold_type = 'CTR 1000LB Release Monday Hold' THEN 'X' ELSE NULL END AS "CTR 1000LB Release Monday Hold",
    CASE WHEN hold_type = 'CTR 500 LB Ship Line Hold' THEN 'X' ELSE NULL END AS "CTR 500 LB Ship Line Hold",
    CASE WHEN hold_type = 'CTR CIF Hold (CMS)' THEN 'X' ELSE NULL END AS "CTR CIF Hold (CMS)",
    CASE WHEN hold_type = 'CTR Credit Check Hold - Manual' THEN 'X' ELSE NULL END AS "CTR Credit Check Hold - Manual",
    CASE WHEN hold_type = 'CTR Customer Sign Off Hold (CMS)' THEN 'X' ELSE NULL END AS "CTR Customer Sign Off Hold (CMS)",
    CASE WHEN hold_type = 'CTR Engineering Hold (CMS)' THEN 'X' ELSE NULL END AS "CTR Engineering Hold (CMS)",
    CASE WHEN hold_type = 'CTR Export Packing Req (CMS)' THEN 'X' ELSE NULL END AS "CTR Export Packing Req (CMS)",
    CASE WHEN hold_type = 'CTR Freight Accumulation (CMS)' THEN 'X' ELSE NULL END AS "CTR Freight Accumulation (CMS)",
    CASE WHEN hold_type = 'CTR Hold For Customer Approval' THEN 'X' ELSE NULL END AS "CTR Hold For Customer Approval",
    CASE WHEN hold_type = 'CTR Hold Line Invoicing (CMS)' THEN 'X' ELSE NULL END AS "CTR Hold Line Invoicing (CMS)",
    CASE WHEN hold_type = 'CTR Hold Production (CMS)' THEN 'X' ELSE NULL END AS "CTR Hold Production (CMS)",
    CASE WHEN hold_type = 'CTR IMS ATO Scheduling Hold' THEN 'X' ELSE NULL END AS "CTR IMS ATO Scheduling Hold",
    CASE WHEN hold_type = 'CTR Item Status Hold (CMS)' THEN 'X' ELSE NULL END AS "CTR Item Status Hold (CMS)",
    CASE WHEN hold_type = 'CTR Line Pick ' || CHR(38) || ' Ship Hold(CMS)' THEN 'X' ELSE NULL END AS "CTR Line Pick & Ship Hold(CMS)",
    CASE WHEN hold_type = 'CTR MASTER SCHED HOLD' THEN 'X' ELSE NULL END AS "CTR MASTER SCHED HOLD",
    CASE WHEN hold_type = 'CTR Need Address (CMS)' THEN 'X' ELSE NULL END AS "CTR Need Address (CMS)",
    CASE WHEN hold_type = 'CTR Order Hold (CMS)' THEN 'X' ELSE NULL END AS "CTR Order Hold (CMS)",
    CASE WHEN hold_type IN ('CTR Pend Hold(CMS)', 'CTR Pend Hold (CMS)') THEN 'X' ELSE NULL END AS "CTR Pend Hold(CMS)",
    CASE WHEN hold_type = 'CTR Phase Out Item Hold (CMS)' THEN 'X' ELSE NULL END AS "CTR Phase Out Item Hold (CMS)",
    CASE WHEN hold_type = 'CTR Pre-Ship Requirements' THEN 'X' ELSE NULL END AS "CTR Pre-Ship Requirements",
    CASE WHEN hold_type = 'CTR Price Approval Hold (CMS)' THEN 'X' ELSE NULL END AS "CTR Price Approval Hold (CMS)",
    CASE WHEN hold_type = 'CTR Price Approval Hold(AMS)' THEN 'X' ELSE NULL END AS "CTR Price Approval Hold(AMS)",
    CASE WHEN hold_type = 'CTR Price Approvals Hold(AMS)' THEN 'X' ELSE NULL END AS "CTR Price Approvals Hold(AMS)",
    CASE WHEN hold_type = 'CTR Price Check Hold (CMS)' THEN 'X' ELSE NULL END AS "CTR Price Check Hold (CMS)",
    CASE WHEN hold_type = 'CTR Proprietory Inventory(CMS)' THEN 'X' ELSE NULL END AS "CTR Proprietory Inventory(CMS)",
    CASE WHEN hold_type = 'CTR Quality Hold (CMS)' THEN 'X' ELSE NULL END AS "CTR Quality Hold (CMS)",
    CASE WHEN hold_type = 'CTR RLM SALES ORDER HOLD (CMS)' THEN 'X' ELSE NULL END AS "CTR RLM SALES ORDER HOLD (CMS)",
    CASE WHEN hold_type = 'CTR Release Test Other Plant' THEN 'X' ELSE NULL END AS "CTR Release Test Other Plant",
    CASE WHEN hold_type = 'CTR Release on Monday Hold' THEN 'X' ELSE NULL END AS "CTR Release on Monday Hold",
    CASE WHEN hold_type = 'CTR SALES ORDER HOLD AMS' THEN 'X' ELSE NULL END AS "CTR SALES ORDER HOLD AMS",
    CASE WHEN hold_type = 'CTR Ship Complete Hold (CMS)' THEN 'X' ELSE NULL END AS "CTR Ship Complete Hold (CMS)",
    CASE WHEN hold_type = 'CTR Test Apvl Customer (CMS)' THEN 'X' ELSE NULL END AS "CTR Test Apvl Customer (CMS)",
    CASE WHEN hold_type = 'CTR Test Apvl Engineering(CMS)' THEN 'X' ELSE NULL END AS "CTR Test Apvl Engineering(CMS)",
    CASE WHEN hold_type = 'CTR Will Advise Address (CMS)' THEN 'X' ELSE NULL END AS "CTR Will Advise Address (CMS)",
    CASE WHEN hold_type = 'Epayment Failure Hold' THEN 'X' ELSE NULL END AS "Epayment Failure Hold",
    CASE WHEN hold_type = 'Epayment Server Failure Hold' THEN 'X' ELSE NULL END AS "Epayment Server Failure Hold",
    CASE WHEN hold_type = 'Export Compliance Hold' THEN 'X' ELSE NULL END AS "Export Compliance Hold",
    CASE WHEN hold_type = 'GSA Violation' THEN 'X' ELSE NULL END AS "GSA Violation",
    CASE WHEN hold_type = 'Gross Margin Hold' THEN 'X' ELSE NULL END AS "Gross Margin Hold",
    CASE WHEN hold_type = 'IMS ATO Scheduling Hold' THEN 'X' ELSE NULL END AS "IMS ATO Scheduling Hold",
    CASE WHEN hold_type = 'Internal Requisition Approval Hold' THEN 'X' ELSE NULL END AS "Internal Requisition Approval Hold",
    CASE WHEN hold_type IN ('Quill Process Hold', 'QUILL Process Hold (CMS)') THEN 'X' ELSE NULL END AS "Quill Process Hold",
    CASE WHEN hold_type = 'CMC CTQX Customer Approval Hold' THEN 'X' ELSE NULL END AS "CMC CTQX Customer Approval Hold",
    CASE WHEN hold_type = 'CMC CTQX HS HF Drives Hold' THEN 'X' ELSE NULL END AS "CMC CTQX HS HF Drives Hold",
    CASE WHEN hold_type = 'CMC CTQX Shipping Hold' THEN 'X' ELSE NULL END AS "CMC CTQX Shipping Hold",
    CASE WHEN hold_type = 'CMC S' || CHR(38) || 'OP Hold' THEN 'X' ELSE NULL END AS "CMC S&OP Hold",
    CASE WHEN hold_type = 'Pending Payment Authorization Hold' THEN 'X' ELSE NULL END AS "Pending Payment Authorization Hold",
    CASE WHEN hold_type = 'Pending Process Payment Hold' THEN 'X' ELSE NULL END AS "Pending Process Payment Hold",
    CASE WHEN hold_type = 'Preconfig Perpetual Hold' THEN 'X' ELSE NULL END AS "Preconfig Perpetual Hold",
    CASE WHEN hold_type = 'Pricing Error Hold' THEN 'X' ELSE NULL END AS "Pricing Error Hold",
    CASE WHEN hold_type = 'Promotion Line' THEN 'X' ELSE NULL END AS "Promotion Line",
    CASE WHEN hold_type = 'Promotion Order' THEN 'X' ELSE NULL END AS "Promotion Order",
    CASE WHEN hold_type = 'CFG_CONFIG_VALID_HOLD' THEN 'X' ELSE NULL END AS "CFG_CONFIG_VALID_HOLD",
    CASE WHEN hold_type = 'TOD Line Make ' || CHR(38) || ' Hold - Pick' THEN 'X' ELSE NULL END AS "TOD Line Make & Hold - Pick",
    CASE WHEN hold_type = 'TOD Line Make ' || CHR(38) || ' Hold - Ship' THEN 'X' ELSE NULL END AS "TOD Line Make & Hold - Ship"
FROM synchronized_hold_data
ORDER BY
    order_number,
    report_line_number,
    hold_level,
    hold_type
