# S&OP Star Schema

A star schema for manufacturing S&OP, with the same KPIs written twice: as SQL queries and as DAX measures for a Power BI model. A Python script loads everything into an in-memory SQLite database and checks every KPI, so the SQL is tested, not just written.

All data is **invented** (see `demo/CONTRATO.md`).

## Model

```text
              dim_date
                 |
dim_line -- fact_production -- dim_item -- fact_inventory -- dim_date
```

| Table | Grain |
|---|---|
| `fact_production` | line x item x day: planned, actual and good units, planned and run minutes, ideal cycle time |
| `fact_inventory` | item x day: on hand and daily forecast |
| `dim_date`, `dim_line`, `dim_item` | calendar (ISO week, workday flag), production lines, items with safety stock |

Constraints (`CHECK`, foreign keys) reject impossible rows, such as more good units than produced or more run time than planned.

## KPIs

| KPI | Formula | SQL | DAX |
|---|---|---|---|
| Availability | run time / planned time | `oee_by_line` | `Availability %` |
| Performance | (ideal cycle x actual units) / run time | `oee_by_line` | `Performance %` |
| Quality | good units / actual units | `oee_by_line` | `Quality %` |
| OEE | Availability x Performance x Quality | `oee_by_line` | `OEE %` |
| Schedule adherence | sum(min(actual, planned)) / sum(planned); overproduction does not count | `schedule_adherence_by_week` | `Schedule Adherence %` |
| Overproduction | sum(max(actual - planned, 0)) | - | `Overproduction Units` |
| Days of coverage | on hand / daily forecast, empty when there is no demand | `coverage_latest_day` | `Days of Coverage` |

## Files

| File | Language | Purpose |
|---|---|---|
| `sql/schema.sql` | SQL | Tables, keys and constraints (portable; runs on SQLite) |
| `sql/kpi_queries.sql` | SQL | KPI queries written with CTEs |
| `dax/measures.dax` | DAX | The same KPIs as Power BI measures (`DIVIDE`, one `VAR` per step) |
| `generar_demo.py` | Python | Writes the invented `demo/seed.sql` |
| `verify.py` | Python | Loads schema and seed into SQLite, runs every query, checks ranges |
| `docs/PRD.md` | Markdown | Goal, KPIs and acceptance criteria |

## How to run

```bash
python generar_demo.py
python verify.py
```

`verify.py` ends with `Completed: all KPI queries ran and every value is in range.` No installs needed: `sqlite3` ships with Python.

---

*Made by: Hazzard*
