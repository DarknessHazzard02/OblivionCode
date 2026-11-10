---
name: "gizmo-coding-standards"
description: "Coding standards for VBA, Power Query (M), SQL, Oracle SQL, Python, pandas, PySpark, DAX and automation flows, including the work vs personal signature rule and known PySpark traps in Fabric. Use it whenever code is written, reviewed, fixed or refactored - a macro, an Excel script, an M query, a SQL or Oracle query, a Python script or notebook, a DAX measure or a Power Automate flow - and when ORA-24374, Option Explicit, parquet or a venv come up. / Estándares de código para VBA, Power Query (M), SQL, Oracle, Python, pandas, PySpark, DAX y flujos, con la regla de firma laboral vs personal y las trampas conocidas de PySpark en Fabric. Úsala siempre que se escriba, revise, corrija o refactorice código."
---

# Coding Standards / Estándares de Código

## English

**When to use:** any time code is written, reviewed, fixed or refactored.

**Steps**
1. Decide the destination: **work** (anything of the company) or **personal** (Haz's own projects). In doubt, work.
2. Apply the language rules from the reference file, in full.
3. Signature: work = none at all. Personal = the per-language signature in the reference table.
4. Deliver complete, copy-ready blocks with no "...".
5. When reviewing, list each deviation with the rule it breaks and the corrected code.

**Non-negotiable rules**
- No silent errors and no silent defaults: unreadable values become null and are counted, never 0.
- VBA: Option Explicit; On Error GoTo ErrorHandler that restores Application; section banners.
- M: English CamelCase steps; no blank lines inside let...in; one description line.
- SQL: CTEs, descriptive aliases (never a/b/t1), no SELECT *, explicit null handling.
- Oracle: no comment before the first statement (ORA-24374) and no trailing ";".
- PySpark: eqNullSafe for nullable comparisons; read tables by path; prefix columns before joins; verify bucket counts add up to the input.
- DAX: VAR per step, DIVIDE() instead of /.
- Never credentials in code.

**Reference:** read `references/coding-standards.en.html` for the full rules, examples and the PySpark trap table.

## Español

**Cuándo usarla:** siempre que se escriba, revise, corrija o refactorice código.

**Pasos**
1. Decide el destino: **laboral** (todo lo de la empresa) o **personal** (proyectos propios de Haz). En duda, laboral.
2. Aplica completas las reglas del lenguaje que trae el archivo de referencia.
3. Firma: laboral, ninguna. Personal, la firma por lenguaje de la tabla de referencia.
4. Entrega bloques completos y listos para copiar, sin "...".
5. Al revisar, lista cada desviación con la regla que rompe y el código corregido.

**Reglas que no se negocian**
- Sin errores ni defaults silenciosos: un valor ilegible sale nulo y contado, nunca 0.
- VBA: Option Explicit; On Error GoTo ErrorHandler que restaure Application; banners por sección.
- M: pasos en inglés y CamelCase; sin líneas en blanco dentro de let...in; una línea de descripción.
- SQL: CTEs, alias descriptivos (nunca a/b/t1), sin SELECT *, nulos explícitos.
- Oracle: sin comentario antes de la primera sentencia (ORA-24374) y sin ";" final.
- PySpark: eqNullSafe al comparar columnas anulables; leer tablas por ruta; prefijar columnas antes de unir; verificar que las cubetas sumen la entrada.
- DAX: un VAR por paso, DIVIDE() en lugar de /.
- Nunca credenciales en el código.

**Referencia:** lee `references/estandares-de-codigo.es.html` para las reglas completas, los ejemplos y la tabla de trampas de PySpark.

## Close / Cierre

End with "What you need to do" / "Lo que tienes que hacer": numbered steps, each with where, what success looks like, and what a silent failure looks like.
