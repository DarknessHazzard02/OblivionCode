# SAP_MB52_ZSD_DMND — Inventory coverage vs demand

Tablero HTML que reemplaza al Excel `MB52_SD48_Analysis.xlsx` (hoja *Final*). Cruza el inventario
de MB52 contra la demanda de ZSD_DMND y muestra:

- qué materiales están en faltante (inmediato o dentro de 3 meses),
- la **fecha de afectación** del faltante,
- los materiales con demanda **sin inventario** que la cubra.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html`, `app.js`, `estilos.css` | el tablero (sin JS inline; listo para el portal) |
| `generar_datos.py` | arma los JSON desde los CSV. Es el cálculo del notebook `NB_MB52_ZSD_DMND.py`, en Python estándar (sin pandas), salvo la regla de demanda (ver Avisos) |
| `generar_demo.py` | escribe CSV **inventados** en `demo/source/` y arma `data/` con ellos |
| `demo/source/*.csv` | datos inventados con las mismas columnas que los CSV del pipeline (ver `demo/CONTRATO.md`) |
| `data/dashboard.json`, `data/meta.json` | salida de los datos inventados (`"demo": true`); es lo que trae el repo |
| `data_real/` | salida con los datos reales de OneLake. **Ignorada por git** |
| `config.local.json` | ruta de la carpeta OneLake (`{"source": "..."}`). **Ignorado por git** |
| `actualizar.cmd` | recalcula con el corte del día y abre el tablero |
| `shared/` | copia de `Portal-BI/shared` (Chart.js, SheetJS, `seguro.js`, `csv.js`) para correrlo fuera del portal. En el portal se borra: ahí ya existe |
| `NB_MB52_ZSD_DMND.py` | notebook del pipeline (referencia) |

## Cómo se actualiza y se abre

Doble clic en `actualizar.cmd`, o:

```bash
python generar_datos.py
python -m http.server 8765 --bind 127.0.0.1
```

Abrir `http://127.0.0.1:8765/`. Abrir el `index.html` con doble clic **no** funciona: el navegador
no deja leer los JSON desde `file://`.

**De dónde lee.** `generar_datos.py` toma la carpeta de los CSV en este orden: argumento →
variable `MB52_SD48_SOURCE` → `config.local.json` → `demo/source`. Lo primero que imprime es el modo
(`REAL` o `DEMO`) y la carpeta. Con datos reales escribe en `data_real/`; el tablero la busca antes
que `data/`.

**Para el corte real**, crea `config.local.json` junto a este README:

```json
{ "source": "C:\\Users\\<usuario>\\OneLake - Microsoft\\CMA BI Team\\CMA_BI_Lake.Lakehouse\\Files\\MB52_ZSD_DMND" }
```

En el explorador de archivos, clic derecho en esa carpeta → *Mantener siempre en este dispositivo*.
`ZSD_DMND_Report.csv` pesa ~60 MB y OneLake lo baja al abrirlo: sin esa opción, la primera lectura
tarda minutos o se corta.

**Sin `config.local.json`** el tablero sale con los datos inventados y una banda que lo avisa. Para
regenerarlos: `python generar_demo.py`.

> Los datos reales nunca se commitean: `source/`, `data_real/`, `config.local.json`, `*.csv` (salvo
> `demo/source/`) y `*.xlsx` están en `.gitignore`.

## Cómo se validó

Con `DEMAND_RULE = 'neto_abs'` y las hojas MB52 y ZSD_DMND del propio `MB52_SD48_Analysis.xlsx` como
entrada, `generar_datos.py` reproduce su hoja *Final* sin diferencias: 12,711 materiales, las 24
columnas, tolerancia 0.1%.

## Avisos

- **La demanda NO es la del Excel.** El notebook suma `Qty_Valor` por material y fecha y toma el
  valor absoluto. Las recepciones de ZSD_DMND (ShipNt, PchOrd, PurRqs, PlOrd, PrdOrd, QM lot) vienen en
  positivo, así que cuando caen solas en una fecha cuentan como demanda. `generar_datos.py` cuenta
  **solo requerimientos** (`DEMAND_RULE = 'requerimientos'`). Con los CSV del 2026-10-09, la demanda
  de 3 meses baja de 296 M a 19.6 M unidades, y 929 materiales cambian de estatus.
  `DEMAND_RULE = 'neto_abs'` reproduce el Excel sin diferencias. El notebook del pipeline sigue con
  la regla vieja.
- **Cortes distintos.** Si MB52 y ZSD_DMND de OneLake vienen de días distintos, el tablero lo avisa con
  una banda cuando difieren más de un día.
- **Leer los CSV:** el delimitador es coma, la comilla es `"` y el escape es `\` (como en Spark). Con el
  lector de CSV por defecto, 126 renglones de MB52 se corren de columna por descripciones con `\"`.

## Para llevarlo al portal

Carpeta `sap-mb52-zsd-dmnd/` con `index.html`, `app.js` y `estilos.css`. Además:

- la lista blanca y las rutas en `app.py`;
- la tarjeta del portal;
- una actividad Copy que publique `meta.json` y `dashboard.json` a `PORTAL-DATA\sap-mb52-zsd-dmnd\`.

El tablero ya busca primero en `/api/sap-mb52-zsd-dmnd/`.
