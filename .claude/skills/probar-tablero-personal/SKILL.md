---
name: probar-tablero-personal
description: Prueba un tablero en el navegador integrado de la app (sin instalar nada) con una lista fija - consola sin errores, red sin 404, banda de frescura y de datos inventados o semi-ficticios, KPIs con número, cross-filter, filtros, tabla paginada, export CSV y Excel, ES/EN, botón de copiar, ancho de celular y tema oscuro - y deja evidencia (texto y capturas) y el sello de prueba. Úsala SIEMPRE que se edite un tablero de Main_Dev_Projects (index.html, app.js, estilos.css, data*/), cuando el hook exigir_antes_de_commit niegue un commit por falta de prueba, antes de auditar-entrega-personal, y cuando se diga "pruébalo", "ábrelo en el navegador", "valida el tablero", "¿funciona?" o "revisa que no falle en silencio". También sirve para validar un tablero del Portal en su copia local (portal-local).
---

# Probar tablero

Inspirada en `playwright-cli` (snapshot con referencias, consola, red, capturas), pero con el
**navegador integrado** (`mcp__Claude_Browser__*`): no se instala Node ni Playwright.

## 1. Levantarlo

| Dónde vive el tablero | Cómo se sirve |
|---|---|
| `Main_Dev_Projects/<Proyecto>/` | `preview_start` con `name: "tablero-<Proyecto>"` de `.claude/launch.json` (`python -m http.server <puerto> --directory Main_Dev_Projects/<Proyecto>`); URL `http://127.0.0.1:<puerto>/`. La raíz es la carpeta del proyecto porque los tableros piden `/shared/...` con ruta absoluta. Si falta la entrada, se agrega con el siguiente puerto libre desde 8761 |
| El Portal (copia local) | skill `portal-local` → `iniciar_portal.cmd` en 8080; `preview_start` con `name: "portal-local"`. Así pasan la lista blanca y las rutas reales, que `http.server` no prueba |

Si `launch.json` no tiene la entrada, se agrega (no se borra ninguna que ya exista).

## 2. Ahorrar tokens

- Leer con `get_page_text`, `read_page` (`filter: "interactive"`) y `find`. Las capturas pesan.
- **Capturas solo como evidencia**: estado inicial, un filtro aplicado, celular, oscuro. `scale: 0.5`.
- Acciones encadenadas con `browser_batch`.
- `read_console_messages` con `onlyErrors: true`; `read_network_requests` con `urlPattern` de los datos.

## 3. La lista

Cada punto da **PASA / FALLA / N/A** con el dato que lo prueba. Lo que dice cómo debe verse está en
`dashboard-standards`; aquí solo se comprueba.

| # | Qué | Cómo se comprueba | Falla en silencio si… | Sección |
|---|---|---|---|---|
| P01 | Carga sin errores | consola solo errores = 0 | hay `TypeError` y la página igual se ve | 14 |
| P02 | Datos llegan | red: `meta.json` y `dashboard.json` con 200 y tamaño > 0 | 404 o 200 vacío y los KPIs dicen 0 | 13, 15 |
| P03 | Banda de aviso / frescura | texto "Actualizado" / "Datos al" y la banda de inventados o semi | sin fecha, o fecha de hoy inventada | 8, 14 |
| P04 | KPIs con número | `get_page_text`: ningún KPI en `—`, `NaN`, `undefined`, `0` sospechoso | todos en 0 con datos cargados | 12, 13 ter |
| P05 | Cross-filter | clic en una barra/segmento → KPIs y tabla cambian; clic otra vez → vuelven | solo cambia la gráfica clicada | 2 |
| P06 | Panel de filtros | abrir, elegir un valor, el chip aparece, KPIs cambian, limpiar regresa | el chip sale pero los datos no cambian | 5 |
| P07 | Tabla de detalle | paginación avanza; el total de filas cuadra con el KPI | página 2 repite la 1 | 6 |
| P08 | Export CSV / Excel | el botón existe y dispara descarga (red o consola), sin error | descarga vacía o con formato de pantalla | 7 |
| P09 | ES / EN | cambiar idioma: títulos cambian, sin claves crudas (`kpi.total`) | quedan textos sin traducir | 4 |
| P10 | Botón ⧉ | si hay números de parte: existe y no da error al clic | no existe en la tabla | 6 bis |
| P11 | Regreso al portal | botón "← Back to the Portal" con URL relativa | URL absoluta o falta | 10 |
| P12 | Celular | `resize_window` mobile, recargar: sin scroll horizontal, filtros usables | tabla corta columnas sin scroll | 11 |
| P13 | Tema oscuro | `colorScheme: dark`: texto legible, gráficas visibles | texto negro sobre fondo oscuro | 1 |
| P14 | Formato de textos | títulos y etiquetas en Proper, frases con punto | mezcla de mayúsculas | `formato-textos` |

Al terminar: `resize_window` preset `desktop` y `preview_stop` si el servidor lo levantó esta prueba.

## 4. Evidencia y sello

- Tabla P01-P14 en `.claude/estado/pruebas-<Proyecto>.md` (o en el chat si no es repo de git).
- Capturas: se describen en la tabla; no se guardan archivos de imagen en el repo.
- Si todo es PASA o N/A y es repo de git:
  `python .claude/hooks/sellar.py pruebas Main_Dev_Projects/<Proyecto> --evidencia .claude/estado/pruebas-<Proyecto>.md`
  El sello es la huella de html, js, css, json y svg del tablero a cualquier profundidad (también
  `pages/`, `static/`), y de todo `data*/` y `shared/`; no cuentan `docs/`, `build/`, `Modified/` ni `Original/`. Si después cambia uno de esos
  archivos (también los datos), el hook pide probar otra vez antes del commit.
- **Cuándo se exige:** solo al hacer commit de cambios de un tablero, no en cada turno. Mientras se
  trabaja, se prueba cuando tenga sentido; no hace falta repetir la lista entera por cada ajuste chico.
- Una FALLA **no se sella**. Se reporta con el dato que la prueba y la ruta para reproducirla.
