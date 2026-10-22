#!/usr/bin/env python3
# ===============================================
# Generador de proyectos para Main_Dev_Projects
# Author: Haz
# ===============================================
"""
Arma Main_Dev_Projects/<Nombre>/ con la estructura del estándar personal.

    python crear_proyecto.py <Nombre> --tipo tablero|etl|notebook [--repo BI_DataNexus|OblivionCode]
                             [--descripcion "qué hace"] [--portal logistics|sop]

Tipos:
  tablero   HTML + app.js + estilos.css + shared/, datos por contrato (data/, demo/source/, data_real/)
  etl       main.py + config.py + requirements.txt, salida a Output/ (parquet y csv), log
  notebook  NB_<Nombre>.py con banners por sección, listo para pegar en Fabric o correr local

Todo lleva su firma, su README, su .gitignore (data_real/, config.local.json, salidas) y, si maneja
datos, su CONTRATO.md con `datos: inventados`. No sobreescribe nada: si la carpeta existe, se detiene.
"""
import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

REPOS = Path.home() / 'Documents' / 'GitHub'
HOY = date.today().isoformat()

GITIGNORE = """# Datos reales: nunca al repo. Viven en la carpeta de origen (config.local.json).
/data_real/
/config.local.json
/source/
/Output/
*.csv
!demo/source/**/*.csv
*.xlsx
*.xlsm
*.parquet
*.log
__pycache__/
.venv/
"""

CONTRATO = """# Datos inventados — no son de ningún sistema

datos: inventados

La línea de arriba es la marca que lee el candado de git; sin ella, los archivos de esta carpeta se tratan
como datos reales.

{detalle}

Si aquí aparece un archivo con datos reales, no debe commitearse: los reales van en `data_real/`, que está
en `.gitignore`.
"""

CONFIG_EJEMPLO = '{\n  "source": "C:\\<servidor>\<carpeta>"\n}\n'

# --- tablero --------------------------------------------------------------------------------------------
TAB_GENERAR_DATOS = '''# ===============================================
# {nombre}: arma data/dashboard.json y data/meta.json
# Author: Haz
# ===============================================
# De donde lee (en este orden): argumento -> variable {env} -> config.local.json -> demo/source.
# Con datos reales escribe en data_real/ (ignorada por git); con los demo, en data/.

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DEMO_SOURCE = AQUI / 'demo' / 'source'
ARCHIVO = 'ejemplo.csv'          # TODO: el archivo (o archivos) de la fuente real

def resolve_source():
    if len(sys.argv) > 1:
        return Path(sys.argv[1]), 'argumento'
    if os.environ.get('{env}'):
        return Path(os.environ['{env}']), '{env}'
    config = AQUI / 'config.local.json'
    if config.exists():
        source = json.loads(config.read_text(encoding='utf-8-sig')).get('source')
        if source:
            return Path(source), 'config.local.json'
    return DEMO_SOURCE, 'default'

# ===============================================
# Read Source File
# ===============================================
SOURCE, SOURCE_FROM = resolve_source()
DEMO = SOURCE.resolve() == DEMO_SOURCE.resolve()
OUT = AQUI / ('data' if DEMO else 'data_real')
print(f'Modo: {{"DEMO (datos inventados)" if DEMO else "REAL"}}  Origen ({{SOURCE_FROM}}): {{SOURCE}}')

ruta = SOURCE / ARCHIVO
if not ruta.is_file():
    raise SystemExit(f'Falta {{ruta}}: no se genera el tablero.')
with open(ruta, encoding='utf-8-sig', newline='') as fh:
    filas = list(csv.DictReader(fh))
if not filas:
    raise SystemExit(f'{{ruta}} vino vacio: no se genera el tablero.')

# ===============================================
# Validate Schema
# ===============================================
expected_columns = ['id', 'categoria', 'fecha', 'valor']     # TODO: las columnas reales
missing = [c for c in expected_columns if c not in filas[0]]
if missing:
    raise SystemExit(f'Missing columns: {{missing}}')

# ===============================================
# Transform
# ===============================================
detalle = [{{'id': f['id'], 'categoria': f['categoria'], 'fecha': f['fecha'][:10],
             'valor': float(f['valor']) if f['valor'] else None}} for f in filas]
sin_valor = sum(1 for d in detalle if d['valor'] is None)     # nunca un default silencioso: se cuenta

# ===============================================
# Write Output
# ===============================================
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'dashboard.json').write_text(json.dumps({{'detalle': detalle}}, ensure_ascii=False, separators=(',', ':')),
                                    encoding='utf-8')
meta = {{
    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
    'demo': DEMO,
    'fuente': 'datos inventados (generar_demo.py)' if DEMO else 'generar_datos.py',
    'counts': {{'filas': len(detalle), 'sin_valor': sin_valor}},
    'fuentes': [{{'nombre': ARCHIVO, 'nombre_en': ARCHIVO, 'sistema': 'TODO', 'tabla': ARCHIVO,
                 'extraido_el': None,          # TODO: de la fecha del NOMBRE del archivo, nunca de hoy
                 'actualizado': None, 'dato_al': max((d['fecha'] for d in detalle), default=None),
                 'filas': len(detalle), 'falta': False}}],
}}
(OUT / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'Escrito: {{OUT / "dashboard.json"}} ({{len(detalle):,}} filas, {{sin_valor}} sin valor)')
'''

TAB_GENERAR_DEMO = '''# ===============================================
# {nombre}: datos INVENTADOS para demo/source y data/
# Author: Haz
# ===============================================
# Nada de aqui sale de un sistema: ids, categorias y valores son aleatorios con semilla fija.

import csv
import random
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SRC = AQUI / 'demo' / 'source'
rnd = random.Random({semilla})

SRC.mkdir(parents=True, exist_ok=True)
with open(SRC / 'ejemplo.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['id', 'categoria', 'fecha', 'valor'])
    for i in range(1, 201):
        d = date.today() - timedelta(days=rnd.randint(0, 90))
        w.writerow([f'EJ-{{i:05d}}', rnd.choice(['A', 'B', 'C', 'D']), d.isoformat(),
                    '' if rnd.random() < 0.03 else round(rnd.uniform(10, 5000), 2)])
print(f'Inventados: 200 renglones en {{SRC / "ejemplo.csv"}}')
sys.exit(subprocess.call([sys.executable, '-I', str(AQUI / 'generar_datos.py'), str(SRC)]))
'''

TAB_INDEX = '''<!DOCTYPE html>
<!-- Made by: Hazzard -->
<html lang="es" data-theme="corporativo">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<link rel="stylesheet" href="estilos.css">
</head>
<body>
<div class="app">
  <div class="banner" id="banner" role="alert" hidden></div>
  <header class="hdr">
    <a class="btn-portal" id="btnPortal" href="#">← <span>Volver al Portal</span></a>
    <h1 class="hdr__title"><span>{titulo}</span><small>{descripcion}</small></h1>
    <div class="hdr__meta"><span>Actualizado: <b id="metaUpdated">–</b></span></div>
  </header>
  <main class="app__main">
    <div class="loading" id="loading">Cargando datos…</div>
    <div class="kpi-row" id="kpis"></div>
    <section class="card">
      <div class="card__header"><h3 class="card__title">Detalle</h3><span class="btn-export__count" id="rowCount"></span></div>
      <div class="tbl-wrap"><table class="tbl"><thead><tr id="head"></tr></thead><tbody id="body"></tbody></table></div>
    </section>
  </main>
  <footer class="ftr"><span class="ftr__credit">Made by Hazzard</span><span id="ftrFuente"></span></footer>
</div>
<script src="app.js"></script>
</body>
</html>
'''

TAB_APP = '''// Made by: Hazzard
// {titulo}: esqueleto. Crecer siguiendo dashboard-standards (filtros, cross-filter, export, i18n).
"use strict";
const CONFIG = {{
  portalUrl: "/{portal}/",
  dataUrls: ["/api/{slug}/", "./data_real/", "./data/"],   // portal; local real (fuera de git); inventados
  columnas: [["id", "ID"], ["categoria", "Categoría"], ["fecha", "Fecha"], ["valor", "Valor"]]
}};
const $ = id => document.getElementById(id);

async function leerJSON(nombre) {{
  for (const base of CONFIG.dataUrls) {{
    try {{ const r = await fetch(base + nombre, {{ cache: "no-cache" }}); if (r.ok) return await r.json(); }}
    catch (e) {{ /* siguiente ruta */ }}
  }}
  throw new Error(nombre);
}}
function banda(nivel, titulo, detalle) {{
  const b = $("banner"); b.className = `banner banner--${{nivel}}`; b.textContent = "";
  const t = document.createElement("span"); t.className = "banner__title"; t.textContent = titulo;
  const d = document.createElement("span"); d.className = "banner__detail"; d.textContent = detalle;
  b.append(t, d); b.hidden = false;
}}
function kpi(valor, etiqueta, rol) {{
  const c = document.createElement("div"); c.className = `card kpi kpi--${{rol}}`;
  const v = document.createElement("div"); v.className = "kpi__value"; v.textContent = valor;
  const l = document.createElement("div"); l.className = "kpi__label"; l.textContent = etiqueta;
  c.append(v, l); $("kpis").appendChild(c);
}}
async function init() {{
  $("btnPortal").href = CONFIG.portalUrl;
  let meta, dash;
  try {{ [meta, dash] = await Promise.all([leerJSON("meta.json"), leerJSON("dashboard.json")]); }}
  catch (e) {{ $("loading").hidden = true; banda("critical", "No se pudieron leer los datos del tablero.", "Nada de lo que se ve es confiable."); return; }}
  $("loading").hidden = true;
  if (meta.semi) banda("warn", "Datos semi-ficticios.", "Forma real, identidades inventadas.");
  else if (meta.demo) banda("warn", "Datos inventados.", "Configura config.local.json y corre generar_datos.py para ver el corte real.");
  $("metaUpdated").textContent = meta.generated_at || "–";
  $("ftrFuente").textContent = meta.fuente || "";
  const filas = dash.detalle || [];
  kpi(filas.length.toLocaleString("en-US"), "Filas", "neutral");
  kpi((meta.counts && meta.counts.sin_valor) ?? "–", "Sin valor", "warn");
  CONFIG.columnas.forEach(([, etiqueta]) => {{ const th = document.createElement("th"); th.textContent = etiqueta; $("head").appendChild(th); }});
  filas.slice(0, 25).forEach(f => {{
    const tr = document.createElement("tr");
    CONFIG.columnas.forEach(([campo]) => {{ const td = document.createElement("td"); td.textContent = f[campo] ?? "–"; tr.appendChild(td); }});
    $("body").appendChild(tr);
  }});
  $("rowCount").textContent = `${{filas.length.toLocaleString("en-US")}} filas`;
}}
init();
'''

TAB_ACTUALIZAR = '''@echo off
rem Made by: Hazzard
rem Recalcula {nombre} con el corte del dia y lo abre en http://127.0.0.1:{puerto}/
cd /d "%~dp0"
python generar_datos.py
if errorlevel 1 (
  echo.
  echo No se pudo generar el tablero. Revisa el mensaje de arriba.
  pause
  exit /b 1
)
start "" http://127.0.0.1:{puerto}/
python -m http.server {puerto} --bind 127.0.0.1
'''

# --- etl ------------------------------------------------------------------------------------------------
ETL_CONFIG = '''# ===============================================
# {nombre}: configuracion
# Author: Haz
# ===============================================
# Las rutas reales NO van aqui: salen de config.local.json (ignorado por git) o de variables de ambiente.

import json
import os
from pathlib import Path

AQUI = Path(__file__).resolve().parent
_local = AQUI / 'config.local.json'
_cfg = json.loads(_local.read_text(encoding='utf-8-sig')) if _local.is_file() else {{}}

SOURCE_FOLDER = Path(os.environ.get('{env}', _cfg.get('source', AQUI / 'demo' / 'source')))
FILE_PREFIX = _cfg.get('file_prefix', 'ejemplo')          # TODO: prefijo de los archivos de origen
OUTPUT_FOLDER = AQUI / 'Output'
LOG_FILE = OUTPUT_FOLDER / '{nombre}.log'
EXPECTED_COLUMNS = ['id', 'categoria', 'fecha', 'valor']    # TODO: columnas reales
'''

ETL_MAIN = '''# ===============================================
# {nombre} ETL
# Author: Haz
# ===============================================
# {descripcion}

import logging
import sys

import pandas as pd

import config

# ===============================================
# Logging
# ===============================================
config.OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler(config.LOG_FILE, encoding='utf-8'), logging.StreamHandler()])
log = logging.getLogger('{nombre}')

def read_sources():
    archivos = sorted(config.SOURCE_FOLDER.rglob(f'{{config.FILE_PREFIX}}*'))
    if not archivos:
        raise FileNotFoundError(f'No files with prefix {{config.FILE_PREFIX}} in {{config.SOURCE_FOLDER}}')
    log.info('Found %d source files', len(archivos))
    return pd.concat([pd.read_csv(a, dtype=str).assign(SOURCE_FILE=a.name) for a in archivos], ignore_index=True)

def validate(df):
    missing = [c for c in config.EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f'Missing columns: {{missing}}')

def transform(df):
    df = df.drop_duplicates()
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
    log.info('Rows without numeric value: %d', df['valor'].isna().sum())
    return df

def main():
    # ===============================================
    # Read Source Files
    # ===============================================
    df = read_sources()
    validate(df)
    # ===============================================
    # Transform
    # ===============================================
    df = transform(df)
    # ===============================================
    # Export
    # ===============================================
    df.to_parquet(config.OUTPUT_FOLDER / '{nombre}.parquet', index=False)
    df.to_csv(config.OUTPUT_FOLDER / '{nombre}.csv', index=False, encoding='utf-8-sig')
    log.info('Completed: %d rows exported to %s', len(df), config.OUTPUT_FOLDER)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        log.exception('ETL failed')
        sys.exit(1)
'''

ETL_DEMO = '''# ===============================================
# {nombre}: archivo de origen INVENTADO para probar el ETL
# Author: Haz
# ===============================================
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'demo' / 'source'
SRC.mkdir(parents=True, exist_ok=True)
rnd = random.Random({semilla})
with open(SRC / 'ejemplo_01.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['id', 'categoria', 'fecha', 'valor'])
    for i in range(1, 101):
        w.writerow([f'EJ-{{i:05d}}', rnd.choice('ABCD'), (date.today() - timedelta(days=i)).isoformat(),
                    round(rnd.uniform(1, 999), 2)])
print('Inventado:', SRC / 'ejemplo_01.csv')
'''

# --- notebook -------------------------------------------------------------------------------------------
NOTEBOOK = '''# ===============================================
# {nombre}
# Author: Haz
# ===============================================
# {descripcion}
# Correr local o pegar en Fabric. En Fabric: rutas relativas (Files/...), sin IDs ni credenciales.

# ===============================================
# Parameters
# ===============================================
SOURCE_PATH = 'demo/source/ejemplo.csv'   # TODO
OUTPUT_PATH = 'Output/{nombre}.parquet'
EXPECTED_COLUMNS = ['id', 'categoria', 'fecha', 'valor']

# ===============================================
# Read Source File
# ===============================================
import pandas as pd

df = pd.read_csv(SOURCE_PATH, dtype=str)
missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
if missing:
    raise ValueError(f'Missing columns: {{missing}}')

# ===============================================
# Transform
# ===============================================
df['valor'] = pd.to_numeric(df['valor'], errors='coerce')

# ===============================================
# Export
# ===============================================
df.to_parquet(OUTPUT_PATH, index=False)
print(f'Completed: {{len(df)}} rows -> {{OUTPUT_PATH}}')
'''

README = '''# {nombre}

{descripcion}

Creado el {hoy} con la skill `nuevo-proyecto` (tipo **{tipo}**).

## Archivos

| Archivo | Qué es |
|---|---|
{tabla}

## Cómo se corre

{correr}

## Datos

- **Inventados** en `demo/source/` (con `CONTRATO.md`); es lo único que entra al repo.
- **Reales**: la carpeta de `config.local.json` (`{{"source": "..."}}`, ignorado por git). La salida con datos
  reales va a `data_real/` u `Output/`, también ignoradas.
- Antes de cada commit corre el `candado-personal`: detiene datos reales, secretos y archivos grandes.

## Pendiente

- [ ] Reemplazar los `TODO` (archivo de origen, columnas esperadas, fecha de extracción).
- [ ] Documentar aquí de dónde salen los datos reales y cada cuánto.

Made by Hazzard
'''

TABLAS = {
    'tablero': [('`index.html`, `app.js`, `estilos.css`', 'el tablero (sin JS inline)'),
                ('`generar_datos.py`', 'arma `data/` (o `data_real/`) desde la fuente'),
                ('`generar_demo.py`', 'escribe datos inventados en `demo/source/` y arma `data/`'),
                ('`data/`, `demo/`', 'contrato con datos inventados (`CONTRATO.md`)'),
                ('`actualizar.cmd`', 'recalcula y abre el tablero en local'),
                ('`shared/`', 'librerías locales (Chart.js, SheetJS) para correrlo fuera del portal')],
    'etl': [('`main.py`', 'el ETL: lee, valida esquema, transforma, exporta parquet y csv, deja log'),
            ('`config.py`', 'rutas y columnas esperadas; las reales salen de `config.local.json`'),
            ('`generar_demo.py`', 'archivo de origen inventado en `demo/source/`'),
            ('`requirements.txt`', 'dependencias con versión'),
            ('`Output/`', 'salida (ignorada por git)')],
    'notebook': [('`NB_{nombre}.py`', 'el notebook, con banners por sección'),
                 ('`demo/`', 'archivo de origen inventado (`CONTRATO.md`)')],
}
CORRER = {
    'tablero': '```bash\npython generar_demo.py            # datos inventados -> data/\npython -m http.server {puerto} --bind 127.0.0.1\n```\n\nAbrir `http://127.0.0.1:{puerto}/`. Con el corte real: crea `config.local.json` y doble clic en `actualizar.cmd`.',
    'etl': '```bash\npython -m venv .venv\n.venv\\<servidor>\<carpeta> install -r requirements.txt\n.venv\\<servidor>\<carpeta> generar_demo.py\n.venv\\<servidor>\<carpeta> main.py\n```',
    'notebook': '```bash\npython NB_{nombre}.py\n```',
}

def buscar_shared(repo):
    """Copia de shared/ (librerías locales) de otro tablero, primero del mismo repo."""
    for r in [repo] + [REPOS / x for x in ('BI_DataNexus', 'OblivionCode') if REPOS / x != repo]:
        for s in sorted((r / 'Main_Dev_Projects').glob('*/shared')):
            if (s / 'vendor').is_dir():
                return s
    return None

def buscar_estilos(repo):
    """estilos.css de otro tablero; primero uno que traiga .kpi-row (la fila de KPIs del esqueleto)."""
    candidatos = []
    for r in [repo] + [REPOS / x for x in ('BI_DataNexus', 'OblivionCode') if REPOS / x != repo]:
        candidatos += sorted((r / 'Main_Dev_Projects').glob('*/estilos.css'))
    for e in candidatos:
        if '.kpi-row' in e.read_text(encoding='utf-8', errors='ignore'):
            return e
    return candidatos[0] if candidatos else None

def plantilla_prd(repo, nombre):
    """La plantilla del PRD sale de la skill escribir-prd del repo, para no tener dos copias que se separen."""
    skill = repo / '.claude' / 'skills' / 'escribir-prd' / 'SKILL.md'
    if skill.is_file():
        m = re.search(r'```markdown\n(.*?)\n```', skill.read_text(encoding='utf-8'), re.S)
        if m:
            texto = m.group(1).replace('<Proyecto>', nombre).replace('<AAAA-MM-DD>', HOY)
            return texto.replace('Estado: borrador | aprobado', 'Estado: borrador') + '\n'
    return None

def escribir(ruta, texto):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding='utf-8', newline='\n')

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser()
    ap.add_argument('nombre')
    ap.add_argument('--tipo', choices=['tablero', 'etl', 'notebook'], required=True)
    ap.add_argument('--repo', default='BI_DataNexus', choices=['BI_DataNexus', 'OblivionCode'])
    ap.add_argument('--descripcion', default='TODO: qué hace este proyecto, para quién y de dónde lee.')
    ap.add_argument('--portal', default='logistics', choices=['logistics', 'sop'])
    a = ap.parse_args()

    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', a.nombre):
        raise SystemExit('El nombre va en el estilo de la carpeta: letras, números y _ (ej. Y_Meadows, BOM_Join_Project).')
    repo = REPOS / a.repo
    if not (repo / '.git').is_dir():
        raise SystemExit(f'{repo} no es un repo clonado en esta máquina.')
    dst = repo / 'Main_Dev_Projects' / a.nombre
    if dst.exists():
        raise SystemExit(f'{dst} ya existe: no se sobreescribe nada.')

    nombre, slug = a.nombre, a.nombre.lower().replace('_', '-')
    env = re.sub(r'[^A-Z0-9]', '_', nombre.upper()) + '_SOURCE'
    semilla = int(HOY.replace('-', ''))
    puerto = 8700 + sum(map(ord, nombre)) % 200
    titulo = nombre.replace('_', ' ')
    f = dict(nombre=nombre, slug=slug, env=env, semilla=semilla, puerto=puerto, titulo=titulo,
             descripcion=a.descripcion, portal=a.portal, hoy=HOY, tipo=a.tipo)

    escribir(dst / '.gitignore', GITIGNORE)
    escribir(dst / 'config.local.ejemplo.json', CONFIG_EJEMPLO)
    escribir(dst / 'demo' / 'CONTRATO.md', CONTRATO.format(
        detalle='`source/` lo escribe `generar_demo.py` con números aleatorios y semilla fija: mismas columnas que la fuente real, ningún valor real.'))
    avisos = []
    if a.tipo == 'tablero':
        escribir(dst / 'data' / 'CONTRATO.md', CONTRATO.format(
            detalle='`dashboard.json` y `meta.json` salen de `python generar_demo.py` sobre `demo/source/`. `meta.json` lleva `"demo": true` y el tablero lo avisa con una banda.'))
        escribir(dst / 'generar_datos.py', TAB_GENERAR_DATOS.format(**f))
        escribir(dst / 'generar_demo.py', TAB_GENERAR_DEMO.format(**f))
        escribir(dst / 'index.html', TAB_INDEX.format(**f))
        escribir(dst / 'app.js', TAB_APP.format(**f))
        escribir(dst / 'actualizar.cmd', TAB_ACTUALIZAR.format(**f).replace('\n', '\r\n'))
        estilos = buscar_estilos(repo)
        if estilos:
            texto = estilos.read_text(encoding='utf-8')
            if texto.startswith('/* Made by'):
                texto = texto.split('\n', 1)[1]
            # El tema principal se llama "corporativo" en el proyecto personal (el alterno se queda "alt"),
            # y el encabezado no dice de quién era la hoja original.
            texto = re.sub(r'data-theme="(?!alt")[^"]+"', 'data-theme="corporativo"', texto)
            texto = re.sub(r'(Dashboard Design Tokens)\s+[—-][^\n]*', r'\1', texto)
            # Lo demás que nombre a la empresa: las mismas reglas privadas del hook de copia
            privadas = Path.home() / '.claude' / 'hooks' / 'copiar_skills_reglas.json'
            if privadas.is_file():
                for patron, repl in json.loads(privadas.read_text(encoding='utf-8'))['reglas']:
                    texto = re.sub(patron, repl, texto)
            else:
                avisos.append('sin las reglas privadas: revisa a mano que estilos.css no nombre a la empresa')
            escribir(dst / 'estilos.css', '/* Made by: Hazzard */\n' + texto)
        else:
            escribir(dst / 'estilos.css', '/* Made by: Hazzard */\n')
            avisos.append('no encontré un estilos.css de otro tablero: estilos.css quedó vacío')
        shared = buscar_shared(repo)
        if shared:
            shutil.copytree(shared, dst / 'shared')
        else:
            avisos.append('no encontré shared/ de otro tablero: el HTML no tendrá Chart.js ni SheetJS locales')
    elif a.tipo == 'etl':
        escribir(dst / 'config.py', ETL_CONFIG.format(**f))
        escribir(dst / 'main.py', ETL_MAIN.format(**f))
        escribir(dst / 'generar_demo.py', ETL_DEMO.format(**f))
        escribir(dst / 'requirements.txt', 'pandas==2.2.3\npyarrow==17.0.0\n')
    else:
        escribir(dst / f'NB_{nombre}.py', NOTEBOOK.format(**f))
        escribir(dst / 'demo' / 'source' / 'ejemplo.csv', 'id,categoria,fecha,valor\nEJ-00001,A,2026-01-01,100.5\nEJ-00002,B,2026-01-02,\n')
        (dst / 'Output').mkdir(exist_ok=True)
    prd = plantilla_prd(repo, nombre)
    if prd:
        escribir(dst / 'docs' / 'PRD.md', prd)
    else:
        avisos.append('no encontré la skill escribir-prd en el repo: docs/PRD.md no se creó')
    tabla = '\n'.join(f'| {x.format(**f)} | {y} |' for x, y in TABLAS[a.tipo] + [('`docs/PRD.md`', 'objetivo, KPIs y criterios de aceptación (borrador; lo llena `escribir-prd`)')])
    escribir(dst / 'README.md', README.format(tabla=tabla, correr=CORRER[a.tipo].format(**f), **f))

    print(f'Creado: {dst}')
    for p in sorted(dst.rglob('*')):
        if p.is_file() and 'shared' not in p.relative_to(dst).parts:
            print('  ', p.relative_to(dst).as_posix())
    if (dst / 'shared').is_dir():
        print('   shared/ (copiado de otro tablero)')
    for av in avisos:
        print('  aviso:', av)

if __name__ == '__main__':
    main()
