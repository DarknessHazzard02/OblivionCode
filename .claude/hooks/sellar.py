#!/usr/bin/env python3
# ===============================================
# Sellos de revision y de pruebas
# Author: Haz
# ===============================================
"""Deja el sello de que una revision o una prueba se hizo sobre una version exacta.

Usos:

    python sellar.py revision [--reporte <ruta>]               sella el diff en stage
    python sellar.py pruebas <carpeta_tablero> [--evidencia <ruta>]
                                                             sella la huella del tablero probado
    python sellar.py estado                                  muestra los sellos y si siguen valiendo

Los sellos viven en `.claude/estado/` del repo (ignorada por git) y los lee el hook
`exigir_antes_de_commit.py`. Si el diff o el tablero cambian despues del sello, el sello ya no vale.
Este script no revisa ni prueba nada: solo anota. Lo llaman las skills `revisar-antes-de-commit`
y `probar-tablero` despues de hacer su trabajo.

La huella de un tablero es el blob de git de cada archivo que lo forma (html, js y css de la raiz
del proyecto, `data*/` y `shared/`). Al sellar se calcula sobre la copia de trabajo; el hook la
calcula sobre el stage. Coinciden solo si lo que se va a commitear es lo que se probo.
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

EXT_CODIGO = {'.html', '.js', '.css'}
EXT_DOCS = {'.md', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.pdf'}
CARPETA_PROYECTOS = 'Main_Dev_Projects'


# ── Git ──────────────────────────────────────────────────────────────────
def git(raiz, *args, entrada=None, binario=False):
    # quotepath=off: con acentos en la ruta git la devolveria entre comillas y con escapes octales
    salida = subprocess.run(['git', '-C', str(raiz), '-c', 'core.quotepath=off', *args], input=entrada,
                            capture_output=True, text=not binario,
                            encoding=None if binario else 'utf-8')
    if salida.returncode != 0:
        raise RuntimeError(f'git {" ".join(args)}: {salida.stderr}')
    return salida.stdout


def raiz_repo(desde='.'):
    return Path(git(desde, 'rev-parse', '--show-toplevel').strip())


def carpeta_estado(raiz):
    d = Path(raiz) / '.claude' / 'estado'
    d.mkdir(parents=True, exist_ok=True)
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
    """Documento que no pide revision. Lo de .claude/ no cuenta: son instrucciones del asistente."""
    nombre = Path(rel).name.lower()
    if '.claude' in rel.split('/') or nombre == 'claude.md' or nombre.startswith('requirements'):
        return False
    return Path(rel).suffix.lower() in EXT_DOCS


# ── Huellas ──────────────────────────────────────────────────────────────
def hash_stage(raiz):
    diff = git(raiz, 'diff', '--cached', '--binary', binario=True)
    return hashlib.sha256(diff).hexdigest(), len(diff)


def es_de_tablero(rel):
    """`Main_Dev_Projects/<P>/...` que forma parte de la pantalla de un tablero."""
    partes = rel.split('/')
    if len(partes) < 3 or partes[0] != CARPETA_PROYECTOS:
        return False
    if len(partes) == 3:
        return Path(partes[2]).suffix.lower() in EXT_CODIGO
    return partes[2].startswith('data') or partes[2] == 'shared'


def proyecto_de(rel):
    return '/'.join(rel.split('/')[:2])


def huella(lineas):
    return hashlib.sha256('\n'.join(sorted(lineas)).encode('utf-8')).hexdigest()


def huella_stage(raiz, proyecto):
    lineas = []
    for renglon in git(raiz, 'ls-files', '-s', '--', proyecto).splitlines():
        meta, rel = renglon.split('\t', 1)
        if es_de_tablero(rel):
            lineas.append(f'{rel} {meta.split()[1]}')
    return huella(lineas)


def huella_trabajo(raiz, proyecto):
    rels = [r for r in git(raiz, 'ls-files', '-co', '--exclude-standard', '--', proyecto).splitlines()
            if es_de_tablero(r) and (Path(raiz) / r).is_file()]
    rels = sorted(set(rels))
    if not rels:
        return huella([])
    blobs = git(raiz, 'hash-object', '--stdin-paths', entrada='\n'.join(rels) + '\n').split()
    return huella(f'{r} {b}' for r, b in zip(rels, blobs))


def es_tablero(raiz, proyecto):
    return (Path(raiz) / proyecto / 'index.html').is_file()


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
        sys.exit('sellar: falta la carpeta del tablero (Main_Dev_Projects/<Proyecto>)')
    proyecto = Path(args[0]).resolve().relative_to(raiz).as_posix()
    if not es_tablero(raiz, proyecto):
        sys.exit(f'sellar: {proyecto} no tiene index.html; no es un tablero')
    evidencia = args[args.index('--evidencia') + 1] if '--evidencia' in args else None
    h = huella_trabajo(raiz, proyecto)
    sellos = leer_sello(raiz, 'pruebas.json')
    sellos[proyecto] = {'huella': h, 'fecha': datetime.now().isoformat(timespec='seconds'),
                        'evidencia': evidencia}
    (carpeta_estado(raiz) / 'pruebas.json').write_text(json.dumps(sellos, indent=2), encoding='utf-8')
    aviso = '' if h == huella_stage(raiz, proyecto) else \
        ' (ojo: lo probado no es igual al stage; haz git add de lo probado, incluidos archivos nuevos)'
    print(f'prueba sellada: {proyecto} {h[:12]}{aviso}')


def estado(raiz):
    rev = leer_sello(raiz, 'revision.json')
    h, n = hash_stage(raiz)
    print('revision:', 'sin sello' if not rev else
          f"{rev['fecha']} - {'VALE' if rev['hash'] == h else 'ya no coincide con el stage'}")
    for proyecto, s in leer_sello(raiz, 'pruebas.json').items():
        vale = s['huella'] == huella_stage(raiz, proyecto)
        print(f"pruebas {proyecto}: {s['fecha']} - {'VALE' if vale else 'ya no coincide con el stage'}")


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
