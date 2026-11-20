# Odin Library

A small book catalog: add books through a modal form, mark them read or unread, remove them. Books are objects made by a `Book` constructor, with `toggleRead` on its prototype; each card is tied to its book by a `crypto.randomUUID()` id.

Source: The Odin Project, Full Stack JavaScript path.

## Files

| File | Language | Purpose |
|---|---|---|
| `index.html` | HTML | Shelf and `<dialog>` form |
| `styles.css` | CSS | Dark theme, card grid |
| `app.js` | JavaScript | Model (constructor, prototype) and rendering with `textContent` only |

## How to run

From the repo root (ES modules do not load from `file://`):

```bash
"C:/Program Files/Python315/python.exe" -m http.server 8765 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8765/Main_Dev_Projects/Odin_Library/index.html>.

---

*Made by: Hazzard*
