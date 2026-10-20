---
name: haz-estandares-codigo
description: Estándares personales de código de Haz para VBA, Power Query (M), SQL y Oracle SQL, Python/pandas/PySpark y DAX - estructura, nombres, manejo de errores, banners por sección y cuándo va la firma "Made by - Hazzard" (solo en sus repos personales). Úsala SIEMPRE que se escriba, revise, corrija o refactorice una macro, módulo VBA, script de Excel, consulta M, paso de Power Query, query SQL, consulta a Oracle, script o notebook de Python, ETL a parquet o medida DAX. También cuando se mencione Option Explicit, ORA-24374, Blitz Report, parquet, pyarrow o un venv.
---

# Estándares de código de Haz

## 0. Antes de escribir: ¿repo personal o laboral?

Corre `git remote -v` (o mira la ruta).

| Contexto | Cómo se reconoce | Firma / autor |
|---|---|---|
| **Personal** | remote `HazielA-Dev/*` o `DarknessHazzard02/*` (BI_DataNexus, OblivionCode) | **Sí**: firma y `Author: Haz` según el lenguaje |
| **Laboral** | remote `SRVC-ADMON/*`, carpeta de N:, cualquier entregable del equipo, o sin git y sin certeza | **No**: ni firma, ni `Author`, ni alias. Ver `portal-seguridad` y `validar-antes-de-entregar` |

En duda, **sin firma**. En trabajo del equipo mandan además `fabric-sap-ingesta`, `dashboard-standards`, `apps-base-datos` y `apps-estandar`; estas reglas solo rellenan lo que ellas no dicen.

Lo que sí aplica en ambos: todo lo demás de este archivo.

## 1. Principios

- Mantenible primero: limpio, modular, idempotente (correrlo dos veces da lo mismo).
- Calidad, legibilidad y rendimiento por encima de "que funcione hoy".
- Nombres y código en **inglés**; la explicación al usuario en español.
- Sin errores tragados en silencio: si algo se ignora, que sea explícito y acotado.

## 2. VBA

- `Option Explicit` en la primera línea de **todo** módulo.
- Manejo de errores con `On Error GoTo ErrorHandler`; el handler restaura la configuración de Application y avisa qué falló. `On Error Resume Next` solo envolviendo una línea, seguido de `On Error GoTo 0`.
- Secciones con banner:

```vba
    '================================================================
    ' Variable Declaration
    '================================================================
```

  Orden típico: Variable Declaration → Application Settings → lógica → Restore Application Settings.
- Apagar `ScreenUpdating` / `Calculation = xlCalculationManual` (y `EnableEvents` si aplica) y **restaurarlos siempre**, también en el handler.
- Variables descriptivas en PascalCase (`CurrentWorkbook`, `CurrentTable`); trabajar con `ListObject` en vez de rangos fijos.
- **Firma (solo personal):** última línea del archivo, después de `End Sub`, nunca arriba:

```vba
'Made by: Hazzard
```

## 3. Power Query (M)

- **Firma (solo personal):** al **inicio**, con una sola línea de descripción debajo:

```m
// Made by: Hazzard
// Cleans the MB52 export and keeps unrestricted stock by plant
let
    Source = Csv.Document(File.Contents(FilePath), [Delimiter = ";", Encoding = 65001]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    CleanedHeaders = Table.TransformColumnNames(PromotedHeaders, Text.Trim),
    FilteredRows = Table.SelectRows(CleanedHeaders, each [Plant] <> null)
in
    FilteredRows
```

  En laboral: sin la línea de firma; la descripción se queda.
- **Sin líneas en blanco** entre pasos.
- Pasos cortos con nombre descriptivo (`CleanedHeaders`, `FilteredRows`, `ChangedTypes`), nunca `#"Changed Type1"`.
- No comentar cada transformación: el nombre del paso es la documentación.
- Se permite reordenar pasos por rendimiento (filtrar y quitar columnas temprano, conservar query folding).
- No pasar argumento de cultura en conversiones salvo que de verdad haga falta.

## 4. SQL

- Alias descriptivos para tablas y columnas (`inv_head`, `fact_ord`, `po_line`), nunca `a`, `b`, `t1`.
- CTEs (`WITH`) en lugar de subconsultas anidadas; cada CTE con una intención clara.
- Columnas explícitas, nada de `SELECT *` en algo que se entrega.
- Formato por intención analítica: una cláusula por línea, joins alineados.

### Oracle (EBS, Blitz Report)

- **No empezar con comentario**: provoca `ORA-24374`. La consulta arranca directo con `SELECT` o `WITH`.
- **Sin `;` final.**
- Si hace falta documentar, el comentario va **dentro** de la consulta, después del `SELECT`/`WITH`, o fuera del archivo que se ejecuta.
- Pesada contra Oracle = respetar la ventana del DBA (Regla 4 del equipo cuando es laboral).

## 5. Python / pandas / PySpark

- ETL con `pandas` + `pyarrow`, salida en `.parquet`.
- Entorno virtual aislado por proyecto; dependencias declaradas.
- Configuración fuera del código (rutas, nombres de tablas, columnas esperadas en un dict/archivo de config).
- Logging estructurado (`logging`), no solo `print`; mensaje final de completado.
- Validación de esquema antes de transformar:

```python
expected_columns = ["PO_NUM", "VENDOR_NUM", "ITEM_NUM", "QUANTITY", "NEED_BY_DATE"]
missing = [c for c in expected_columns if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}")
```

- Secciones con banner:

```python
# ===============================================
# Read Source File
# ===============================================
```

- **Encabezado (solo personal):**

```python
# ===============================================
# Oracle Open PO Standardization Notebook
# Author: Haz
# ===============================================
```

  En laboral: el título se queda, la línea `Author` no.
- Notebooks de Fabric en trabajo del equipo: seguir `fabric-sap-ingesta` (formato del item, `notebook-content.py`).

## 6. DAX

- Medidas con nombre de negocio legible (`Schedule Adherence %`), variables con `VAR` para cada paso, `DIVIDE()` en vez de `/`.
- Modelo en estrella; medidas en una tabla de medidas.

## 7. Al entregar código

- Bloque completo, listo para copiar y pegar, sin `...` que haya que rellenar.
- Si se cambió algo de un archivo existente, respetar su estilo antes que estas reglas.
