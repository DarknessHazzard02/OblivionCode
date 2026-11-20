# Odin Weather App

Search a city to see the current weather and a 5-day forecast, with a Celsius / Fahrenheit toggle. Data comes from Open-Meteo, which is free and needs **no API key**. Uses `async`/`await`, shows a loading state, and every failure (unknown city, network, bad response) shows a message instead of a blank page. The background color follows the weather.

Source: The Odin Project, Full Stack JavaScript path.

## Files

| File | Language | Purpose |
|---|---|---|
| `index.html` | HTML | Search form, status, result |
| `styles.css` | CSS | Dark theme, weather-based glow |
| `js/api.js` | JavaScript | Geocoding and forecast calls, WMO code descriptions |
| `js/index.js` | JavaScript | UI, loading and error states |

## How to run

From the repo root (ES modules do not load from `file://`):

```bash
"C:/Program Files/Python315/python.exe" -m http.server 8765 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8765/Main_Dev_Projects/Odin_Weather_App/index.html>.

---

*Made by: Hazzard*
