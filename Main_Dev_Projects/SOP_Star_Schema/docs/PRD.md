# PRD - S&OP Star Schema

Version: 1 · Date: 2026-11-19 · Status: done (portfolio showcase)

## 1. Goal
Give an S&OP meeting one trusted definition of OEE, schedule adherence and days of coverage, the same in SQL and in Power BI, so the numbers in the report and in the database never disagree.

## 2. Users
| Who | What they do with it | How often |
|---|---|---|
| Production planner | Reviews adherence by line and week | Weekly |
| Plant manager | Compares OEE across lines | Weekly |
| Inventory analyst | Watches items below safety stock | Daily |

## 3. Sources and data contract
| Source | Table | Data in the repo |
|---|---|---|
| Production log | `fact_production` | Invented (`demo/seed.sql`) |
| Inventory snapshot and forecast | `fact_inventory` | Invented |

Contract: `demo/CONTRATO.md`.

## 4. KPIs
| KPI | Exact formula | Unit |
|---|---|---|
| OEE | (Σ run / Σ planned) x (Σ ideal_cycle x actual / Σ run) x (Σ good / Σ actual) | % |
| Schedule adherence | Σ min(actual, planned) / Σ planned | % |
| Days of coverage | on_hand / forecast_daily on the latest date; empty when forecast = 0 | days |

## 5. Screens
None here: the model feeds a BI report. The measures are in `dax/measures.dax`.

## 6. Out of scope
- Downtime reason codes (Pareto of stops).
- Slowly changing dimensions.

## 7. Acceptance criteria
- CA-01: `python generar_demo.py` then `python verify.py` loads 14 dates, 4 lines, 12 items, 40 production rows and 168 inventory rows.
- CA-02: `verify.py` ends with `Completed: all KPI queries ran and every value is in range.`
- CA-03: Every availability, performance, quality, OEE and schedule adherence value is in (0, 1].
- CA-04: ITM-012 has no demand and shows `NO_DEMAND` with an empty days of coverage.
- CA-05: Inserting a production row with `good_qty` greater than `actual_qty` fails with a CHECK constraint error.
- CA-06: Every DAX division uses `DIVIDE`, and each measure has one `VAR` per step.

---

*Made by: Hazzard*
