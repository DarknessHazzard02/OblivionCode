---
name: preview-local
description: Patrón (adaptado de experiencia laboral, ofuscado) para ver un cambio de un portal o sitio con varios tableros antes de aprobarlo - copia local del repo sin .git con su venv, overlays de los tableros que todavía no están en el repo (tarjeta, lista blanca, rutas), pruebas de rutas, servidor en 127.0.0.1 y un zip de demo con solo datos inventados. Úsala cuando se quiera previsualizar un PR, una rama o un tablero nuevo dentro del portal completo, o se diga "vista previa", "preview", "verlo antes de aprobar" o "demo del portal".
---

# Preview local

> Adaptado de experiencia laboral, ofuscado.

## Por qué una copia y no la rama

Una copia sin `.git` se puede romper, rearmar y comprimir sin tocar el repo ni su historial. La rama se queda limpia hasta que el cambio se aprueba.

## Pasos

1. **Copia:** `robocopy <repo> <copia> /MIR /XD .git .venv node_modules __pycache__` (o `rsync -a --delete --exclude .git`).
2. **Entorno:** `python -m venv .venv` en la copia, `pip install -r requirements.txt`.
3. **Overlays:** los tableros que aún no están en el repo se montan encima desde una carpeta propia (`_local/reemplazos/`) y se registran en un `_local/tableros.json`: carpeta, ruta, tarjeta y entrada de lista blanca.
4. **Pruebas de rutas:** cada tablero responde 200 en su ruta, sus `data/*.json` responden 200, y una ruta fuera de la lista blanca responde 404 (también con `..`, `%2e%2e` y `\`).
5. **Servidor:** solo en `127.0.0.1`, nunca en `0.0.0.0`.
6. **Probar** cada tablero con `probar-tablero`.
7. **Zip de demo** (opcional): solo si todos los `data/` tienen `CONTRATO.md` con `datos: inventados`; si uno no lo tiene, no se arma.

## Reglas

- La copia se rearma desde cero en cada corrida: no se edita a mano.
- Una copia por rama o PR (`<copia>-<rama>`), para comparar dos cambios lado a lado.
- Nada de la copia vuelve al repo: lo aprobado se hace en la rama.
