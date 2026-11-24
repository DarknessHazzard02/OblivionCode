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
]
PUSH = re.compile(r'\bgit\b(?:\s+-C\s+\S+)?[^;&|\n]*?\bpush\b([^;&|\n]*)', re.I)
RAMA_PROTEGIDA = re.compile(r'(^|[\s:+/])(main|master)(\s|$)')
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


def revisar_push(herramienta, entrada, rama=None):
    cmd = comando_de(entrada)
    for m in PUSH.finditer(cmd):
        resto = m.group(1)
        args = [a for a in resto.split() if not a.startswith('-')]
        if RAMA_PROTEGIDA.search(' ' + resto + ' '):
            return 'Detenido: el push a main/master lo hace Haz a mano.'
        if len(args) <= 1 and '--all' not in resto and '--mirror' not in resto:
            actual = rama if rama is not None else rama_actual(entrada.get('cwd'))
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
              ('no es push pasa', U('git status') is None)]
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
        motivo = revisar_push(herramienta, entrada)
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
