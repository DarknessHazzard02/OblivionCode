# PastDue_OpenOrders — Past Due Open Orders (S&OP)

Extrae de Oracle EBS y de D365 los insumos del reporte de órdenes vencidas (holds, inventario, tránsito,
estatus de embarque, overrides) y los publica en SharePoint. El tablero sustituye al Excel
*Past Due Open Orders* (`.xlsm`): aplica sus fórmulas, la macro de asignación y los ajustes manuales,
y muestra el past due por sitio responsable.

## Arquitectura

```
Oracle EBS (ODBC) ─┐
D365 BYOD (ODBC) ──┴─ PL_Past_Due_Report (Data Pipeline, 22 actividades)
                        11 Copy: SQL ───► Files/Past_Due_Reports/*.csv
                        11 Copy ────────► Shared Documents/Past_Due_Reports/*.csv
                                              │
                        dashboard/generar_datos.py (fórmulas de detailtab + macro + ajustes)
                                              ▼
                        dashboard/ (HTML + JS) ──► Portal BI
```

## Componentes

| Ruta | Qué es |
|---|---|
| `fabric/PL_Past_Due_Report.DataPipeline/sql/` | las 11 consultas: 10 de Oracle EBS y 1 de D365 (`AX_Inventory`) |
| `dashboard/` | el tablero: `index.html`, `app.js`, `estilos.css`, `generar_datos.py`, generadores de datos inventados |

## Trabajo realizado

- **Separación (Fase 1):** las 11 consultas salieron del JSON del pipeline. El separador ya reconoce
  las que empiezan con `/* ... */`.
- **SQL de Oracle:** se cambiaron los alias de Discoverer (`o100902`, `o100365`, `o100754`…) por nombres
  descriptivos (`onhand_balance`, `org_item`, `so_line`…), los joins con coma por `INNER JOIN … ON` y
  las subconsultas anidadas de `Override_SO` por CTEs. La firma y la hoja de origen van dentro del
  `SELECT`/`WITH`.
- **SQL de D365:** `AX_Inventory` calcula peso, disponible y costo una sola vez con `CROSS APPLY`. El
  costo sigue fallando si un item trae dos costos, en lugar de duplicar filas.
- **Firma** en los archivos propios del tablero (`shared/` no se toca).

## Hallazgos en el sistema original

- `CTR_Order_Holds_Report` filtra por fechas escritas a mano (`2026-01-01` a `2027-02-01`). Después de
  enero de 2027 deja fuera los pedidos nuevos sin avisar.

## Abrir el tablero

`python build/generar_contrato.py data` dentro de `dashboard/` regenera los datos inventados;
luego `python -m http.server 8765 --bind 127.0.0.1` y abrir `http://127.0.0.1:8765/`.

Made by Hazzard
