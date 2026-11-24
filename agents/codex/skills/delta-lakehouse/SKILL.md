---
name: delta-lakehouse
description: Cómo se escribe un notebook PySpark que lleva archivos a tablas Delta en un lakehouse (Microsoft Fabric o Databricks) - parámetros, validación de esquema antes de transformar, capa cruda y capa limpia, unionByName con allowMissingColumns, columnas de control, escritura idempotente (overwrite por partición o merge), autolimpieza de staging y las trampas de PySpark que truenan en silencio. Úsala SIEMPRE que se escriba o revise un notebook de PySpark, una carga a Delta, un lakehouse, un merge, o se mencione Spark, Delta, saveAsTable, overwrite, partición o staging.
---

# Notebook PySpark a Delta

Versión completa, con formato de items de Fabric y errores conocidos: `sap-fabric-ingesta`.

## Orden del notebook (banners)

Parameters → Read → Validate Schema → Raw (cruda) → Clean (limpia) → Write → Validate Target → Cleanup Staging → Summary.

## Reglas

| Regla | Cómo |
|---|---|
| Sin credenciales | Nada de llaves, tokens ni cadenas con secreto en el notebook: la conexión del lakehouse o la identidad del workspace |
| Esquema antes de transformar | `missing = set(expected) - set(df.columns)` → `raise ValueError` |
| Dos capas | `<TABLA>_RAW` tal como llegó (todo string) y `<TABLA>_CLEAN` tipada; las reglas de negocio viven en la limpia |
| Columnas de control | `_SOURCE_FILE` (nombre del archivo) y `_LOAD_TS` (momento de la carga) en las dos capas |
| Alinear esquemas | `df_a.unionByName(df_b, allowMissingColumns=True)` |
| Tipar sin tronar | `try_to_date` / `try_cast` (o `to_date` dentro de un `when` que valide el patrón): `to_date` con un valor que no casa **truena** en Spark ANSI |
| Idempotente | Overwrite de la partición que se carga (`replaceWhere`) o `MERGE` por llave; nunca `append` ciego |
| Validar el destino | Conteo destino = conteo origen − descartados declarados; si no, `raise` |
| Autolimpieza | Borrar de `Files/Temporal/` solo lo que esta corrida creó, **después** de validar la tabla |
| Cero huérfanos | Sin tablas de prueba ni archivos sueltos al terminar |

## Trampas que salen en verde

- `count()` antes y después de un `join` que multiplica filas: comparar contra la llave, no solo el total.
- Un `filter` sobre una columna con nulos descarta los nulos sin avisar: contarlos aparte.
- Rutas de `Files/` distinguen mayúsculas.
- Un cuadre por totales no prueba el día a día: comparar por fecha y llave.
- Cambiar el parser no recarga lo ya cargado si hay bitácora de archivos procesados: limpiar la bitácora de esos archivos.
