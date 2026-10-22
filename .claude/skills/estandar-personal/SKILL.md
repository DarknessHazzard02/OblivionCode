---
name: estandar-personal
description: Índice del estándar de Haz para sus repos personales (BI_DataNexus, OblivionCode) - qué cambia frente al estándar laboral (firma "Made by Hazzard" en cada lenguaje, quién autoriza, push, candado), qué skills y hooks viven en el repo, cómo se estructura un repo y un proyecto, qué datos pueden entrar y qué skills conviene crear después. Úsala al empezar cualquier trabajo en un repo con remote HazielA-Dev o DarknessHazzard02, al crear un proyecto nuevo en Main_Dev_Projects o un snippet en Dev_Coding, cuando haya duda de si algo es personal o laboral, y cuando se pregunte "estándar personal", "qué skills tengo en el repo", "cómo firmo" o "qué hooks suben al repo".
---

# Estándar Personal

Para los repos de Haz: **BI_DataNexus** (`HazielA-Dev`) y **OblivionCode** (`DarknessHazzard02`).
Si el trabajo es de la empresa, aplica el estándar laboral, no este.

## Cómo se reconoce: tres tipos de repo

| Repo | Tipo | Qué guarda | Qué estándar manda |
|---|---|---|---|
| **OblivionCode** (`DarknessHazzard02`) | **personal** | solo lo personal: nada de la empresa (ni rutas, ni nombres, ni datos) | este, completo |
| **BI_DataNexus** (`HazielA-Dev`) | **híbrido** | proyectos de trabajo **y** skills y notas personales | en lo de trabajo, el laboral (sin firma, reglas de datos del equipo); en lo personal (`.claude/`, `Dev_Coding/`, notas), este |
| repos del equipo (organización de la empresa) | laboral | solo trabajo | el laboral |

**Lo que se publica sigue al destino, no al origen:**
- hacia un repo o portal del equipo → **estrictamente laboral**: sin firma personal, sin notas personales, sin
  mención de los repos personales;
- hacia OblivionCode → **solamente personal**: nada de la empresa, aunque venga de BI_DataNexus.

El tipo de cada repo vive en `.candado-modo` (raíz del repo: `personal` o `hibrido`), que lee el
`candado-personal`. Sin remote o en duda: **no** es personal.

## Qué cambia frente al estándar laboral

| | Laboral | Personal |
|---|---|---|
| Firma en el código | nunca | **sí**, con la tabla de abajo (en BI_DataNexus, solo en lo personal) |
| Quién autoriza excepciones | quien lleve el estándar laboral | **Haz** |
| Push a `main` | solo por PR | directo a `main` permitido; lo hace Haz (el hook local de la sesión bloquea al asistente) |
| Candado de git | el del equipo | el del equipo excluido (`includeIf` → `~/.gitconfig-personal`); en su lugar, `candado-personal` en `.git/hooks` |
| Formato de respuesta | corto, con cierre obligatorio | según `haz-forma-de-trabajo` |
| Firma de IA (`Co-Authored-By`, "Generated with") | nunca | **tampoco**: el trabajo sale a nombre de Haz |

Lo que **no** cambia, en ningún tipo de repo:

- **Datos de la empresa: nunca reales en git.** Se usan datos inventados o **semi-ficticios** (forma real,
  identidades inventadas, validados valor por valor contra el real); los reales se quedan en `data_real/`,
  `Output/` o la carpeta de `config.local.json`, ignoradas por git. Una salida de un ETL sobre datos reales
  **nunca** se versiona.
- **Credenciales: nunca** en código, commits ni chat.
- Nada del repo personal en mensajes o reportes de trabajo.

## La firma

| Lenguaje | Firma | Dónde |
|---|---|---|
| VBA | `'Made by: Hazzard` | **última** línea, después de `End Sub` |
| Power Query (M) | `// Made by: Hazzard` + una línea de descripción | primera línea |
| Python | banner con `# Author: Haz` | encabezado |
| SQL | `-- Made by: Hazzard` | primera línea; en Oracle **dentro** de la consulta, después del `SELECT`/`WITH` (`ORA-24374`) |
| DAX | `// Made by: Hazzard` | antes de la primera `VAR` |
| JS / TS / C# / Java | `// Made by: Hazzard` | primera línea, después de lo que el lenguaje exija arriba |
| CSS | `/* Made by: Hazzard */` | primera línea |
| HTML | `<!-- Made by: Hazzard -->` | después de `<!DOCTYPE html>` |
| YAML / Bash / PowerShell | `# Made by: Hazzard` | primera línea, después del shebang |
| JSON | — | no admite comentarios |

Código ajeno: la firma original se queda y se agrega `Updated by Haz`. Detalle en `haz-estandares-codigo`.

## Estructura de los repos

```
<repo>/
  .claude/skills/        copias limpias de las skills (las pone el hook; no se editan aquí)
                         + las 5 del flujo de 4 pasos, que viven solo aquí (ver abajo)
  .claude/agents/        revisor-seguridad-personal, revisor-codigo-personal, auditor
  .claude/hooks/         hooks que se pueden compartir (ver abajo)
  .claude/settings.json  registra exigir_antes_de_commit.py (solo para sesiones en este repo)
  .claude/launch.json    servidores para probar tableros (tableros, portal-local)
  .claude/estado/        sellos y evidencia de revisión y pruebas; ignorada por git
  Dev_Coding/<Lenguaje>/ snippets y consultas sueltas, uno por archivo, con su firma
  Main_Dev_Projects/<Proyecto>/
    README.md            qué es, de dónde lee, cómo se corre, avisos
    docs/PRD.md          objetivo, KPIs, criterios de aceptación (escribir-prd); lo lee el auditor
    .gitignore           data_real/, config.local.json, *.csv/*.xlsx salvo demo/
    data/CONTRATO.md     dice que los datos son inventados o semi-ficticios
    demo/source/         fuentes inventadas o semi-ficticias, con la forma de las reales
```

- **Las skills se editan en `~/.claude/skills`, nunca en la copia del repo:** el hook la sobreescribe.
  **Excepción:** las piezas del flujo de 4 pasos (skills, agentes y hooks de abajo) viven solo en los
  repos. Se editan en BI_DataNexus y se espejan a OblivionCode con
  `python .claude/hooks/sincronizar_repo.py` (`--revisar` para ver qué difiere).
- Commits en español, en imperativo y con el qué: `Y_Meadows: tablero de control de órdenes`.

## Skills que viven en el repo

| Skill | Origen | Uso personal |
|---|---|---|
| `haz-estandares-codigo`, `haz-forma-de-trabajo`, `haz-core-sop` | personales | tal cual |
| `formato-textos` | personal | tal cual |
| `candado-personal` | personal | candado de git de estos repos |
| `nuevo-proyecto` | personal | arma un proyecto en `Main_Dev_Projects` (tablero, ETL o notebook) con esta estructura |
| `estandar-personal` | personal | este índice |
| `dashboard-standards`, `entregar-tablero`, `portal-local`, `portal-seguridad`, `validar-antes-de-entregar` | estándar laboral, genéricas | el método de tableros sirve igual; donde dice "quien autoriza", es Haz |
| `fabric-sap-ingesta`, `sap-catalogo-fuentes`, `apps-estandar`, `apps-base-datos` | estándar laboral, genéricas | referencia de método; los IDs y rutas son marcadores (`<GUID>`, `<lakehouse>`) |

`estandar-laboral` **no** está aquí a propósito: nombra personas y sistemas de la empresa.

## Flujo de 4 pasos (solo en los repos)

| Paso | Skill | Agente | Qué deja |
|---|---|---|---|
| 1. PRD | `entrevista-prd` → `escribir-prd` | — | `docs/PRD.md` con criterios de aceptación |
| 2. Revisión | `revisar-antes-de-commit` | `revisor-seguridad-personal` + `revisor-codigo-personal` en paralelo | sello `revision.json` del diff en stage |
| 3. Auditor | `auditar-entrega` | `auditor` (Sonnet, sin la conversación) | PASA / FALLA / SIN EVIDENCIA por criterio |
| 4. Pruebas | `probar-tablero` | — (navegador integrado) | sello `pruebas.json` con la huella del tablero |

Orden de un commit: `git add` → revisión → prueba (si toca un tablero) → `git commit`. El hook
`exigir_antes_de_commit.py` niega el commit del asistente si falta un sello o ya no coincide con el stage.

**Costo** (medido sobre dos tableros completos del portal: revisión 270 k, auditor 88 k,
prueba ~70 k). Sobre un diff normal es bastante menos. Para no gastar de más:
- los commits solo de docs (`.md`, `.txt`, imágenes) no piden nada;
- con un diff de menos de 50 líneas, el revisor de código hace una sola pasada;
- la prueba se exige al commitear un tablero, no en cada turno;
- el auditor se corre al cerrar una entrega, no en cada commit.

## Hooks

| Hook | ¿En el repo? | Qué hace |
|---|---|---|
| `copiar_skills.py` | **sí**, `.claude/hooks/` | PostToolUse: al crear o editar una skill en `~/.claude/skills`, la copia limpia a BI_DataNexus y OblivionCode; si queda algo que no debe salir, no copia y dice qué línea |
| `copiar_skills_reglas.json` | **no** | sus reglas de limpieza; nombran justo lo que hay que quitar. En el repo va `copiar_skills_reglas.ejemplo.json` con la forma |
| `avisar_skills_equipo.py` | **sí**, `.claude/hooks/` (copia genérica) | SessionStart: `git pull` del clon del repo de skills del equipo y aviso de qué skill cambió desde la última marca. **No copia**: las skills locales son copias corregidas y se llevan los cambios a mano (`--marcar <skill>` al terminar). Cada corrida deja `skills_equipo_ultima.json` (fecha, resultado del pull, commit, qué encontró) y `--estado` lo muestra: así se sabe si corrió aunque no haya avisado nada. El clon se apunta con `SKILLS_EQUIPO_CLON` |
| `candado-personal` (pre-commit y commit-msg) | **sí**, en la skill `candado-personal` | git, en cada commit: detiene secretos, datos reales sin `CONTRATO.md`, `data_real/`, archivos de más de 10 MB, material de la empresa y firmas de IA en el mensaje; avisa de código sin firma. Se instala por máquina con `instalar.py` |
| `exigir_antes_de_commit.py` | **sí**, `.claude/hooks/` + `.claude/settings.json` | PreToolUse (Bash/PowerShell): si el asistente hace `git commit` en este repo, pide el sello de revisión del diff en stage y, si toca un tablero, el de prueba. Niega también lo que commitea algo distinto del stage sellado (`git add … && git commit`, `-a`, `-i`, `-o`, `-p`, rutas sueltas) y, si algo truena al revisar un commit de este repo, niega en vez de dejar pasar. Lee `cd`/`Set-Location`, `git -C`, rutas `/c/…`, `bash -c`, prefijos (`VAR=x`, `time`, `if … then`), redirecciones y alias; si dice `git … commit` y no lo puede leer, niega. Sale en la primera línea si el comando no dice commit. El commit a mano en la terminal no pasa por aquí. Pruebas: `--self-test` (57 casos) |
| `sellar.py` | **sí**, `.claude/hooks/` | lo llaman `revisar-antes-de-commit` (`revision`) y `probar-tablero` (`pruebas <carpeta>`); `estado` dice qué sello sigue valiendo |
| `sincronizar_repo.py` | **sí**, `.claude/hooks/` | espeja las piezas del flujo de BI_DataNexus a OblivionCode |
| hooks del estándar laboral | **no** | se quedan en la máquina |

Instalarlo en otra máquina: copiar los dos archivos a `~/.claude/hooks/`, renombrar el ejemplo a
`copiar_skills_reglas.json`, llenarlo, y agregar en `~/.claude/settings.json`:

```json
"PostToolUse": [{ "matcher": "Write|Edit|MultiEdit",
  "hooks": [{ "type": "command", "command": "python", "args": ["-I", "~/.claude/hooks/copiar_skills.py"] }] }]
```

El aviso de skills del equipo: copiar `avisar_skills_equipo.py` a `~/.claude/hooks/`, correr una vez
`python ~/.claude/hooks/avisar_skills_equipo.py --marcar-todo` y agregar:

```json
"SessionStart": [{ "hooks": [{ "type": "command", "command": "python",
  "args": ["-I", "~/.claude/hooks/avisar_skills_equipo.py"], "timeout": 40 }] }]
```

Para ver si corrió: `python ~/.claude/hooks/avisar_skills_equipo.py --estado`.

## Skills que conviene crear después

| Skill sugerida | Por qué | Base |
|---|---|---|
| `datos-semi-ficticios` | el método ya existe en `Main_Dev_Projects/_semi/`; como skill se reusa en cualquier proyecto nuevo | `seudonimo.py` y los `generar_semi.py` |
| `dev-coding-snippets` | cómo se guarda un snippet en `Dev_Coding/<Lenguaje>/`: nombre, encabezado, firma, versión original vs modificada | las carpetas por lenguaje que ya existen |
| `oracle-ebs-sql` | las consultas de EBS y Blitz Report tienen reglas propias (`ORA-24374`, sin `;`, alias, CTEs); hoy viven dentro de `haz-estandares-codigo` | `Dev_Coding/SQL` |
| `vba-excel` | patrones de macros (banners, `ListObject`, restaurar `Application`, manejo de errores) con plantillas | `Dev_Coding/VBA` |
