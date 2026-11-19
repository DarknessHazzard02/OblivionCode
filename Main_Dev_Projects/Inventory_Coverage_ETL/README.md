# Inventory Coverage ETL

A small, honest inventory ETL: it reads three extracts (inventory snapshot, weekly demand forecast, open supply orders), validates them, and builds one row per item and site with **days of coverage**, **projected shortage date** and a **status**. Every row it drops or doubts is counted in a quality report, so a "green" run can't hide missing data.

All data in this repo is **invented** (see `demo/CONTRATO.md`).

## What it does

| Step | Detail |
|---|---|
| Read | Picks the newest `<prefix>YYYYMMDD.csv` of each source by the date in the file name, never by today's date |
| Validate | Fails with the list of missing columns if a file doesn't match its schema (`config.SOURCES`) |
| Clean | Drops malformed rows (too many or too few cells), duplicates, blank keys, negative quantities and bad dates; keeps the first row when two share a business key; counts each reason |
| Transform | Spreads weekly forecast over days, projects stock day by day for 8 weeks with incoming supply (overdue orders count as arriving on the extract date) |
| Export | `Output/inventory_coverage.csv`, plus `.parquet` when `pyarrow` is installed, plus `quality_report.json` and a log |

## KPIs

| KPI | Formula |
|---|---|
| Average daily demand | sum of daily forecast over the next 28 days / 28 |
| Days of coverage | on hand / average daily demand. Left empty when demand is 0, never shown as 0 or infinite |
| Projected shortage date | first day in the next 56 days where on hand + receipts - demand < 0 |
| Status | `SHORTAGE` if a shortage date exists (always wins), else `NO_DEMAND` if the next 28 days have no demand, else `BELOW_SAFETY` if on hand < safety stock, else `OK` |

## Files

| File | Purpose |
|---|---|
| `main.py` | The ETL (standard library; Parquet through `pyarrow` if present) |
| `config.py` | Sources, expected columns, horizon. Real paths come from `config.local.json` (ignored by git) |
| `generar_demo.py` | Writes the invented extracts in `demo/source/`, with a few broken rows on purpose |
| `requirements.txt` | Optional: `pyarrow` for the Parquet output |
| `docs/PRD.md` | Goal, KPIs and acceptance criteria |

## How to run

```bash
python generar_demo.py
python main.py
```

Optional, for Parquet:

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

Expected on the demo data: 40 item-site rows, and a quality report counting 1 malformed row, 1 duplicate, 1 key conflict, 1 blank key, 1 bad date, 1 negative quantity and 1 forecast item without inventory. The report also lists the extract date of each file; if they differ, the log shows a WARNING.

---

*Made by: Hazzard*
