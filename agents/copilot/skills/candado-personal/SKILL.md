---
name: candado-personal
description: Candado de git (pre-commit y commit-msg) para los repos de Haz - detiene secretos, datos reales sin CONTRATO.md, data_real/, config.local.json, archivos de más de 10 MB, material de la organización y firmas de IA en el mensaje; avisa de código sin la firma personal. Úsala SIEMPRE que se instale, revise, ajuste o quite el candado, cuando un commit en un repo personal se detenga con "CANDADO PERSONAL", cuando haya que permitir un archivo a propósito (.candado-permitidos), al clonar un repo personal en otra máquina, y cuando se pregunte por seguridad, secretos o datos en los repos personales.
---

# Candado personal

Lo corre **git**, en cada commit, sin depender del agente (Claude, Codex, Copilot o Gemini). El script
vive en `agents/_comun/candado/` del repo, fuera de la carpeta de cualquier agente.

## Qué hace

| Revisa | Decisión | Ejemplos |
|---|---|---|
| Secretos | **detiene** | llave privada, `ghp_…`, `AKIA…`, `xox…`, `Bearer …`, `AccountKey=`, `sig=`, `Password=` en cadena de conexión, `API_KEY = "…"`; archivos `.env`, `.pem`, `.pfx`, `.key`, `id_rsa` |
| Datos reales | **detiene** | Excel, CSV, parquet, bases de datos, comprimidos o JSON en `data/` **sin** `CONTRATO.md` en su carpeta o arriba; todo `data_real/` y `config.local.json` |
| Tamaño | **detiene** > 10 MB · avisa > 2 MB | |
| Material de la organización | **detiene** | los patrones `prohibido` de un archivo privado **fuera del repo** (variable `CANDADO_REGLAS`; si no, `~/.claude/hooks/copiar_skills_reglas.json`), sobre las líneas agregadas. Sin ese archivo se avisa y no se revisa |
| Mensaje del commit | **detiene** | `Co-Authored-By` de un asistente, "Generated with …" |
| Firma personal | **avisa** | código nuevo o modificado sin `Made by: Hazzard` / `Author: Haz` / `Updated by Haz` (no revisa carpetas de agentes, `demo/`, `data/`, `shared/`, `vendor/`) |

- En un archivo modificado revisa **solo las líneas agregadas**: lo que ya estaba no detiene un commit nuevo.

### Modo del repo (`.candado-modo` en la raíz)

| Modo | Repo | Diferencia |
|---|---|---|
| `personal` (default) | todo repo de Haz | todo lo de arriba |
| `hibrido` | un repo que mezcla código ajeno sin firma | **no** revisa material de la organización ni avisa de firma; secretos, datos sin contrato, tamaño y firma de IA se revisan igual |

Primer renglón del archivo: `personal` o `hibrido`, con un comentario opcional después de `#`.
- Los marcadores no cuentan como secreto (`"<tu-contraseña>"`, `changeme`, `xxx`, `Password=;`).

### Con el hook del asistente

En los commits que hace el asistente, antes del candado corre `exigir_antes_de_commit.py` (hook de la
sesión de Claude; en los otros agentes, la instrucción de la skill `revisar-antes-de-commit`): pide los sellos de revisión y de prueba. No se pisan:

| Orden | Quién | Revisa | Cuándo corre |
|---|---|---|---|
| 1 | hook del asistente | que el diff en stage se revisó y que el tablero tocado se probó | solo en commits del asistente |
| 2 | este candado (git) | secretos, datos, tamaño, material de la organización, firma | en **todo** commit, también los hechos a mano |

Pasar el hook no salta el candado, y el candado no reemplaza la revisión: uno ve calidad y el otro, fugas.

## Instalar

```bash
python agents/_comun/candado/instalar.py
```

Escribe `pre-commit` y `commit-msg` en `.git/hooks` del repo. Si ya había un hook que no es el candado,
lo respalda como `<hook>.antes-del-candado`. El wrapper llama `agents/_comun/candado/candado_personal.py`
del propio repo; para otro repo: `instalar.py <ruta>` (ese repo necesita su copia de `agents/_comun/`).

`.git/hooks` no viaja con el repo: **en cada máquina se instala una vez**.

## Probar

```bash
python agents/_comun/candado/candado_personal.py --self-test
```

23 casos en un repo temporal; ninguno toca los repos reales.

## Cuando detiene un commit

1. Lee qué archivo y por qué.
2. Si no debía entrar: `git restore --staged <archivo>` y agrégalo a `.gitignore`.
3. Si son datos inventados: un `CONTRATO.md` en esa carpeta que lo diga.
4. Si de verdad debe entrar, una excepción con su motivo en `.candado-permitidos` (raíz del repo):

```
Dev_Coding/SQL/ejemplos/*.csv   # salida de ejemplo, sin datos de la organización
```

Sin motivo, la excepción no cuenta. Saltarse el candado (`--no-verify`) lo decide Haz, a mano; el asistente
no lo hace (el hook `proteger-secretos` se lo impide).

## Quitar

```bash
python agents/_comun/candado/instalar.py --quitar
```

Quita solo lo que instaló y devuelve el respaldo si lo había.
