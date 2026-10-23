#!/usr/bin/env python3
# ===============================================
# Espejo del flujo de 4 pasos entre repos personales
# Author: Haz
# ===============================================
"""Copia las piezas del flujo (PRD, revision, pruebas, auditor) de BI_DataNexus a OblivionCode.

    python sincronizar_repo.py --revisar     solo dice que difiere
    python sincronizar_repo.py               copia lo que difiere

La fuente es BI_DataNexus: ahi se editan. Estas piezas viven solo en los repos (no en
~/.claude/skills), asi que `copiar_skills.py` no las toca. No hace commit.
"""
import filecmp
import shutil
import sys
from pathlib import Path

REPOS = Path.home() / 'Documents' / 'GitHub'
ORIGEN = REPOS / 'BI_DataNexus' / '.claude'
DESTINO = REPOS / 'OblivionCode' / '.claude'
PIEZAS = [
    'skills/entrevista-prd-personal', 'skills/escribir-prd-personal', 'skills/revisar-antes-de-commit-personal',
    'skills/probar-tablero-personal', 'skills/auditar-entrega-personal',
    'agents/revisor-seguridad-personal.md', 'agents/revisor-codigo-personal.md', 'agents/auditor-personal.md',
    'hooks/sellar.py', 'hooks/exigir_antes_de_commit.py', 'hooks/sincronizar_repo.py',
    'settings.json', '.gitignore',  # launch.json no: cada repo tiene sus tableros
]


def archivos(pieza):
    p = ORIGEN / pieza
    return [p] if p.is_file() else sorted(x for x in p.rglob('*') if x.is_file() and '__pycache__' not in x.parts)


def main():
    solo_revisar = '--revisar' in sys.argv
    distintos = []
    for pieza in PIEZAS:
        for src in archivos(pieza):
            dst = DESTINO / src.relative_to(ORIGEN)
            if not dst.is_file() or not filecmp.cmp(src, dst, shallow=False):
                distintos.append(src.relative_to(ORIGEN).as_posix())
                if not solo_revisar:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
    accion = 'difieren' if solo_revisar else 'copiados'
    print(f'{len(distintos)} {accion}' + (':\n  ' + '\n  '.join(distintos) if distintos else ''))


if __name__ == '__main__':
    main()
