# Flujo de datos — PL_MB52_ZSD_DMND → Portal BI

Workspace **CMA BI Team** (repo `Fabric-Repo`, carpeta `SAP_TRANSACTIONS/SAP_MB52_ZSD_DMND`).
El workspace de pruebas `CMA BI` no participa.

## Diagrama

```
Lakehouse CMA_BI_Lake
  Tables/sap_mb52 ─────► MB52_Table (Copy) ──────► Files/MB52_ZSD_DMND/MB52_Report.csv ───► MB52_Sharepoint
  Tables/sap_zsd_dmnd ──► ZSD_DMND_Table (Copy) ───► Files/MB52_ZSD_DMND/ZSD_DMND_Report.csv ► ZSD_DMND_Sharepoint
                                     │
                                     ▼
                       Merge_File = NB_MB52_ZSD_DMND
                         celdas 04-10 → modelo de cobertura
                         celda 11 ──► Files/MB52_ZSD_DMND/MB52_SD48_Analysis.xlsx ──► Sharepoint_Merge
                         celda 12 ──► Files/dashboard/sap-mb52-zsd-dmnd/{meta,dashboard}.json
                                     │
                                     ▼
                       Publicar a PORTAL-BI (Copy, Binary, gateway 00000000)
                                     │
                                     ▼
       D:\Data\…\PORTAL-DATA\sap-mb52-zsd-dmnd\ ──► app.py (_leer_mb52_json) ──► tablero
```

## 1. Origen

| Pieza | Qué es |
|---|---|
| `sap_mb52` | tabla Delta `SAP_MB52`; la escribe `SAP_TRANSACTIONS/sap_carga_01_archivos` con lo que deja `SAPCARGA_MB52_COPYJOB` |
| `sap_zsd_dmnd` | tabla Delta `SAP_ZSD_DMND`; la escribe `SAP_TRANSACTIONS/sap_carga_01_archivos` con lo que deja `SAPCARGA_ZSD_DMND_COPYJOB` |

**No hay SQL ni Power Query anidado.** Las dos actividades Copy leen la tabla completa
(`LakehouseTableSource`, sin query). Lo único que se puede desacoplar es el notebook.

## 2. Transformación (notebook por celda)

| Celda | Responsabilidad |
|---|---|
| 01 | encabezado |
| 02 | imports, rutas, `BASE_ROWS` (storage location → ubicación resumida) |
| 03 | helpers: `resolve_column`, `stockout_date`, `sunday_only_workdays`, validación de archivos |
| 04 | carga los dos CSV con Spark (`FAILFAST`, se detiene si vienen vacíos) |
| 05 | normaliza MB52 y fija la fecha de análisis y los 3 periodos |
| 06 | normaliza ZSD_DMND; cuenta y descarta filas sin material o fecha |
| 07-09 | demanda por material/fecha, inventario por material, modelo final (regla **neto absoluto**, la del Excel) |
| 10 | controles de calidad |
| 11 | escribe el Excel |
| 12 | **nueva:** escribe el JSON del Portal (regla **solo requerimientos**, la del tablero) |

La celda 12 recalcula en vez de reusar `final` porque el tablero y el Excel usan reglas de demanda
distintas: en ZSD_DMND las recepciones llegan en positivo y el Excel las cuenta como demanda. El
cálculo de la celda 12 es el mismo de `dashboard/generar_datos.py` (probado: mismo `dashboard.json`
byte a byte con los datos inventados).

### Columnas que usa la celda 12

| Fuente | Columna | Tipo |
|---|---|---|
| MB52 | `Material` | texto, sin `.0` final |
| MB52 | `Material_Description`, `Plant`, `Storage_Location`, `Material_Type`, `Material_Group`, `SOURCE_FILE` | texto |
| MB52 | `Unrestricted`, `Quality_Inspection`, `Blocked` | decimal (`Total Inv` = suma de los tres) |
| MB52 | `FILE_DATE` | fecha → fecha de análisis |
| MB52 | `LOAD_DATE` | fecha-hora → `actualizado` |
| ZSD_DMND | `Material` | texto, sin `.0` final |
| ZSD_DMND | `Date` | fecha |
| ZSD_DMND | `Qty_Valor` | decimal; solo cuenta si es negativo |
| ZSD_DMND | `MRP` | texto (filtro del tablero) |
| ZSD_DMND | `FILE_DATE`, `LOAD_DATE`, `SOURCE_FILE` | texto → frescura en `meta.json` |

El contrato de salida (`meta.json`, `dashboard.json`) está en `../dashboard/data/CONTRATO.md`.

## 3. Destinos

| Actividad | Destino | Formato |
|---|---|---|
| `MB52_Sharepoint`, `ZSD_DMND_Sharepoint` | SharePoint | CSV |
| `Sharepoint_Merge` | SharePoint `Shared Documents/MB52_SD48/` | xlsx |
| **`Publicar a PORTAL-BI`** | `PORTAL-DATA/sap-mb52-zsd-dmnd` por el gateway | JSON |

### Publicar a PORTAL-BI

Clon de la actividad del mismo nombre en `MONITOR/PIPELINE_MONITOR`; solo cambian la carpeta de
origen, la de destino y `dependsOn: Merge_File`.

- **Origen:** Lakehouse `CMA_BI_Lake`, `Files/dashboard/sap-mb52-zsd-dmnd`, `*.json`, Binary.
- **Destino:** FileServer, conexión `<connection-id-09>`, `PORTAL-DATA/sap-mb52-zsd-dmnd`.
- **Mapeo de columnas:** no aplica; es copia binaria. Los tipos se fijan en la celda 12.
- **Paralelismo y compresión:** los de la plantilla. Son dos archivos chicos y el portal lee JSON
  plano, así que no se comprime.
- **Sin credenciales:** la escritura a N: la hace la conexión del gateway.
- Si la celda 12 se detiene, el Copy no corre y el portal sigue mostrando el corte anterior.
  La banda de frescura del tablero (`generated_at`, `dato_al`) es la que lo delata.

## Siguiente en fila

`S&OP\Past Due Open Orders` (carpeta del portal `pastdue-open-orders`), en espera de validación técnica.

Made by Hazzard
