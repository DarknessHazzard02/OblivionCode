---
applyTo: "**/*.sql"
description: "Estándar de SQL y Oracle"
---

# SQL y Oracle

Detalle: skill `estandares-codigo §4`.

- CTEs en lugar de subconsultas anidadas; alias descriptivos, nunca `a`, `b`, `t1`.
- Columnas explícitas: nada de `SELECT *`.
- Nulos explícitos (`COALESCE` / `NVL`).
- SQL: primera línea `-- Made by: Hazzard`.
- Oracle: **ningún comentario antes de la primera sentencia** (`ORA-24374`), **sin `;` final**; la firma va dentro, después de `WITH`/`SELECT`.
