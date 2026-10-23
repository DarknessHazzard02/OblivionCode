#!/usr/bin/env python3
# ===============================================
# Hook PreToolUse: revision y pruebas antes de commit
# Author: Haz
# ===============================================
"""Niega un `git commit` del asistente si falta la revision o la prueba de lo que va a entrar.

Paso 3 del flujo de 4 pasos (skill estandar-personal). Junta dos reglas en un solo arranque de
Python (ya hay otros hooks en cada Bash):

    H1  el diff en stage tiene que tener el sello de `revisar-antes-de-commit-personal`
        (`.claude/estado/revision.json` con el mismo hash).
    H2  si el stage toca un tablero (carpeta de primer o segundo nivel con index.html), ese
        tablero tiene que tener el sello de `probar-tablero-personal` con la misma huella que el stage
        (`.claude/estado/pruebas.json`).

Donde vigila:
    - instalado en `~/.claude/hooks/` (lo normal, ONBOARDING): todo repo de git donde el
      asistente haga commit;
    - instalado en `<repo>/.claude/hooks/`: solo ese repo.

El sello es del stage, asi que tambien se niega lo que haria que se commitee otra cosa:
    - `git add/rm/mv/restore/reset/...` en el mismo comando antes del commit (el hook ve el stage
      de antes); el commit va en un comando aparte, despues de sellar;
    - `-a`, `-i`, `-o`, `-p`, `--pathspec-from-file` o rutas sueltas (commitean la copia de trabajo).

Lo que NO detiene:
    - un comando sin la palabra git (sale en la primera linea, sin llamar a git);
    - instalado en un repo: un commit en otro repo (`git -C <otro>`, `cd <otro>`);
    - un commit solo de documentos (.md, .txt, imagenes, pdf) fuera de `.claude/`, `skills/` y
      `agents/`, salvo CLAUDE.md, SKILL.md, REGLAS-EQUIPO.md y requirements*.txt (ver sellar.es_solo_doc);
    - `git commit --dry-run`;
    - comandos que crean commits sin ser `commit` (`merge`, `pull`, `rebase`, `cherry-pick`,
      `revert`, `am`, o `commit-tree` con `update-ref`): solo cuentan como cambio de stage;
    - un interprete que arma el comando por dentro (`python -c "os.system(...)"`), o git llamado
      por una variable o una expansion (`$X commit`, `g$()it commit`).
Y niega de mas (falla cerrado): un heredoc o un texto cuyo renglon empieza con `git commit` (un
script que se escribe con `cat > x.sh <<EOF`, el cuerpo de un PR con pasos). Esos archivos se
escriben con el editor, no por la terminal.
Es un control de proceso, no una frontera de seguridad: el sello no prueba que la revision se
hizo, solo que alguien la sello sobre ese diff exacto.
Si algo falla al revisar un commit que apunta a un repo vigilado, niega (un control que falla
abierto no es control). El commit hecho a mano en la terminal no pasa por aqui: es la salida de
la persona. Aflojar o quitar este hook es decision de Haz.

    python exigir_antes_de_commit.py --self-test     pruebas en repos temporales
"""
import json
import re
import sys


def se_puede_saltar(texto):
    """Sin la palabra git no hay commit posible. No basta con buscar 'commit': un alias
    (`git ci`) o unas comillas (`git c''ommit`) hacen commit sin escribir la palabra.
    Se mira solo el comando, no el cwd: bajo una carpeta `GitHub` el cwd siempre dice "git" y el
    hook corria completo (con llamadas a git) en cada comando. Si la entrada no se lee, se mira toda."""
    try:
        datos = json.loads(texto)
        comando = ((datos.get('tool_input') or datos).get('command') or '') if isinstance(datos, dict) else texto
    except ValueError:
        comando = texto
    limpio = re.sub(r'[\'"\\^`]', '', str(comando).lower())
    return 'git' not in limpio and not re.search(r'\b(powershell|pwsh)\b', limpio)


ENTRADA = sys.stdin.read() if __name__ == '__main__' and '--self-test' not in sys.argv else ''
if __name__ == '__main__' and '--self-test' not in sys.argv and se_puede_saltar(ENTRADA):
    sys.exit(0)

import os
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


def repo_del_hook():
    """El repo si el hook vive en `<repo>/.claude/hooks/`; None si es la instalacion global."""
    carpeta = Path(__file__).resolve().parent
    raiz = carpeta.parent.parent
    if carpeta.parent.name == '.claude' and raiz != Path.home().resolve() and (raiz / '.git').exists():
        return raiz
    return None


RAIZ_HOOK = repo_del_hook()
PUNTUACION = set(';&|()<>')
CAMBIAN_DIR = {'cd', 'set-location', 'sl', 'pushd', 'push-location', 'chdir'}
DIR_DESCONOCIDO = {'popd', 'pop-location'}
SHELLS = {'bash', 'sh', 'cmd', 'powershell', 'pwsh', 'eval', 'invoke-expression', 'iex'}
ENVOLTORIOS = {'env', 'command', 'call', 'time', 'exec', 'nohup', 'sudo', 'xargs', 'nice', 'timeout', 'start',
               'start-process', 'saps',
               'then', 'do', 'else', 'if', 'while', 'until', '{', '}', '!'}
TOCAN_STAGE = {'add', 'stage', 'rm', 'mv', 'restore', 'reset', 'stash', 'apply', 'checkout', 'switch',
               'merge', 'cherry-pick', 'revert', 'pull', 'am', 'rebase', 'update-index', 'read-tree'}
VALOR_CORTO = set('mFCct')           # banderas cortas de commit que se comen un valor (-e no)
VALOR_PEGADO = set('Su')             # -S<llave>, -u<modo>: el valor va pegado
VALOR_LARGO = {'--message', '--file', '--author', '--date', '--reuse-message', '--reedit-message',
               '--fixup', '--squash', '--template', '--cleanup', '--trailer'}
NATIVOS = {'status', 'log', 'diff', 'show', 'branch', 'fetch', 'push', 'remote', 'config', 'rev-parse',
           'ls-files', 'ls-tree', 'ls-remote', 'init', 'clone', 'tag', 'grep', 'blame', 'describe',
           'worktree', 'submodule', 'archive', 'cat-file', 'hash-object', 'notes', 'bisect', 'clean',
           'gc', 'reflog', 'shortlog', 'help', 'version', 'commit-tree', 'for-each-ref', 'symbolic-ref',
           'write-tree', 'format-patch', 'range-diff', 'sparse-checkout', 'maintenance', 'lfs',
           'rev-list', 'name-rev', 'whatchanged', 'difftool', 'mergetool', 'var', 'count-objects',
           'check-ignore', 'check-attr', 'merge-base', 'show-ref', 'cherry', 'fsck', 'prune', 'show-branch',
           'diff-tree', 'diff-index', 'diff-files', 'bundle', 'verify-commit', 'verify-tag', 'mktag'}
# Variables que cambian el indice, el repo o la config que lee el commit. Con un commit en el
# comando se buscan en cualquier forma (VAR=, export, $env:, Set-Item, SetEnvironmentVariable).
# GIT_SSH_COMMAND, GIT_TRACE y demas no cambian lo que se commitea: pasan.
RE_ENTORNO_GIT = re.compile(
    r'GIT_(?:INDEX_FILE|DIR|WORK_TREE|CONFIG\w*|OBJECT_DIRECTORY|ALTERNATE_OBJECT_DIRECTORIES|'
    r'NAMESPACE|COMMON_DIR)\b', re.I)
ECO = {'echo', 'printf', 'write-host', 'write-output', 'write-verbose', 'write-information'}
LECTURA = {'man', 'tldr', 'grep', 'rg', 'select-string', 'sls', 'findstr', 'cat', 'less', 'more',
           'get-content', 'gc', 'type', 'head', 'tail', 'wc', 'which', 'where', 'get-command'}
ENTORNO_INOFENSIVO = {'GIT_EDITOR', 'GIT_PAGER', 'GIT_TERMINAL_PROMPT', 'GIT_SEQUENCE_EDITOR'}
COMMITEAN_OTRA_COSA = {'--all', '--include', '--only', '--pathspec-from-file', '--patch', '--interactive'}
# git ... commit en posicion de comando: al inicio, tras un separador o tras un envoltorio/asignacion.
# Dentro de un texto (echo "git commit", un string de Python) no cuenta.
RE_COMMIT_SUELTO = re.compile(
    r'(?:^|[;&|{\n`]\s*|\$\(\s*|\s/{1,2}[ck]\s+|\s-command\s+|(?:^|[;&|{\n]\s*)\.\s+|'
    r'\b(?:then|do|else|time|exec|nohup|sudo|xargs|env|command|eval|nice|timeout|start|start-process|saps)\s+'
    r'(?:(?:-\S+|\d+)\s+)*|^\s*\w+=\S*\s+|[;&|\n]\s*\w+=\S*\s+)'
    r'["\']?(?:[\w.:/\\-]*[/\\])?git(?:\.exe)?["\']?\s+(?:-[Cc]\s+\S+\s+|--?[\w-]+(?:=\S+)?\s+)*commit(?![\w-])',
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


def segmentos(comando, bash=True):
    if bash:
        comando = comando.replace('\\\r\n', '').replace('\\\n', '')   # continuacion de linea
        comando = re.sub(r'\\(?![ "\'\\$`])', '/', comando)        # respeta \" \' \\ \$ y \ espacio
    else:
        comando = comando.replace('\\', '/')                          # PowerShell/cmd: \ es literal
    lex = shlex.shlex(comando.replace('\n', ' ; '), posix=True,
                      punctuation_chars=';&|()<>')
    lex.whitespace_split = True
    lex.commenters = ''   # x#y no es comentario; un # real que deje rutas visibles se niega (falla cerrado)
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


def leer_git(tokens, base, adivinar_alias=True):
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
            elif tokens[i + 1].lower().startswith(('alias.', 'include', 'core.worktree', 'core.bare')):
                alias = True
            i += 2; continue
        if t.startswith(('--git-dir=', '--work-tree=')):
            d = resolver(d, t.split('=', 1)[1])
        if t.startswith('--config-env'):
            alias = True
            i += 1 if '=' in t else 2
            continue
        i += 1
    sub = tokens[i] if i < len(tokens) else ''
    resto = tokens[i + 1:]
    if ' ' in sub or ',' in sub:
        partes = [x for x in re.split(r'[\s,]+', sub) if x] if ',' in sub else shlex.split(sub)
        sub, resto = (partes[0] if partes else ''), partes[1:] + resto
    if alias:
        sub = 'commit?'
    elif sub and d is not None and sub not in TOCAN_STAGE and sub != 'commit':
        # un alias propio (git ci) que lleve commit cuenta como commit, tambien en cadena
        # (c2 = ci, ci = commit -a) o si es de shell (!...)
        nombre = sub
        for _ in range(5):
            try:
                definicion = sellar.git(d, 'config', '--get', f'alias.{nombre}').strip()
            except (RuntimeError, OSError):
                break
            definicion = re.sub(r'[\'"\\]', '', definicion)   # git parte el alias quitando comillas
            if re.search(r'\bcommit\b', definicion) or definicion.startswith('!'):
                sub = 'commit?'
                break
            nombre = definicion.split()[0] if definicion else ''
            if not nombre:
                break
            if nombre in NATIVOS or nombre in TOCAN_STAGE:
                break
    elif adivinar_alias and sub and d is None and sub not in NATIVOS and sub not in TOCAN_STAGE and sub != 'commit':
        # sin saber el repo no se puede leer el alias: un subcomando que no es de git se toma como uno
        sub = 'commit?'
    return d, sub, resto


def opciones_ps(tokens):
    """Las opciones de powershell/pwsh antes del script: lo que va despues es del script."""
    for i, tok in enumerate(tokens):
        if not tok.startswith(('-', '/')) or tok.lower().lstrip('-/') in ('file', 'f', 'command', 'c'):
            return tokens[:i]
    return tokens


def es_codificado(token):
    """-EncodedCommand de PowerShell o cualquiera de sus abreviaturas (-e, -ec, -en, -enc...)."""
    if not token.startswith(('-', '/')):
        return False
    t = token.lower().lstrip('-/')
    return t == 'ec' or (t.startswith('e') and 'encodedcommand'.startswith(t))


def es_git(tok):
    """git, /ruta/git.exe, o git con una letra escapada (g\\it llega como g/it)."""
    base = tok.rsplit('/', 1)[-1].lower().removesuffix('.exe')
    if base == 'git':
        return True
    return ':' not in tok and not tok.startswith('/') and tok.replace('/', '').lower().removesuffix('.exe') == 'git'


def recorrer(comando, base, eventos, bash=True):
    """Junta en `eventos` cada git que toca el stage y cada commit, con su directorio, en orden."""
    for seg in segmentos(comando, bash):
        envuelto, asignaciones = False, []
        while seg and (seg[0].lower() in ENVOLTORIOS or re.match(r'^\w+=', seg[0])
                       or (envuelto and (seg[0].startswith('-') or seg[0].isdigit()
                                         or re.match(r'^/{1,2}[a-z]$', seg[0], re.I)))):
            envuelto = envuelto or seg[0].lower() in ENVOLTORIOS
            if re.match(r'^\w+=', seg[0]):
                asignaciones.append(seg[0].split('=', 1)[0].upper())
            seg = seg[1:]
        if envuelto:
            for k, tok in enumerate(seg):
                if es_git(tok):
                    seg = seg[k:]
                    break
        if not seg:
            continue
        nombre = 'git' if es_git(seg[0]) else seg[0].rsplit('/', 1)[-1].lower().removesuffix('.exe')
        convertido = False
        if nombre != 'git' and nombre not in CAMBIAN_DIR | DIR_DESCONOCIDO | SHELLS | ECO | LECTURA:
            for k, tok in enumerate(seg[1:], 1):
                if es_git(tok):
                    seg, nombre, convertido = seg[k:], 'git', True
                    break
        if nombre in CAMBIAN_DIR:
            args = [t for t in seg[1:] if not t.startswith('-') or t == '-']
            base = resolver(base, args[0]) if args else None
        elif nombre in DIR_DESCONOCIDO:
            base = None
        elif nombre in SHELLS:
            # bash -c 'git ...' llega en un token; cmd /c git commit ... llega en varios
            resto = seg[1:]
            while resto and re.match(r'^(-|/{1,2}[a-z]+$)', resto[0], re.I):
                resto = resto[1:]
            if nombre in ('powershell', 'pwsh') and any(es_codificado(r) for r in opciones_ps(seg[1:])):
                eventos.append(('commit', base, ['--oculto']))
            elif len(resto) == 1:
                recorrer(resto[0], base, eventos, bash)
            elif resto:
                recorrer(shlex.join(resto), base, eventos, bash)
        elif nombre == 'git':
            d, sub, args = leer_git(seg, base, adivinar_alias=not convertido)
            if sub in ('commit', 'commit?') and any(RE_ENTORNO_GIT.fullmatch(a) for a in asignaciones):
                eventos.append(('commit', d, ['--entorno']))
            elif sub in ('commit', 'commit?'):
                eventos.append(('commit', d, args if sub == 'commit' else ['--alias']))
            elif sub in TOCAN_STAGE:
                eventos.append(('stage', d, args))
            elif sub and sub not in NATIVOS:
                eventos.append(('raro', d, args))
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
        if t == '--entorno':
            return 'lleva variables GIT_* que cambian el indice o el repo: commitea algo distinto del stage'
        if t == '--oculto':
            return 'va codificado (-EncodedCommand): no se puede leer que commitea'
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
    rutas = [r for r in sellar.git(raiz, 'diff', '--cached', '--name-only', '--no-renames').splitlines() if r]
    if not rutas or all(sellar.es_solo_doc(r) for r in rutas):
        return None
    faltan = []
    h, _ = sellar.hash_stage(raiz)
    rev = sellar.leer_sello(raiz, 'revision.json')
    if rev.get('hash') != h:
        faltan.append('la revision de seguridad y codigo de este diff (skill revisar-antes-de-commit-personal)'
                      + (': el stage cambio despues del sello' if rev else ''))
    pruebas = sellar.leer_sello(raiz, 'pruebas.json')
    for p in sellar.tableros_tocados(raiz, rutas):
        sello = pruebas.get(p) if isinstance(pruebas.get(p), dict) else {}
        if sello.get('huella') != sellar.huella_stage(raiz, p):
            faltan.append(f'la prueba en el navegador de {p} (skill probar-tablero-personal)'
                          + (': lo que esta en stage no es lo que se probo' if sello else ''))
    if faltan:
        return ('Commit detenido. Falta: ' + '; '.join(faltan) + '. Corre lo que falta y vuelve a hacer '
                'git add si cambiaste algo. Si es un falso positivo, la persona puede commitear a mano en su '
                'terminal.')
    return None


def decidir(comando, cwd, vigilada=RAIZ_HOOK, herramienta='Bash'):
    """None si deja pasar; el motivo (texto) si niega. vigilada=None: todo repo de git."""
    if vigilada is None:
        # global: si el cwd no es un repo, un `git -C <repo>` igual cuenta (falla cerrado)
        apunta_aqui = raiz_de(cwd) is not None or re.search(r'\bgit\b', comando) is not None
    else:
        vigilada = Path(vigilada)
        apunta_aqui = dentro(cwd, vigilada) or vigilada.name.lower() in comando.lower()
    try:
        return _decidir(comando, cwd, vigilada, apunta_aqui, herramienta.lower() != 'powershell')
    except Rechazo as e:
        return str(e)
    except Exception as e:  # noqa: BLE001 - un control que truena no debe dejar pasar
        if apunta_aqui and re.search(r'\bgit\b', comando):
            return (f'No pude revisar este commit ({type(e).__name__}: {e}). Por seguridad se detiene: '
                    'corre git commit solo, con -m, en un comando aparte.')
        return None


def _decidir(comando, cwd, vigilada, apunta_aqui, bash=True):
    if not bash and '`' in comando and apunta_aqui and any(
            e[0] in ('commit', 'raro') for e in recorrer(comando.replace('`', ''), Path(cwd), [], False)):
        raise Rechazo('En PowerShell el backtick escapa caracteres y no lo puedo leer junto a git. '
                      'Corre git commit solo, sin backticks, con -m.')
    try:
        eventos = recorrer(comando, Path(cwd), [], bash)
    except ValueError:
        if apunta_aqui and re.search(r'\bgit\b', comando):
            raise Rechazo('No pude leer el comando (comillas sin cerrar). Corre git commit solo, con -m.')
        return None
    if apunta_aqui and RE_COMMIT_SUELTO.search(comando) and not any(e[0] == 'commit' for e in eventos):
        raise Rechazo('El comando parece hacer git commit pero no lo pude leer. Corre git commit solo, '
                      'sin prefijos ni envoltorios, con -m.')
    if apunta_aqui and RE_ENTORNO_GIT.search(comando) and any(e[0] in ('commit', 'raro') for e in eventos):
        raise Rechazo('El comando pone variables GIT_* que cambian el indice, el repo o la config de git: '
                      'el sello no las ve. Corre git commit solo, con -m, sin esas variables.')
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
        if vigilada is not None and raiz.resolve() != vigilada.resolve():
            continue
        if tipo == 'stage':
            hubo_stage = True
            continue
        if tipo == 'raro':
            continue
        problema = problema_de_args(args)
        if problema == 'dry':
            continue
        if problema:
            raise Rechazo(f'El commit {problema}. Haz git add de lo que va, corre /revisar-antes-de-commit-personal '
                          'y commitea solo con -m.')
        if hubo_stage:
            raise Rechazo('El comando cambia el stage y commitea en el mismo paso: el hook solo ve el stage '
                          'de antes. Haz el git add, sella con /revisar-antes-de-commit-personal y corre el commit aparte.')
        motivo = revisar_sellos(raiz)
        if motivo:
            raise Rechazo(motivo)
    return None


def main():
    try:
        datos = json.loads(ENTRADA)
        comando = (datos.get('tool_input') or {}).get('command') or ''
        motivo = decidir(comando, datos.get('cwd') or os.getcwd(), herramienta=datos.get('tool_name') or 'Bash')
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
        def D(c, cwd=r):
            sellar._CON_INDEX.clear()   # el self-test cambia el stage entre casos
            return decidir(c, cwd, r)
        niega = lambda c, txt='', cwd=r: txt in (D(c, cwd) or '') and D(c, cwd) is not None  # noqa: E731

        casos.append(('no es commit', D('git status') is None))
        casos.append(('echo con la palabra commit', D('echo "voy a hacer commit"') is None))
        escribe(r, 'NOTAS.md', 'nota\n'); sh(r, 'add', 'NOTAS.md')
        casos.append(('solo docs pasa', D('git commit -m "notas"') is None))
        sh(r, 'commit', '-q', '-m', 'notas')
        escribe(r, '.claude/skills/x/SKILL.md', 'regla\n'); sh(r, 'add', '.claude')
        casos.append(('.md de .claude pide revision', niega('git commit -m "skill"', 'revision')))
        sh(r, 'commit', '-q', '-m', 'skill')

        escribe(r, 'scripts/x.py', 'print(1)\n'); sh(r, 'add', '.')
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
        casos.append(('ruta suelta se niega', niega('git commit -m x scripts/x.py', 'ruta')))
        casos.append(('add y commit juntos se niega', niega('git add . && git commit -m x', 'mismo paso')))
        casos.append(('commit seguido de otro con -a', niega('git commit -m a && git commit -am b', '-a')))
        (r / '.claude' / 'estado' / 'revision.json').write_text('{roto', encoding='utf-8')
        casos.append(('sello corrupto no truena y niega', niega('git commit -m x', 'revision')))
        sella(r, 'revision')
        casos.append(('VAR=x git commit -am se niega', niega('GIT_EDITOR=true git commit -am x', '-a')))
        casos.append(('if/then con -a se niega', niega('if true; then git commit -am x; fi', '-a')))
        casos.append(('PowerShell { } pasa con sello', D('if ($?) { git commit -m x }') is None))
        casos.append(('time git commit pasa con sello', D('time git commit -m x') is None))
        casos.append(('-e no come la ruta', niega('git commit -m x -e scripts/x.py', 'ruta')))
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
        casos.append(('alias git ci no se salta la entrada', not se_puede_saltar('{"command": "git ci -m x"}')))
        casos.append(("git c''ommit se niega", niega("git c''ommit -am x", '-a')))
        casos.append(('sin git se salta', se_puede_saltar('{"command": "ls -la"}')))
        casos.append(('cwd con GitHub no impide saltar',
                      se_puede_saltar('{"tool_input": {"command": "ls"}, "cwd": "C:/Users/x/Documents/GitHub/r"}')))
        casos.append(('comando con git en tool_input se revisa',
                      not se_puede_saltar('{"tool_input": {"command": "git ci -m x"}, "cwd": "C:/x"}')))
        casos.append(('entrada ilegible se revisa completa', not se_puede_saltar('no es json pero dice git')))
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
        escribe(r, 'scripts/x.py', 'print(2)\n'); sh(r, 'add', '.')
        casos.append(('stage cambio despues del sello', niega('git commit -m "x"', 'cambio')))
        sh(r, 'commit', '-q', '-m', 'x')

        escribe(r, 'T/index.html', '<html></html>\n')
        escribe(r, 'T/app.js', 'let a = 1;\n')
        escribe(r, 'T/data/dashboard.json', '{}\n')
        escribe(r, 'T/data/CONTRATO.md', 'datos: inventados\n')
        sh(r, 'add', '.')
        sella(r, 'revision')
        m = D('git commit -m "t"') or ''
        casos.append(('tablero sin prueba se niega', 'probar-tablero-personal' in m and 'revision' not in m))
        sella(r, 'pruebas', 'T')
        casos.append(('tablero probado y revisado pasa', D('git commit -m "t"') is None))
        escribe(r, 'T/data/dashboard.json', '{"a": 1}\n'); sh(r, 'add', '.')
        sella(r, 'revision')
        casos.append(('datos cambiaron: prueba vencida', niega('git commit -m "t"', 'probar-tablero-personal')))
        sella(r, 'pruebas', 'T')
        casos.append(('prueba de nuevo y pasa', D('git commit -m "t"') is None))
        escribe(r, 'T/app.js', 'let a = 2;\n')
        casos.append(('cambio sin add no afecta el stage', D('git commit -m "t"') is None))
        sh(r, 'commit', '-q', '-m', 't')
        sh(r, 'checkout', '-q', '--', '.')

        escribe(r, 'tableros/Logística/index.html', '<html></html>\n')
        sh(r, 'add', 'tableros')
        sella(r, 'revision')
        casos.append(('tablero con acento pide prueba', niega('git commit -m "l"', 'probar-tablero-personal')))
        sh(r, 'reset', '-q')

        escribe(r, 'etl/E/main.py', 'print(1)\n'); sh(r, 'add', 'etl/E')
        sella(r, 'revision')
        casos.append(('ETL sin index.html no pide prueba', D('git commit -m "e"') is None))
        sh(r, 'commit', '-q', '-m', 'e')
        escribe(r, 'etl/E/requirements.txt', 'pandas\n'); sh(r, 'add', '.')
        casos.append(('requirements.txt pide revision', niega('git commit -m r', 'revision')))
        sh(r, 'reset', '-q')
        escribe(r, 'scripts/y.py', 'print(3)\n'); sh(r, 'add', 'scripts')
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
        sh(r, 'reset', '-q')

        # El index.html de la raiz (la portada del portal) no es un tablero: solo pide revision.
        escribe(r, 'index.html', '<html>portada</html>\n'); sh(r, 'add', 'index.html')
        sella(r, 'revision')
        casos.append(('portada de la raiz no pide prueba', D('git commit -m "p"') is None))
        sh(r, 'commit', '-q', '-m', 'p')

        # Instalacion global (~/.claude/hooks): vigila cualquier repo, tambien el "otro".
        def G(c, cwd):
            sellar._CON_INDEX.clear()
            return decidir(c, cwd, None)
        escribe(otro, 'scripts/z.py', 'print(4)\n'); sh(otro, 'add', '.')
        casos.append(('global: otro repo sin sello se niega', 'revision' in (G('git commit -m z', otro) or '')))
        casos.append(('global: git -C al otro repo se niega',
                      'revision' in (G(f'git -C "{otro}" commit -m z', afuera) or '')))
        sella(otro, 'revision')
        casos.append(('global: otro repo con sello pasa', G('git commit -m z', otro) is None))
        casos.append(('global: carpeta sin git pasa', G('git status', afuera) is None))
        escribe(r, 'T/app.js', 'let a = 3;\n'); sh(r, 'add', '.')
        sella(r, 'revision')
        casos.append(('global: tablero sin prueba se niega', 'probar-tablero-personal' in (G('git commit -m t', r) or '')))
        casos.append(('global: backticks desde fuera se niegan',
                      G(f'echo `git -C "{r}" commit -am x`', afuera) is not None))
        casos.append(('git commit-tree no es commit', D('git commit-tree HEAD^{tree} -m x') is None))
        sh(r, 'reset', '-q')
        sella(r, 'pruebas', 'T')
        escribe(r, 'T/pages/p.js', 'let p = 1;\n'); sh(r, 'add', 'T/pages')
        sella(r, 'revision')
        casos.append(('subcarpeta del tablero pide prueba', niega('git commit -m p', 'probar-tablero-personal')))
        sh(r, 'reset', '-q')
        escribe(r, 'T/docs/PRD.md', 'prd\n'); sh(r, 'add', 'T/docs')
        sella(r, 'revision')
        casos.append(('docs del tablero no piden prueba', D('git commit -m d') is None))
        sh(r, 'reset', '-q')
        sh(r, 'mv', 'T/app.js', 'scripts/app.js')
        sella(r, 'revision')
        casos.append(('git mv fuera del tablero pide prueba', niega('git commit -m mv', 'probar-tablero-personal')))
        sh(r, 'mv', 'scripts/app.js', 'T/app.js')
        escribe(r, 'G/index.html', '<html>grupo</html>\n')
        escribe(r, 'G/S/index.html', '<html></html>\n'); escribe(r, 'G/S/app.js', 'let s = 1;\n')
        sh(r, 'add', 'G'); sh(r, 'commit', '-q', '-m', 'g')
        escribe(r, 'G/S/app.js', 'let s = 2;\n'); sh(r, 'add', 'G')
        sella(r, 'revision')
        casos.append(('tablero dentro de un grupo con index pide prueba', niega('git commit -m s', 'G/S')))
        sh(r, 'reset', '-q')
        escribe(r, 'scripts/w.py', 'print(5)\n'); sh(r, 'add', 'scripts/w.py')
        casos.append(('cmd /c git commit sin comillas se niega', niega('cmd /c git commit -am x', '-a')))
        casos.append(('powershell -Command git commit se niega',
                      niega('powershell -NoProfile -Command git commit -am x', '-a')))
        casos.append(('start /b git commit se niega', niega('start /b git commit -am x', '-a')))
        casos.append(('-EncodedCommand se niega', niega('powershell -EncodedCommand ZwBpAHQA', 'codificado')))
        casos.append(('powershell -e se niega', niega('powershell -e ZwBpAHQA', 'codificado')))
        casos.append(('powershell -ec se niega', niega('pwsh -ec ZwBpAHQA', 'codificado')))
        casos.append(('-EncodedCommand no se salta la entrada',
                      not se_puede_saltar('{"command": "powershell -EncodedCommand ZwBpAHQA", "cwd": "C:/x"}')))
        casos.append(('cmd //c de Git Bash se niega', niega('cmd //c git commit -am x', '-a')))
        casos.append(('GIT_SSH_COMMAND git push pasa', D('GIT_SSH_COMMAND="ssh -i k" git push') is None))
        casos.append(('GIT_TRACE git status pasa', D('GIT_TRACE=1 git status') is None))
        casos.append(('$env:GIT_SSH_COMMAND; git fetch pasa', D('$env:GIT_SSH_COMMAND="ssh"; git fetch') is None))
        casos.append(('bash -e script pasa', D('bash -e build.sh') is None))
        casos.append(('pwsh -File con -e del script pasa', D('pwsh -File d.ps1 -e dev; git status') is None))
        casos.append(('git check-ignore tras cd $X pasa', D('cd "$X" && git check-ignore a') is None))
        casos.append(('export "GIT_INDEX_FILE=o" se niega', niega('export "GIT_INDEX_FILE=o"; git commit -m y', 'GIT_')))
        casos.append(('Set-Item env:GIT_INDEX_FILE se niega', niega('Set-Item env:GIT_INDEX_FILE o; git commit -m y', 'GIT_')))
        casos.append(('powershell /enc se niega', niega('powershell /enc ZwBpAHQA', 'codificado')))
        casos.append(('Program\\ Files con escape se niega',
                      niega('C:/Program\\ Files/Git/cmd/git.exe commit -am x', '-a')))
        casos.append(('-c core.worktree se niega', niega('git -c core.worktree=/tmp commit -m y', 'alias')))
        casos.append(('. git commit de PowerShell se niega', niega('. git commit -am x', '-a')))
        casos.append(('echo "$(git commit)" se niega', niega('echo "$(git commit -m x)"', 'no lo pude leer')))
        casos.append(('x="$(git commit)" se niega', niega('x="$(git commit -m x)"', 'no lo pude leer')))
        casos.append(('g escapado se niega', niega('g\\it commit -am x', '-a')))
        casos.append(('continuacion de linea se niega', niega('g\\\nit commit -am x', '-a')))
        casos.append(('cd $X y grep git pasa', D('cd "$TMPDIR" && grep -rn git .') is None))
        casos.append(('popd y grep git pasa', D('popd; grep git a.py') is None))
        casos.append(('man git commit pasa', D('man git commit') is None))
        P = lambda c: decidir(c, r, r, 'PowerShell')  # noqa: E731
        casos.append(('PowerShell: rutas C:\\x\\ y Start-Process se niega',
                      'commit' in (P('cd "C:\\repo\\"; Start-Process git -ArgumentList "commit -am x"; cd "C:\\otro\\"') or '')))
        casos.append(('PowerShell: rutas C:\\x\\ y winpty se niega',
                      'commit' in (P('cd "C:\\repo\\"; winpty git commit -am x; cd "C:\\otro\\"') or '')))
        casos.append(('PowerShell: & ruta de git.exe se niega',
                      'commit' in (P('ls "C:\\src\\"; & "C:\\Program Files\\Git\\cmd\\git.exe" commit -am x; ls "C:\\dst\\"') or '')))
        casos.append(('PowerShell: git status pasa', P('git status') is None))
        casos.append(('x#y con ruta se niega', niega('git commit -m x#y a.py', 'ruta')))
        casos.append(('x#y con -a se niega', niega('git commit -m x#y -a', '-a')))
        casos.append(('PowerShell: git log con `t pasa', P('git log --format="%h`t%s"') is None))
        casos.append(('PowerShell: Write-Host `n y git status pasa', P('Write-Host "a`nb"; git status') is None))
        casos.append(('PowerShell: g`it se niega', 'backtick' in (P('g`it commit -am x') or '')))
        casos.append(("PowerShell: `' alrededor de la ruta se niega",
                      'backtick' in (P("git commit -m `' a.py -m `'") or '')))
        casos.append(("PowerShell: `' alrededor de -am se niega", 'backtick' in (P("git commit -m `' -am `'") or '')))
        sella(r, 'revision')
        casos.append(('mensaje con comillas escapadas pasa', D('git commit -m "a \\"b c\\""') is None))
        casos.append(('comillas escapadas y ruta se niega', niega('git commit -m "x \\"y\\"" a.py', 'ruta')))
        casos.append(('; . git commit se niega', niega('git status; . git commit -am x', '-a')))
        casos.append(('winpty git commit se niega', niega('winpty git commit -am x', '-a')))
        casos.append(('stdbuf -o0 git commit se niega', niega('stdbuf -o0 git commit -am x', '-a')))
        casos.append(('wsl git commit se niega', niega('wsl git commit -am x', '-a')))
        casos.append(('echo git commit sin comillas no se toca', D('echo git commit -am x') is None))
        casos.append(('grep git en un archivo pasa', D('grep -n git README.md') is None))
        sh(r, 'config', 'alias.x', '"com"mit -a')
        casos.append(('alias con comillas se niega', niega('git x -m y', 'alias')))
        sh(r, 'config', '--unset', 'alias.x')
        casos.append(('timeout -s KILL 60 git se niega', niega('timeout -s KILL 60 git commit -am y', '-a')))
        casos.append(('sudo -u me git se niega', niega('sudo -u me git commit -am y', '-a')))
        casos.append(('cmd //c start /wait git se niega', niega('cmd //c start /wait git commit -am y', '-a')))
        casos.append(('${env:GIT_INDEX_FILE} se niega', niega("${env:GIT_INDEX_FILE}='o'; git commit -m y", 'GIT_')))
        casos.append(('SetEnvironmentVariable se niega',
                      niega("[Environment]::SetEnvironmentVariable('GIT_INDEX_FILE','o'); git commit -m y", 'GIT_')))
        casos.append(('Start-Process con comas se niega',
                      niega("Start-Process git -ArgumentList 'commit','-am','x'", '-a')))
        casos.append(('export GIT_INDEX_FILE antes se niega', niega('export GIT_INDEX_FILE=o; git commit -m y', 'GIT_')))
        casos.append(('$env:GIT_INDEX_FILE antes se niega', niega("$env:GIT_INDEX_FILE='o'; git commit -m y", 'GIT_')))
        casos.append(('GIT_CONFIG_COUNT con alias se niega', niega('GIT_CONFIG_COUNT=1 git ci -m y', 'GIT_')))
        casos.append(('-c include.path se niega', niega('git -c include.path=x.cfg ci -m y', 'alias')))
        casos.append(('cd $PWD y alias se niega', niega('cd "$PWD" && git ci -m x', 'que repo')))
        casos.append(('cd $PWD y git status pasa', D('cd "$PWD" && git status') is None))
        casos.append(('Start-Process git se niega',
                      niega('Start-Process git -ArgumentList "commit -am x"', '-a')))
        casos.append(("g''it se revisa", not se_puede_saltar('{"command": "g\'\'it commit -am x"}')))
        sh(r, 'config', 'alias.ci', 'commit -a'); sh(r, 'config', 'alias.c2', 'ci')
        casos.append(('alias en cadena se niega', niega('git c2 -m x', 'alias')))
        sh(r, 'config', 'alias.sh1', '!git commit -am x')
        casos.append(('alias de shell se niega', niega('git sh1', 'alias')))
        sh(r, 'config', 'alias.st', 'status')
        casos.append(('alias inofensivo no se toma por commit', D('git st') is None))
        for a in ('ci', 'c2', 'sh1', 'st'):
            sh(r, 'config', '--unset', f'alias.{a}')
        casos.append(('--config-env se niega', niega('git --config-env=alias.ci=X ci -m x', 'alias')))
        casos.append(('GIT_INDEX_FILE se niega', niega('GIT_INDEX_FILE=x git commit -m y', 'GIT_')))
        casos.append(('GIT_CONFIG_* se niega', niega('GIT_CONFIG_COUNT=1 git commit -m y', 'GIT_')))
        sella(r, 'revision')
        casos.append(('GIT_EDITOR sigue pasando', D('GIT_EDITOR=true git commit -m y') is None))
        sh(r, 'reset', '-q')

        # 200 archivos en stage: el hook tiene 30 s y uno vencido deja pasar el commit
        import time
        for k in range(200):
            escribe(r, f'lib/m{k % 20}/f{k}.py', f'print({k})\n')
        sh(r, 'add', 'lib')
        sella(r, 'revision')
        sellar._CON_INDEX.clear()
        t0 = time.time()
        res = D('git commit -m grande')
        casos.append((f'200 archivos en menos de 5 s ({time.time() - t0:.1f} s)',
                      res is None and time.time() - t0 < 5))

    malos = [n for n, ok in casos if not ok]
    for n, ok in casos:
        print(('OK   ' if ok else 'FALLA') + ' ' + n)
    print(f'{len(casos) - len(malos)}/{len(casos)} casos bien')
    sys.exit(1 if malos else 0)


if __name__ == '__main__':
    self_test() if '--self-test' in sys.argv else main()
