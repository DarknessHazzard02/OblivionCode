#!/usr/bin/env python3
# ===============================================
# Guardias de los agentes: secretos, candado, push a main, inicio de sesion y firma
# Author: Haz
# ===============================================
"""Hooks comunes para Claude Code, Copilot y Gemini (Codex no tiene hooks: lo cubre el candado de git).

    python guardias.py proteger      PreToolUse: niega leer secretos y saltarse el candado
    python guardias.py push-main     PreToolUse: niega `git push` a main/master
    python guardias.py inicio        SessionStart: rama, atraso contra origin/main, cambios y candado
    python guardias.py firma         PostToolUse: avisa si un archivo de codigo quedo sin firma
    python guardias.py --self-test   casos de prueba

Lee el JSON del hook por stdin. Entiende la forma de Claude/Gemini (`tool_name`, `tool_input`) y la de
Copilot (`toolName`, `toolArgs` como texto JSON). Para negar: imprime el JSON de decision y sale con
codigo 2 con el motivo en stderr, que es lo que bloquea en los tres.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

# ===============================================
# Configuration
# ===============================================
SECRETO_RUTA = re.compile(
    r'(^|[\\/])(\.env(\.[\w-]+)?|config\.local\.json|credentials(\.json)?|secrets?\.(json|ya?ml|toml)'
    r'|id_(rsa|ed25519|ecdsa)|[^\\/]+\.(pem|pfx|p12|key))$', re.I)
SECRETO_PERMITIDO = re.compile(r'\.(example|ejemplo|sample|template)(\.|$)', re.I)
LEE_EN_SHELL = re.compile(r'\b(cat|type|get-content|gc|more|less|head|tail|sed|awk|grep|rg|select-string|copy|cp|scp)\b', re.I)
SALTA_CANDADO = [
    (re.compile(r'--no-verify\b'), '--no-verify salta el candado de git'),
    (re.compile(r'\bgit\b[^;&|\n]*\bcommit\b[^;&|\n]*\s-[a-zA-Z]*n[a-zA-Z]*\b'), 'git commit -n salta el candado de git'),
    (re.compile(r'\bgit\b[^;&|\n]*\badd\b[^;&|\n]*\s(-f|--force)\b'), 'git add -f mete archivos ignorados a proposito'),
    (re.compile(r'core\.hooksPath', re.I), 'cambiar core.hooksPath apaga el candado'),
    (re.compile(r'[\\/]\.git[\\/]hooks\b', re.I), 'tocar .git/hooks cambia el candado; lo instala agents/_comun/candado/instalar.py a mano'),
    (re.compile(r'\bHUSKY=0\b|\bSKIP_HOOKS?\b', re.I), 'apagar hooks por variable'),
    (re.compile(r'CANDADO_CAMBIO_CONFIG', re.I), 'CANDADO_CAMBIO_CONFIG confirma un cambio a la configuracion del candado'),
    (re.compile(r'CANDADO_REGLAS|\b(HOME|USERPROFILE)=\S*\s+git\b|\$env:(HOME|USERPROFILE)\s*=', re.I),
     'cambiar CANDADO_REGLAS, HOME o USERPROFILE esconde las reglas privadas del candado'),
    # Plumbing que crea o mueve commits sin pasar por el pre-commit
    (re.compile(r'\bgit(\s+-[cC]\s+\S+)*\s+(commit-tree|update-ref|fast-import|mktree|replace|am|symbolic-ref)\b'
                r'|\bgit\b[^;&|\n]*\bhash-object\b[^;&|\n]*\s-w\b', re.I),
     'commit-tree, update-ref, fast-import, mktree, replace, am, symbolic-ref y hash-object -w hacen commits sin el candado'),
]
PUSH = re.compile(r'\bgit\b(?:\s+-C\s+\S+)?[^;&|\n]*?\bpush\b([^;&|\n]*)', re.I)
# main/master como nombre completo, rodeado de lo que sea menos parte de un nombre de rama:
# tambien HEAD:main), main>o.txt, main,feat/x y {main,x}
RAMA_PROTEGIDA = re.compile(r'(?<![\w.@-])(main|master)(?![\w./@{~^-])', re.I)
# Push sin rama explicita en un comando que antes cambia de rama o de carpeta: la rama se lee antes de correr
CAMBIA_CONTEXTO = re.compile(r'\b(checkout|switch|cd|set-location|sl|pushd|chdir)\b|\bbranch\s+-[mMcC]\b'
                             r'|\bgit\s+-C\b', re.I)
MENSAJE_COMMIT = re.compile(r'(-m|--message)(=|\s+)("[^"]*"|\'[^\']*\')')
# Refspec que empuja la rama actual sin nombrarla: HEAD, @, +HEAD o HEAD:HEAD
REFSPEC_IMPLICITA = re.compile(r'^\+?(HEAD|@)(:(HEAD|@))?$', re.I)
# Opciones de git push cuyo valor va separado por espacio
OPCION_CON_VALOR = re.compile(r'-o|--push-option|--repo|--receive-pack|--exec', re.I)
# Configuracion del candado que solo cambia Haz a mano: con ella se apaga la revision sin --no-verify
# Se busca el prefijo en cualquier parte: tambien pegado a una redireccion (>.candado-modo) o con glob
CONFIG_CANDADO = re.compile(r'\.candado-', re.I)
# Un comando que nombra esa configuracion solo pasa si TODOS sus tramos son de lectura (lo que va
# despues de un tubo tambien recibe el archivo) y ninguno trae una opcion que escriba o ejecute
LECTURA_EN_SHELL = re.compile(
    r'^\s*(cat|type|get-content|gc|head|tail|grep|rg|select-string|ls|dir|get-childitem|test-path|wc'
    r'|git(\s+-C\s+\S+)?\s+(diff|log|show|status|blame|ls-files|check-ignore))\b', re.I)
OPCION_QUE_ESCRIBE = re.compile(r'--(output|pre|pre-glob|ext-diff|textconv)\b', re.I)
# Lo que corre otro comando dentro del tramo: $( ), ` `, <( ), >( ) y ( ) de PowerShell
SUBCOMANDO = re.compile(r'\$\(|`|[<>]\(|\(')
# Push que empuja mas que la rama nombrada: refspec con comodin o config que cambia que se empuja
# Llegar a main en el remoto sin git push: merge de un PR, merge por la API o sync del repo
MERGE_REMOTO = re.compile(r'\bgh\s+pr\s+merge\b|\bgh\s+api\b[^;&|\n]*\bmerges?\b|\bgh\s+repo\s+sync\b', re.I)
# Un alias de git esconde la palabra push: tambien se niega
PUSH_AMPLIO = re.compile(r'remote\.[^\s=]+\.push\b|push\.default|\bpush\.\w*matching|\balias\.', re.I)
REDIRECCION_INOFENSIVA = re.compile(r'\d?>&\d|\d?>\s*(/dev/null|\$null|nul)\b', re.I)
TRAMOS_SHELL = re.compile(r'&&|\|\||[;|&\n]')
SOLO_LECTURA = {'read', 'read_file', 'read_many_files', 'grep', 'glob', 'view', 'ls', 'list_directory'}
EXT_CODIGO = {'.py', '.sql', '.bas', '.cls', '.vba', '.pq', '.m', '.dax', '.js', '.ts', '.jsx', '.tsx',
              '.cs', '.java', '.css', '.html', '.ps1', '.sh', '.rb', '.yml', '.yaml'}
FIRMA = re.compile(r'Made by: Hazzard|Author: Haz|Updated by Haz')
SIN_FIRMA_RUTA = re.compile(r'(^|[\\/])(\.claude|\.agents|\.github|\.gemini|\.codex|agents|node_modules|\.venv|venv|vendor|shared|demo|data)[\\/]')


# ===============================================
# Read Hook Input
# ===============================================
def leer_evento(texto):
    try:
        d = json.loads(texto or '{}')
    except ValueError:
        return {}, '', {}
    herramienta = d.get('tool_name') or d.get('toolName') or ''
    entrada = d.get('tool_input') or d.get('toolArgs') or {}
    if isinstance(entrada, str):
        try:
            entrada = json.loads(entrada)
        except ValueError:
            entrada = {'command': entrada}
    return d, herramienta, entrada if isinstance(entrada, dict) else {}


def comando_de(entrada):
    return str(entrada.get('command') or entrada.get('cmd') or entrada.get('script') or '')


def rutas_de(entrada):
    claves = ('file_path', 'path', 'filePath', 'absolute_path', 'notebook_path', 'target_file')
    return [str(entrada[k]) for k in claves if entrada.get(k)]


def negar(motivo):
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
                                             'permissionDecisionReason': motivo},
                      'permissionDecision': 'deny', 'permissionDecisionReason': motivo,
                      'decision': 'deny', 'reason': motivo}, ensure_ascii=False))
    print(motivo, file=sys.stderr)
    sys.exit(2)


# ===============================================
# Guards
# ===============================================
def revisar_proteger(herramienta, entrada):
    """Motivo para negar, o None."""
    cmd = comando_de(entrada)
    for rx, motivo in SALTA_CANDADO:
        if cmd and rx.search(cmd):
            return f'Detenido: {motivo}. Si de verdad hace falta, lo hace Haz a mano.'
    aviso_candado = ('Detenido: .candado-permitidos y .candado-modo deciden qué revisa el candado; '
                     'cambiarlos lo apaga igual que --no-verify. Los edita Haz a mano.')
    if herramienta.lower() not in SOLO_LECTURA and any(CONFIG_CANDADO.search(r) for r in rutas_de(entrada)):
        return aviso_candado
    sin_mensaje = MENSAJE_COMMIT.sub(' ', cmd)                   # nombrarlos en el texto de un commit no escribe nada
    if cmd and CONFIG_CANDADO.search(sin_mensaje):
        limpio = REDIRECCION_INOFENSIVA.sub(' ', sin_mensaje)
        tramos = [t for t in TRAMOS_SHELL.split(limpio) if t.strip()]
        if '>' in limpio or OPCION_QUE_ESCRIBE.search(limpio) or SUBCOMANDO.search(limpio) \
                or not all(LECTURA_EN_SHELL.match(t) for t in tramos):
            return aviso_candado
    for ruta in rutas_de(entrada):
        if SECRETO_RUTA.search(ruta) and not SECRETO_PERMITIDO.search(ruta):
            return f'Detenido: {Path(ruta).name} puede traer secretos. Usa el archivo .ejemplo o pide a Haz el dato que falta.'
    if cmd and LEE_EN_SHELL.search(cmd):
        for token in re.split(r'[\s"\'<>|;&]+', cmd):
            if token and SECRETO_RUTA.search(token) and not SECRETO_PERMITIDO.search(token):
                return f'Detenido: el comando lee {Path(token).name}, que puede traer secretos.'
    return None


def rama_actual(cwd=None):
    try:
        return subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True,
                              cwd=cwd, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ''


def revisar_push(herramienta, entrada, rama=None, cwd=None):
    cmd = comando_de(entrada)
    if MERGE_REMOTO.search(cmd):
        return 'Detenido: mergear un PR o sincronizar el repo cambia main en el remoto; lo hace Haz a mano.'
    if PUSH_AMPLIO.search(cmd):                                # en un push o guardado con git config
        return ('Detenido: push.default, remote.*.push y los alias de git cambian que empuja git push; '
                'lo hace Haz a mano.')
    for m in PUSH.finditer(cmd):
        # "main", 'HEAD:main', ma\in y $'main' cuentan igual que main
        resto = re.sub(r'\$(?=["\'])|["\'`\\]', '', m.group(1))
        args, saltar = [], False
        for a in resto.split():
            if saltar:                                         # valor de -o/--push-option/--repo...: no es refspec
                saltar = False
            elif OPCION_CON_VALOR.fullmatch(a):
                saltar = True
            elif not a.startswith('-'):
                args.append(a)
        if RAMA_PROTEGIDA.search(' ' + resto + ' '):
            return 'Detenido: el push a main/master lo hace Haz a mano.'
        if any('*' in a for a in args[1:]):
            return 'Detenido: un refspec con comodin puede empujar main.'
        implicita = any(REFSPEC_IMPLICITA.match(a) for a in args[1:])
        if (len(args) <= 1 or implicita) and '--all' not in resto and '--mirror' not in resto:
            if CAMBIA_CONTEXTO.search(cmd):
                return 'Detenido: el push sin rama explicita va en un comando aparte, sin cambiar de rama ni de carpeta.'
            actual = rama if rama is not None else rama_actual(cwd or entrada.get('cwd'))
            if actual in ('main', 'master'):
                return f'Detenido: estas en {actual}; el push a main lo hace Haz a mano.'
        if '--all' in resto or '--mirror' in resto:
            return 'Detenido: --all/--mirror tambien empuja main.'
    return None


def resumen_inicio(cwd='.'):
    def git(*a):
        try:
            r = subprocess.run(['git', *a], capture_output=True, text=True, cwd=cwd, timeout=15)
            return r.stdout.strip() if r.returncode == 0 else ''
        except (OSError, subprocess.SubprocessError):
            return ''
    raiz = git('rev-parse', '--show-toplevel')
    if not raiz:
        return 'INICIO: no es un repo de git.'
    rama = git('rev-parse', '--abbrev-ref', 'HEAD') or '?'
    cuenta = git('rev-list', '--left-right', '--count', 'origin/main...HEAD')
    atras, adelante = (cuenta.split() + ['?', '?'])[:2] if cuenta else ('?', '?')
    sucios = len([l for l in git('status', '--porcelain').splitlines() if l.strip()])
    hook = Path(raiz, '.git', 'hooks', 'pre-commit')
    candado = 'instalado' if hook.is_file() and 'candado-personal' in hook.read_text(encoding='utf-8', errors='ignore') \
        else 'NO instalado: python agents/_comun/candado/instalar.py'
    lineas = [f'INICIO: rama {rama}; contra origin/main: {atras} atras, {adelante} adelante; '
              f'{sucios} archivos sin commit; candado {candado}.']
    if atras not in ('0', '?'):
        lineas.append('Siguiente paso: git pull --rebase origin main antes de editar.')
    return '\n'.join(lineas)


def aviso_firma(entrada):
    for ruta in rutas_de(entrada):
        p = Path(ruta)
        if p.suffix.lower() not in EXT_CODIGO or SIN_FIRMA_RUTA.search(str(p)) or not p.is_file():
            continue
        try:
            texto = p.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        if not FIRMA.search(texto):
            return f'{p.name} quedo sin firma. Agrega la de su lenguaje (skill estandares-codigo).'
    return None


# ===============================================
# Self Test
# ===============================================
def self_test():
    casos = []
    def P(cmd=None, **k):
        e = dict(k)
        if cmd is not None:
            e['command'] = cmd
        return revisar_proteger('Bash', e)
    casos += [('no-verify', P('git commit --no-verify -m x') is not None),
              ('commit -n', P('git commit -nm x') is not None),
              ('commit -m normal pasa', P('git commit -m "nuevo tablero"') is None),
              ('add -f', P('git add -f data_real/x.csv') is not None),
              ('add normal pasa', P('git add app.js') is None),
              ('hooksPath', P('git config core.hooksPath /dev/null') is not None),
              ('leer .env', P(file_path='C:/r/.env') is not None),
              ('leer .env.ejemplo pasa', P(file_path='C:/r/.env.ejemplo') is None),
              ('leer config.local.json', P(file_path='proj/config.local.json') is not None),
              ('cat id_rsa', P('cat ~/.ssh/id_rsa') is not None),
              ('Get-Content .pem', P('Get-Content .\\cert.pem') is not None),
              ('leer app.py pasa', P(file_path='app.py') is None),
              ('copilot toolArgs', revisar_proteger('bash', leer_evento(json.dumps(
                  {'toolName': 'bash', 'toolArgs': json.dumps({'command': 'git push --no-verify'})}))[2]) is not None)]
    U = lambda c, rama='feat/x': revisar_push('Bash', {'command': c}, rama=rama)
    casos += [('push origin main', U('git push origin main') is not None),
              ('push HEAD:main', U('git push origin HEAD:main') is not None),
              ('push rama pasa', U('git push -u origin feat/agents') is None),
              ('push en main sin refspec', U('git push', rama='main') is not None),
              ('push en rama sin refspec pasa', U('git push') is None),
              ('push --all', U('git push --all') is not None),
              ('push -C repo main', U('git -C ../r push origin master') is not None),
              ('no es push pasa', U('git status') is None),
              ('push "main" con comillas', U('git push origin "main"') is not None),
              ("push 'HEAD:main' con comillas", U("git push origin 'HEAD:main'") is not None),
              ('push origin HEAD en main', U('git push origin HEAD', rama='main') is not None),
              ('push -u origin @ en main', U('git push -u origin @', rama='main') is not None),
              ('push origin HEAD en rama pasa', U('git push origin HEAD') is None),
              ('push HEAD:feat en main pasa', U('git push origin HEAD:feat/x', rama='main') is None)]
    E = lambda herr, **k: revisar_proteger(herr, k)
    casos += [('Write .candado-permitidos', E('Write', file_path='C:/r/.candado-permitidos') is not None),
              ('Edit .candado-modo', E('Edit', file_path='.candado-modo') is not None),
              ('Read .candado-permitidos pasa', E('Read', file_path='.candado-permitidos') is None),
              ('echo > .candado-permitidos', E('Bash', command="echo '*  # x' > .candado-permitidos") is not None),
              ('Set-Content .candado-modo', E('PowerShell', command='Set-Content .candado-modo hibrido') is not None),
              ('cat .candado-permitidos pasa', E('Bash', command='cat .candado-permitidos') is None),
              ('redireccion pegada', E('Bash', command="echo '*  # x' >.candado-permitidos") is not None),
              ('>> pegado', E('Bash', command='echo hibrido >>.candado-modo') is not None),
              ('glob del shell', E('Bash', command='echo x > .candado-permitid*') is not None),
              ('git checkout del archivo', E('Bash', command='git checkout HEAD~1 -- .candado-permitidos') is not None),
              ('tee en tubo', E('Bash', command='cat a.txt | tee .candado-modo') is not None),
              ('python que escribe', E('Bash', command="python -c \"open('.candado-modo','w')\"") is not None),
              ('grep con 2>/dev/null pasa', E('Bash', command='grep candado .candado-permitidos 2>/dev/null') is None),
              ('git diff del archivo pasa', E('Bash', command='git diff -- .candado-modo') is None),
              ('git -C diff del archivo pasa', E('Bash', command='git -C ../r diff .candado-modo') is None),
              ('tubo a Set-Content', E('PowerShell', command='Get-ChildItem .candado-permitidos | Set-Content -Value x') is not None),
              ('tubo a xargs rm', E('Bash', command='ls .candado-modo | xargs rm') is not None),
              ('git diff --output', E('Bash', command='git diff --no-index --output=.candado-permitidos a b') is not None),
              ('rg --pre', E('Bash', command='rg --pre ./x.sh foo .candado-modo') is not None),
              ('cat y wc pasa', E('Bash', command='cat .candado-permitidos | wc -l') is None),
              ('sort -o', E('Bash', command='sort -o .candado-permitidos nuevo.txt') is not None),
              ('uniq entrada salida', E('Bash', command='uniq nuevo.txt .candado-modo') is not None),
              ('cat $( )', E('Bash', command='cat $(cp nuevo.txt .candado-modo)') is not None),
              ('cat con backticks', E('Bash', command='cat `cp nuevo.txt .candado-modo`') is not None),
              ('cat <( )', E('Bash', command='cat <(cp nuevo.txt .candado-modo)') is not None),
              ('Get-Content ( )', E('PowerShell', command='Get-Content (Copy-Item n.txt .candado-modo -PassThru)') is not None),
              ('variable de confirmacion', E('Bash', command='CANDADO_CAMBIO_' + 'CONFIG=1 git commit -m x') is not None)]
    casos += [('push -o valor en main', U('git push -o ci.skip origin', rama='main') is not None),
              ('push --push-option valor en main', U('git push --push-option x origin', rama='main') is not None),
              ('push -o valor y rama pasa', U('git push -o ci.skip origin feat/x', rama='main') is None),
              ('push ma\\in', U('git push origin ma\\in') is not None),
              ("push $'ma'in", U("git push origin $'ma'in") is not None),
              ('push --force-with-lease rama pasa', U('git push --force-with-lease origin feat/x') is None),
              ('push refspec con comodin', U("git push origin 'refs/heads/*:refs/heads/*'") is not None),
              ('push refs/heads/*', U('git push origin refs/heads/*') is not None),
              ('push -c remote.origin.push', U('git -c remote.origin.push=refs/heads/*:refs/heads/* push origin') is not None),
              ('git config push.default', U('git config push.default matching') is not None),
              ('push entre parentesis', U('(git push origin HEAD:main)') is not None),
              ('push main>archivo', U('git push origin main>o.txt') is not None),
              ('push main,feat', U('git push origin main,feat/x') is not None),
              ('push {main,x}', U('git push origin {main,x}') is not None),
              ('push a rama con main adentro pasa', U('git push origin user/haz/maintenance') is None),
              ('switch y push en un comando', U('git switch main && git push') is not None),
              ('checkout y push HEAD', U('git checkout main; git push origin HEAD') is not None),
              ('git -C sin refspec', U('git -C ../otro push') is not None),
              ('alias de git', U('git config alias.p push') is not None),
              ('-c alias', U('git -c alias.p=push p origin x') is not None),
              ('gh pr merge', U('gh pr merge 3 --merge') is not None),
              ('gh pr merge --admin', U('gh pr merge --squash --admin') is not None),
              ('gh api merges', U('gh api repos/o/r/merges -f base=x -f head=y') is not None),
              ('gh repo sync', U('gh repo sync') is not None),
              ('gh pr create pasa', U('gh pr create --base x --title t --body b') is None),
              ('gh pr view pasa', U('gh pr view 3') is None)]
    casos += [('commit-tree', P('git commit-tree abc -p HEAD -m x') is not None),
              ('update-ref', P('git update-ref refs/heads/feat abc') is not None),
              ('git am', P('git am parche.mbox') is not None),
              ('hash-object -w', P('git hash-object -w x.csv') is not None),
              ('commit con "am" en el mensaje pasa', P('git commit -m "I am here"') is None),
              ('CANDADO_REGLAS', P('CANDADO_REGLAS=x git commit -m y') is not None),
              ('USERPROFILE antes de git', P('USERPROFILE=x git commit -m y') is not None),
              ('$env:HOME', P('$env:HOME="x"; git commit -m y') is not None),
              ('mensaje que nombra la config pasa', P('git commit -m "lee .candado-modo de HEAD"') is None),
              ('mensaje y escritura juntos', P('git commit -m "x"; cp a .candado-modo') is not None)]
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        Path(t, 'a.py').write_text('print(1)\n', encoding='utf-8')
        Path(t, 'b.py').write_text('# Author: Haz\nprint(1)\n', encoding='utf-8')
        Path(t, 'c.md').write_text('x', encoding='utf-8')
        casos += [('py sin firma avisa', aviso_firma({'file_path': str(Path(t, 'a.py'))}) is not None),
                  ('py con firma pasa', aviso_firma({'file_path': str(Path(t, 'b.py'))}) is None),
                  ('md no aplica', aviso_firma({'file_path': str(Path(t, 'c.md'))}) is None)]
    malos = [n for n, ok in casos if not ok]
    for n, ok in casos:
        print(('ok    ' if ok else 'FALLA ') + n)
    print(f'\n{len(casos) - len(malos)}/{len(casos)} casos bien')
    return 1 if malos else 0


# ===============================================
# Main
# ===============================================
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    modo = sys.argv[1] if len(sys.argv) > 1 else ''
    if modo == '--self-test':
        sys.exit(self_test())
    texto = '' if sys.stdin.isatty() else sys.stdin.read()
    datos, herramienta, entrada = leer_evento(texto)
    if modo == 'proteger':
        motivo = revisar_proteger(herramienta, entrada)
        if motivo:
            negar(motivo)
    elif modo == 'push-main':
        motivo = revisar_push(herramienta, entrada, cwd=datos.get('cwd'))
        if motivo:
            negar(motivo)
    elif modo == 'inicio':
        print(resumen_inicio(datos.get('cwd') or '.'))
    elif modo == 'firma':
        aviso = aviso_firma(entrada)
        if aviso:
            print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PostToolUse', 'additionalContext': aviso}},
                             ensure_ascii=False))
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
