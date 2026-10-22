#!/usr/bin/env python3
# Made by: Hazzard
# Instala el candado personal (pre-commit y commit-msg) en los repos personales.
"""
    python instalar.py                 instala en BI_DataNexus y OblivionCode (los que estén clonados)
    python instalar.py <ruta-repo>     instala en ese repo
    python instalar.py --quitar [...]  lo quita y deja el respaldo que hubiera

Los repos personales usan `.git/hooks` (por `includeIf` → `~/.gitconfig-personal`), así que el candado
se escribe ahí. Si ya hay un hook que no es el candado, se respalda como `<hook>.antes-del-candado`.
El wrapper busca el script primero en `~/.claude/skills` (la versión que se edita) y si no está, en la
copia del propio repo (`.claude/skills/candado-personal`), para que funcione en cualquier clon.
"""
import stat
import sys
from pathlib import Path

REPOS = Path.home() / 'Documents' / 'GitHub'
PERSONALES = ['BI_DataNexus', 'OblivionCode']
MARCA = '# candado-personal'
WRAPPER = """#!/bin/sh
{marca} ({hook}). Lo instala candado-personal/scripts/instalar.py; no editar a mano.
RAIZ="$(git rev-parse --show-toplevel)"
S="$HOME/.claude/skills/candado-personal/scripts/candado_personal.py"
[ -f "$S" ] || S="$RAIZ/.claude/skills/candado-personal/scripts/candado_personal.py"
if [ ! -f "$S" ]; then
  echo "candado-personal: no encuentro candado_personal.py; el commit sigue SIN revisar." >&2
  exit 0
fi
PY="$(command -v python || command -v python3 || command -v py)"
exec "$PY" -I "$S" {hook} "$@"
"""

def instalar(repo, quitar=False):
    hooks = Path(repo) / '.git' / 'hooks'
    if not hooks.is_dir():
        return f'{repo}: no es un repo de git (no hay .git/hooks)'
    hechos = []
    for hook in ('pre-commit', 'commit-msg'):
        f = hooks / hook
        respaldo = hooks / f'{hook}.antes-del-candado'
        actual = f.read_text(encoding='utf-8', errors='replace') if f.is_file() else ''
        if quitar:
            if MARCA in actual:
                f.unlink()
                if respaldo.is_file():
                    respaldo.rename(f)
                hechos.append(f'{hook} quitado')
            continue
        if actual and MARCA not in actual:
            f.rename(respaldo)
            hechos.append(f'{hook} anterior respaldado')
        f.write_text(WRAPPER.format(marca=MARCA, hook=hook), encoding='utf-8', newline='\n')
        f.chmod(f.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        hechos.append(f'{hook} instalado')
    return f'{Path(repo).name}: ' + ', '.join(hechos or ['nada que hacer'])

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    destinos = args or [REPOS / r for r in PERSONALES if (REPOS / r / '.git').is_dir()]
    for d in destinos:
        print(instalar(d, quitar='--quitar' in sys.argv))
