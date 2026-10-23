---
name: entrevista-prd-personal
description: Entrevista a Haz sobre una idea, tablero, ETL o cambio de los repos personales (BI_DataNexus, OblivionCode) hasta que no quede ninguna decisión abierta - una pregunta a la vez, en rondas según qué depende de qué, y con desacuerdo cuando algo no cuadra. No escribe archivos; al terminar se pasa a escribir-prd-personal. Úsala SIEMPRE que se diga "entrevístame", "grill me", "hazme preguntas antes", "quiero armar un PRD", "tengo una idea de tablero" o "antes de empezar pregúntame", y al iniciar un proyecto nuevo en Main_Dev_Projects antes de nuevo-proyecto. No es para trabajo de la empresa.
---

# Entrevista para PRD

Basada en `grill-me` (mattpocock/skills), en español y para los proyectos de este repo.
El objetivo es **llegar a decisiones que Haz pueda defender**, no producir un plan rápido.

## Cómo se hace

1. **Una pregunta por mensaje.** Con `AskUserQuestion` cuando la respuesta cabe en 2-4 opciones;
   la recomendada va primero con "(Recomendada)". Si no cabe, pregunta abierta en una línea.
2. **Por rondas, según dependencias.** Solo se pregunta lo que ya se puede contestar con lo resuelto.
   Orden típico: para qué y para quién → fuente de datos → qué se mide (fórmula) → pantallas →
   qué queda fuera → cómo se sabe que está terminado.
3. **Antes de preguntar, busca.** Si el repo ya contesta (un `CONTRATO.md`, un `meta.json`, un
   tablero parecido), no se pregunta: se dice lo que se encontró y se pide confirmar.
4. **Discrepa.** Si una respuesta choca con otra o con el estándar (`dashboard-standards`,
   `haz-estandares-codigo`), dilo y propón la alternativa. "Sí a todo" da un plan que nadie decidió.
5. **"No sé" es respuesta válida.** Se anota como pendiente con quién lo resuelve; no se inventa.
6. **Si hace falta verlo para decidir** (cómo se siente un filtro, cómo luce una gráfica), propón
   un prototipo desechable y vuelve a la entrevista.

## Cuándo para

- No quedan ramas abiertas, **o**
- Van más de ~15 preguntas: el alcance es grande. Propón partirlo en fases y entrevistar solo la primera.

## No usar en modo plan

El modo plan empuja a cerrar con un plan y corta la entrevista. Si está activo, avísalo y sigue
preguntando; el plan va después, con `escribir-prd-personal`.

## Al cerrar

Resume en una tabla `Tema | Decisión | Pendiente (quién)` y ofrece `escribir-prd-personal`. No escribe
ningún archivo por sí misma.
