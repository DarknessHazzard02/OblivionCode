-- Made by: Hazzard
-- S&OP KPI queries over the star schema. Each statement is separated by a line with only
-- "-- name: <query>" so verify.py can run them one by one.
--
-- OEE                 = Availability x Performance x Quality
--   Availability      = run_time / planned_time
--   Performance       = (ideal_cycle x actual_qty) / run_time
--   Quality           = good_qty / actual_qty
-- Schedule adherence  = sum(min(actual, planned)) / sum(planned)   (overproduction does not count)
-- Days of coverage    = on_hand / forecast_daily                    (NULL when there is no demand)

-- name: oee_by_line
WITH line_totals AS (
    SELECT
        fact_prod.line_key,
        SUM(fact_prod.planned_time_min)                              AS planned_min,
        SUM(fact_prod.run_time_min)                                  AS run_min,
        SUM(fact_prod.ideal_cycle_sec * fact_prod.actual_qty) / 60.0 AS ideal_min,
        SUM(fact_prod.actual_qty)                                    AS actual_qty,
        SUM(fact_prod.good_qty)                                      AS good_qty
    FROM fact_production AS fact_prod
    GROUP BY fact_prod.line_key
),
line_factors AS (
    SELECT
        line_totals.line_key,
        run_min / NULLIF(planned_min, 0)  AS availability,
        ideal_min / NULLIF(run_min, 0)    AS performance,
        good_qty / NULLIF(actual_qty, 0)  AS quality
    FROM line_totals
)
SELECT
    prod_line.line_code,
    ROUND(line_factors.availability, 4)                                                   AS availability,
    ROUND(line_factors.performance, 4)                                                    AS performance,
    ROUND(line_factors.quality, 4)                                                        AS quality,
    ROUND(line_factors.availability * line_factors.performance * line_factors.quality, 4) AS oee
FROM line_factors
JOIN dim_line AS prod_line ON prod_line.line_key = line_factors.line_key
ORDER BY oee;

-- name: schedule_adherence_by_week
WITH capped AS (
    SELECT
        cal.iso_week,
        prod_line.line_code,
        fact_prod.planned_qty,
        CASE
            WHEN fact_prod.actual_qty < fact_prod.planned_qty THEN fact_prod.actual_qty
            ELSE fact_prod.planned_qty
        END                      AS on_plan_qty
    FROM fact_production AS fact_prod
    JOIN dim_date AS cal       ON cal.date_key = fact_prod.date_key
    JOIN dim_line AS prod_line ON prod_line.line_key = fact_prod.line_key
)
SELECT
    capped.iso_week,
    capped.line_code,
    SUM(capped.planned_qty)                                              AS planned_qty,
    SUM(capped.on_plan_qty)                                              AS on_plan_qty,
    ROUND(SUM(capped.on_plan_qty) / NULLIF(SUM(capped.planned_qty), 0), 4) AS schedule_adherence
FROM capped
GROUP BY capped.iso_week, capped.line_code
ORDER BY capped.iso_week, capped.line_code;

-- name: coverage_latest_day
WITH latest AS (
    SELECT MAX(fact_inv.date_key) AS date_key
    FROM fact_inventory AS fact_inv
)
SELECT
    item.item_code,
    item.family,
    fact_inv.on_hand_qty,
    fact_inv.forecast_daily_qty,
    ROUND(fact_inv.on_hand_qty / NULLIF(fact_inv.forecast_daily_qty, 0), 1) AS days_of_coverage,
    CASE
        WHEN fact_inv.forecast_daily_qty = 0          THEN 'NO_DEMAND'
        WHEN fact_inv.on_hand_qty < item.safety_stock THEN 'BELOW_SAFETY'
        ELSE 'OK'
    END                                                                    AS coverage_status
FROM fact_inventory AS fact_inv
JOIN latest            ON latest.date_key = fact_inv.date_key
JOIN dim_item AS item  ON item.item_key = fact_inv.item_key
ORDER BY
    CASE WHEN fact_inv.forecast_daily_qty = 0 THEN 1 ELSE 0 END,
    days_of_coverage;
