---
name: auditar-entrega
description: Auditoría independiente antes de dar por terminado un proyecto, tablero o cambio de los repos personales - el agente auditor (otro modelo, sin la conversación) compara cada criterio de aceptación del PRD contra el diff y la evidencia de probar-tablero y revisar-antes-de-commit, y da un veredicto por criterio PASA / FALLA / SIN EVIDENCIA. Úsala SIEMPRE antes de decir que algo "ya quedó", al cerrar un proyecto o fase, antes de un PR o una entrega, y cuando se pida "audítalo", "¿de verdad está terminado?", "segunda opinión" o "revisión independiente".
---

# Auditar entrega

> **Gemini / Antigravity no lanza subagentes como Claude.** Carga la skill `rol-<agente>` y haz cada revisión en una pasada aparte, juzgando solo el diff y los archivos, no lo que sabes de la conversación.

El que hizo el cambio no se audita a sí mismo. El agente `auditor` corre con **otro modelo** y
**sin la conversación**: solo ve lo que quedó escrito.

## 1. Juntar la entrada

| Pieza | De dónde | Si no existe |
|---|---|---|
| Criterios | `Main_Dev_Projects/<Proyecto>/docs/PRD.md`, sección 7 | se usa la lista de `probar-tablero` + `tablero-estandar` como criterios, y se dice en el veredicto |
| Cambio | `git diff <base>...HEAD` o la lista de archivos | — |
| Evidencia de pruebas | `.agentes-estado/pruebas-<Proyecto>.md` o la tabla del chat | todo criterio de pantalla queda SIN EVIDENCIA |
| Evidencia de revisión | `.agentes-estado/revision.md` | se dice |

## 2. Lanzar

`Agent` con `subagent_type: auditor` (si no aparece: `general-purpose`, `model: sonnet`, con el
cuerpo de `.agents/skills/rol-auditor/SKILL.md`). El prompt lleva **las rutas y el texto de la evidencia**,
nunca un resumen de "lo que hicimos": el resumen es justo lo que se está auditando.

## 3. Lo que regresa y qué se hace

| Criterio | Veredicto | Prueba citada | Nota |

- **FALLA** → se arregla y se vuelve a probar ese punto.
- **SIN EVIDENCIA** → no es PASA: se consigue la evidencia (una prueba más) o se dice que falta.
- Se reporta tal cual a Haz, sin suavizar. Solo si todo es PASA se dice "terminado".
