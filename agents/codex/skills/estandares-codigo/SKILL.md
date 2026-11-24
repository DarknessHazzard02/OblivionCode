---
name: estandares-codigo
description: Estándares de código de Haz para VBA, Power Query (M), SQL y Oracle SQL, Python/pandas/PySpark, DAX, JavaScript/HTML/CSS y flujos de automatización - estructura, nombres, manejo de errores, banners por sección y la firma "Made by: Hazzard" en cada lenguaje. Úsala SIEMPRE que se escriba, revise, corrija o refactorice una macro, módulo VBA, consulta M, paso de Power Query, query SQL, consulta a Oracle, script o notebook de Python, ETL a parquet, medida DAX, página web o flujo. También cuando se mencione Option Explicit, ORA-24374, Blitz Report, parquet, pyarrow, venv o la firma.
---

# Estándares de código de Haz

## 0. Firma (siempre)

| Lenguaje | Firma | Dónde |
|---|---|---|
| VBA | `'Made by: Hazzard` | **Última** línea, después de `End Sub` |
| Power Query (M) | `// Made by: Hazzard` + una línea de descripción | Primera línea |
| Python | Banner con `# Author: Haz` | Encabezado (§5) |
| SQL | `-- Made by: Hazzard` | Primera línea |
| Oracle | `-- Made by: Hazzard` | **Dentro** de la consulta, después de `SELECT`/`WITH` (un comentario al inicio da `ORA-24374`) |
| DAX | `// Made by: Hazzard` | Antes del primer `VAR` |
| JS / TS / C# / Java | `// Made by: Hazzard` | Primera línea, después de lo que el lenguaje exija arriba (`"use strict";`, `using`, `package`) |
| CSS | `/* Made by: Hazzard */` | Primera línea |
| HTML | `<!-- Made by: Hazzard -->` | Después de `<!DOCTYPE html>` (el doctype va primero o entra en modo quirks) |
| YAML / Bash / PowerShell / Ruby | `# Made by: Hazzard` | Primera línea, después del shebang |
| JSON | — | No admite comentarios |

Código ajeno: la firma original se queda y se agrega `Updated by Haz` junto a ella. **Nunca** firmas de herramientas de IA (`Co-Authored-By`, "Generated with").

## 1. Principios

- Mantenible primero: limpio, modular e **idempotente** (correrlo dos veces da lo mismo).
- **Sin errores tragados en silencio y sin defaults silenciosos**: lo que falta o es inválido se ve.
- Bloques completos, listos para copiar, sin `...` por rellenar.
- Nombres y código en inglés; la explicación en el idioma de Haz.
- Si se modifica un archivo existente, su estilo gana sobre estas reglas.

## 2. VBA

- `Option Explicit` en la primera línea de todo módulo.
- `On Error GoTo ErrorHandler`; el handler restaura `Application` y dice qué falló. `On Error Resume Next` solo envolviendo una línea, seguido de `On Error GoTo 0`.
- Banners en este orden: Variable Declaration → Application Settings → lógica → Restore Application Settings.

```vba
    '================================================================
    ' Variable Declaration
    '================================================================
```

- Apagar `ScreenUpdating`, `Calculation = xlCalculationManual` y `EnableEvents`, y **restaurarlos siempre**, también en el handler.
- PascalCase descriptivo (`CurrentWorkbook`, `CurrentTable`). `ListObject` en lugar de rangos fijos.
- Plantilla: `_comun/plantillas/codigo/Module_Template.bas`.

## 3. Power Query (M)

```m
// Made by: Hazzard
// Cleans the inventory export and keeps unrestricted stock by plant
let
    Source = Csv.Document(File.Contents(FilePath), [Delimiter = ";", Encoding = 65001]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    CleanedHeaders = Table.TransformColumnNames(PromotedHeaders, Text.Trim),
    FilteredRows = Table.SelectRows(CleanedHeaders, each [Plant] <> null)
in
    FilteredRows
```

- Pasos en inglés y CamelCase; nunca `#"Changed Type1"`.
- **Sin líneas en blanco** dentro de `let ... in`. No se comenta cada paso: el nombre es la documentación.
- Filtrar y quitar columnas temprano para conservar el *query folding*.
- Sin argumento de cultura salvo que haga falta de verdad.

## 4. SQL

- CTEs en lugar de subconsultas anidadas, cada una con una intención clara.
- Alias descriptivos (`inv_head`, `fact_ord`, `po_line`); nunca `a`, `b`, `t1`.
- Columnas explícitas: nada de `SELECT *` en algo que se entrega.
- Una cláusula por línea, joins alineados; nulos explícitos (`COALESCE` / `NVL`).

### Oracle (EBS, Blitz Report)

- **Ningún comentario antes de la primera sentencia** (`ORA-24374`): arranca con `SELECT` o `WITH`.
- **Sin `;` final.**
- La documentación va dentro de la consulta, después del `SELECT`/`WITH`.
- Consultas pesadas solo en la ventana acordada con el DBA.

## 5. Python, pandas y PySpark

```python
# ===============================================
# Inventory Coverage ETL
# Author: Haz
# ===============================================
```

- `pandas` + `pyarrow`, salida `.parquet`; en un lakehouse, tabla **Delta**.
- Un `venv` por proyecto con dependencias versionadas. Configuración (rutas, tablas, columnas) fuera del código.
- `logging` en lugar de `print`, con mensaje final de completado.
- Validar esquema antes de transformar:

```python
expected_columns = ["PO_NUM", "VENDOR_NUM", "ITEM_NUM", "QUANTITY", "NEED_BY_DATE"]
missing = [c for c in expected_columns if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}")
```

- `unionByName(other, allowMissingColumns=True)` para alinear esquemas.
- `try / except` con error visible en toda lectura de archivos y barrido de carpetas.
- Trampas de PySpark y notebooks: `delta-lakehouse` y `sap-fabric-ingesta`.

## 6. DAX

```dax
Schedule Adherence % =
// Made by: Hazzard
VAR PlannedQty = SUM ( FactSchedule[PlannedQty] )
VAR CappedActual = SUMX ( FactSchedule, MIN ( FactSchedule[ActualQty], FactSchedule[PlannedQty] ) )
RETURN
    DIVIDE ( CappedActual, PlannedQty )
```

- Nombre de negocio legible, un `VAR` por paso, `DIVIDE()` en vez de `/`.
- Tabla de medidas sobre un modelo estrella.

## 7. JavaScript, HTML y CSS

- `const`/`let`, nunca `var`. Funciones cortas con nombre; sin lógica en atributos `onclick`.
- **Nunca** `innerHTML` con datos: `textContent` o un escapador (ver `seguridad-web`).
- Sin librerías por CDN en lo que se entrega: copia local en `shared/vendor/` con su versión.
- CSS con variables (`--color-*`) del tema; nada de colores sueltos.

## 8. Flujos de automatización

- Orden: Trigger → Actions → Conditions → Outputs → Error handling.
- Conexiones de mínimo privilegio y reutilizables; sin bucles innecesarios.
- Idempotencia y reintentos explícitos.

## 9. Ruby y C# (aprendizaje)

- Ruby: RuboCop por default, `snake_case`, specs con RSpec junto al código.
- C#: `PascalCase` para tipos y métodos, `async` hasta arriba, sin `catch {}` vacío.
