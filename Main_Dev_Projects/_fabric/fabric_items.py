# ===============================================
# Fabric Items - Split and Rebuild
# Author: Haz
# ===============================================
"""
Separa los items de Fabric (DataPipeline, CopyJob, Notebook, Dataflow) en piezas de un solo
lenguaje y los vuelve a armar:

- DataPipeline / CopyJob: el SQL embebido en el JSON sale a sql/<actividad>.sql y en el JSON
  queda el marcador @@sql:sql/<archivo>.sql@@.
- Notebook: cada celda sale a cells/NN.<py|sql|md>; el SQL entre triples comillas dentro de
  una celda de Python sale a sql/ con el mismo marcador. El orden y los metadatos van en
  notebook.manifest.json.
- Dataflow: cada consulta de mashup.pq sale a queries/<nombre>.pq; el orden va en
  mashup.manifest.json.

'probar' separa cada item de Original en una carpeta temporal y lo vuelve a armar: el notebook
y el dataflow deben salir idénticos byte por byte, el JSON idéntico en contenido. Es la prueba
de que separar y ensamblar no pierden nada.

'verificar' arma cada item de Modified y lo compara contra Original. Como Modified se reescribe
a propósito, sus diferencias son el reporte de cambios, no errores.

En este portafolio no hay Original/ ni Modified/: aquí solo aplica 'ensamblar'.

Uso:
    python fabric_items.py separar   <item_original> <carpeta_destino> [--forzar]
    python fabric_items.py ensamblar <item_modificado> <carpeta_destino>
    python fabric_items.py probar    <carpeta_original>
    python fabric_items.py verificar <carpeta_original> <carpeta_modificada>
"""

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

# =====================================================================================
# CONSTANTES
# =====================================================================================

ITEM_SUFFIXES = ('.Notebook', '.DataPipeline', '.CopyJob', '.Dataflow')
SQL_START = re.compile(r'^\s*(?:(?:--[^\n]*\n|/\*.*?\*/)\s*)*(SELECT|WITH|INSERT|MERGE|CREATE|DELETE|UPDATE|TRUNCATE|DROP|ALTER|DECLARE|EXEC|BEGIN)\b', re.I | re.S)
SQL_KEYS = {'query', 'sqlreaderquery', 'oraclereaderquery', 'sqlquery', 'text', 'script'}
MARKER = '@@sql:{}@@'
MARKER_RE = re.compile(r'@@sql:([^@]+)@@')
CELL_RE = re.compile(r'^# (?:PARAMETERS )?(?:CELL|MARKDOWN|METADATA) \*+\s*$', re.M)
TRIPLE_RE = re.compile(r'("""|\'\'\')(.*?)\1', re.S)
SHARED_RE = re.compile(r'^shared ', re.M)
M_STRING_RE = re.compile(r'"((?:[^"]|"")*)"')
M_ESCAPE_RE = re.compile(r'#\(((?:cr|lf|tab)(?:,(?:cr|lf|tab))*)\)')
M_ESCAPES = {'cr': '\r', 'lf': '\n', 'tab': '\t'}

# =====================================================================================
# UTILIDADES
# =====================================================================================

def safe_name(text):
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', text).strip('_')[:80] or 'query'


def unique(path_dir, stem, ext):
    candidate, n = path_dir / f'{stem}{ext}', 2
    while candidate.exists():
        candidate, n = path_dir / f'{stem}_{n}{ext}', n + 1
    return candidate


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode('utf-8'))


def read_text(path):
    return path.read_bytes().decode('utf-8')

# =====================================================================================
# DATAPIPELINE / COPYJOB (JSON)
# =====================================================================================

def split_json(src_file, dst_dir):
    data = json.loads(read_text(src_file))
    sql_dir = dst_dir / 'sql'

    def walk(node, owner):
        if isinstance(node, dict):
            owner = node.get('name', owner) if isinstance(node.get('name'), str) else owner
            for key, value in node.items():
                if isinstance(value, str) and key.lower() in SQL_KEYS and SQL_START.match(value):
                    sql_dir.mkdir(parents=True, exist_ok=True)
                    target = unique(sql_dir, safe_name(owner), '.sql')
                    write_text(target, value)
                    node[key] = MARKER.format(f'sql/{target.name}')
                else:
                    walk(value, owner)
        elif isinstance(node, list):
            for value in node:
                walk(value, owner)

    walk(data, src_file.parent.stem)
    write_text(dst_dir / src_file.name, json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def rebuild_json(mod_file, item_dir):
    text = read_text(mod_file)
    data = json.loads(text)

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                node[key] = inject(value) if isinstance(value, str) else walk(value) or value
        elif isinstance(node, list):
            for i, value in enumerate(node):
                node[i] = inject(value) if isinstance(value, str) else walk(value) or value
        return None

    def inject(value):
        hit = MARKER_RE.fullmatch(value)
        return read_text(item_dir / hit.group(1)) if hit else value

    walk(data)
    return data

# =====================================================================================
# NOTEBOOK (notebook-content.py)
# =====================================================================================

def split_notebook(src_file, dst_dir):
    text = read_text(src_file)
    starts = [m.start() for m in CELL_RE.finditer(text)]
    bounds = [0] + starts + [len(text)]
    manifest, cell_no = [], 0
    for a, b in zip(bounds, bounds[1:]):
        chunk = text[a:b]
        if not chunk:
            continue
        header, _, body = chunk.partition('\n')
        if not CELL_RE.match(header + '\n') or header.startswith('# METADATA'):
            manifest.append({'raw': chunk})
            continue
        cell_no += 1
        lines = body.split('\n')
        code = [l for l in lines if l.strip()]
        if header.startswith('# MARKDOWN'):
            ext = '.md'
        elif code and all(l.startswith('# MAGIC ') or l == '# MAGIC' for l in code) and code[0].startswith('# MAGIC %%sql'):
            ext = '.sql'
        else:
            ext = '.py'
        entry = {'header': header}
        if ext != '.py':
            stripped = unprefix(lines, '# MAGIC' if ext == '.sql' else '#')
            if stripped is None:
                ext = '.py'
            else:
                body, entry['prefix'], entry['bare'], entry['short'] = stripped
        cell_file = f'cells/{cell_no:02d}{ext}'
        if ext == '.py':
            body = extract_python_sql(body, dst_dir, cell_no)
        write_text(dst_dir / cell_file, body)
        entry['file'] = cell_file
        manifest.append(entry)
    write_text(dst_dir / 'notebook.manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')


def unprefix(lines, prefix):
    # Quita '# MAGIC ' o '# ' de cada renglón; los renglones vacíos sin prefijo se anotan
    # para devolverlos igual al ensamblar. None si algún renglón no sigue el formato.
    out, bare, short = [], [], []
    for i, line in enumerate(lines):
        if line.startswith(prefix + ' '):
            out.append(line[len(prefix) + 1:])
        elif line == prefix:
            out.append('')
            short.append(i)
        elif line == '':
            out.append('')
            bare.append(i)
        else:
            return None
    return '\n'.join(out), prefix, bare, short


def reprefix(body, prefix, bare, short):
    bare, short = set(bare), set(short)
    lines = body.split('\n')
    empty = {i for i, line in enumerate(lines) if line == ''}
    # Los vacíos que no están en bare ni en short eran 'prefijo + espacio' y salen igual.
    # Si un índice guardado ya no cae en un renglón vacío, la celda se editó: regla de
    # Fabric, vacíos al inicio y al final sin prefijo, vacíos de en medio como 'prefijo '.
    if not (bare | short) <= empty:
        filled = [i for i, line in enumerate(lines) if line != '']
        first, last = (filled[0], filled[-1]) if filled else (len(lines), -1)
        bare = {i for i in empty if i < first or i > last}
        short = set()
    return '\n'.join('' if i in bare else prefix if i in short else f'{prefix} {l}'
                     for i, l in enumerate(body.split('\n')))


def extract_python_sql(body, dst_dir, cell_no):
    counter = [0]

    def repl(m):
        if not SQL_START.match(m.group(2)) or len(m.group(2).strip()) < 30:
            return m.group(0)
        counter[0] += 1
        target = dst_dir / 'sql' / f'cell{cell_no:02d}_query{counter[0]}.sql'
        write_text(target, m.group(2))
        return m.group(1) + MARKER.format(f'sql/{target.name}') + m.group(1)

    return TRIPLE_RE.sub(repl, body)


def rebuild_notebook(item_dir):
    manifest = json.loads(read_text(item_dir / 'notebook.manifest.json'))
    parts = []
    for entry in manifest:
        if 'raw' in entry:
            parts.append(entry['raw'])
            continue
        body = read_text(item_dir / entry['file'])
        body = MARKER_RE.sub(lambda m: read_text(item_dir / m.group(1)), body)
        if 'prefix' in entry:
            body = reprefix(body, entry['prefix'], entry['bare'], entry['short'])
        parts.append(entry['header'] + '\n' + body)
    return ''.join(parts)

# =====================================================================================
# DATAFLOW (mashup.pq)
# =====================================================================================

def split_dataflow(src_file, dst_dir):
    text = read_text(src_file)
    starts = [m.start() for m in SHARED_RE.finditer(text)]
    bounds = [0] + starts + [len(text)]
    manifest = []
    for a, b in zip(bounds, bounds[1:]):
        chunk = text[a:b]
        if not chunk:
            continue
        if not chunk.startswith('shared '):
            manifest.append({'raw': chunk})
            continue
        name = re.match(r'shared\s+(#"(?:[^"]|"")*"|\S+)', chunk).group(1).strip('#"')
        target = unique(dst_dir / 'queries', safe_name(name), '.pq')
        write_text(target, extract_m_sql(chunk, dst_dir, safe_name(name)))
        manifest.append({'file': f'queries/{target.name}'})
    write_text(dst_dir / 'mashup.manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')


def m_decode(literal):
    text = literal.replace('""', '"')
    return M_ESCAPE_RE.sub(lambda m: ''.join(M_ESCAPES[code] for code in m.group(1).split(',')), text)


def m_encode(text):
    return text.replace('"', '""').replace('\r', '#(cr)').replace('\n', '#(lf)').replace('\t', '#(tab)')


def extract_m_sql(chunk, dst_dir, query_name):
    # SQL nativo dentro de un texto M (Odbc.Query, Value.NativeQuery, Sql.Database [Query=...]).
    # Solo se separa si al volver a codificarlo queda idéntico; si no, se deja en el .pq.
    def repl(m):
        literal = m.group(1)
        sql = m_decode(literal)
        if m_encode(sql) != literal or not SQL_START.match(sql) or len(sql.strip()) < 40:
            return m.group(0)
        target = unique(dst_dir / 'sql', query_name, '.sql')
        write_text(target, sql)
        return '"' + MARKER.format(f'sql/{target.name}') + '"'

    return M_STRING_RE.sub(repl, chunk)


def rebuild_dataflow(item_dir):
    manifest = json.loads(read_text(item_dir / 'mashup.manifest.json'))
    text = ''.join(e['raw'] if 'raw' in e else read_text(item_dir / e['file']) for e in manifest)
    return MARKER_RE.sub(lambda m: m_encode(read_text(item_dir / m.group(1))), text)

# =====================================================================================
# ITEM COMPLETO
# =====================================================================================

def split_item(src_item, dst_item, force=False):
    # El destino suele ser Modified/<item>, con SQL y celdas ya reescritos: no se pisa sin --forzar
    if dst_item.exists():
        if not force:
            raise FileExistsError(f'{dst_item} ya existe; usa --forzar para reemplazarlo')
        shutil.rmtree(dst_item)
    dst_item.mkdir(parents=True)
    for f in src_item.iterdir():
        if f.name == 'notebook-content.py':
            split_notebook(f, dst_item)
        elif f.name == 'mashup.pq':
            split_dataflow(f, dst_item)
        elif f.suffix == '.json' and f.name in ('pipeline-content.json', 'copyjob-content.json'):
            split_json(f, dst_item)
        elif f.is_file():
            shutil.copy2(f, dst_item / f.name)


def rebuild_item(mod_item, out_item):
    out_item.mkdir(parents=True, exist_ok=True)
    skip = {'notebook.manifest.json', 'mashup.manifest.json'}
    for f in mod_item.iterdir():
        if f.is_dir() or f.name in skip:
            continue
        if f.name in ('pipeline-content.json', 'copyjob-content.json'):
            write_text(out_item / f.name, json.dumps(rebuild_json(f, mod_item), indent=2, ensure_ascii=False))
        else:
            shutil.copy2(f, out_item / f.name)
    if (mod_item / 'notebook.manifest.json').exists():
        write_text(out_item / 'notebook-content.py', rebuild_notebook(mod_item))
    if (mod_item / 'mashup.manifest.json').exists():
        write_text(out_item / 'mashup.pq', rebuild_dataflow(mod_item))


def find_items(root):
    return sorted(p for p in root.rglob('*') if p.is_dir() and p.name.endswith(ITEM_SUFFIXES))


def verify(orig_root, mod_root):
    failures, checked = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        for orig in find_items(orig_root):
            mod = mod_root / orig.relative_to(orig_root)
            if not mod.exists():
                failures.append(f'falta en Modified: {orig.relative_to(orig_root)}')
                continue
            out = Path(tmp) / str(checked)
            rebuild_item(mod, out)
            checked += 1
            for f in orig.iterdir():
                if not f.is_file():
                    continue
                rebuilt = out / f.name
                if not rebuilt.exists():
                    failures.append(f'{orig.name}/{f.name}: no se armó')
                elif f.suffix == '.json':
                    if json.loads(read_text(f)) != json.loads(read_text(rebuilt)):
                        failures.append(f'{orig.name}/{f.name}: contenido distinto')
                elif f.read_bytes() != rebuilt.read_bytes():
                    failures.append(f'{orig.name}/{f.name}: bytes distintos')
    return checked, failures

# =====================================================================================
# MAIN
# =====================================================================================

def round_trip(orig_root):
    # Separa Original en una carpeta temporal y la compara contra sí misma al volver a armar
    with tempfile.TemporaryDirectory() as tmp:
        split_root = Path(tmp) / 'separado'
        for orig in find_items(orig_root):
            split_item(orig, split_root / orig.relative_to(orig_root))
        return verify(orig_root, split_root)


def report(checked, failures):
    for line in failures:
        print('FALLA', line)
    print(f'{checked} items armados de nuevo, {len(failures)} diferencias')
    return 1 if failures or checked == 0 else 0


def main(argv):
    args = [a for a in argv[1:] if a != '--forzar']
    force = '--forzar' in argv
    expected = {'separar': 3, 'ensamblar': 3, 'verificar': 3, 'probar': 2}
    if not args or args[0] not in expected or len(args) != expected[args[0]]:
        print(__doc__)
        return 2
    action, paths = args[0], [Path(p) for p in args[1:]]
    if action == 'separar':
        split_item(paths[0], paths[1], force)
    elif action == 'ensamblar':
        rebuild_item(paths[0], paths[1])
    elif action == 'probar':
        return report(*round_trip(paths[0]))
    else:
        return report(*verify(paths[0], paths[1]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
