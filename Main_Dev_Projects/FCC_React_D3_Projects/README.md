# freeCodeCamp React and D3 Projects

Ten projects from two freeCodeCamp certifications, run from one page:

- **Front End Development Libraries (React):** Random Quote Machine, Markdown Previewer, Drum Machine, JavaScript Calculator, 25 + 5 Clock.
- **Data Visualization (D3):** Bar Chart, Scatterplot Graph, Heat Map, Choropleth Map, Treemap Diagram.

## Files

| File | Language | Purpose |
|---|---|---|
| `FCC_JS_Runner.html` | HTML | Loads one app from `apps/` by `?app=<Name>`. Only listed apps load. CDN libraries are version-pinned with SRI hashes |
| `FCC_JS_Runner.css` | CSS | Shared dark theme |
| `apps/*.js` | JavaScript | One file per project. React apps use `React.createElement` (no JSX, no build step). D3 apps fetch the public freeCodeCamp datasets |

## How to run

From the repo root:

```bash
"C:/Program Files/Python315/python.exe" -m http.server 8765 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8765/Main_Dev_Projects/FCC_React_D3_Projects/FCC_JS_Runner.html?app=Bar_Chart>, or pick a project from the top menu. The charts need internet access for the CDN libraries and datasets.

If a page stays blank after editing a file, hard-reload (Ctrl+Shift+R): the browser may be holding the old copy.

---

*Made by: Hazzard*
