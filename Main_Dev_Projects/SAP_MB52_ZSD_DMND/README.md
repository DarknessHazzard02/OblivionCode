# SAP_MB52_ZSD_DMND — Inventory Coverage vs Demand

Cruza el inventario de SAP (MB52) contra la demanda (ZSD_DMND) para saber qué materiales caen en
faltante, en qué fecha, y cuáles tienen demanda sin inventario que la cubra. El tablero sustituye al
Excel `MB52_SD48_Analysis.xlsx`.

## Arquitectura

```
Lakehouse: tablas MB52 y ZSD_DMND
  └─ PL_MB52_ZSD_DMND (Data Pipeline)
       MB52_Table / ZSD_DMND_Table   Copy ──► Files/MB52_ZSD_DMND/*.csv ──► SharePoint
       Merge_File                   Notebook NB_MB52_ZSD_DMND ──► MB52_SD48_Analysis.xlsx
       Sharepoint_Merge             Copy (binario) ──► Shared Documents/MB52_SD48/
       Merge_File (celda 12)        ──► Files/dashboard/sap-mb52-zsd-dmnd/{meta,dashboard}.json
       Publicar a PORTAL-BI         Copy (binario, gateway) ──► PORTAL-DATA/sap-mb52-zsd-dmnd/
                                              │
                                              ▼
                  Portal BI (app.py) ──► tablero dashboard/ (HTML + JS)
```

En local, `dashboard/generar_datos.py` hace el mismo cálculo que la celda 12 con Python estándar.
Detalle de origen, transformación y destinos: `fabric/docs/flujo-de-datos.md`.

## Componentes

| Ruta | Qué es |
|---|---|
| `fabric/PL_MB52_ZSD_DMND.DataPipeline/` | el pipeline (sin SQL: lee tablas del lakehouse) y la publicación al Portal |
| `fabric/NB_MB52_ZSD_DMND.Notebook/cells/` | 12 celdas: normaliza MB52 y ZSD_DMND, calcula cobertura a 3 meses y fecha de faltante, escribe el Excel (11) y el JSON del Portal (12) |
| `fabric/docs/` | flujo de datos desacoplado: origen, celdas, destinos y columnas |
| `dashboard/` | el tablero |

## Trabajo realizado

- **Notebook:** banner del estándar en cada celda e imports ordenados (sin los que no se usaban). Se
  cambiaron los `print` por `logging`.
- **Lo que antes fallaba en silencio:**
  - Una columna opcional ausente (Quality_Inspection, Blocked…) quedaba en 0 y bajaba `Total Inv`.
    Ahora avisa con un `warning`.
  - Un CSV con encabezado y sin filas generaba un Excel vacío. Ahora se detiene.
  - Las filas de ZSD_DMND sin material o sin fecha se descartaban sin contarlas. Ahora se cuentan.
  - Se avisa qué storage locations no están en `BASE_ROWS`.
- **El cálculo no cambió:** cobertura, fecha de faltante, estatus y Excel son los mismos.
- **Publicación al Portal (2026-10-23):** celda 12 y actividad `Publicar a PORTAL-BI` (clon de la de
  `PIPELINE_MONITOR`). La celda usa la regla de demanda del tablero (solo requerimientos), no la del
  Excel. Con los datos inventados da el mismo `dashboard.json` que `generar_datos.py`, byte a byte.
  Si no hay materiales se detiene y el Portal conserva el corte anterior.

## Pendiente

- El notebook no se ha corrido en Fabric; la celda 12 se probó en su parte de cálculo.

## Abrir el tablero

`python build/generar_contrato.py data` dentro de `dashboard/` regenera los datos inventados;
luego `python -m http.server 8765 --bind 127.0.0.1` y abrir `http://127.0.0.1:8765/`.

Made by Hazzard
