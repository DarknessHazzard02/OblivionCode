---
name: revisar-antes-de-commit-personal
description: Revisión de seguridad y de código del diff en stage antes de un commit en los repos personales (BI_DataNexus, OblivionCode) - lanza en paralelo los agentes revisor-seguridad-personal y revisor-codigo-personal, junta solo hallazgos con confianza de 80 o más, y si no hay bloqueantes sella la revisión para que el commit pase. Úsala SIEMPRE antes de un git commit en un repo personal, cuando el hook exigir_antes_de_commit niegue un commit por falta de revisión, o cuando se pida "revisa antes de commitear", "revisa el diff" o "revisa lo que voy a subir". También sirve sobre archivos completos (modo archivos) para validar un tablero o un proyecto que no tiene diff. No reemplaza al revisor-seguridad del equipo en repos de la empresa.
---

# Revisar antes de commit

Junta dos ideas: `claude-code-security-review` (categorías de vulnerabilidad y filtro de falsos
positivos) y el plugin `code-review` (pasadas en paralelo, solo hallazgos con confianza ≥ 80).

## 1. Qué se revisa

| Modo | Entrada | Cuándo |
|---|---|---|
| `stage` (default) | `git diff --cached` + los archivos completos que toca | antes de commit |
| `archivos` | una lista de archivos o carpetas, completos | validar algo que no tiene diff (un tablero ya hecho, una copia sin git) |

**Se salta** (y se dice) si el stage es solo `.md`, `.txt`, imágenes o `.pdf` **fuera de `.claude/`**, salvo `CLAUDE.md`, `SKILL.md`, `REGLAS-EQUIPO.md`, `requirements*.txt` y lo
que esté bajo `skills/` o `agents/` (la regla es `sellar.es_solo_doc`): no hay código que revisar. Lo de `.claude/` (skills, agentes) sí se revisa: son instrucciones del asistente.
Si el diff tiene menos de 50 líneas, A2 hace una sola pasada en vez de tres.

## 2. Lanzar los dos agentes en paralelo

En **un solo mensaje**, dos llamadas a `Agent`:

- `subagent_type: revisor-seguridad-personal`
- `subagent_type: revisor-codigo-personal`

Prompt de cada uno: modo, ruta del repo, lista de archivos y —en `stage`— el diff completo pegado.
No se les pasa la conversación: revisan lo que hay, no lo que se quiso hacer.
Si el agente no aparece (sesión vieja), usa `general-purpose` con el cuerpo de
`.claude/agents/<agente>.md` como prompt.

## 3. Juntar

Tabla única, de más grave a menos:

| # | Agente | Gravedad | Confianza | Archivo:línea | Hallazgo | Arreglo propuesto |

- Se descarta lo que tenga confianza < 80.
- Se descarta lo que esté en `.claude/revision/falsos_positivos.md` (si existe), y se dice cuántos.
- **Bloqueante** = gravedad Alta en seguridad, o un bug que rompe lo que el commit dice hacer.

## 4. Sellar

Solo en modo `stage` y **solo si no hay bloqueantes**:

```bash
python .claude/hooks/sellar.py revision --reporte .claude/estado/revision.md
```

Antes guarda la tabla en `.claude/estado/revision.md`. Si hay bloqueantes, **no se sella**: se
arreglan, se vuelve a hacer `git add` y se revisa otra vez (el sello es del diff exacto).

## 5. Si un falso positivo bloquea

No se sella "para que pase". Se le dice a Haz cuál es; si confirma que es falso positivo, se anota
en `.claude/revision/falsos_positivos.md` con fecha, patrón y motivo, y se vuelve a correr.
El commit manual en su terminal siempre está disponible: el hook es solo del asistente.

## 6. Orden con el hook y el candado

`git add` → esta skill (sella) → `probar-tablero-personal` si el stage toca un tablero (sella) → `git commit -m`
**en un comando aparte**. El hook niega `git add … && git commit`, `-a`, `-i`, `-o`, `-p` y rutas sueltas:
todos commitean algo distinto del stage sellado.
El hook `exigir_antes_de_commit.py` compara los sellos con el stage **antes** de que corra git; luego
el `candado-personal` revisa secretos y datos. Si cambias algo después de sellar, el sello ya no vale:
`git add` otra vez y se vuelve a revisar. `python .claude/hooks/sellar.py estado` dice qué sigue valiendo.
