# PastDue_OpenOrders — Past Due Open Orders

Tablero HTML que reemplaza al archivo *Past Due Open Orders* (`.xlsm`). Toma el Open Orders y las
pestañas grises, aplica las fórmulas de `detailtab`, la macro de asignación y los ajustes manuales, y
muestra el past due por sitio responsable.

**Estado: demo.** Corre con datos inventados. Después pasa al Portal leyendo JSON con datos reales.

## Qué hay en el tablero

Las pestañas del Excel quedaron como **vistas** (barra de arriba) y las pestañas `1`–`10` como un
**selector de vista del detalle**:

| Vista | Del Excel |
|---|---|
| Resumen ejecutivo | Executive Summary: tabla por sitio, *Past Due Reason By Site*, contra Request/Promise Date |
| Tendencias | Charts: *Daily Past Due Trend*, *Past Due <1 Day*, *Monthly Past Due Trend*, *Not On Hold vs On Hold By Plant*, *Past Due By Plant* |
| Razones y familias | *Past Due Reasons* (pastel), *Past Due Sales$ By Prod Family* (top 50), antigüedad |
| Bridge | Bridge: número de marketing → past due del reporte |
| Captura manual | Sheet2 y demás capturas: qué archivos se leyeron y qué ajustes se aplicaron |
| Detalle → *Vista* | tabs `1`–`10`, *Customer Past Due Details*, *Buyout Past Due Details* |

Todo lo que depende de captura manual lleva la marca **✎ manual**.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html`, `app.js`, `estilos.css` | el tablero (sin JS inline; listo para el portal) |
| `generar_datos.py` | el cálculo: fórmulas de detailtab + macro (`Orgs_Assignment`, `Customerr`, `ovrwrite`, `Not_PD`) + ajustes manuales. Python estándar |
| `generar_demo.py` | escribe fuentes **inventadas** en `demo/source/` y arma `data/` |
| `demo/source/`, `demo/source/manual/` | fuentes inventadas con las columnas reales (ver `demo/CONTRATO.md`) |
| `data/` | salida de los datos inventados (`"demo": true`) |
| `data_real/`, `config.local.json` | salida y ruta de las fuentes reales. **Ignorados por git** |
| `actualizar.cmd` | recalcula con el corte del día y abre el tablero |
| `shared/` | copia de `Portal-BI/shared` (Chart.js, SheetJS, `seguro.js`, `csv.js`). En el portal se borra |

## Cómo se abre

```bash
python generar_demo.py
python -m http.server 8766 --bind 127.0.0.1
```

Abrir `http://127.0.0.1:8766/`. Con doble clic en `index.html` no carga: el navegador no deja leer
los JSON desde `file://`.

**Con datos reales:** crea `config.local.json` con `{"source": "<carpeta con los CSV y manual/>"}` y
corre `actualizar.cmd`. Para que el día quede en la tendencia: `python generar_datos.py --guardar-historial`.

## Decisiones y diferencias con el Excel

- **Día de gracia.** El Excel tiene dos reglas que no coinciden: la columna BL resta 1 día fijo y la
  CE usa la fecha de orden con 1 o 2 días según el día de la semana. Aquí se usa la regla del
  proceso: **1 día hábil sobre Schedule Ship Date**. Si el corte es lunes, cubre viernes a domingo.
  Se cambia en `DIAS_GRACIA_HABILES`.
- **Recálculo durante la macro.** En Excel las fórmulas se recalculan mientras corre la macro (por
  ejemplo, cuando C71 pasa a C71-2). Aquí se calculan una vez con la org original.
- **La macro tal cual**, incluidos sus detalles:
  - la condición `H05 Or R01` siempre es verdadera; el resultado final es el mismo porque esas orgs
    se limpian después;
  - para RVT-MS con inventario mira la columna *Delivery*, no *Shipment Status*.
- **Nombres reales fuera del código.** La lista de clientes que la macro manda a Customer/Commercial
  y los nombres de Mkt DIV viven en `manual/` de la carpeta de fuentes, no en el código.
- **Witness** sale de `manual/razon_sitio.csv` (columna *Site to Fill*); la macro sola nunca lo asigna.

## Pendiente

- Validar contra un corte real: mismo día del Excel → misma tabla por sitio.
- Llevar las fuentes a Fabric y publicar `meta.json` / `dashboard.json` a `PORTAL-DATA\pastdue-open-orders\`.
  El tablero ya busca primero en `/api/pastdue-open-orders/`.
