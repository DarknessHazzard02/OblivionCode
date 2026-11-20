# Odin Todo List

Projects that hold todos with title, description, due date, priority and notes. Todos can be expanded, edited, completed and deleted, and everything is saved to `localStorage`. The application logic (`model.js`) has no DOM code; `storage.js` rebuilds objects on load; invalid saved items are skipped one by one, the original data is backed up to a second key, and a notice says what happened.

Source: The Odin Project, Full Stack JavaScript path.

## Files

| File | Language | Purpose |
|---|---|---|
| `index.html` | HTML | Sidebar, todo list, edit dialog |
| `styles.css` | CSS | Dark theme, priority colors |
| `js/model.js` | JavaScript | Project and todo factories, store |
| `js/storage.js` | JavaScript | `localStorage` load and save |
| `js/ui.js` | JavaScript | Rendering and forms |
| `js/index.js` | JavaScript | Entry point, first-run sample |

## How to run

From the repo root (ES modules do not load from `file://`):

```bash
"C:/Program Files/Python315/python.exe" -m http.server 8765 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8765/Main_Dev_Projects/Odin_Todo_List/index.html>.

---

*Made by: Hazzard*
