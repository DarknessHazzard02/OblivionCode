---
name: consulta-oracle
description: Escribe una consulta de Oracle EBS lista para Blitz Report. Úsala cuando Haz pida "consulta-oracle" o algo equivalente.
disable-model-invocation: true
---

# consulta-oracle

Escribe la consulta de Oracle EBS para el requerimiento: CTEs con intención clara, alias descriptivos, columnas explícitas, `NVL` en los nulos. **Ningún comentario antes de la primera sentencia** (`ORA-24374`) y **sin `;` final**; la firma `-- Made by: Hazzard` va dentro, después del `WITH`/`SELECT`. Si es pesada, recuerda la ventana del DBA. Base: `agents/_comun/plantillas/codigo/Oracle_Template.sql`.

Cierra con `Lo que tienes que hacer`.
