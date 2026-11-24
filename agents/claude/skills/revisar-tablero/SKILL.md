---
name: revisar-tablero
description: Revisa un tablero contra el estándar: defaults silenciosos, frescura, cross-filter y export. Úsala cuando Haz pida "revisar-tablero" o algo equivalente.
disable-model-invocation: true
---

# revisar-tablero

Revisa el tablero indicado contra `tablero-estandar` y `seguridad-web`: defaults silenciosos y modo degradado, frescura y fuente visibles, cross-filter entre todas las gráficas, filtros, tabla paginada, export CSV/Excel sin formato de pantalla, ES/EN, celular (`tablero-celular`), `innerHTML` con datos y CDN. Da cada hallazgo con archivo:línea y el arreglo. Si se puede levantar, corre `probar-tablero`.

Cierra con `Lo que tienes que hacer`.
