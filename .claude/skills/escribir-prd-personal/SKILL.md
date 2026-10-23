---
name: escribir-prd-personal
description: Convierte las decisiones de una entrevista (entrevista-prd-personal) o de la conversación en el PRD de un proyecto de los repos personales - Main_Dev_Projects/<proyecto>/docs/PRD.md con objetivo, usuarios, fuentes y contrato de datos, KPIs con fórmula, pantallas, fuera de alcance, criterios de aceptación numerados y verificables, riesgos y pendientes. Es lo que lee el auditor (auditar-entrega-personal). Úsala SIEMPRE que se pida "escribe el PRD", "pásalo a spec", "documenta lo que decidimos", al terminar entrevista-prd-personal, o cuando un proyecto de Main_Dev_Projects no tenga docs/PRD.md y se vaya a auditar.
---

# Escribir el PRD

Basada en `to-spec` (mattpocock/skills). Se escribe **en la misma conversación** de la entrevista:
una sesión nueva ya no sabe por qué se decidió cada cosa.

## Dónde

`Main_Dev_Projects/<Proyecto>/docs/PRD.md`. Si ya existe, se edita: no se sobreescribe sin decirlo.

## Plantilla

```markdown
# PRD — <Proyecto>

Versión: 1 · Fecha: <AAAA-MM-DD> · Estado: borrador | aprobado

## 1. Objetivo
Una o dos frases: qué decisión ayuda a tomar y a quién.

## 2. Usuarios
| Quién | Qué hace con esto | Cada cuánto |

## 3. Fuentes y contrato de datos
| Fuente | Archivo / tabla | Frescura | Datos del repo (inventados / semi-ficticios) |
Enlaza el `CONTRATO.md`. Nada real en el repo.

## 4. KPIs
| KPI | Fórmula exacta | Unidad | Umbral / semáforo |

## 5. Pantallas
Qué se ve y qué filtra a qué (cross-filter).

## 6. Fuera de alcance
Lo que se decidió NO hacer, con el motivo.

## 7. Criterios de aceptación
CA-01 … CA-nn. Cada uno **verificable** por alguien que no estuvo en la conversación:
qué se hace, qué se debe ver, con un número o un texto concreto.
- Mal: "Los filtros funcionan bien."
- Bien: "CA-04: al elegir Planta = X en el panel, el KPI Total y la tabla muestran solo filas de X;
  el chip 'Planta: X' aparece en el encabezado."

## 8. Riesgos y cómo se ve si falla en silencio
| Riesgo | Señal de que pasó |

## 9. Pendientes
| Pendiente | Quién lo resuelve |
```

## Reglas

- **Solo lo decidido.** Lo que quedó en "no sé" va a Pendientes, no se rellena.
- Los criterios de aceptación salen de las secciones 4 y 5 y de los estándares que apliquen
  (`dashboard-standards` para tableros). Si un estándar aplica, se cita la sección, no se copia.
- Texto con `formato-textos`.
- Al terminar, muestra la lista de CA y pide aprobación; con el sí, `Estado: aprobado`.
