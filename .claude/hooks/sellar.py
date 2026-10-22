#!/usr/bin/env python3
# Author: Haz
"""Deja el sello de que una revision o una prueba se hizo sobre una version exacta.

Usos:

    python sellar.py revision [--reporte <ruta>]   sella el hash de `git diff --cached`
    python sellar.py pruebas <archivo> [...]        sella el hash de cada archivo probado
    python sellar.py estado                         muestra los sellos actuales

Los sellos viven en `.claude/estado/` del repo (ignorada por git). Los leen los hooks
`exigir_revision_commit.py` y `exigir_pruebas_tablero.py`: si el diff o el archivo cambio
despues del sello, el sello ya no vale. No revisa ni prueba nada: solo anota.
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# ── Rutas ────────────────────────────────────────────────────────────────
def raiz_repo():
    salida = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                            capture_output=True, text=True)
    if salida.returncode != 0:
        sys.exit('sellar: no estoy dentro de un repo de git')
    return Path(salida.stdout.strip())


def carpeta_estado(raiz):
    d = raiz / '.claude' / 'estado'
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── Hashes ───────────────────────────────────────────────────────────────
def hash_stage(raiz):
    diff = subprocess.run(['git', 'diff', '--cached', '--binary'], cwd=raiz,
                          capture_output=True).stdout
    return hashlib.sha256(diff).hexdigest(), len(diff)


def hash_archivo(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


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


def sellar_pruebas(raiz, archivos):
    if not archivos:
        sys.exit('sellar: faltan los archivos probados')
    ruta = carpeta_estado(raiz) / 'pruebas.json'
    sellos = json.loads(ruta.read_text(encoding='utf-8')) if ruta.is_file() else {}
    for a in archivos:
        rel = Path(a).resolve().relative_to(raiz).as_posix()
        sellos[rel] = {'hash': hash_archivo(a), 'fecha': datetime.now().isoformat(timespec='seconds')}
        print(f'prueba sellada: {rel}')
    ruta.write_text(json.dumps(sellos, indent=2), encoding='utf-8')


def estado(raiz):
    for nombre in ('revision.json', 'pruebas.json'):
        ruta = carpeta_estado(raiz) / nombre
        print(f'== {nombre}')
        print(ruta.read_text(encoding='utf-8') if ruta.is_file() else '(sin sello)')


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ('revision', 'pruebas', 'estado'):
        sys.exit(__doc__)
    raiz = raiz_repo()
    {'revision': lambda: sellar_revision(raiz, sys.argv[2:]),
     'pruebas': lambda: sellar_pruebas(raiz, sys.argv[2:]),
     'estado': lambda: estado(raiz)}[sys.argv[1]]()


if __name__ == '__main__':
    main()
