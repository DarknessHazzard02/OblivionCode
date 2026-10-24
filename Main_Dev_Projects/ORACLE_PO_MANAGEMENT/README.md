# ORACLE_PO_MANAGEMENT — Reporte de órdenes de compra abiertas (Oracle)

Extrae de Oracle EBS las órdenes de compra abiertas y aprobadas de las orgs C71, C74 y C75, las lleva
al formato del reporte para proveedores y las publica en SharePoint de lunes a viernes a las 08:00.

## Arquitectura

```
Oracle EBS (ODBC)
  └─ PL_OpenPO_Report (Data Pipeline)
       1. STG_OPEN_PO_C   Copy: consulta SQL ─────────► Files/PO_Report/OpenPO_Report_C.csv
       2. MERGE           Notebook NB_OpenPO_Report ──► Files/PO_Report/OpenPOs_Report.csv
       3. SHAREPOINT      Copy ───────────────────────► Shared Documents/OpenPO_Reports/Oracle_OpenPOs_Report.csv
```

## Componentes

| Ruta | Qué es |
|---|---|
| `fabric/PL_OpenPO_Report.DataPipeline/` | el pipeline; el SQL está separado en `sql/STG_OPEN_PO_C.sql` |
| `fabric/NB_OpenPO_Report.Notebook/cells/01.py` | estandariza columnas y fechas y escribe un solo CSV |
| `mail/Oracle_OpenPOs_Mail.html` | plantilla del correo del reporte |

## Trabajo realizado

- **Separación (Fase 1):** el SQL salió del JSON del pipeline a `sql/`. En el JSON queda la marca
  `@@sql:sql/STG_OPEN_PO_C.sql@@`.
- **SQL:** alias descriptivos (`po_header`, `po_line`, `po_shipment`, `po_distribution`…), joins
  ordenados y `DECODE` → `NVL2`. La firma va dentro del `SELECT`, porque un comentario al inicio da
  `ORA-24374`. Las columnas de salida no cambiaron.
- **Notebook:** `CONFIG` con las rutas y un solo diccionario `OUTPUT_COLUMNS` para validar y
  seleccionar. Usa `logging`, se detiene si el CSV de origen llega vacío y siempre borra la carpeta
  temporal (`try/finally`).
- **Pipeline:** el paso `SHAREPOINT` copiaba `OpenPO_Report_C.csv` (crudo) en vez de
  `OpenPOs_Report.csv`, el estandarizado. En esta versión ya toma el estandarizado.

## Hallazgos en el sistema original

- La corrección del paso `SHAREPOINT` solo está en esta versión; Fabric sigue publicando el crudo.

## Armar el item para Fabric

```bash
python Main_Dev_Projects/_fabric/fabric_items.py ensamblar Main_Dev_Projects/ORACLE_PO_MANAGEMENT/fabric/PL_OpenPO_Report.DataPipeline <carpeta_destino>
```

Made by Hazzard
