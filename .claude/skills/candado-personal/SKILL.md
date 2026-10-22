---
name: candado-personal
description: Candado de git (pre-commit y commit-msg) para los repos personales de Haz (BI_DataNexus, OblivionCode), que no tienen el candado del equipo - detiene secretos, datos reales sin CONTRATO.md, data_real/, config.local.json, archivos de más de 10 MB, material de la empresa y firmas de IA en el mensaje; avisa de código sin la firma personal. Úsala SIEMPRE que se instale, revise, ajuste o quite el candado, cuando un commit en un repo personal se detenga con "CANDADO PERSONAL", cuando haya que permitir un archivo a propósito (.candado-permitidos), al clonar un repo personal en otra máquina, y cuando se pregunte por seguridad, secretos o datos en los repos personales.
---

# Candado personal

Los repos personales están fuera del candado del equipo (`includeIf` → `~/.gitconfig-personal`, hooks en
`.git/hooks`). Este candado cubre ese hueco: lo corre **git**, en cada commit, sin depender de la sesión.

## Qué hace

| Revisa | Decisión | Ejemplos |
|---|---|---|
| Secretos | **detiene** | llave privada, `ghp_…`, `AKIA…`, `xox…`, `Bearer …`, `AccountKey=`, `sig=`, `Password=` en cadena de conexión, `API_KEY = "…"`; archivos `.env`, `.pem`, `.pfx`, `.key`, `id_rsa` |
| Datos reales | **detiene** | Excel, CSV, parquet, bases de datos, comprimidos o JSON en `data/` **sin** `CONTRATO.md` en su carpeta o arriba; todo `data_real/` y `config.local.json` |
| Tamaño | **detiene** > 10 MB · avisa > 2 MB | |
| Material de la empresa | **detiene** | los patrones `prohibido` del archivo privado del hook de copia (`~/.claude/hooks/copiar_skills_reglas.json`), sobre las líneas agregadas. Sin ese archivo (otra máquina) se avisa y no se revisa |
| Mensaje del commit | **detiene** | `Co-Authored-By` de un asistente, "Generated with …" |
| Firma personal | **avisa** | código nuevo o modificado sin `Made by: Hazzard` / `Author: Haz` / `Updated by Haz` (no revisa `.claude/`, `demo/`, `data/`, `shared/`, `vendor/`) |

- En un archivo modificado revisa **solo las líneas agregadas**: lo que ya estaba no detiene un commit nuevo.

### Modo del repo (`.candado-modo` en la raíz)

| Modo | Repo | Diferencia |
|---|---|---|
| `personal` (default) | OblivionCode | todo lo de arriba |
| `hibrido` | BI_DataNexus | **no** revisa material de la empresa ni avisa de firma (ahí vive trabajo, que va sin firma); secretos, datos sin contrato, tamaño y firma de IA se revisan igual |

Primer renglón del archivo: `personal` o `hibrido`, con un comentario opcional después de `#`.
- Los marcadores no cuentan como secreto (`"<tu-contraseña>"`, `changeme`, `xxx`, `Password=;`).

## Instalar

```bash
python ~/.claude/skills/candado-personal/scripts/instalar.py
```

Escribe `pre-commit` y `commit-msg` en `.git/hooks` de BI_DataNexus y OblivionCode. Si ya había un hook que
no es el candado, lo respalda como `<hook>.antes-del-candado`. El wrapper busca el script en
`~/.claude/skills` y, si no está, en la copia del repo (`.claude/skills/candado-personal`): en un clon nuevo
basta con correr el instalador apuntando al repo (`instalar.py <ruta>`).

`.git/hooks` no viaja con el repo: **en cada máquina se instala una vez**.

## Probar

```bash
python ~/.claude/skills/candado-personal/scripts/candado_personal.py --self-test
```

21 casos en un repo temporal; ninguno toca los repos reales.

## Cuando detiene un commit

1. Lee qué archivo y por qué.
2. Si no debía entrar: `git restore --staged <archivo>` y agrégalo a `.gitignore`.
3. Si son datos inventados: un `CONTRATO.md` en esa carpeta que lo diga.
4. Si de verdad debe entrar, una excepción con su motivo en `.candado-permitidos` (raíz del repo):

```
Dev_Coding/SQL/ejemplos/*.csv   # salida de ejemplo, sin datos de la empresa
```

Sin motivo, la excepción no cuenta. Saltarse el candado (`--no-verify`) lo decide Haz, a mano; el asistente
no lo hace (el hook de la sesión se lo impide).

## Quitar

```bash
python ~/.claude/skills/candado-personal/scripts/instalar.py --quitar
```

Quita solo lo que instaló y devuelve el respaldo si lo había.
