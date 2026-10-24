# NB_ZMM_MD04_Report — Seguimiento de órdenes de compra SAP (ZMM_MD04)

Ingesta diaria del reporte ZMM_MD04 de SAP (órdenes de compra y necesidades de material) a tablas
Delta, más el reporte de PO abiertas para proveedores que se publica en SharePoint.

## Arquitectura

```
SAP (job diario ~06:00) ──► TXT con pipes en la carpeta de red
  └─ ZMM_MD04_ON_PREM_DATA_TO_LAKEHOUSE (Copy Job, gateway) ──► Files/SAP/ZMM_MD04/ZMM_MD04 RAW/
       └─ ZMM_MD04_PIPELINE_CI (Data Pipeline)
            ├─ sap_zmm_md04      Notebook ──► sap_zmm_md04_vigente   (carga vigente, archivo completo)
            ├─ ZMM_MD04_CI_NB    Notebook ──► SAP_ZMM_MD04_TEST      (réplica del dataflow original)
            └─ bitácora SAP_ZMM_MD04_LOG + correo con el resumen JSON

PL_ZMM_MD04_Report (Data Pipeline)
  ZMM_MD04 Copy ──► NB_ZMM_MD04_Report (filtra la corrida del día) ──► SHAREPOINT
```

## Componentes

| Ruta | Qué es |
|---|---|
| `fabric/sap_zmm_md04.Notebook/` | la carga vigente: parsea el TXT, cuarentena las filas desalineadas, es idempotente con bitácora y tiene redes de seguridad para no perder historia |
| `fabric/ZMM_MD04_CI_NB.Notebook/` | la versión anterior (réplica 1:1 del Dataflow Gen2) |
| `fabric/NB_ZMM_MD04_Report.Notebook/` | el reporte de PO abiertas para proveedores |
| `fabric_test/ZMM_MD04_CURRENT_DAY.Dataflow/` | el Dataflow Gen2 original en Power Query M (solo en Test) |
| `mail/SAP_OpenPOs_Mail.html` | plantilla del correo del reporte |

## Trabajo realizado

- **NB_ZMM_MD04_Report:** se reescribió con el mismo patrón que el de Oracle: `CONFIG`,
  `resolve_column()` para los encabezados con acento mal decodificados, `to_report_date()`,
  `logging` y `try/finally`.
- **sap_zmm_md04 y ZMM_MD04_CI_NB:**
  - Leer la tabla o la bitácora atrapaba **cualquier** error y lo tomaba como "la tabla no existe".
    Un error de permisos podía desarmar la red que evita perder las fotos acumuladas. Ahora
    `delta_exists()` revisa el `_delta_log` y cualquier otro error detiene la corrida.
  - Se quitó una celda basura y la nota de un generador que no existe.
  - Los nombres no se tradujeron: el pipeline les pasa parámetros por nombre.
- **Dataflow (M):** de 137 a 69 líneas, sin renglones en blanco, con pasos con nombre y las listas de
  negocio arriba. Las mismas columnas y el mismo resultado.

## Hallazgos en el sistema original

- `ZMM_MD04_PIPELINE_CI` corre dos cargas en paralelo: la vigente y la réplica, que sigue escribiendo
  `SAP_ZMM_MD04_TEST` todos los días.
- Si falla un archivo, el notebook solo lo reporta en el JSON y el pipeline sale en verde. El correo
  de falla (`Office365Email2`) está inactivo.
- El Dataflow descarta filas en silencio con `RemoveRowsWithErrors` (por ejemplo, el stock negativo
  con signo al final).

Made by Hazzard
