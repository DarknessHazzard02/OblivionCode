# PRD - S&OP KPI Dashboard

Version: 1 · Date: 2026-11-19 · Status: done (portfolio showcase)

## 1. Goal
Give a weekly S&OP review one page that answers: are the lines running well (OEE), are we building what we planned (schedule adherence), and will stock last (coverage)?

## 2. Users
| Who | What they do with it | How often |
|---|---|---|
| Production planner | Finds lines and days under the adherence target | Weekly |
| Plant manager | Compares OEE across lines | Weekly |
| Inventory analyst | Checks items below safety stock | Daily |

## 3. Sources and data contract
| Source | File | Data in the repo |
|---|---|---|
| Production by line and day | `data/dashboard.json` → `production` | Invented |
| Latest inventory | `data/dashboard.json` → `inventory` | Invented |
| Freshness | `data/meta.json` | Invented, `"demo": true` |

Contract: `data/CONTRATO.md`.

## 4. KPIs
| KPI | Exact formula | Unit | Threshold |
|---|---|---|---|
| OEE | (Σ run / Σ planned) x (Σ ideal_cycle x actual / 60 / Σ run) x (Σ good / Σ actual) | % | - |
| Schedule adherence | Σ min(actual, planned) / Σ planned | % | 95% target |
| Avg days of coverage | mean(on_hand / forecast_daily) over items with demand | days | - |
| Items below safety | count(on_hand < safety_stock and forecast > 0) | items | > 0 needs action |

## 5. Screens
One page: KPI cards, OEE by line (filters everything), adherence by day, production detail, inventory coverage.

## 6. Out of scope
- Bilingual labels (the portfolio is in English).
- Excel export (CSV only, to stay library-free).
- Copy button next to item codes: the codes are invented demo keys, not part numbers anyone copies into another system.
- Freshness alert by age: the demo is a fixed snapshot (2026-01-25), so an age threshold would always fire. The date and source are always shown.

## 7. Acceptance criteria
- CA-01: With the demo data, the band reads "Demo: every number on this page is invented." and the header reads "Data as of 2026-01-25".
- CA-02: The four KPI cards show numbers (no `—`, `NaN` or `undefined`); OEE shows 72.3% for all lines.
- CA-03: Clicking the LINE_03 bar sets the LINE_03 chip as pressed, the detail table shows only LINE_03 (15 rows, 2 pages) and OEE changes.
- CA-04: Page 2 of the detail table shows different rows than page 1.
- CA-05: `toCsv` writes a cell `=1+1` as `'=1+1`.
- CA-06: If `data/dashboard.json` is missing, a red band names the error and the KPI cards show `—` with "Data could not be loaded."
- CA-07: At 375 px wide there is no horizontal page scroll; the tables scroll inside their card.
- CA-08: ITM-012 (no demand) shows status NO DEMAND and `—` coverage.

---

*Made by: Hazzard*
