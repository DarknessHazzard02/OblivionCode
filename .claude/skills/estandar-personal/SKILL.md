---
name: estandar-personal
description: Índice del estándar de Haz para sus repos personales (BI_DataNexus, OblivionCode) - qué cambia frente al estándar laboral (firma "Made by Hazzard" en cada lenguaje, quién autoriza, push, candado), qué skills y hooks viven en el repo, cómo se estructura un repo y un proyecto, qué datos pueden entrar y qué skills conviene crear después. Úsala al empezar cualquier trabajo en un repo con remote HazielA-Dev o DarknessHazzard02, al crear un proyecto nuevo en Main_Dev_Projects o un snippet en Dev_Coding, cuando haya duda de si algo es personal o laboral, y cuando se pregunte "estándar personal", "qué skills tengo en el repo", "cómo firmo" o "qué hooks suben al repo".
---

# Estándar Personal

Para los repos de Haz: **BI_DataNexus** (`HazielA-Dev`) y **OblivionCode** (`DarknessHazzard02`).
Si el trabajo es de la empresa, aplica el estándar laboral, no este.

## Cómo se reconoce

`git remote -v` → `HazielA-Dev/*` o `DarknessHazzard02/*`. Sin remote o en duda: **no** es personal.

## Qué cambia frente al estándar laboral

| | Laboral | Personal |
|---|---|---|
| Firma en el código | nunca | **sí**, con la tabla de abajo |
| Quién autoriza excepciones | quien lleve el estándar laboral | **Haz** |
| Push a `main` | solo por PR | directo a `main` permitido; lo hace Haz (el hook local de la sesión bloquea al asistente) |
| Candado de git | el del equipo | el del equipo excluido (`includeIf` → `~/.gitconfig-personal`); en su lugar, `candado-personal` en `.git/hooks` |
| Formato de respuesta | corto, con cierre obligatorio | según `haz-forma-de-trabajo` |
| Firma de IA (`Co-Authored-By`, "Generated with") | nunca | **tampoco**: el trabajo sale a nombre de Haz |

Lo que **no** cambia, aunque el repo sea personal:

- **Datos de la empresa: nunca reales.** Un repo personal en GitHub es un destino personal. Se usan datos
  inventados o **semi-ficticios** (forma real, identidades inventadas, validados valor por valor contra el
  real); los reales se quedan en `data_real/`, ignorada por git.
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
  .claude/hooks/         hooks que se pueden compartir (ver abajo)
  Dev_Coding/<Lenguaje>/ snippets y consultas sueltas, uno por archivo, con su firma
  Main_Dev_Projects/<Proyecto>/
    README.md            qué es, de dónde lee, cómo se corre, avisos
    .gitignore           data_real/, config.local.json, *.csv/*.xlsx salvo demo/
    data/CONTRATO.md     dice que los datos son inventados o semi-ficticios
    demo/source/         fuentes inventadas o semi-ficticias, con la forma de las reales
```

- **Las skills se editan en `~/.claude/skills`, nunca en la copia del repo:** el hook la sobreescribe.
- Commits en español, en imperativo y con el qué: `Y_Meadows: tablero de control de órdenes`.

## Skills que viven en el repo

| Skill | Origen | Uso personal |
|---|---|---|
| `haz-estandares-codigo`, `haz-forma-de-trabajo`, `haz-core-sop` | personales | tal cual |
| `formato-textos` | personal | tal cual |
| `candado-personal` | personal | candado de git de estos repos |
| `estandar-personal` | personal | este índice |
| `dashboard-standards`, `entregar-tablero`, `portal-local`, `portal-seguridad`, `validar-antes-de-entregar` | estándar laboral, genéricas | el método de tableros sirve igual; donde dice "quien autoriza", es Haz |
| `fabric-sap-ingesta`, `sap-catalogo-fuentes`, `apps-estandar`, `apps-base-datos` | estándar laboral, genéricas | referencia de método; los IDs y rutas son marcadores (`<GUID>`, `<lakehouse>`) |

`estandar-laboral` **no** está aquí a propósito: nombra personas y sistemas de la empresa.

## Hooks

| Hook | ¿En el repo? | Qué hace |
|---|---|---|
| `copiar_skills.py` | **sí**, `.claude/hooks/` | PostToolUse: al crear o editar una skill en `~/.claude/skills`, la copia limpia a BI_DataNexus y OblivionCode; si queda algo que no debe salir, no copia y dice qué línea |
| `copiar_skills_reglas.json` | **no** | sus reglas de limpieza; nombran justo lo que hay que quitar. En el repo va `copiar_skills_reglas.ejemplo.json` con la forma |
| `candado-personal` (pre-commit y commit-msg) | **sí**, en la skill `candado-personal` | git, en cada commit: detiene secretos, datos reales sin `CONTRATO.md`, `data_real/`, archivos de más de 10 MB, material de la empresa y firmas de IA en el mensaje; avisa de código sin firma. Se instala por máquina con `instalar.py` |
| hooks del estándar laboral | **no** | se quedan en la máquina |

Instalarlo en otra máquina: copiar los dos archivos a `~/.claude/hooks/`, renombrar el ejemplo a
`copiar_skills_reglas.json`, llenarlo, y agregar en `~/.claude/settings.json`:

```json
"PostToolUse": [{ "matcher": "Write|Edit|MultiEdit",
  "hooks": [{ "type": "command", "command": "python", "args": ["-I", "~/.claude/hooks/copiar_skills.py"] }] }]
```

## Skills que conviene crear después

| Skill sugerida | Por qué | Base |
|---|---|---|
| `datos-semi-ficticios` | el método ya existe en `Main_Dev_Projects/_semi/`; como skill se reusa en cualquier proyecto nuevo | `seudonimo.py` y los `generar_semi.py` |
| `nuevo-proyecto` | arma `Main_Dev_Projects/<Proyecto>/` con README, `.gitignore`, `data/CONTRATO.md`, `demo/`, `config.local.json` de ejemplo y la firma | la estructura de arriba |
| `dev-coding-snippets` | cómo se guarda un snippet en `Dev_Coding/<Lenguaje>/`: nombre, encabezado, firma, versión original vs modificada | las carpetas por lenguaje que ya existen |
| `oracle-ebs-sql` | las consultas de EBS y Blitz Report tienen reglas propias (`ORA-24374`, sin `;`, alias, CTEs); hoy viven dentro de `haz-estandares-codigo` | `Dev_Coding/SQL` |
| `vba-excel` | patrones de macros (banners, `ListObject`, restaurar `Application`, manejo de errores) con plantillas | `Dev_Coding/VBA` |
