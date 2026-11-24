---
name: entregar-por-pr
description: Patrón (adaptado de experiencia laboral, ofuscado) para entregar un tablero o un cambio por Pull Request en lugar de zips o carpetas compartidas - rama por tarea, qué va a git (código y datos inventados) y qué no (datos reales), estructura de la carpeta, descripción corta del PR, cómo se revisan varios PR juntos antes de mergear y qué hacer después de un squash. Úsala cuando se quiera montar un flujo de PR en un repo con más de una persona, se reciba un tablero como zip o carpeta suelta, o se pregunte cómo entregar, integrar o mergear un tablero.
---

# Entregar por Pull Request

> Adaptado de experiencia laboral, ofuscado. En los repos de Haz el push a `main` es directo y lo hace él; este patrón aplica cuando un repo tiene colaboradores.

## El flujo

1. Una rama por tarea: `user/<nombre>/<tarea>`, en minúsculas, sin acentos ni espacios.
2. El repo al día antes de editar: `git pull --rebase origin <rama-base>`.
3. Push de la rama y PR hacia la rama de integración (`staging`), nunca directo a `main`.
4. Quien revisa baja la rama, la prueba en local (`preview-local`) y mergea.
5. De integración a `main` lo hace solo quien es dueño del repo.

## Qué va a git y qué no

| Va | No va |
|---|---|
| Código del tablero (`index.html`, `app.js`, estilos) | Datos reales (se quedan en el origen o en una carpeta ignorada) |
| `data/` con datos **inventados** y su `CONTRATO.md` | `config.local.json`, `.env`, llaves |
| `README.md` y `docs/PRD.md` | Exports, zips, `.xlsx` de trabajo |

## Carpeta de un tablero

```
<tablero>/
  index.html  app.js  estilos.css
  data/ (inventados) + CONTRATO.md
  docs/PRD.md
  README.md   (de dónde salen los datos, qué falta)
```

Quien hace el tablero entrega **solo su carpeta**. Conectarlo al portal (ruta, lista blanca, tarjeta) lo hace quien integra.

## Descripción del PR

- Cambio corto: **máximo 2 líneas**. Cambio complejo: **máximo 6**.
- Qué cambia y para qué. Sin tablas ni explicación del código: eso está en el diff. Sin firmas de herramientas.

## Varios PR a la vez

Antes de mergear, se juntan en una rama temporal (`git merge --no-ff` de cada uno) y se prueban juntos: dos tableros pueden pisar la misma lista blanca o la misma tarjeta.

## Después de un squash

La rama terminó: no se le hace rebase. Lo siguiente va en una rama nueva desde la base: `git switch -c user/<nombre>/<tarea> origin/staging`. Si la rama ya estaba subida y se hizo rebase: `git push --force-with-lease`, solo en la rama propia.
