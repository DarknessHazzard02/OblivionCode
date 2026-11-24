---
trigger: glob
globs: **/*.{js,ts,jsx,tsx,html,css}
description: Estándar de JavaScript, HTML y CSS
---

# JavaScript, HTML y CSS

Detalle: skill `estandares-codigo §7, tablero-estandar, seguridad-web`.

- Firma: `// Made by: Hazzard` (JS/TS), `/* Made by: Hazzard */` (CSS), `<!-- Made by: Hazzard -->` después del doctype (HTML).
- Nunca `innerHTML` con datos: `textContent` o un escapador.
- Sin librerías por CDN: copia local en `shared/vendor/`.
- Colores solo desde las variables del tema (`--c-*`).
- Un dato que falta se ve como estado degradado, nunca como 0 o vacío.
