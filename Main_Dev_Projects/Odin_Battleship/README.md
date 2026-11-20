# Odin Battleship

Battleship against the computer on two 10x10 boards. `Ship`, `Gameboard` and `Player` hold all the rules and are tested with node's built-in test runner; the computer never repeats a square and hunts the neighbours of a hit. The original project uses Jest and webpack; this version needs no installs.

Source: The Odin Project, Full Stack JavaScript path.

## Files

| File | Language | Purpose |
|---|---|---|
| `index.html` | HTML | Both boards and status |
| `styles.css` | CSS | Dark theme |
| `js/ship.js, js/gameboard.js, js/player.js` | JavaScript | Game logic |
| `js/index.js` | JavaScript | DOM and turns |
| `tests/battleship.test.js` | JavaScript | 5 tests with `node:test` |
| `package.json` | JSON | Marks the folder as ES modules for node; no dependencies |

## How to run

From the repo root (ES modules do not load from `file://`):

```bash
"C:/Program Files/Python315/python.exe" -m http.server 8765 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8765/Main_Dev_Projects/Odin_Battleship/index.html>.

Run the tests from this folder:

```bash
node --test
```

---

*Made by: Hazzard*
