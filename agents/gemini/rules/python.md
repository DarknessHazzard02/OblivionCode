---
trigger: glob
globs: **/*.py
description: Estándar de Python, pandas y PySpark
---

# Python, pandas y PySpark

Detalle: skill `estandares-codigo §5, etl-python, delta-lakehouse`.

- Banner con `# Author: Haz` en el encabezado y banners por sección.
- `logging` en vez de `print`, con mensaje final de completado.
- Configuración fuera del código; `venv` por proyecto.
- Validar esquema antes de transformar: `ValueError(f"Missing columns: {missing}")`.
- `try/except` con error visible en lecturas y barridos; sin defaults silenciosos.
- Salida `.parquet` con pyarrow; en un lakehouse, Delta.
