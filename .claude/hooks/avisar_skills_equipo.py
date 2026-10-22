#!/usr/bin/env python3
"""Al iniciar la sesion trae lo ultimo del repo de skills del equipo y avisa que skill cambio.

Usos:

    (hook SessionStart)               git pull del clon y aviso de las skills que cambiaron
    python avisar_skills_equipo.py --estado          ultima corrida del hook y lo pendiente, sin avisar al harness
    python avisar_skills_equipo.py --marcar <skill>  la skill ya se llevo a la copia local
    python avisar_skills_equipo.py --marcar-todo     todas quedan al dia (primera vez)

No copia nada: las skills de ~/.claude/skills son COPIAS CORREGIDAS, y pisarlas con las del
equipo deshace las correcciones. El aviso dice que commits trajo cada skill para llevarlos a mano.
Las reglas del equipo no necesitan aviso: si CLAUDE.md las lee directo del clon, el pull basta.

El ultimo commit visto por skill vive en skills_equipo_estado.json, junto a este archivo. Cada corrida
del hook deja en skills_equipo_ultima.json cuando corrio, como le fue al pull y que encontro: sin ese
registro, una corrida sin cambios no se distingue de un hook que no corrio.
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
# El clon del repo de skills del equipo; en otra maquina se apunta con SKILLS_EQUIPO_CLON
CLON = Path(os.environ.get('SKILLS_EQUIPO_CLON', Path.home() / 'Documents' / 'GitHub' / 'repo-skills'))
SKILLS = 'plugins/logistics-bi/skills'
ESTADO = AQUI / 'skills_equipo_estado.json'
ULTIMA = AQUI / 'skills_equipo_ultima.json'


def git(*args, timeout=20):
    r = subprocess.run(['git', '-C', str(CLON), *args], capture_output=True, timeout=timeout)
    return r.returncode, r.stdout.decode('utf-8', 'replace').strip()


def ultimo_commit(skill):
    return git('log', '-1', '--format=%H', 'origin/main', '--', f'{SKILLS}/{skill}')[1]


def skills_equipo():
    _, txt = git('ls-tree', '--name-only', f'origin/main:{SKILLS}')
    return [s for s in txt.splitlines() if s]


def leer_estado():
    try:
        return json.loads(ESTADO.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def guardar_estado(estado):
    ESTADO.write_text(json.dumps(estado, indent=1, sort_keys=True), encoding='utf-8')


def pendientes(estado):
    """{skill: [renglones de commits nuevos]} de las skills que cambiaron desde la ultima marca."""
    out = {}
    for s in skills_equipo():
        visto = estado.get(s)
        if visto == ultimo_commit(s):
            continue
        rango = f'{visto}..origin/main' if visto else 'origin/main'
        _, log = git('log', '--format=%h %ad %s', '--date=short', rango, '--', f'{SKILLS}/{s}')
        out[s] = log.splitlines()[:5] or ['(skill nueva en el equipo)']
    return out


def main():
    if not CLON.is_dir():
        return
    estado = leer_estado()

    if len(sys.argv) > 1:
        if sys.argv[1] == '--marcar-todo':
            git('fetch', '--quiet', 'origin')
            guardar_estado({s: ultimo_commit(s) for s in skills_equipo()})
            print('todas las skills quedan al dia')
        elif sys.argv[1] == '--marcar' and len(sys.argv) > 2:
            estado[sys.argv[2]] = ultimo_commit(sys.argv[2])
            guardar_estado(estado)
            print(f'{sys.argv[2]} al dia')
        elif sys.argv[1] == '--estado':
            try:
                u = json.loads(ULTIMA.read_text(encoding='utf-8'))
                print(f'Ultima corrida del hook: {u["fecha"]} - pull: {u["pull"]} - clon en {u["commit"]}')
                print('  encontro: ' + (', '.join(u['pendientes']) or 'nada nuevo'))
            except (OSError, ValueError, KeyError):
                print('Ultima corrida del hook: sin registro (todavia no corre al iniciar una sesion)')
            pend = pendientes(estado)
            print('Pendiente ahora:' + ('' if pend else ' nada'))
            for s, log in pend.items():
                print(f'  {s}', *(f'    {x}' for x in log), sep='\n')
        return

    # Hook: un pull que falle (sin red, clon con cambios) no detiene la sesion
    try:
        codigo, salida = git('pull', '--quiet', '--ff-only', timeout=25)
        resultado_pull = 'ok' if codigo == 0 else 'fallo: ' + (salida.splitlines() or ['sin detalle'])[-1][:120]
    except subprocess.TimeoutExpired:
        resultado_pull = 'fallo: tardo mas de 25 s'
    pend = pendientes(estado)
    try:
        ULTIMA.write_text(json.dumps({
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'pull': resultado_pull,
            'commit': git('rev-parse', '--short', 'HEAD')[1], 'pendientes': sorted(pend),
        }, indent=1), encoding='utf-8')
    except OSError:
        pass   # sin registro, el aviso de abajo sigue saliendo
    if not pend:
        return
    detalle = '\n'.join(f'- {s}: ' + '; '.join(log) for s, log in pend.items())
    print(json.dumps({
        'systemMessage': f'Skills del equipo con cambios por llevar a la copia local: {", ".join(pend)}',
        'hookSpecificOutput': {
            'hookEventName': 'SessionStart',
            'additionalContext': (
                'El repo de skills del equipo trae cambios que todavia no estan en las copias corregidas '
                'de ~/.claude/skills. No pisar la copia con la del equipo: llevar solo esos commits '
                '(git diff <commit>~1 <commit> -- plugins/logistics-bi/skills/<skill>) y luego correr '
                f'`python ~/.claude/hooks/avisar_skills_equipo.py --marcar <skill>`.\n{detalle}'),
        },
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
