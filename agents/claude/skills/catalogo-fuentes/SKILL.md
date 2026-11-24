---
name: catalogo-fuentes
description: Patrón y plantilla (adaptado de experiencia laboral, ofuscado) para documentar de dónde sale cada dato de un ERP - transacción, cómo se extrae (query, variante, layout), cómo se llama el archivo, dónde cae, en qué tabla termina, qué contiene y quién es dueño - con entradas de ejemplo inventadas. Úsala cuando se arme o actualice un catálogo de fuentes, se agregue una fuente nueva a un pipeline, o se pregunte "de dónde sale este dato" o "qué transacción da esto".
---

# Catálogo de fuentes

> Adaptado de experiencia laboral, ofuscado. Las entradas son **inventadas**: el catálogo real de una organización no entra a este repo.

## Una fila por fuente

| Campo | Qué lleva |
|---|---|
| Fuente | Nombre corto estable (`MB52`, `ZXX_SALES`) |
| Sistema | SAP, Oracle EBS, otro |
| Transacción / reporte | La estándar o la propia (ofuscada `ZXX_*`) |
| Cómo se extrae | Query o user group, variante, layout, programación |
| Archivo | Patrón del nombre con la fecha (`MATERIAL_LIST_MB52_YYYY-MM-DD_hh-mm-ss.csv`) |
| Formato | ALV (ver `parser-alv-sap`), XLSX, CSV real |
| Dónde cae | `\\Servidor\Recurso\<fuente>\` |
| Tabla destino | `SAP_<FUENTE>_RAW` y `SAP_<FUENTE>_CLEAN` |
| Grano | Una fila por material × almacén, por orden, etc. |
| Frescura | De dónde sale la fecha: nombre del archivo o columna |
| Dueño | Rol, no persona (`<responsable de la fuente>`) |

## Ejemplo (inventado)

| Fuente | Transacción | Extracción | Archivo | Tabla | Grano |
|---|---|---|---|---|---|
| `MB52` | MB52 | Variante `/STOCK_ALL`, layout `/HZ01`, diario 02:00 | `MATERIAL_LIST_MB52_YYYY-MM-DD_hh-mm-ss.csv` | `SAP_MB52_CLEAN` | Material × planta × almacén |
| `COOIS_HEADERS` | COOIS | Layout `/HDR`, semanal | `COOIS_Headers_MM.DD.YYYY.xlsx` | `SAP_COOIS_HEADERS_CLEAN` | Orden de producción |
| `ZXX_SALES` | ZXX_SALES (propia) | Query en SQ00, variante `/OPEN` | `PD_REPORT_YYYY-MM-DD_hh-mm-ss.csv` | `SAP_ZXX_SALES_CLEAN` | Línea de pedido |

## Reglas

- Una fuente nueva no entra al pipeline sin su fila.
- Si dos fuentes dan el mismo dato con diferente valor: se anota la discrepancia y se pregunta cuál manda.
- Reproducir una descarga a mano debe ser posible solo con la fila.
