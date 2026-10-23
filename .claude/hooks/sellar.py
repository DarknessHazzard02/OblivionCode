#!/usr/bin/env python3
# ===============================================
# Sellos de revision y de pruebas
# Author: Haz
# ===============================================
"""Deja el sello de que una revision o una prueba se hizo sobre una version exacta.

Usos (desde la raiz del repo):

    python .claude/hooks/sellar.py revision [--reporte <ruta>]     sella el diff en stage
    python .claude/hooks/sellar.py pruebas <carpeta_tablero> [--evidencia <ruta>]
                                                                    sella la huella del tablero probado
    python .claude/hooks/sellar.py estado                         muestra los sellos y si siguen valiendo

Los sellos viven en `.claude/estado/` del repo, que se crea con su propio `.gitignore` (no se
commitean), y los lee el hook `exigir_antes_de_commit.py`. Si el diff o el tablero cambian despues
del sello, el sello ya no vale. Este script no revisa ni prueba nada: solo anota. Lo llaman las
skills `revisar-antes-de-commit-personal` y `probar-tablero-personal` despues de hacer su trabajo.

Un tablero es una carpeta de segundo o primer nivel del repo con `index.html` (en el portal,
`<tablero>/index.html`), en disco o en el stage. Su huella es el blob de git de cada archivo que
lo forma: html, js, css, json y svg a cualquier profundidad (tambien `pages/`, `static/`), y todo
lo que haya en sus `data*/` y `shared/`; no cuentan `docs/`, `build/`, `Modified/` ni `Original/`. Al sellar se calcula
sobre la copia de trabajo; el hook la calcula sobre el stage. Coinciden solo si lo que se va a
commitear es lo que se probo.

No cubre el `shared/` de la raiz del portal (librerias y js comunes): un cambio ahi pide la
revision, pero no la prueba de ningun tablero. Quien lo cambie prueba a mano al menos uno.
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

EXT_CODIGO = {'.html', '.js', '.css', '.json', '.svg'}
EXT_DOCS = {'.md', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.pdf'}
NIVELES_TABLERO = (2, 1)   # <grupo>/<tablero>/index.html antes que <tablero>/index.html
FUERA_DE_LA_HUELLA = {'docs', 'build', 'Modified', 'Original'}   # Modified/Original: pipelines de Fabric


# ── Git ──────────────────────────────────────────────────────────────────
def git(raiz, *args, entrada=None, binario=False):
    # quotepath=off: con acentos en la ruta git la devolveria entre comillas y con escapes octales
    # diff.external, textconv y fsmonitor apagados: el hook corre antes del permiso y no debe
    # ejecutar programas que traiga la configuracion de un repo ajeno.
    salida = subprocess.run(['git', '-C', str(raiz), '-c', 'core.quotepath=off', '-c', 'core.fsmonitor=false',
                             '-c', 'diff.external=', *args], input=entrada,
                            capture_output=True, text=not binario,
                            encoding=None if binario else 'utf-8')
    if salida.returncode != 0:
        raise RuntimeError(f'git {" ".join(args)}: {salida.stderr}')
    return salida.stdout


def raiz_repo(desde='.'):
    return Path(git(desde, 'rev-parse', '--show-toplevel').strip())


def carpeta_estado(raiz):
    """`.claude/estado/` con un .gitignore propio: los sellos nunca entran a un commit."""
    d = Path(raiz) / '.claude' / 'estado'
    d.mkdir(parents=True, exist_ok=True)
    ignora = d / '.gitignore'
    if not ignora.exists():
        ignora.write_text('*\n', encoding='utf-8')
    return d


def leer_sello(raiz, nombre):
    """El sello, o {} si no existe o esta roto (un sello roto no vale, no truena)."""
    ruta = Path(raiz) / '.claude' / 'estado' / nombre
    try:
        datos = json.loads(ruta.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}
    return datos if isinstance(datos, dict) else {}


def es_solo_doc(rel):
    """Documento que no pide revision. Lo de .claude/, skills/ y agents/ no cuenta: son instrucciones
    del asistente (en el repo de skills viven en plugins/, fuera de .claude/)."""
    nombre = Path(rel).name.lower()
    partes = set(rel.split('/'))
    if partes & {'.claude', 'skills', 'agents'} or nombre in ('claude.md', 'skill.md', 'reglas-equipo.md') \
            or nombre.startswith('requirements'):
        return False
    return Path(rel).suffix.lower() in EXT_DOCS


# ── Huellas ──────────────────────────────────────────────────────────────
def hash_stage(raiz):
    diff = git(raiz, 'diff', '--cached', '--binary', '--no-ext-diff', '--no-textconv', binario=True)
    return hashlib.sha256(diff).hexdigest(), len(diff)


_CON_INDEX = {}


def carpetas_con_index(raiz):
    """Carpetas de nivel 1 y 2 con index.html en el stage. Una sola llamada a git por repo: el
    hook tiene 30 s y un subproceso por archivo lo hacia vencer (y un hook vencido deja pasar)."""
    clave = str(Path(raiz).resolve())
    if clave not in _CON_INDEX:
        salida = git(raiz, 'ls-files', '--', ':(glob)*/index.html', ':(glob)*/*/index.html')
        _CON_INDEX[clave] = {r.rsplit('/', 1)[0] for r in salida.splitlines() if r}
    return _CON_INDEX[clave]


def es_tablero(raiz, carpeta):
    """Tiene index.html en disco o en el stage (borrarlo del disco no lo saca de la regla)."""
    return (Path(raiz) / carpeta / 'index.html').is_file() or carpeta in carpetas_con_index(raiz)


def carpeta_tablero(raiz, rel):
    """La carpeta del tablero al que pertenece `rel`, o None. La raiz del repo no es un tablero."""
    partes = rel.split('/')
    for n in NIVELES_TABLERO:
        if len(partes) > n and es_tablero(raiz, '/'.join(partes[:n])):
            return '/'.join(partes[:n])
    return None


def es_de_tablero(rel, carpeta):
    """`rel` forma parte de la pantalla del tablero en `carpeta`."""
    if not rel.startswith(carpeta + '/'):
        return False
    partes = rel[len(carpeta) + 1:].split('/')
    if len(partes) > 1 and partes[0] in FUERA_DE_LA_HUELLA:
        return False
    if len(partes) > 1 and (partes[0].startswith('data') or partes[0] == 'shared'):
        return True
    return Path(partes[-1]).suffix.lower() in EXT_CODIGO


def tableros_tocados(raiz, rutas):
    tocados = set()
    for r in rutas:
        c = carpeta_tablero(raiz, r)
        if c and es_de_tablero(r, c):
            tocados.add(c)
    return sorted(tocados)


def huella(lineas):
    return hashlib.sha256('\n'.join(sorted(lineas)).encode('utf-8')).hexdigest()


def huella_stage(raiz, carpeta):
    lineas = []
    for renglon in git(raiz, 'ls-files', '-s', '--', carpeta).splitlines():
        meta, rel = renglon.split('\t', 1)
        if es_de_tablero(rel, carpeta) and carpeta_tablero(raiz, rel) == carpeta:
            lineas.append(f'{rel} {meta.split()[1]}')
    return huella(lineas)


def huella_trabajo(raiz, carpeta):
    rels = [r for r in git(raiz, 'ls-files', '-co', '--exclude-standard', '--', carpeta).splitlines()
            if es_de_tablero(r, carpeta) and carpeta_tablero(raiz, r) == carpeta and (Path(raiz) / r).is_file()]
    rels = sorted(set(rels))
    if not rels:
        return huella([])
    blobs = git(raiz, 'hash-object', '--stdin-paths', entrada='\n'.join(rels) + '\n').split()
    return huella(f'{r} {b}' for r, b in zip(rels, blobs))


# ── Comandos ─────────────────────────────────────────────────────────────
def sellar_revision(raiz, args):
    h, n = hash_stage(raiz)
    if n == 0:
        sys.exit('sellar: no hay nada en stage')
    reporte = args[args.index('--reporte') + 1] if '--reporte' in args else None
    sello = {'hash': h, 'bytes': n, 'fecha': datetime.now().isoformat(timespec='seconds'),
             'reporte': reporte}
    (carpeta_estado(raiz) / 'revision.json').write_text(json.dumps(sello, indent=2), encoding='utf-8')
    print(f'revision sellada: {h[:12]} ({n} bytes en stage)')


def sellar_pruebas(raiz, args):
    if not args or args[0].startswith('--'):
        sys.exit('sellar: falta la carpeta del tablero')
    carpeta = Path(args[0]).resolve().relative_to(raiz).as_posix()
    if not es_tablero(raiz, carpeta):
        sys.exit(f'sellar: {carpeta} no tiene index.html; no es un tablero')
    evidencia = args[args.index('--evidencia') + 1] if '--evidencia' in args else None
    h = huella_trabajo(raiz, carpeta)
    sellos = leer_sello(raiz, 'pruebas.json')
    sellos[carpeta] = {'huella': h, 'fecha': datetime.now().isoformat(timespec='seconds'),
                       'evidencia': evidencia}
    (carpeta_estado(raiz) / 'pruebas.json').write_text(json.dumps(sellos, indent=2), encoding='utf-8')
    aviso = '' if h == huella_stage(raiz, carpeta) else \
        ' (ojo: lo probado no es igual al stage; haz git add de lo probado, incluidos archivos nuevos)'
    print(f'prueba sellada: {carpeta} {h[:12]}{aviso}')


def estado(raiz):
    rev = leer_sello(raiz, 'revision.json')
    h, n = hash_stage(raiz)
    print('revision:', 'sin sello' if not rev else
          f"{rev['fecha']} - {'VALE' if rev['hash'] == h else 'ya no coincide con el stage'}")
    for carpeta, s in leer_sello(raiz, 'pruebas.json').items():
        vale = s['huella'] == huella_stage(raiz, carpeta)
        print(f"pruebas {carpeta}: {s['fecha']} - {'VALE' if vale else 'ya no coincide con el stage'}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ('revision', 'pruebas', 'estado'):
        sys.exit(__doc__)
    try:
        raiz = raiz_repo()
    except RuntimeError:
        sys.exit('sellar: no estoy dentro de un repo de git')
    {'revision': lambda: sellar_revision(raiz, sys.argv[2:]),
     'pruebas': lambda: sellar_pruebas(raiz, sys.argv[2:]),
     'estado': lambda: estado(raiz)}[sys.argv[1]]()


if __name__ == '__main__':
    main()
