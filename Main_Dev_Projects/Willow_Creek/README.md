# Willow_Creek — Willow Creek Order Control

Tablero que cruza los reportes diarios de Willow Creek (captura automática de órdenes) contra SAP.
Muestra las órdenes que no se procesaron, las que se procesaron mal capturadas y las que nunca pasaron
por Willow Creek. No tiene items de Fabric: lee archivos de una carpeta local.

## Arquitectura

```
Carpeta de origen
  ├─ Willow Creek Orders Report/*.csv   (varios cortes al día)
  ├─ WC_FOLLOWUP_*.xlsx              órdenes abiertas de SAP
  ├─ SDD167_WILLOWCREEK_ENA_*.csv       job de SAP (lista ALV)
  └─ ZWCCUST_*.xlsx                  clientes dados de alta y su Order Manager
        └─ dashboard/generar_datos.py (Python estándar; el Excel se lee como zip)
              └─ data/ ──► dashboard/ (HTML + JS) ──► Portal BI
```

## Componentes

| Ruta | Qué es |
|---|---|
| `dashboard/` | el tablero, el cálculo y el generador de datos inventados |

## Trabajo realizado

- La firma se agregó a `index.html`, `app.js`, `estilos.css`, los `.py` y `actualizar.cmd`.

## Abrir el tablero

`python build/generar_contrato.py data` dentro de `dashboard/` regenera los datos inventados;
luego `python -m http.server 8765 --bind 127.0.0.1` y abrir `http://127.0.0.1:8765/`.

Made by Hazzard
