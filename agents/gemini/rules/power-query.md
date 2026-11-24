---
trigger: glob
globs: **/*.{pq,m,pqm}
description: Estándar de Power Query (M)
---

# Power Query (M)

Detalle: skill `estandares-codigo §3`.

- Primera línea `// Made by: Hazzard` y una línea de descripción.
- Pasos en inglés y CamelCase; nunca `#"Changed Type1"`.
- Sin líneas en blanco dentro de `let ... in`.
- Filtrar y quitar columnas temprano (query folding).
- Sin argumento de cultura salvo que haga falta.
