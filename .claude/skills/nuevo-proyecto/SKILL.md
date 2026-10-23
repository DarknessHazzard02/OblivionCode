---
name: nuevo-proyecto
description: Arma un proyecto nuevo en Main_Dev_Projects de los repos personales de Haz (BI_DataNexus, OblivionCode) con la estructura del estándar personal - tablero (HTML + app.js + datos por contrato), ETL (main.py, config.py, requirements, salida a Output/) o notebook - con firma, README, .gitignore, CONTRATO.md y datos inventados, listo para pasar el candado-personal. Úsala SIEMPRE que se pida crear, empezar, armar o iniciar un proyecto, tablero, dashboard, ETL, script de carga o notebook nuevo en un repo personal, o cuando se diga "nuevo proyecto", "plantilla de proyecto", "esqueleto" o "estructura de Main_Dev_Projects".
---

# Nuevo proyecto

Para repos **personales**. Un proyecto de la empresa sigue el estándar laboral (`entregar-tablero`,
`dashboard-standards`), no esta skill.

## Crear

```bash
python ~/.claude/skills/nuevo-proyecto/scripts/crear_proyecto.py <Nombre> --tipo tablero|etl|notebook
       [--repo BI_DataNexus|OblivionCode] [--descripcion "qué hace"] [--portal logistics|sop]
```

- `<Nombre>` en el estilo de las carpetas que ya hay: letras, números y `_` (`Y_Meadows`, `BOM_Join_Project`).
- Repo por default: BI_DataNexus. **Nunca sobreescribe**: si la carpeta existe, se detiene.
- Pregunta antes de crear: el tipo, el repo y una descripción de una línea. Lo demás tiene default.
- **Antes de crear**, si la idea todavía no está clara, ofrece `entrevista-prd-personal`. Con lo decidido,
  `escribir-prd-personal` llena el `docs/PRD.md` que deja esta skill.

## Qué arma cada tipo

Común a los tres: `README.md` (qué es, archivos, cómo se corre, de dónde salen los datos, pendientes),
`.gitignore` (`data_real/`, `config.local.json`, `Output/`, Excel/CSV/parquet salvo `demo/source/`),
`config.local.ejemplo.json`, `demo/CONTRATO.md` con `datos: inventados` y `docs/PRD.md` (plantilla de
`escribir-prd-personal` en estado borrador). Todo el código va firmado.

| Tipo | Archivos | Se parece a |
|---|---|---|
| `tablero` | `index.html`, `app.js` (lee `meta.json` + `dashboard.json` de `CONFIG.dataUrls`, banda de inventados/semi-ficticios, KPIs, detalle), `estilos.css` y `shared/` copiados de otro tablero, `generar_datos.py` (fuente: argumento → variable → `config.local.json` → `demo/source`; reales a `data_real/`), `generar_demo.py`, `data/CONTRATO.md`, `actualizar.cmd` | los tableros de BI_DataNexus |
| `etl` | `main.py` (lee por prefijo, valida esquema, quita duplicados, exporta parquet y csv, log), `config.py` (rutas desde `config.local.json` o variable de ambiente), `requirements.txt` con versión, `generar_demo.py` | `BOM_Join_Project` de BI_DataNexus |
| `notebook` | `NB_<Nombre>.py` con banners (Parameters → Read → Transform → Export), `demo/source/ejemplo.csv` | los `NB_*` de BI_DataNexus |

Al copiar `estilos.css` de otro tablero, el tema principal se renombra a `corporativo` y se le aplican las
reglas privadas del hook de copia (`copiar_skills_reglas.json`), para que no traiga nada de la empresa.

## Después de crear

1. Reemplazar los `TODO`: archivo de origen, columnas esperadas, **fecha de extracción** (de la fecha del
   nombre del archivo, nunca la de hoy) y el sistema de la fuente.
2. `python generar_demo.py` para tener datos inventados y ver que corre.
3. Si los datos inventados deben parecerse a los reales, usar el método semi-ficticio de
   `Main_Dev_Projects/_semi/` (forma real, identidades inventadas) y validar valor por valor.
4. El tablero crece siguiendo `dashboard-standards` (filtros, cross-filter, export, bilingüe) y el texto
   con `formato-textos`.
5. Llenar `docs/PRD.md` (con `escribir-prd-personal`): sus criterios de aceptación son lo que audita `auditar-entrega-personal`.
6. Commit: `git add` → `revisar-antes-de-commit-personal` → `probar-tablero-personal` (si es tablero; lo sirve
   `.claude/launch.json` → `tablero-<Proyecto>`, que la skill agrega si falta) → `git commit`. El hook `exigir_antes_de_commit` lo pide y el
   `candado-personal` revisa que no entren datos reales ni secretos.

## Cómo se comprobó

Se crearon los tres tipos en un repo real, se corrieron sus `generar_demo.py`, el tablero se abrió en el
navegador con datos y tema, y los tres pasaron el `candado-personal` sin avisos. Después se borraron.
