# Willow_Creek — Control de órdenes Willow Creek

Tablero HTML que cruza los reportes diarios de Willow Creek contra SAP y muestra:

- las órdenes que **no se procesaron** (bloqueadas, rechazadas, error de WC o de SAP, sin respuesta, éxito sin SO),
- las que fallaron en WC pero **ya se capturaron a mano** en SAP,
- las que se crearon pero **mal capturadas** (PO o Sold-To distinto en SAP, sin Sold-To, OM distinto, bloqueo de entrega…),
- las órdenes abiertas de SAP de clientes WC que **nunca pasaron por WC**,
- y la revisión de los **reportes recibidos**, para encontrar el que sea distinto (el consolidado mensual).

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html`, `app.js`, `estilos.css` | el tablero (sin JS inline; listo para el portal) |
| `generar_datos.py` | arma los JSON desde la carpeta de Willow Creek. Solo librería estándar (el Excel se lee como zip) |
| `generar_demo.py` | escribe archivos **inventados** en `demo/source/` y arma `data/` con ellos |
| `demo/source/` | datos inventados con la misma forma que la carpeta real (ver `demo/CONTRATO.md`) |
| `data/dashboard.json`, `data/meta.json` | salida de los datos inventados (`"demo": true`); es lo que trae el repo |
| `data_real/` | salida con los datos reales. **Ignorada por git** |
| `config.local.json` | ruta de la carpeta de origen (`{"source": "..."}`). **Ignorado por git** |
| `actualizar.cmd` | recalcula con los archivos del día y abre el tablero |
| `shared/` | copia de `Portal-BI/shared` (Chart.js, SheetJS, `seguro.js`, `csv.js`) para correrlo fuera del portal |

## Lo que lee

La carpeta de origen (hoy `C:\Users\<usuario>\Documents\Developer\Willow_Creek`) con:

| Archivo | Para qué |
|---|---|
| `Willow Creek Orders Report\*.csv` | reportes de Willow Creek; la fecha y hora del corte salen del nombre (`2026-10-21 11 AM.csv.csv`) |
| `WC_FOLLOWUP_*.xlsx` (o `.csv`) | órdenes abiertas de SAP: SO, PO, Sold-To, bloqueos de entrega |
| `SDD167_WILLOWCREEK_ENA_*.csv` | job de SAP (lista ALV); se usa para validar que sus SO estén en WC_FOLLOWUP |
| `ZWCCUST_*.xlsx` (o `.csv`) | clientes dados de alta para WC y su Order Manager |

De cada patrón se toma el archivo más reciente por nombre. `Reporting Notes.docx` no se lee: sus
estatus, notas y parejas válidas están copiados en `generar_datos.py` (`WC_STATUS_DOC`, `NOTAS_DOC`, `PARES_DOC`).

## Cómo se actualiza y se abre

Doble clic en `actualizar.cmd`, o:

```bash
python generar_datos.py
python -m http.server 8767 --bind 127.0.0.1
```

Abrir `http://127.0.0.1:8767/`. Con doble clic al `index.html` **no** funciona: el navegador no deja
leer los JSON desde `file://`.

**De dónde lee.** `generar_datos.py` toma la carpeta en este orden: argumento → variable
`WILLOWCREEK_SOURCE` → `config.local.json` → `demo/source`. Lo primero que imprime es el modo (`REAL` o
`DEMO`). Con datos reales escribe en `data_real/`, que el tablero busca antes que `data/`.

## Reglas

- **Una orden = un PO.** Manda la última actualización; si algún envío del PO ya quedó creado en SAP
  (Success con SO), manda ese, porque un rechazo posterior suele ser el duplicado del mismo PO.
- **Situación:** *Con error / sin procesar* · *Error en WC, capturada a mano en SAP* · *Pendiente* ·
  *Procesada con observaciones* · *Procesada*. El catálogo de hallazgos está en el panel 📖.
- **Capturada a mano:** el PO se busca en WC_FOLLOWUP solo con letras y números y sin `PO` al inicio.
- **Archivo distinto:** se marca *consolidado* el reporte que junta 15 o más fechas de recepción
  (`CONSOLIDADO_MIN_DIAS`). También se marcan los de formato anterior, los idénticos a otro y los que
  pasan de 3 veces la mediana de renglones.

## Avisos

- WC_FOLLOWUP solo trae órdenes **abiertas**: una SO surtida no aparece. Por eso "SO no está abierta
  en SAP" es informativo.
- Los datos reales nunca se commitean: `data_real/`, `config.local.json`, `*.csv` (salvo
  `demo/source/`), `*.xlsx` y `*.docx` están en `.gitignore`.

## Para llevarlo al portal

Carpeta `willow-creek-orders/` con `index.html`, `app.js` y `estilos.css`, más la lista blanca, las rutas
y la tarjeta (Logistics · Order Management). El tablero ya busca primero en `/api/willow-creek-orders/`.
Falta quién publique `meta.json` y `dashboard.json` en `PORTAL-DATA\willow-creek-orders\`: hoy los
archivos de Willow Creek viven en una carpeta local.
