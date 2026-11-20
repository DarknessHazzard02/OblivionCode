# S&OP KPI Dashboard

A dark-theme dashboard for a weekly S&OP review: OEE, schedule adherence, days of coverage and items below safety stock. Built with plain HTML, CSS and JavaScript (charts are hand-drawn SVG), so it has no libraries, no CDN and no build step.

All data is **invented** (see `data/CONTRATO.md`), and the page says so in a band at the top.

## What it shows

| Visual | Detail |
|---|---|
| KPI cards | OEE, Schedule Adherence (target 95%), Avg Days of Coverage, Items Below Safety |
| OEE by Line | SVG bars; clicking a bar filters every visual to that line, clicking again clears it |
| Schedule Adherence by Day | SVG line with the 95% target; red dots are days under target |
| Production Detail | 10 rows per page, CSV export of the current filter |
| Inventory Coverage | Latest day, sorted by days of coverage, with status |

## Rules it follows

- **No silent defaults.** A KPI without data shows `—` with a note, never 0. If the data can't load, a red band says why and every KPI is marked as unavailable.
- **Freshness and source** are always shown (`Data as of ...`).
- **Data is validated** on load: missing fields stop the page with a message instead of drawing wrong numbers.
- **Safe CSV.** Cells that start with `=`, `+`, `-` or `@` get a leading `'`, so a spreadsheet won't run them as formulas.
- **Text only.** The DOM is built with `textContent` (no `innerHTML`).

## KPIs

| KPI | Formula |
|---|---|
| OEE | (Σ run / Σ planned) x (Σ ideal cycle x actual / Σ run) x (Σ good / Σ actual) |
| Schedule Adherence | Σ min(actual, planned) / Σ planned |
| Days of Coverage | on hand / daily forecast; `NO DEMAND` when the forecast is 0 |

The same definitions are in SQL and DAX in `../SOP_Star_Schema`.

## Files

| File | Purpose |
|---|---|
| `index.html` | Layout |
| `styles.css` | Dark theme, responsive grid |
| `app.js` | Load, validate, KPIs, SVG charts, cross-filter, table, export |
| `generar_demo.py` | Writes `data/dashboard.json` and `data/meta.json` (invented, fixed seed) |
| `docs/PRD.md` | Goal, KPIs and acceptance criteria |

## How to run

```bash
python generar_demo.py
python -m http.server 8765 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8765/>. Run the server from this folder, or from the repo root and open `/Main_Dev_Projects/SOP_KPI_Dashboard/`.

---

*Made by: Hazzard*
