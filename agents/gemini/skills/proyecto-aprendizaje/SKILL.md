---
name: proyecto-aprendizaje
description: Cómo se trabaja un proyecto o ejercicio de aprendizaje de Haz (freeCodeCamp, The Odin Project, cursos de Python, SQL, Ruby, C#, JavaScript, React, D3) - dónde va en el repo, cómo se nombra, cómo se explica según su etapa, qué se prueba, y la regla de no resolverle el ejercicio sin que lo pida. Úsala SIEMPRE que se mencione freeCodeCamp, FCC, The Odin Project, Odin, curso, certificación, ejercicio, kata, práctica, "estoy aprendiendo", o se cree algo en Dev_Coding o en un Main_Dev_Projects con prefijo Odin_ o FCC_.
---

# Proyecto de aprendizaje

## Dónde va

| Qué | Ruta | Nombre |
|---|---|---|
| Ejercicio suelto | `Dev_Coding/<Lenguaje>/<fuente>/` (`freecodecamp`, `odin_project`, `other_sources`) | `Snake_Case` descriptivo, un archivo por ejercicio |
| Proyecto con página | `Main_Dev_Projects/<Prefijo>_<Nombre>/` | `Odin_Todo_List`, `FCC_React_D3_Projects`, `Tribute_Page` |
| Ejercicio con pruebas (Ruby, JS) | junto al código: `spec/`, `*.test.js` | el nombre del ejercicio |

Todo firmado (`estandares-codigo`). Si el curso da código base, la firma original se queda y se agrega `Updated by Haz`.

## Cómo se ayuda

1. **Primero se pregunta qué quiere**: pista, revisión o solución. Por default, **pista**: el objetivo es que lo aprenda.
2. Se explica con el nivel de su ruta (`forma-de-trabajo`): el porqué del patrón la primera vez, con un ejemplo aplicado a datos o manufactura cuando se pueda.
3. Si pide revisión: lo que está bien, lo que se rompe (con el caso que lo rompe) y una mejora, en ese orden.
4. Nunca se sube una solución copiada de otra persona o de un repo de respuestas.

## Qué se prueba

| Tipo | Prueba |
|---|---|
| Página (HTML/CSS/JS) | Las historias de usuario del curso, una por una; consola sin errores; celular a 375 px |
| JS con lógica | `node --test` o el runner del curso |
| Ruby | `rspec` con los specs del proyecto |
| Python / SQL | El caso del enunciado y un caso borde (vacío, nulo, duplicado) |

La evidencia va en `.agentes-estado/pruebas-<Proyecto>.md` (ignorada por git).

## README del proyecto

Qué pedía el curso (con link al enunciado), qué se hizo, qué se aprendió en 2–3 bullets y cómo se corre. Es lo que se ve en el portafolio.
