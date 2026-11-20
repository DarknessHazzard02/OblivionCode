# PRD - Inventory Coverage ETL

Version: 1 · Date: 2026-11-19 · Status: done (portfolio showcase)

## 1. Goal
Tell a planner, for every item and site, how many days the stock will last and when it will run out, so expediting starts before the shortage instead of after it.

## 2. Users
| Who | What they do with it | How often |
|---|---|---|
| Supply planner | Sorts by projected shortage date and expedites | Daily |
| Inventory analyst | Reads the quality report before trusting the numbers | Daily |

## 3. Sources and data contract
| Source | File | Freshness | Data in the repo |
|---|---|---|---|
| Inventory snapshot | `inventory_snapshot_YYYYMMDD.csv` | Daily | Invented |
| Weekly demand forecast | `demand_forecast_YYYYMMDD.csv` | Weekly | Invented |
| Open supply orders | `open_orders_YYYYMMDD.csv` | Daily | Invented |

Contract: `demo/CONTRATO.md`. Nothing real is in the repo.

## 4. KPIs
| KPI | Exact formula | Unit | Threshold |
|---|---|---|---|
| Average daily demand | sum(daily forecast, next 28 days) / 28 | units/day | - |
| Days of coverage | on_hand / average daily demand; empty when demand = 0 | days | - |
| Projected shortage date | first day d in [extract, extract + 56) where on_hand + Σ receipts(≤ d) - Σ demand(≤ d) < 0 | date | any date = SHORTAGE |
| Status | SHORTAGE > NO_DEMAND (no demand in the next 28 days) > BELOW_SAFETY (on_hand < safety) > OK | - | - |

## 5. Screens
None: the output is a table (CSV / Parquet) and a quality report for a dashboard or BI model to read.

## 6. Out of scope
- Lead times and order policies (it projects, it does not plan replenishment).
- Multi-level BOM explosion.

## 7. Acceptance criteria
- CA-01: `python generar_demo.py` then `python main.py` ends with the log line `Completed: 40 item-site rows exported`.
- CA-02: `Output/quality_report.json` shows `inventory_malformed_rows: 1`, `inventory_duplicates: 1`, `inventory_key_conflicts: 1`, `inventory_blank_keys: 1`, `forecast_invalid_values: 1`, `orders_invalid_values: 1`, `forecast_items_without_inventory: 1`.
- CA-03: Every row with `avg_daily_demand` 0 has an empty `days_of_coverage`, and its status is `NO_DEMAND` unless a shortage is projected (then `SHORTAGE`).
- CA-04: Removing the `on_hand` column from the inventory file makes the run stop with `missing columns: ['on_hand']`.
- CA-05: Without `pyarrow`, the log shows a WARNING that Parquet was skipped and the CSV is still written.
- CA-06: The extract date in the output is 2026-01-05 (from the file name), not the run date.
- CA-07: If the three extract dates differ, the log shows a WARNING and the quality report lists each date.

## 8. Risks and open items
- Weekly forecast is spread evenly over 7 days; real demand is lumpier.

---

*Made by: Hazzard*
