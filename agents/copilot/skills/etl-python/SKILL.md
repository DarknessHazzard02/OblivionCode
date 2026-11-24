---
name: etl-python
description: Cómo se arma un ETL en Python de Haz - pandas + pyarrow con salida parquet, venv por proyecto, configuración fuera del código (config.py + config.local.json ignorado), logging, validación de esquema con ValueError, lectura por prefijo, deduplicado, idempotencia y un mensaje final de completado. Úsala SIEMPRE que se escriba o revise un script de carga, transformación, limpieza o consolidación de archivos (Excel, CSV, exports), cuando se mencione ETL, pandas, pyarrow, parquet, main.py, config.py, requirements.txt o venv, o cuando se quiera reemplazar un proceso manual de Excel por un script.
---

# ETL en Python

Plantilla completa en `_comun/plantillas/etl/` (la usa `nuevo-proyecto --tipo etl`).

## Estructura

```
<Proyecto>/
  main.py                  orquesta: leer → validar → transformar → exportar
  config.py                rutas y columnas; lee config.local.json o variables de ambiente
  config.local.ejemplo.json la forma, sin rutas reales
  requirements.txt         pandas==…, pyarrow==… (con versión)
  generar_demo.py          datos inventados con semilla fija
  demo/source/ + CONTRATO.md
  Output/                  salida, ignorada por git
```

## Reglas

| Regla | Cómo |
|---|---|
| Config fuera del código | `config.py` lee `config.local.json` → variable de ambiente → `demo/source/`. Si nada existe, `FileNotFoundError` con la lista de lo que buscó |
| Validar antes de transformar | Columnas esperadas en config; faltan → `ValueError(f"Missing columns: {missing}")` |
| Errores visibles | `try/except` en cada lectura y barrido de carpeta; se registra el archivo y se sigue **solo** si la config lo permite, y el resumen lo cuenta |
| Tipos explícitos | `dtype=` al leer; fechas con `format=`; nunca confiar en la inferencia |
| Idempotente | La salida se sobreescribe completa (o por partición); correrlo dos veces da lo mismo |
| Duplicados | Llave declarada en config; se reporta cuántos se quitaron |
| Logging | `logging.basicConfig(level=INFO, format="%(asctime)s %(levelname)s %(message)s")`; último mensaje: `ETL completado: N filas, M archivos, K descartados` |
| Salida | `.parquet` (pyarrow, `index=False`) y, si se pide, `.csv` con `utf-8-sig` |
| Frescura | La fecha de los datos sale del nombre o del contenido del archivo, nunca de `datetime.now()` |

## Banners

```python
# ===============================================
# Read Source Files
# ===============================================
```

Orden: Configuration → Read Source Files → Validate Schema → Transform → Export → Summary.

## Cómo se comprueba

1. `python generar_demo.py && python main.py` corre limpio con datos inventados.
2. Quitar una columna del demo → el ETL truena con `Missing columns: [...]`, no sigue.
3. Correrlo dos veces → la salida tiene las mismas filas (idempotente).
