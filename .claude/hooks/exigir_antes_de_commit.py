#!/usr/bin/env python3
# ===============================================
# Hook PreToolUse: revision y pruebas antes de commit
# Author: Haz
# ===============================================
"""Niega un `git commit` del asistente si falta la revision o la prueba de lo que va a entrar.

Junta dos reglas en un solo arranque de Python (ya hay otros hooks en cada Bash):

    H1  el diff en stage tiene que tener el sello de `revisar-antes-de-commit`
        (`.claude/estado/revision.json` con el mismo hash).
    H2  si el stage toca un tablero de Main_Dev_Projects, ese tablero tiene que tener el sello
        de `probar-tablero` con la misma huella que el stage (`.claude/estado/pruebas.json`).

El sello es del stage, asi que tambien se niega lo que haria que se commitee otra cosa:
    - `git add/rm/mv/restore/reset/...` en el mismo comando antes del commit (el hook ve el stage
      de antes); el commit va en un comando aparte, despues de sellar;
    - `-a`, `-i`, `-o`, `-p`, `--pathspec-from-file` o rutas sueltas (commitean la copia de trabajo).

Lo que NO detiene:
    - un comando sin la palabra commit (sale en la primera linea, sin llamar a git);
    - un commit en otro repo (`git -C <otro>`, `cd <otro>`): solo vigila el repo donde vive;
    - un commit solo de documentos (.md, .txt, imagenes, pdf) fuera de `.claude/`;
    - `git commit --dry-run`.
Si algo falla al revisar un commit que apunta a este repo, niega (un control que falla abierto
no es control). El commit hecho a mano en la terminal no pasa por aqui: es la salida de Haz.

    python exigir_antes_de_commit.py --self-test     pruebas en repos temporales
"""
import sys

ENTRADA = sys.stdin.read() if __name__ == '__main__' and '--self-test' not in sys.argv else ''
if __name__ == '__main__' and '--self-test' not in sys.argv and 'commit' not in ENTRADA:
    sys.exit(0)

import json
import os
import re
import shlex
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import sellar  # noqa: E402
except Exception as e:  # noqa: BLE001 - sin sellar no hay control: si es un commit, se niega
    if 'git' in ENTRADA:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
                          'permissionDecisionReason': f'El hook no pudo cargar sellar.py ({e}): commit detenido.'}}))
        sys.exit(0)
    raise

RAIZ_HOOK = Path(__file__).resolve().parents[2]
PUNTUACION = set(';&|()<>')
CAMBIAN_DIR = {'cd', 'set-location', 'sl', 'pushd', 'push-location', 'chdir'}
DIR_DESCONOCIDO = {'popd', 'pop-location'}
SHELLS = {'bash', 'sh', 'cmd', 'powershell', 'pwsh', 'eval', 'invoke-expression', 'iex'}
ENVOLTORIOS = {'env', 'command', 'call', 'time', 'exec', 'nohup', 'sudo', 'xargs', 'nice', 'timeout',
               'then', 'do', 'else', 'if', 'while', 'until', '{', '}', '!'}
TOCAN_STAGE = {'add', 'stage', 'rm', 'mv', 'restore', 'reset', 'stash', 'apply', 'checkout', 'switch',
               'merge', 'cherry-pick', 'revert', 'pull', 'am', 'rebase', 'update-index', 'read-tree'}
VALOR_CORTO = set('mFCct')           # banderas cortas de commit que se comen un valor (-e no)
VALOR_PEGADO = set('Su')             # -S<llave>, -u<modo>: el valor va pegado
VALOR_LARGO = {'--message', '--file', '--author', '--date', '--reuse-message', '--reedit-message',
               '--fixup', '--squash', '--template', '--cleanup', '--trailer'}
COMMITEAN_OTRA_COSA = {'--all', '--include', '--only', '--pathspec-from-file', '--patch', '--interactive'}
# git ... commit en posicion de comando: al inicio, tras un separador o tras un envoltorio/asignacion.
# Dentro de un texto (echo "git commit", un string de Python) no cuenta.
RE_COMMIT_SUELTO = re.compile(
    r'(?:^|[;&|{\n`]\s*|\b(?:then|do|else|time|exec|nohup|sudo|xargs|env|command|eval|nice|timeout)\s+'
    r'(?:(?:-\S+|\d+)\s+)*|^\s*\w+=\S*\s+|[;&|\n]\s*\w+=\S*\s+)'
    r'["\']?(?:[\w.:/\\-]*[/\\])?git(?:\.exe)?["\']?\s+(?:-[Cc]\s+\S+\s+|--?[\w-]+(?:=\S+)?\s+)*commit\b',
    re.I)


class Rechazo(Exception):
    pass


# ── Leer el comando ──────────────────────────────────────────────────────
def resolver(base, texto):
    """Ruta de un `cd`/`-C`: ~, $HOME, $env:USERPROFILE, %USERPROFILE% y /c/... de Git Bash."""
    """None si no se puede saber (cd -, variables, o relativa sobre una base desconocida)."""
    if texto == '-':
        return None
    sin_casa = re.sub(r'^(~|\$HOME|\$env:USERPROFILE|%USERPROFILE%)', '', texto, flags=re.I)
    if re.search(r'[$%`(]', sin_casa):
        return None
    casa = str(Path.home()).replace('\\', '/')
    s = re.sub(r'^(~|\$HOME|\$env:USERPROFILE|%USERPROFILE%)(?=/|$)', casa, texto, flags=re.I)
    m = re.match(r'^/([a-zA-Z])(/.*|$)', s)
    if m:
        s = f'{m.group(1).upper()}:{m.group(2) or "/"}'
    p = Path(s)
    if p.is_absolute():
        return p
    return None if base is None else Path(base) / p


def segmentos(comando):
    lex = shlex.shlex(comando.replace('\\', '/').replace('\n', ' ; '), posix=True,
                      punctuation_chars=';&|()<>')
    lex.whitespace_split = True
    actual, saltar = [], False
    for t in lex:
        es_punt = set(t) <= PUNTUACION
        if saltar:
            saltar = False
            if not es_punt:
                continue
        if es_punt and ('<' in t or '>' in t):
            # redireccion (2>&1, > archivo): no separa; el numero de antes y el destino no son argumentos
            if actual and actual[-1].isdigit():
                actual.pop()
            saltar = True
            continue
        if es_punt:
            if actual:
                yield actual
            actual = []
        else:
            actual.append(t)
    if actual:
        yield actual


def leer_git(tokens, base):
    """(directorio, subcomando, argumentos) de `git [opciones globales] <sub> ...`."""
    d, i, alias = base, 1, False
    while tokens and tokens[-1] == '}':
        tokens = tokens[:-1]
    while i < len(tokens) and tokens[i].startswith('-'):
        t = tokens[i]
        if t == '-C' and i + 1 < len(tokens):
            d = resolver(d, tokens[i + 1]); i += 2; continue
        if t in ('-c', '--git-dir', '--work-tree', '--namespace') and i + 1 < len(tokens):
            if t != '-c':
                d = resolver(d, tokens[i + 1])
            elif tokens[i + 1].lower().startswith('alias.'):
                alias = True
            i += 2; continue
        if t.startswith(('--git-dir=', '--work-tree=')):
            d = resolver(d, t.split('=', 1)[1])
        i += 1
    sub = tokens[i] if i < len(tokens) else ''
    if alias:
        sub = 'commit?'
    elif sub and d is not None and sub not in TOCAN_STAGE and sub != 'commit':
        # un alias propio (git ci) que lleve commit cuenta como commit
        try:
            definicion = sellar.git(d, 'config', '--get', f'alias.{sub}')
        except (RuntimeError, OSError):
            definicion = ''
        if re.search(r'\bcommit\b', definicion):
            sub = 'commit?'
    return d, sub, tokens[i + 1:]


def recorrer(comando, base, eventos):
    """Junta en `eventos` cada git que toca el stage y cada commit, con su directorio, en orden."""
    for seg in segmentos(comando):
        envuelto = False
        while seg and (seg[0].lower() in ENVOLTORIOS or re.match(r'^\w+=', seg[0])
                       or (envuelto and (seg[0].startswith('-') or seg[0].isdigit()))):
            envuelto = envuelto or seg[0].lower() in ENVOLTORIOS
            seg = seg[1:]
        if not seg:
            continue
        nombre = seg[0].rsplit('/', 1)[-1].lower().removesuffix('.exe')
        if nombre in CAMBIAN_DIR:
            args = [t for t in seg[1:] if not t.startswith('-') or t == '-']
            base = resolver(base, args[0]) if args else None
        elif nombre in DIR_DESCONOCIDO:
            base = None
        elif nombre in SHELLS:
            for t in seg[1:]:
                if 'git' in t:
                    recorrer(t, base, eventos)
        elif nombre == 'git':
            d, sub, args = leer_git(seg, base)
            if sub in ('commit', 'commit?'):
                eventos.append(('commit', d, args if sub == 'commit' else ['--alias']))
            elif sub in TOCAN_STAGE:
                eventos.append(('stage', d, args))
    return eventos


def problema_de_args(args):
    """None si el commit toma solo el stage; 'dry' si es --dry-run; si no, el motivo."""
    dry, i = False, 0
    while i < len(args):
        t = args[i]
        if t == '--':
            return 'lleva rutas despues de `--`: commitea la copia de trabajo de esas rutas'
        if t == '--alias':
            return 'va por un alias de git: no se puede saber que commitea'
        if t.startswith('--'):
            nombre = t.split('=', 1)[0]
            riesgo = sorted(o for o in COMMITEAN_OTRA_COSA
                            if o == nombre or (len(nombre) >= 4 and o.startswith(nombre)))
            if riesgo:
                return f'lleva `{nombre}` ({riesgo[0]}): commitea algo distinto del stage revisado'
            if nombre == '--dry-run':
                dry = True
            if nombre in VALOR_LARGO and '=' not in t:
                i += 1
        elif t.startswith('-') and len(t) > 1:
            for j, letra in enumerate(t[1:]):
                if letra == 'a':
                    return 'lleva `-a`: commitea cambios que no estan en stage'
                if letra in 'iop':
                    return f'lleva `-{letra}`: commitea algo distinto del stage revisado'
                if letra in VALOR_CORTO:
                    if j == len(t) - 2:
                        i += 1
                    break
                if letra in VALOR_PEGADO:
                    break
        else:
            return f'lleva la ruta `{t}`: commitea la copia de trabajo de esa ruta, no el stage'
        i += 1
    return 'dry' if dry else None


# ── Decidir ──────────────────────────────────────────────────────────────
def dentro(p, raiz):
    try:
        Path(p).resolve().relative_to(Path(raiz).resolve())
        return True
    except (ValueError, OSError):
        return False


def raiz_de(d):
    try:
        return sellar.raiz_repo(d)
    except (RuntimeError, OSError):
        return None


def revisar_sellos(raiz):
    rutas = [r for r in sellar.git(raiz, 'diff', '--cached', '--name-only').splitlines() if r]
    if not rutas or all(sellar.es_solo_doc(r) for r in rutas):
        return None
    faltan = []
    h, _ = sellar.hash_stage(raiz)
    rev = sellar.leer_sello(raiz, 'revision.json')
    if rev.get('hash') != h:
        faltan.append('la revision de seguridad y codigo de este diff (skill revisar-antes-de-commit)'
                      + (': el stage cambio despues del sello' if rev else ''))
    pruebas = sellar.leer_sello(raiz, 'pruebas.json')
    for p in sorted({sellar.proyecto_de(r) for r in rutas if sellar.es_de_tablero(r)}):
        if not sellar.es_tablero(raiz, p):
            continue
        sello = pruebas.get(p) if isinstance(pruebas.get(p), dict) else {}
        if sello.get('huella') != sellar.huella_stage(raiz, p):
            faltan.append(f'la prueba en el navegador de {p} (skill probar-tablero)'
                          + (': lo que esta en stage no es lo que se probo' if sello else ''))
    if faltan:
        return ('Commit detenido. Falta: ' + '; '.join(faltan) + '. Corre lo que falta y vuelve a hacer '
                'git add si cambiaste algo. Si es un falso positivo, Haz puede commitear a mano en su terminal.')
    return None


def decidir(comando, cwd, vigilada=RAIZ_HOOK):
    """None si deja pasar; el motivo (texto) si niega."""
    vigilada = Path(vigilada)
    apunta_aqui = dentro(cwd, vigilada) or vigilada.name.lower() in comando.lower()
    try:
        return _decidir(comando, cwd, vigilada, apunta_aqui)
    except Rechazo as e:
        return str(e)
    except Exception as e:  # noqa: BLE001 - un control que truena no debe dejar pasar
        if apunta_aqui and re.search(r'\bgit\b', comando):
            return (f'No pude revisar este commit ({type(e).__name__}: {e}). Por seguridad se detiene: '
                    'corre git commit solo, con -m, en un comando aparte.')
        return None


def _decidir(comando, cwd, vigilada, apunta_aqui):
    try:
        eventos = recorrer(comando, Path(cwd), [])
    except ValueError:
        if apunta_aqui and re.search(r'\bgit\b', comando):
            raise Rechazo('No pude leer el comando (comillas sin cerrar). Corre git commit solo, con -m.')
        return None
    if apunta_aqui and RE_COMMIT_SUELTO.search(comando) and not any(e[0] == 'commit' for e in eventos):
        raise Rechazo('El comando parece hacer git commit pero no lo pude leer. Corre git commit solo, '
                      'sin prefijos ni envoltorios, con -m.')
    hubo_stage = False
    for tipo, d, args in eventos:
        raiz = raiz_de(d) if d is not None else None
        if raiz is None:
            if tipo == 'stage' and d is None:
                hubo_stage = True
            if tipo == 'commit' and (apunta_aqui or d is None):
                raise Rechazo(f'No pude saber en que repo corre el commit (`{d}`). Usa `git -C <ruta absoluta>` '
                              'o cd a una ruta que exista.')
            continue
        if raiz.resolve() != vigilada.resolve():
            continue
        if tipo == 'stage':
            hubo_stage = True
            continue
        problema = problema_de_args(args)
        if problema == 'dry':
            continue
        if problema:
            raise Rechazo(f'El commit {problema}. Haz git add de lo que va, corre /revisar-antes-de-commit '
                          'y commitea solo con -m.')
        if hubo_stage:
            raise Rechazo('El comando cambia el stage y commitea en el mismo paso: el hook solo ve el stage '
                          'de antes. Haz el git add, sella con /revisar-antes-de-commit y corre el commit aparte.')
        motivo = revisar_sellos(raiz)
        if motivo:
            raise Rechazo(motivo)
    return None


def main():
    try:
        datos = json.loads(ENTRADA)
        comando = (datos.get('tool_input') or {}).get('command') or ''
        motivo = decidir(comando, datos.get('cwd') or os.getcwd())
    except Exception as e:  # noqa: BLE001
        motivo = (f'El hook fallo al leer el comando ({type(e).__name__}): commit detenido.'
                  if re.search(r'\bgit\b', ENTRADA) else None)
    if motivo:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse',
                                                 'permissionDecision': 'deny',
                                                 'permissionDecisionReason': motivo}},
                         ensure_ascii=False))


# ── Pruebas ──────────────────────────────────────────────────────────────
def self_test():
    import subprocess
    import tempfile

    def sh(raiz, *args):
        s = subprocess.run(['git', '-C', str(raiz), *args], capture_output=True, text=True)
        if s.returncode:
            raise SystemExit(f'git {args}: {s.stdout}{s.stderr}')

    def escribe(raiz, rel, texto):
        p = Path(raiz) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding='utf-8')

    def sella(raiz, *args):
        subprocess.run([sys.executable, '-I', str(Path(__file__).with_name('sellar.py')), *args],
                       cwd=raiz, check=True, capture_output=True)

    casos = []
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as otro:
        r = Path(tmp)
        rf = str(r).replace('\\', '/')
        bash = '/' + rf[0].lower() + rf[2:]
        for d in (r, Path(otro)):
            sh(d, 'init', '-q')
            sh(d, 'config', 'user.email', 'prueba.local')  # sin @: no es un correo, git lo acepta igual
            sh(d, 'config', 'user.name', 'Prueba')
            sh(d, 'config', 'core.autocrlf', 'false')
        escribe(r, '.gitignore', '.claude/estado/\n')
        escribe(r, 'README.md', 'x\n')
        sh(r, 'add', '.')
        sh(r, 'commit', '-q', '-m', 'base')
        D = lambda c, cwd=r: decidir(c, cwd, r)  # noqa: E731
        niega = lambda c, txt='', cwd=r: txt in (D(c, cwd) or '') and D(c, cwd) is not None  # noqa: E731

        casos.append(('no es commit', D('git status') is None))
        casos.append(('echo con la palabra commit', D('echo "voy a hacer commit"') is None))
        escribe(r, 'NOTAS.md', 'nota\n'); sh(r, 'add', 'NOTAS.md')
        casos.append(('solo docs pasa', D('git commit -m "notas"') is None))
        sh(r, 'commit', '-q', '-m', 'notas')
        escribe(r, '.claude/skills/x/SKILL.md', 'regla\n'); sh(r, 'add', '.claude')
        casos.append(('.md de .claude pide revision', niega('git commit -m "skill"', 'revision')))
        sh(r, 'commit', '-q', '-m', 'skill')

        escribe(r, 'Dev_Coding/x.py', 'print(1)\n'); sh(r, 'add', '.')
        casos.append(('codigo sin revision se niega', niega('git commit -m "x"', 'revision')))
        casos.append(('--dry-run pasa', D('git commit --dry-run -m "x"') is None))
        casos.append(('--no-pager commit se vigila', niega('git --no-pager commit -m "x"', 'revision')))
        casos.append(('git.exe con ruta se vigila', niega('"/usr/bin/git.exe" commit -m x', 'revision')))
        sella(r, 'revision')
        casos.append(('con revision pasa', D('git commit -m "x"') is None))
        casos.append(('-m con texto -a pasa', D('git commit -m "-a no es bandera"') is None))
        casos.append(('--message valor pasa', D('git commit --message "con -o adentro"') is None))
        casos.append(('-am se niega', niega('git commit -am "x"', '-a')))
        casos.append(('-o se niega', niega('git commit -o -m x', '-o')))
        casos.append(('--include se niega', niega('git commit --include -m x', 'include')))
        casos.append(('ruta suelta se niega', niega('git commit -m x Dev_Coding/x.py', 'ruta')))
        casos.append(('add y commit juntos se niega', niega('git add . && git commit -m x', 'mismo paso')))
        casos.append(('commit seguido de otro con -a', niega('git commit -m a && git commit -am b', '-a')))
        (r / '.claude' / 'estado' / 'revision.json').write_text('{roto', encoding='utf-8')
        casos.append(('sello corrupto no truena y niega', niega('git commit -m x', 'revision')))
        sella(r, 'revision')
        casos.append(('VAR=x git commit -am se niega', niega('GIT_EDITOR=true git commit -am x', '-a')))
        casos.append(('if/then con -a se niega', niega('if true; then git commit -am x; fi', '-a')))
        casos.append(('PowerShell { } pasa con sello', D('if ($?) { git commit -m x }') is None))
        casos.append(('time git commit pasa con sello', D('time git commit -m x') is None))
        casos.append(('-e no come la ruta', niega('git commit -m x -e Dev_Coding/x.py', 'ruta')))
        casos.append(('-e -m pasa', D('git commit -e -m "x"') is None))
        casos.append(('git stage && commit se niega', niega('git stage . && git commit -m x', 'mismo paso')))
        casos.append(("bash -c 'git add' && commit se niega", niega("bash -c 'git add .' && git commit -m x", 'mismo paso')))
        casos.append(('2>&1 no es ruta', D('git commit -m x 2>&1') is None))
        casos.append(('2>/dev/null no es ruta', D('git commit -m x 2>/dev/null') is None))
        casos.append(('-uno y -S<llave> no se leen como -o/-a', D('git commit -uno -Sabcdef -m x') is None))
        casos.append(('--interact abreviado se niega', niega('git commit --interact -m x', 'interactive')))
        casos.append(('-c alias.x=commit se niega', niega('git -c alias.ci=commit ci -m x', 'alias')))
        sh(r, 'config', 'alias.ci', 'commit -a')
        casos.append(('alias propio git ci se niega', niega('git ci -m x', 'alias')))
        sh(r, 'config', '--unset', 'alias.ci')
        casos.append(('cd - antes del commit niega', niega(f'cd "{otro}" && cd - && git commit -m x', 'que repo', otro)))
        casos.append(('git log --grep commit pasa', D('git log --grep commit') is None))
        casos.append(('env -i con -a se niega', niega('env -i git commit -am x', '-a')))
        casos.append(('nice/timeout con -a se niega', niega('timeout 60 git commit -am x', '-a')))
        casos.append(('commit entre backticks se niega', niega('echo `git commit -am x`', 'no lo pude leer')))
        casos.append(('cd - y luego ruta absoluta pasa', D(f'cd - && cd "{r}" && git commit -m x') is None))
        casos.append(('echo "git commit" no se toca', D('echo "git commit -am x"') is None))
        (r / '.claude' / 'estado' / 'revision.json').write_text('{roto', encoding='utf-8')
        sella(r, 'revision')
        escribe(r, 'Dev_Coding/x.py', 'print(2)\n'); sh(r, 'add', '.')
        casos.append(('stage cambio despues del sello', niega('git commit -m "x"', 'cambio')))
        sh(r, 'commit', '-q', '-m', 'x')

        escribe(r, 'Main_Dev_Projects/T/index.html', '<html></html>\n')
        escribe(r, 'Main_Dev_Projects/T/app.js', 'let a = 1;\n')
        escribe(r, 'Main_Dev_Projects/T/data/dashboard.json', '{}\n')
        escribe(r, 'Main_Dev_Projects/T/data/CONTRATO.md', 'datos: inventados\n')
        sh(r, 'add', '.')
        sella(r, 'revision')
        m = D('git commit -m "t"') or ''
        casos.append(('tablero sin prueba se niega', 'probar-tablero' in m and 'revision' not in m))
        sella(r, 'pruebas', 'Main_Dev_Projects/T')
        casos.append(('tablero probado y revisado pasa', D('git commit -m "t"') is None))
        escribe(r, 'Main_Dev_Projects/T/data/dashboard.json', '{"a": 1}\n'); sh(r, 'add', '.')
        sella(r, 'revision')
        casos.append(('datos cambiaron: prueba vencida', niega('git commit -m "t"', 'probar-tablero')))
        sella(r, 'pruebas', 'Main_Dev_Projects/T')
        casos.append(('prueba de nuevo y pasa', D('git commit -m "t"') is None))
        escribe(r, 'Main_Dev_Projects/T/app.js', 'let a = 2;\n')
        casos.append(('cambio sin add no afecta el stage', D('git commit -m "t"') is None))
        sh(r, 'commit', '-q', '-m', 't')
        sh(r, 'checkout', '-q', '--', '.')

        escribe(r, 'Main_Dev_Projects/Logística/index.html', '<html></html>\n')
        sh(r, 'add', 'Main_Dev_Projects')
        sella(r, 'revision')
        casos.append(('tablero con acento pide prueba', niega('git commit -m "l"', 'probar-tablero')))
        sh(r, 'reset', '-q')

        escribe(r, 'Main_Dev_Projects/E/main.py', 'print(1)\n'); sh(r, 'add', 'Main_Dev_Projects/E')
        sella(r, 'revision')
        casos.append(('ETL sin index.html no pide prueba', D('git commit -m "e"') is None))
        sh(r, 'commit', '-q', '-m', 'e')
        escribe(r, 'Main_Dev_Projects/E/requirements.txt', 'pandas\n'); sh(r, 'add', '.')
        casos.append(('requirements.txt pide revision', niega('git commit -m r', 'revision')))
        sh(r, 'reset', '-q')
        escribe(r, 'Dev_Coding/y.py', 'print(3)\n'); sh(r, 'add', 'Dev_Coding')
        afuera = tempfile.gettempdir()
        casos.append(('commit en otro repo pasa', D(f'git -C "{otro}" commit -m "o"') is None))
        casos.append(('cd al otro repo pasa', D(f'cd "{otro}" && git commit -m "o"') is None))
        casos.append(('git -C a este repo se vigila', niega(f'git -C "{r}" commit -m x', 'revision', afuera)))
        casos.append(('cd /c/... de Git Bash se vigila', niega(f'cd {bash} && git commit -m x', 'revision', afuera)))
        casos.append(('cd X; de PowerShell se vigila', niega(f'cd "{r}"; git commit -m x', 'revision', afuera)))
        casos.append(('Set-Location se vigila', niega(f'Set-Location "{r}"; git commit -m x', 'revision', afuera)))
        casos.append(('bash -c se vigila', niega(f"bash -c 'git -C {rf} commit -m x'", 'revision', afuera)))
        casos.append(('carpeta sin git pasa', D('git commit -m "x"', cwd=afuera) is None))
        casos.append(('ruta que no existe hacia este repo niega',
                      niega(f'git -C "{r}/no-existe" commit -m x', 'que repo', afuera)))

    malos = [n for n, ok in casos if not ok]
    for n, ok in casos:
        print(('OK   ' if ok else 'FALLA') + ' ' + n)
    print(f'{len(casos) - len(malos)}/{len(casos)} casos bien')
    sys.exit(1 if malos else 0)


if __name__ == '__main__':
    self_test() if '--self-test' in sys.argv else main()
