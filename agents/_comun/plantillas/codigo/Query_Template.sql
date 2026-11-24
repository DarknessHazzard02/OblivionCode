-- Made by: Hazzard
-- Coverage by plant and material
WITH inv_snapshot AS (
    SELECT plant_code,
           material_code,
           SUM(on_hand_qty) AS on_hand_qty
    FROM   ERP_CORP.dbo.Inventory_MB52
    GROUP  BY plant_code, material_code
),
daily_demand AS (
    SELECT plant_code,
           material_code,
           AVG(demand_qty) AS avg_daily_demand
    FROM   ERP_CORP.dbo.Demand_Daily
    WHERE  demand_date >= DATEADD(DAY, -28, CAST(GETDATE() AS DATE))
    GROUP  BY plant_code, material_code
)
SELECT inv_snapshot.plant_code,
       inv_snapshot.material_code,
       inv_snapshot.on_hand_qty,
       COALESCE(daily_demand.avg_daily_demand, 0) AS avg_daily_demand,
       inv_snapshot.on_hand_qty / NULLIF(daily_demand.avg_daily_demand, 0) AS days_of_coverage
FROM   inv_snapshot
LEFT   JOIN daily_demand
       ON  daily_demand.plant_code = inv_snapshot.plant_code
       AND daily_demand.material_code = inv_snapshot.material_code
