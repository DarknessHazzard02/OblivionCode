#!/usr/bin/env python3
"""Copia las skills locales a los repos personales, limpias de todo lo que no debe salir.

Usos:

    python copiar_skills.py --todas        copia (o recopia) todas las skills a todos los destinos
    python copiar_skills.py --revisar      solo dice que quedaria sucio, sin copiar
    (hook PostToolUse)                     recibe por stdin el JSON de Write/Edit; si el archivo
                                           es de ~/.claude/skills/<skill>/, recopia esa skill

La limpieza no esta en este archivo: vive en `copiar_skills_reglas.json`, junto a el, que es
PRIVADO (nombra justo lo que hay que quitar) y nunca se sube. Sin ese archivo el script no copia
nada: copiar sin limpiar es peor que no copiar.

El JSON trae:
    excluir      skills que nunca salen de la maquina
    reglas       [patron, reemplazo] en orden
    prohibido    {motivo: patron} que no puede quedar despues de limpiar
    correo_ok    correos que son sintaxis, no personas
    parrafo_caso parrafos que se quitan enteros
    titulo_caso  encabezados a los que se les quita la cola

Despues de limpiar, la revision busca lo prohibido; si encuentra algo, NO copia esa skill y dice
que linea fallo, para agregar la regla que falta. No hace commit ni push.
"""
import json
import re
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ORIGEN = Path.home() / '.claude' / 'skills'
REPOS = Path.home() / 'Documents' / 'GitHub'
DESTINOS = [REPOS / 'BI_DataNexus' / '.claude' / 'skills',
            REPOS / 'OblivionCode' / '.claude' / 'skills']
REGLAS_JSON = AQUI / 'copiar_skills_reglas.json'
TEXTO = {'.md', '.py', '.txt', '.cmd', '.html', '.css', '.json', '.ps1', '.sh', '.yml', '.yaml'}


def cargar():
    if not REGLAS_JSON.is_file():
        return None
    d = json.loads(REGLAS_JSON.read_text(encoding='utf-8'))
    return {
        'excluir': set(d.get('excluir', [])),
        'reglas': [(re.compile(p), r) for p, r in d['reglas']],
        'prohibido': {k: re.compile(v) for k, v in d['prohibido'].items()},
        'correo_ok': re.compile(d['correo_ok']),
        'parrafo_caso': re.compile(d['parrafo_caso'], re.I),
        'titulo_caso': re.compile(d['titulo_caso']),
    }


def quitar_casos(texto, cfg):
    """Quita los parrafos (bloques separados por linea en blanco) que cuentan un caso."""
    bloques = re.split(r'(\n[ \t>]*\n)', texto)
    texto = ''.join(b for b in bloques if not (cfg['parrafo_caso'].match(b) and '```' not in b))
    texto = cfg['titulo_caso'].sub(r'\1', texto)
    return re.sub(r'\n{3,}', '\n\n', texto)


def limpiar(texto, cfg):
    texto = quitar_casos(texto, cfg)
    for patron, repl in cfg['reglas']:
        texto = patron.sub(repl, texto)
    return texto


def revisar(texto, cfg):
    """Lista de (linea, motivo, fragmento) de lo que sigue sin poder salir."""
    hallazgos = []
    for n, linea in enumerate(texto.splitlines(), 1):
        for motivo, patron in cfg['prohibido'].items():
            for m in patron.finditer(linea):
                if motivo == 'correo real' and cfg['correo_ok'].search(m.group(0)):
                    continue
                hallazgos.append((n, motivo, m.group(0)))
    return hallazgos


def copiar(skill, cfg, solo_revisar=False):
    """(ok, mensajes). Limpia y revisa todos los archivos; copia solo si todos pasan."""
    if skill in cfg['excluir']:
        return True, [f'{skill}: excluida, no sale de la maquina']
    src = ORIGEN / skill
    if not src.is_dir():
        return False, [f'{skill}: no existe en {ORIGEN}']
    salida, problemas = {}, []
    for f in sorted(src.rglob('*')):
        if not f.is_file() or '__pycache__' in f.parts:
            continue
        rel = f.relative_to(src)
        if f.suffix.lower() in TEXTO:
            limpio = limpiar(f.read_text(encoding='utf-8', errors='replace'), cfg)
            problemas += [f'{skill}/{rel.as_posix()}:{n}: {motivo} -> {frag}' for n, motivo, frag in revisar(limpio, cfg)]
            salida[rel] = limpio.encode('utf-8')
        else:
            salida[rel] = f.read_bytes()
    if problemas:
        return False, problemas
    if solo_revisar:
        return True, [f'{skill}: limpia ({len(salida)} archivos)']
    hechos = []
    for raiz in DESTINOS:
        if not raiz.parent.parent.is_dir():          # el repo no esta clonado en esta maquina
            continue
        dst = raiz / skill
        if dst.exists():
            shutil.rmtree(dst)
        for rel, contenido in salida.items():
            (dst / rel).parent.mkdir(parents=True, exist_ok=True)
            (dst / rel).write_bytes(contenido)
        hechos.append(raiz.parent.parent.name)
    return True, [f'{skill}: copiada a {", ".join(hechos)} ({len(salida)} archivos)']


def todas(cfg, solo_revisar=False):
    fallas = 0
    for d in sorted(p.name for p in ORIGEN.iterdir() if p.is_dir()):
        ok, msgs = copiar(d, cfg, solo_revisar)
        fallas += not ok
        for m in msgs[:40]:
            print(('  ' if ok else '  X ') + m)
    return fallas


def hook(cfg):
    try:
        datos = json.load(sys.stdin)
    except Exception:
        return 0
    ruta = (datos.get('tool_input') or {}).get('file_path') or ''
    try:
        rel = Path(ruta).resolve().relative_to(ORIGEN.resolve())
    except ValueError:
        return 0                      # no es una skill: nada que hacer
    skill = rel.parts[0]
    if cfg is None:
        aviso = f'Skill "{skill}" NO se copio: falta {REGLAS_JSON.name} (las reglas de limpieza).'
    else:
        ok, msgs = copiar(skill, cfg)
        if ok:
            aviso = f'Skill "{skill}": {msgs[0].split(": ", 1)[1]} (sin commit).'
        else:
            aviso = (f'Skill "{skill}" NO se copio a los repos personales: quedan cosas que no deben salir. '
                     f'Agrega la regla que falta en {REGLAS_JSON.name}:\n' + '\n'.join(msgs[:15]))
    print(json.dumps({'systemMessage': aviso,
                      'hookSpecificOutput': {'hookEventName': 'PostToolUse', 'additionalContext': aviso}}))
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    cfg = cargar()
    if '--todas' in sys.argv or '--revisar' in sys.argv:
        if cfg is None:
            print(f'Falta {REGLAS_JSON}: sin reglas de limpieza no se copia nada.')
            sys.exit(1)
        sys.exit(1 if todas(cfg, solo_revisar='--revisar' in sys.argv) else 0)
    sys.exit(hook(cfg))
