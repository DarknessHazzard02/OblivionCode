---
name: estandar-hazzard
description: Índice del estándar de Haz - reglas base (al grano, cierre "Lo que tienes que hacer", credenciales, datos, avisar y parar, sin firma de IA), firma "Made by: Hazzard", flujo de 4 pasos antes del commit, push, candado de git y qué skills, agentes, comandos y hooks existen en este repo y para qué agente. Úsala al empezar cualquier trabajo en un repo de Haz, al crear un proyecto en Main_Dev_Projects o un snippet en Dev_Coding, y cuando se pregunte "qué reglas aplican", "qué skills tengo", "cómo firmo", "qué hooks hay" o "cómo instalo los agentes".
---

# Estándar de Haz

Un solo estándar, para todo lo que vive en este repo. Lo único que viene de experiencia laboral entra **ofuscado** (skill `ofuscar-de-trabajo`).

## 1. Reglas base

| Tema | Regla |
|---|---|
| Respuesta | Al grano; cierre con `Lo que tienes que hacer` (dónde, qué se ve bien, cómo falla en silencio). Ver `forma-de-trabajo` |
| Método | CORE en 2–4 líneas antes de código; CTCO para prompts vagos. Ver `core-kpis` |
| Credenciales | Nunca en código, notebooks, parámetros, commits, PRs, documentos ni chat. Si una se filtra: **rotar primero**, limpiar después |
| Datos | Ningún dato real en git. Toda carpeta de datos lleva `CONTRATO.md`; sin contrato se asumen reales. Ver `datos-semi-ficticios` |
| Avisar y parar | Antes de: exportar volúmenes grandes, mover datos a servicios externos, borrar en masa, instalar software no confiable, desactivar un control, automatizar contra un sistema con sesión iniciada. Se dice qué lo dispara, por qué, la alternativa, y **no se sigue sin un sí** |
| Bloqueos | Si un control bloquea algo, no se le busca la vuelta (`--no-verify`, `git add -f`, apagar hooks) |
| Firma | `Made by: Hazzard` por lenguaje (tabla en `estandares-codigo`). Nunca firmas de IA |
| Commits | En español, imperativo y con el qué: `Inventory_Coverage_ETL: valida esquema de entrada` |
| Push | Directo a `main`, **lo hace Haz a mano**. El agente no hace push a `main` (hook `bloquear-push-main`) |

## 2. Flujo de 4 pasos antes del commit

| Paso | Skill | Agente | Qué deja |
|---|---|---|---|
| 1. PRD | `entrevista-prd` → `escribir-prd` | — | `docs/PRD.md` con criterios verificables |
| 2. Revisión del diff | `revisar-antes-de-commit` | `revisor-seguridad` + `revisor-codigo` | Sello `revision.json` (solo hallazgos ≥ 80) |
| 3. Prueba en navegador | `probar-tablero` (si toca un tablero) | — | Sello `pruebas.json` con evidencia |
| 4. Auditoría | `auditar-entrega` (al cerrar) | `auditor` | PASA / FALLA / SIN EVIDENCIA por criterio |

Orden: `git add` → revisión → prueba → `git commit` en un comando aparte. Los sellos viven en `.agentes-estado/` (ignorada por git) y los escribe `python agents/_comun/flujo/sellar.py`. Los commits solo de documentación no piden sello.

## 3. Estructura del repo

```
agents/
  claude/    copilot/    codex/    gemini/    chatgpt-gpt/   ← una carpeta independiente por agente
  _comun/
    candado/    candado de git (lo corre git, no un agente)
    flujo/      sellar.py y exigir_antes_de_commit.py
    plantillas/ tablero, ETL, notebook, código, documentos, VS Code
Dev_Coding/<Lenguaje>/          snippets, uno por archivo, firmados
Main_Dev_Projects/<Proyecto>/   README.md, docs/PRD.md, data/CONTRATO.md, demo/source/
```

Cada carpeta de agente trae `instalar.ps1`, que copia su contenido a la ruta que ese agente lee (`.claude/`, `.github/`, `.agents/`, `AGENTS.md`, `GEMINI.md`). Lo instalado está en `.gitignore`: **se edita en `agents/<agente>/`**, nunca en la copia instalada.

## 4. Catálogo

| Grupo | Skills |
|---|---|
| Base | `estandar-hazzard`, `forma-de-trabajo`, `estandares-codigo`, `core-kpis` |
| Tableros | `tablero-estandar`, `tablero-celular`, `formato-textos`, `probar-tablero` |
| Datos y ETL | `etl-python`, `delta-lakehouse`, `parser-alv-sap`, `datos-semi-ficticios`, `ofuscar-de-trabajo` |
| Apps | `flask-app`, `sql-schema-app`, `seguridad-web` |
| Proyecto | `nuevo-proyecto`, `proyecto-aprendizaje`, `validar-entregable`, `candado-personal` |
| Flujo | `entrevista-prd`, `escribir-prd`, `revisar-antes-de-commit`, `auditar-entrega` |
| Portafolio (de experiencia laboral, ofuscado) | `sap-fabric-ingesta`, `entregar-por-pr`, `preview-local`, `catalogo-fuentes` |

Agentes: `revisor-seguridad`, `revisor-codigo`, `auditor`, `explorador-funcional`, `verificador-hallazgos`.
Comandos: `macro-vba`, `pasos-power-query`, `consulta-oracle`, `definir-kpi`, `validar-datos`, `verde-pero-mal`, `aplicar-core`, `revisar-tablero`.

## 5. Qué soporta cada agente

| Pieza | Claude Code | Codex | Copilot | Gemini / Antigravity |
|---|---|---|---|---|
| Instrucciones | `CLAUDE.md` | `AGENTS.md` | `.github/copilot-instructions.md` + `instructions/` | `GEMINI.md` + `.agents/rules/` |
| Skills | `.claude/skills/` | `.agents/skills/` | `.github/skills/` | `.agents/skills/` |
| Comandos | skills con `/` | skills con `$` | `.github/prompts/` | `.agents/workflows/` |
| Subagentes | `.claude/agents/` | instrucción en `AGENTS.md` | `.github/agents/` | instrucción en `GEMINI.md` |
| Hooks del agente | `settings.json` (completos) | — (solo el candado de git) | `.github/hooks/` | `.gemini/settings.json` |

El **candado de git** corre igual para los cuatro: es la única protección que no depende del agente.
