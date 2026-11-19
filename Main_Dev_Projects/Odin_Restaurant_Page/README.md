# Odin Restaurant Page

A tabbed page for a fictional grill. The HTML only has the nav and an empty container: each tab (Home, Menu, Contact) is an ES module that builds its own DOM. The original Odin project uses webpack; this version uses native ES modules, so there is no build step.

Source: The Odin Project, Full Stack JavaScript path.

## Files

| File | Language | Purpose |
|---|---|---|
| `index.html` | HTML | Tab bar and `#content` |
| `styles.css` | CSS | Dark theme |
| `js/index.js` | JavaScript | Swaps tabs |
| `js/home.js, js/menu.js, js/contact.js` | JavaScript | One module per tab |
| `js/dom.js` | JavaScript | Small element builder (no `innerHTML`) |

## How to run

From the repo root (ES modules do not load from `file://`):

```bash
"C:/Program Files/Python315/python.exe" -m http.server 8765 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8765/Main_Dev_Projects/Odin_Restaurant_Page/index.html>.

---

*Made by: Hazzard*
