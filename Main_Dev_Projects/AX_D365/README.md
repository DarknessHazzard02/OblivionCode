# AX_D365 — Ingesta de Dynamics 365 (almacén Riverton, C79)

Lleva al lakehouse las tablas operativas de D365 para el almacén de Riverton (C79): inventario,
ubicaciones, transacciones, recepción y put-away, picking, embarques, facturación, órdenes de venta y
de compra, maestro de items, usuarios y reconteos. Sale por ODBC desde la base BYOD de D365.

## Arquitectura

```
D365 BYOD (ODBC, gateway)
  ├─ 16 Data Pipelines   Copy: SQL ──► Tables/D365_* ──► SharePoint (AX_D365/*)
  ├─  9 Dataflows Gen2   Odbc.Query + tipos ──► Tables/D365_* (facturación y cierre de mes)
  └─ Notebooks           vaciar tabla antes de recargar · DROP TABLE · D365_INVOICING_DIF (agrega lo nuevo de 5 días)
```

## Componentes

| Ruta | Qué es |
|---|---|
| `fabric/<tema>/` | una carpeta por tema (`D365_ON_HAND`, `D365_INVOICING`, …) con sus pipelines, Dataflows y notebooks |
| `fabric_test/` | lo que solo existe en Test: versiones GW1/GW2 de cada Dataflow, `INVENTORY_AGING`, `ON_HAND_MONTH_CLOSURE` |
| `**/sql/*.sql` | 46 archivos con 21 consultas distintas, separadas del JSON del pipeline y del texto M del Dataflow |

## Trabajo realizado

- **Separación:** además del SQL de los pipelines, se sacó el SQL que vivía dentro de un texto M
  (`Odbc.Query("dsn=…", "SELECT#(lf)…")`), siempre que se pudiera volver a codificar idéntico.
- **SQL:**
  - Cada consulta distinta se reescribió una vez y se copió a sus duplicados (GW1/GW2,
    pipeline/Dataflow), con alias descriptivos y firma.
  - Los `FULL OUTER JOIN` que el `WHERE` convertía en `LEFT` ahora se escriben como `LEFT JOIN`.
  - Los CASE de 50 categorías y de 35 estatus pasaron a tablas `VALUES` (los pares se comprobaron
    uno por uno).
  - El reporte GP tenía 5 subconsultas correlacionadas por grupo; ahora usa CTEs `ledger_revenue` e
    `invoice_line_total`.
  - Las 5 variantes de facturación salen de una sola plantilla.
- **Notebooks:** los 15 "Borra los registros" atrapaban el error y salían en verde; ahora se detienen.
  `D365_INVOICING_DIF` quedó en una sola celda: las otras tres eran código comentado.
- **M:** firma, una línea que dice qué tabla carga, pasos con nombre y sangría de 4. Los nombres de
  consulta no cambian porque los destinos dependen de ellos.

## Hallazgos en el sistema original

- Los notebooks "Borra los registros" y "Borrar la tabla" de **D365_LOCATIONS** apuntan a
  **D365_ON_HAND** (en Test pasa lo mismo con `D365_INVENTORY_AGING`). En esta versión ya apuntan a su
  propia tabla.
- `D365_ON_HAND_MONTH_CLOSURE_GW1/GW2` escriben en `D365_ON_HAND` (GW2 en modo Append).
- El reporte GP tiene la fecha final fija `2026-01-28`.
- `EMPTY_LOCATIONS` descarta las ubicaciones con causa de bloqueo nula.
- `D365_INVOICING_DIF` cruza por `ACTUAL_SHIPMENT_TIME`; si viene nulo, vuelve a insertar la línea
  en cada corrida.
- `D365_USERS` y `EXCEPTIONS_LOG` siguen con `SELECT *`.
- `D365_INVOICING_GP` usa `@activity('INVOICING_GP_GW1')`, una actividad que no existe en ese pipeline.

Made by Hazzard
