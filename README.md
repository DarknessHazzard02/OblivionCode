# OblivionCode

> *Every manual spreadsheet is a pipeline that hasn't been written yet.*

I'm **Hazzard**. I work where the production plan meets the data: the place where a late material, an overloaded line or a stale Excel file turns into a missed shipment. I learned to code because I got tired of copying and pasting the same report every Monday, and I haven't stopped since.

I approach every problem with **CORE**, a four-step method I designed for myself:

| | Step | What it means |
|---|---|---|
| **C** | Control | Audit the source first: schema, nulls, duplicates, and whether it answers the real business question |
| **O** | Optimize | Automate the manual steps and remove whatever doesn't earn its place |
| **R** | Redesign | Star schemas, clean measures, modular pipelines, visuals built around the decision |
| **E** | Evolve | Monitoring, versioning, and making it ready for the next person |

My one rule: **a number that failed should look like it failed.** No silent zeros, no fake "OK". You'll see that in every dashboard and ETL in this repo.

This repo is my public portfolio: data and BI showcase projects, plus everything I build while working through **freeCodeCamp** and **The Odin Project**. Everything here is my own practice work. All data is invented, and nothing comes from any employer.

---

## Skills

| Area | What I use |
|---|---|
| Data & BI | SQL (CTEs, star schemas), DAX, Power Query (M), KPI design for S&OP (OEE, schedule adherence, coverage) |
| Data engineering | Python ETL with schema validation, logging and data-quality reports; Parquet |
| Front end | HTML, CSS (Flexbox, Grid, responsive), JavaScript (ES modules, async/await), React, D3 |
| Back end & scripting | Node.js, Ruby, Bash, PowerShell, C#, Java, TypeScript |
| Automation | VBA for Excel, GitHub Actions (YAML) |
| Practices | No silent failures, invented data with a written data contract, tests with `node:test` / RSpec / self-checks |

---

## Featured projects

| Project | What it is | Stack |
|---|---|---|
| [S&OP KPI Dashboard](Main_Dev_Projects/SOP_KPI_Dashboard/) | OEE, schedule adherence and coverage with cross-filtering SVG charts, a paginated table, a safe CSV export and a visible degraded state. No libraries | HTML, CSS, JavaScript |
| [S&OP Star Schema](Main_Dev_Projects/SOP_Star_Schema/) | Star schema with the same KPIs in SQL and DAX, verified end to end in SQLite | SQL, DAX, Python |
| [Inventory Coverage ETL](Main_Dev_Projects/Inventory_Coverage_ETL/) | Days of coverage and projected shortage date per item, with a data-quality report that counts every dropped row | Python |
| [freeCodeCamp React & D3](Main_Dev_Projects/FCC_React_D3_Projects/) | 10 front-end projects (calculator, drum machine, choropleth, treemap...) behind one runner page | React, D3 |
| [Battleship](Main_Dev_Projects/Odin_Battleship/) | Battleship against a computer that hunts after a hit; game logic tested with `node:test` | JavaScript |
| [Weather App](Main_Dev_Projects/Odin_Weather_App/) | City search and 5-day forecast from Open-Meteo (no API key), with loading and error states | JavaScript |

---

## Curriculum progress

Counts are of the exercises and projects in this repo. They are not certifications.

### freeCodeCamp

| Area | In this repo | Where |
|---|---|---|
| Responsive Web Design | 5 projects + Cat Photo App | `Main_Dev_Projects/` (Tribute, Survey, Product Landing, Technical Docs, Portfolio), `HTML/freecodecamp` |
| JavaScript Algorithms & Front End | 30 exercises and projects | `JavaScript/freecodecamp` |
| Front End Libraries & Data Visualization | 10 projects | `Main_Dev_Projects/FCC_React_D3_Projects` |
| Back End & APIs, QA, Security (Node) | included in the 30 above | `JavaScript/freecodecamp` |
| Relational Database (Bash + SQL) | 7 SQL + 8 Bash exercises, 3 Bash + SQL projects | `SQL/`, `Bash/`, `Main_Dev_Projects/` |
| Python (scientific computing, data analysis, ML) | 26 exercises and projects | `Python/freecodecamp` |
| Other languages | C# (5), Java, TypeScript, DAX, Power Query, PowerShell, VBA, YAML, JSON | `<Language>/freecodecamp` |

### The Odin Project

| Path | In this repo | Where |
|---|---|---|
| Foundations | 6 projects: Recipes, Landing Page, Rock Paper Scissors, Etch-a-Sketch, Calculator, Sign-up Form | `HTML/odin_project`, `Main_Dev_Projects/Odin_*` |
| Full Stack JavaScript | 6 projects: Library, Tic Tac Toe, Restaurant Page, Todo List, Weather App, Battleship; 5 CS exercises | `Main_Dev_Projects/Odin_*`, `JavaScript/odin_project` |
| Ruby | 4 basics, 5 CS exercises, 5 projects: Mastermind, Hangman, Event Manager, Connect Four, Chess | `Ruby/odin_project` (written without a Ruby install; each has a self-check or spec to run) |

Odin projects that use a bundler or test framework in the original curriculum (webpack, Jest) are built here with native ES modules and `node:test`, so nothing needs installing.

---

## Repository structure

```text
OblivionCode
├── Dev_Coding            ← single-language exercises
│   └── <Language>        (Bash, C#, CSS, DAX, HTML, Java, JavaScript, JSON, PowerQuery,
│                          PowerShell, Python, Ruby, SQL, Typescript, VBA, YAML)
│       ├── freecodecamp     ← freeCodeCamp exercises and projects
│       ├── odin_project     ← The Odin Project (only where there is content)
│       ├── other_sources    ← other courses and personal scripts
│       └── blank.<ext>      ← scratch file
└── Main_Dev_Projects     ← anything that combines languages, one folder per project
    ├── Inventory_Coverage_ETL, SOP_Star_Schema, SOP_KPI_Dashboard   ← data & BI showcase
    ├── Odin_*                                                         ← The Odin Project web projects
    ├── Bike_Rental_Shop, FCC_React_D3_Projects, Number_Guessing_Game, Periodic_Table,
    │   Personal_Portfolio, Product_Landing_Page, Survey_Form,
    │   Technical_Documentation_Page, Tribute_Page                      ← freeCodeCamp projects
    └── Main_Proj_A, Main_Proj_B                                       ← placeholders for future projects
```

Every project folder (all but the two placeholders) has its own README with what it does and how to run it.

---

## How to run things

| Kind | How |
|---|---|
| Web pages and dashboards | From the repo root: `python -m http.server 8765 --bind 127.0.0.1`, then open `http://127.0.0.1:8765/Main_Dev_Projects/<Project>/` |
| Python | `python <file>.py` (the BI projects use only the standard library; `pyarrow` is optional) |
| Node exercises | `node <file>.js`; Battleship tests: `node --test` in its folder |
| Ruby | `ruby <file>.rb` or `ruby <file>.rb --check`; specs: `rspec spec/<file>_spec.rb` from the project folder |
| Bash + SQL | PostgreSQL with a `freecodecamp` user; steps in each project README |

---

*Made by: Hazzard*
