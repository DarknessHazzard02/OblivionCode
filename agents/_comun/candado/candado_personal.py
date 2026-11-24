#!/usr/bin/env python3
# Made by: Hazzard
# Candado de git para los repos personales: revisa lo que entra a cada commit.
"""
Candado personal: pre-commit y commit-msg para los repos de Haz.

    python candado_personal.py pre-commit          revisa el stage (lo llama .git/hooks/pre-commit)
    python candado_personal.py commit-msg <archivo> revisa el mensaje (lo llama .git/hooks/commit-msg)
    python candado_personal.py --self-test         corre los casos de prueba en un repo temporal

DETIENE el commit (exit 1):
  - secretos: llaves privadas, tokens (GitHub, AWS, Slack, Bearer), contraseñas o llaves en cadenas de
    conexión, archivos .env / .pem / .pfx / .key;
  - datos reales: Excel, CSV, parquet, bases de datos, comprimidos o JSON dentro de data/, salvo que la
    carpeta (o una de arriba) tenga CONTRATO.md; cualquier cosa en data_real/ o config.local.json;
  - archivos de más de 10 MB;
  - material de la empresa: si existe el archivo privado de reglas del hook de copia
    (CANDADO_REGLAS o ~/.claude/hooks/copiar_skills_reglas.json; vive fuera del repo), sus patrones "prohibido" sobre las líneas agregadas;
  - en el mensaje: firma de una herramienta de IA (Co-Authored-By de un asistente, "Generated with").

AVISA, sin detener:
  - archivos de código nuevos o modificados sin la firma personal (Made by: Hazzard / Author: Haz /
    Updated by Haz), con la forma de cada lenguaje;
  - archivos de más de 2 MB.

Excepciones a propósito: `.candado-permitidos` en la raíz del repo, una por renglón:
    ruta/o/patron/*.csv   # por qué se permite
Cada excepción lleva su motivo; sin motivo no cuenta. Tampoco cuenta una con comodín en la carpeta de
arriba (`*.csv`, `[!x]*`): se nombra la carpeta (`proyecto/export/*.csv`).
`.candado-permitidos` y `.candado-modo` cuentan desde el último commit (HEAD). Un commit que los cambia
se detiene; Haz lo confirma a mano con CANDADO_CAMBIO_CONFIG=1 en ese commit.
"""
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

MB = 1024 * 1024
LIMITE_DURO, LIMITE_AVISO = 10 * MB, 2 * MB
REGLAS_PRIVADAS = Path(os.environ.get('CANDADO_REGLAS') or Path.home() / '.claude' / 'hooks' / 'copiar_skills_reglas.json')

EXT_DATOS = ('.xlsx', '.xls', '.xlsm', '.xlsb', '.csv', '.tsv', '.parquet', '.avro', '.feather', '.pbix',
             '.accdb', '.mdb', '.db', '.sqlite', '.sqlite3', '.zip', '.7z', '.rar', '.gz', '.tar')
ARCH_SECRETOS = re.compile(r'(?i)(^|/)(\.env(\.[\w-]+)?|id_rsa|id_ed25519|[^/]+\.(pem|pfx|p12|key|jks|keystore))$')
ENV_EJEMPLO = re.compile(r'(?i)\.env\.(example|ejemplo|sample|template)$')
SECRETOS = [
    ('llave privada', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----')),
    ('token de GitHub', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})\b')),
    ('llave de AWS', re.compile(r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b')),
    ('token de Slack', re.compile(r'\bxox[abposr]-[A-Za-z0-9-]{10,}\b')),
    ('token Bearer', re.compile(r'(?i)\bBearer\s+[A-Za-z0-9\-._~+/]{24,}=*')),
    ('llave de storage', re.compile(r'(?i)\b(?:AccountKey|SharedAccessKey)\s*=\s*[A-Za-z0-9+/]{20,}={0,2}')),
    ('firma SAS', re.compile(r'(?i)[?&]sig=[A-Za-z0-9%+/]{20,}')),
    ('contraseña en cadena de conexión', re.compile(r'(?i)\b(?:password|pwd)\s*=\s*(?!["\']?\s*[;"\'<{$*])[^;\s"\']{4,}')),
    ('secreto en asignación', re.compile(
        r'(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|client[_-]?secret)\b\s*[:=]\s*'
        r'["\'](?![<{$*]|x{3,}|\.{3}|changeme|example|ejemplo|tu[_ ]|your[_ ])[^"\'\s]{6,}["\']')),
]
# Sin firma: solo se avisa. Extensión -> el lenguaje tiene comentarios donde va la firma.
EXT_CODIGO = {'.py', '.sql', '.bas', '.cls', '.vba', '.m', '.pq', '.dax', '.js', '.ts', '.tsx', '.jsx', '.cs',
              '.java', '.css', '.html', '.yml', '.yaml', '.sh', '.ps1'}
FIRMA = re.compile(r'Made by:\s*Hazzard|Author:\s*Haz\b|Updated by Haz', re.I)
# Librerías de terceros: se revisan por tipo y tamaño, no por contenido
VENDOR = re.compile(r'(^|/)(vendor|node_modules)/|\.min\.(js|css)$')
SIN_FIRMA_RUTAS = re.compile(r'(^|/)(\.claude|\.agents|\.github|\.gemini|\.codex|agents|\.git|\.vscode|node_modules|venv|\.venv|demo|data|shared|vendor)/')
FIRMA_IA = re.compile(
    r'(?im)^\s*co-authored-by:.*\b(claude|anthropic|copilot|chatgpt|openai|gpt|gemini|cursor|codeium)\b'
    r'|generated (?:with|by) (?:\[?claude|ai\b|chatgpt|copilot)|🤖\s*generated')

def git(*args, raiz=None, binario=False):
    r = subprocess.run(['git', *args], cwd=raiz, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode('utf-8', 'replace').strip())
    return r.stdout if binario else r.stdout.decode('utf-8', 'replace')

CONFIG_CANDADO = ('.candado-permitidos', '.candado-modo')
# Rutas que ninguna excepción legítima cubre: si un patrón las cubre, es tan amplio que apaga el candado
SONDAS = CONFIG_CANDADO + ('.env', 'config.local.json', 'zq9_sonda.zq9', 'zq9_sonda/zq9.zq9',
                           'zq9/data_real/zq9.zq9', 'data_real/zq9.zq9')
# Una excepción nombra su carpeta de arriba: con comodín ahí (`*`, `[!zc.]*`) cubre casi todo el repo
COMODIN = re.compile(r'[*?\[]')

# Variable con la que Haz confirma, a mano, un commit que cambia la configuración del candado
VAR_CAMBIO_CONFIG = 'CANDADO_CAMBIO_CONFIG'

def leer_config(raiz, nombre):
    """(texto, aviso) de la configuración del candado. Cuenta la versión del último commit (HEAD), ni la
    del disco ni la del índice: un cambio nunca vale en el mismo commit que lo usa, y escribirla por
    cualquier vía (shell, script, sin `git add`) no apaga nada en silencio."""
    try:
        texto = git('show', f'HEAD:{nombre}', raiz=raiz)
    except RuntimeError:
        texto = None
    en_disco = Path(raiz) / nombre
    disco = en_disco.read_text(encoding='utf-8', errors='replace') if en_disco.is_file() else None
    aviso = None
    if disco is not None and disco.replace('\r\n', '\n') != (texto or '').replace('\r\n', '\n'):
        aviso = f'{nombre}: la copia en disco no coincide con la del último commit; cuenta la del commit'
    return texto, aviso

def permitidos(raiz):
    """([(patron, motivo)], [patrones ignorados], aviso) de .candado-permitidos.
    No cuenta un renglón sin motivo ni uno que cubra alguna de las SONDAS (`*`, `**/*`, `[!.]*`,
    `.candado-*`): con ellos se apagaría toda la revisión."""
    texto, aviso = leer_config(raiz, '.candado-permitidos')
    salida, ignorados = [], []
    for linea in (texto or '').splitlines():
        patron, _, motivo = linea.partition('#')
        patron = patron.strip()
        if not patron or not motivo.strip():
            continue
        primer_segmento = patron.lstrip('/').split('/', 1)[0]
        if COMODIN.search(primer_segmento) or any(es_permitido(s, [(patron, '')]) for s in SONDAS):
            ignorados.append(patron)
            continue
        salida.append((patron, motivo.strip()))
    return salida, ignorados, aviso

def es_permitido(ruta, lista):
    return any(fnmatch.fnmatch(ruta, p) or ruta.startswith(p.rstrip('*').rstrip('/') + '/') for p, _ in lista)

def tiene_contrato(raiz, ruta, en_stage):
    """CONTRATO.md en la carpeta del archivo o en una de arriba (en disco o en el stage)."""
    partes = ruta.split('/')[:-1]
    for i in range(len(partes), -1, -1):
        c = '/'.join(partes[:i] + ['CONTRATO.md'])
        if c in en_stage or (Path(raiz) / c).is_file():
            return True
    return False

def patrones_privados():
    if not REGLAS_PRIVADAS.is_file():
        return None
    try:
        d = json.loads(REGLAS_PRIVADAS.read_text(encoding='utf-8'))
        return {k: re.compile(v) for k, v in d.get('prohibido', {}).items()}, re.compile(d.get('correo_ok', r'@example\.com'))
    except Exception:
        return None

def lineas_agregadas(raiz, ruta):
    salida = git('diff', '--cached', '-U0', '--no-color', '--', ruta, raiz=raiz)
    return [l[1:] for l in salida.splitlines() if l.startswith('+') and not l.startswith('+++')]

def modo_repo(raiz):
    """('personal' (default) o 'hibrido', aviso), del primer renglón de .candado-modo en HEAD.
    hibrido = el repo también guarda trabajo de la empresa: no se revisa material de la empresa ni la
    firma personal (lo laboral va sin firma); lo demás se revisa igual."""
    texto, aviso = leer_config(raiz, '.candado-modo')
    primero = (texto or '').split('#', 1)[0].strip().lower()
    return (primero if primero in ('personal', 'hibrido') else 'personal'), aviso

def revisar_stage(raiz):
    """(bloqueos, avisos): listas de textos."""
    nombres = [n for n in git('diff', '--cached', '--name-only', '-z', '--diff-filter=ACMR', raiz=raiz).split('\0') if n]
    en_stage = set(nombres)
    nuevos = {n for n in git('diff', '--cached', '--name-only', '-z', '--diff-filter=A', raiz=raiz).split('\0') if n}
    excepciones, ignorados, aviso_permitidos = permitidos(raiz)
    modo, aviso_modo = modo_repo(raiz)
    hibrido = modo == 'hibrido'
    privados = None if hibrido else patrones_privados()
    bloqueos, avisos = [], [a for a in (aviso_permitidos, aviso_modo) if a]
    for patron in ignorados:
        avisos.append(f'.candado-permitidos: "{patron}" es demasiado amplio o cubre al candado; no cuenta')
    confirmado = os.environ.get(VAR_CAMBIO_CONFIG) == '1'
    for config in CONFIG_CANDADO:
        if config in en_stage and not confirmado:
            bloqueos.append(f'{config}: cambia lo que revisa el candado. Lo confirma Haz a mano, solo en ese commit: '
                            f'$env:{VAR_CAMBIO_CONFIG}="1"; git commit ...; Remove-Item Env:{VAR_CAMBIO_CONFIG}  '
                            f'(bash: {VAR_CAMBIO_CONFIG}=1 git commit ...)')
        elif config in en_stage:
            avisos.append(f'{config}: cambio de configuración confirmado con {VAR_CAMBIO_CONFIG}=1')
    for ruta in nombres:
        if es_permitido(ruta, excepciones):
            continue
        bajo = ruta.lower()
        tam = int(git('cat-file', '-s', f':{ruta}', raiz=raiz).strip() or 0)
        if tam > LIMITE_DURO:
            bloqueos.append(f'{ruta}: pesa {tam / MB:.1f} MB (tope {LIMITE_DURO // MB} MB)')
            continue
        if tam > LIMITE_AVISO:
            avisos.append(f'{ruta}: pesa {tam / MB:.1f} MB; ¿de verdad va al repo?')
        if ARCH_SECRETOS.search(ruta) and not ENV_EJEMPLO.search(ruta):
            bloqueos.append(f'{ruta}: es un archivo de secretos (.env, llave o certificado)')
            continue
        segmentos = bajo.split('/')
        if 'data_real' in segmentos[:-1] or segmentos[-1] == 'config.local.json':
            bloqueos.append(f'{ruta}: data_real/ y config.local.json son locales, nunca al repo')
            continue
        contrato = tiene_contrato(raiz, ruta, en_stage)
        if bajo.endswith(EXT_DATOS) and not contrato:
            bloqueos.append(f'{ruta}: archivo de datos sin CONTRATO.md que diga que son inventados')
            continue
        if bajo.endswith('.json') and 'data' in segmentos[:-1] and not contrato:
            bloqueos.append(f'{ruta}: JSON en data/ sin CONTRATO.md (se trata como datos reales)')
            continue
        contenido = git('show', f':{ruta}', raiz=raiz, binario=True)
        if b'\0' in contenido[:8000]:
            continue                                          # binario: ya se revisó por tipo y tamaño
        if VENDOR.search('/' + bajo):
            continue                                          # librería de terceros minificada: sus IDs y su código dan falsos positivos
        agregadas = contenido.decode('utf-8', 'replace').splitlines() if ruta in nuevos else lineas_agregadas(raiz, ruta)
        for n, linea in enumerate(agregadas, 1):
            for motivo, patron in SECRETOS:
                if patron.search(linea):
                    bloqueos.append(f'{ruta}: {motivo} → «{linea.strip()[:80]}»')
            if privados:
                prohibidos, correo_ok = privados
                for motivo, patron in prohibidos.items():
                    for m in patron.finditer(linea):
                        if motivo == 'correo real' and correo_ok.search(m.group(0)):
                            continue
                        bloqueos.append(f'{ruta}: {motivo} ({m.group(0)}) → material de la empresa')
        ext = os.path.splitext(bajo)[1]
        if not hibrido and ext in EXT_CODIGO and not SIN_FIRMA_RUTAS.search('/' + bajo):
            if not FIRMA.search(contenido.decode('utf-8', 'replace')):
                avisos.append(f'{ruta}: sin firma (Made by: Hazzard / Author: Haz / Updated by Haz)')
    if privados is None and not hibrido:
        if os.environ.get('CANDADO_REGLAS'):
            bloqueos.append('CANDADO_REGLAS apunta a un archivo que no existe o no se lee: '
                            'no se puede revisar material de la empresa')
        else:
            avisos.append('sin las reglas privadas del hook de copia: no se revisó material de la empresa')
    return bloqueos, avisos

def revisar_mensaje(texto):
    return [f'firma de IA en el mensaje → «{m.group(0).strip()}»' for m in FIRMA_IA.finditer(texto)]

def reportar(bloqueos, avisos, que):
    for a in avisos:
        print(f'  aviso  {a}')
    if bloqueos:
        print(f'\nCANDADO PERSONAL: {que} detenido.')
        for b in bloqueos:
            print(f'  ✗ {b}')
        print('\nSaca el archivo del stage (git restore --staged <archivo>), quita el secreto o el dato real,\n'
              'o, si de verdad debe entrar, agrégalo a .candado-permitidos con su motivo.')
        return 1
    return 0

# --- pruebas -----------------------------------------------------------------------------------------
def self_test():
    casos = [
        # (archivo, contenido, debe_bloquear, descripcion)
        ('Dev_Coding/SQL/q.sql', '-- Made by: Hazzard\nSELECT 1', False, 'SQL firmado'),
        ('Dev_Coding/Python/x.py', 'import os\n', False, 'Python sin firma: solo aviso'),
        # Los secretos de prueba van partidos para que este archivo pase su propio candado
        ('app/config.py', 'API_KEY = "sk-' + '9f8e7d6c5b4a3210"\n', True, 'llave en asignación'),
        ('app/ejemplo.py', 'PASSWORD = "<tu-contraseña>"\n', False, 'marcador, no secreto'),
        ('app/db.txt', 'Server=x;Database=y;User Id=u;Pass' + 'word=Sup3rSecreta;\n', True, 'contraseña en cadena'),
        ('app/db2.txt', 'Server=x;Password=;\n', False, 'cadena sin contraseña'),
        ('app/k.txt', '-----BEGIN RSA PRIVATE ' + 'KEY-----\nabc\n', True, 'llave privada'),
        ('app/t.md', 'token ghp_' + 'A' * 36 + '\n', True, 'token de GitHub'),
        ('.env', 'X=1\n', True, '.env'),
        ('.env.example', 'X=\n', False, '.env.example'),
        ('proyecto/ventas.csv', 'a,b\n1,2\n', True, 'CSV sin contrato'),
        ('proyecto/demo/source/ventas.csv', 'a,b\n1,2\n', False, 'CSV con contrato'),
        ('proyecto/data/meta.json', '{}', True, 'JSON en data/ sin contrato'),
        ('otro/data_real/meta.json', '{}', True, 'data_real/'),
        ('otro/config.local.json', '{}', True, 'config.local.json'),
        ('permitido/export.csv', 'a\n', False, 'excepción con motivo'),
    ]
    fallos = 0
    with tempfile.TemporaryDirectory() as t:
        git('init', '-q', raiz=t)
        git('config', 'user.email', 'prueba@example.com', raiz=t)
        git('config', 'user.name', 'prueba', raiz=t)
        Path(t, 'proyecto/demo').mkdir(parents=True)
        Path(t, 'proyecto/demo/CONTRATO.md').write_text('datos: inventados\n', encoding='utf-8')
        Path(t, '.candado-permitidos').write_text('permitido/*.csv   # export de prueba sin datos\n', encoding='utf-8')
        git('add', '.candado-permitidos', raiz=t)               # cuenta la de HEAD: se fija en un commit base
        git('commit', '-q', '-m', 'base', raiz=t)
        for ruta, contenido, debe, desc in casos:
            git('reset', '-q', raiz=t)
            p = Path(t, ruta)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(contenido, encoding='utf-8')
            git('add', '-f', ruta, raiz=t)
            bloqueos, _ = revisar_stage(t)
            obtenido = any(b.startswith(ruta) for b in bloqueos)
            ok = obtenido == debe
            fallos += not ok
            print(f"  {'ok ' if ok else 'FALLA'}  {'DETIENE' if obtenido else 'PASA   '}  {desc}")
        # archivo grande
        git('reset', '-q', raiz=t)
        Path(t, 'grande.bin').write_bytes(b'\0' * (LIMITE_DURO + 1))
        git('add', 'grande.bin', raiz=t)
        ok = any('grande.bin' in b for b in revisar_stage(t)[0])
        fallos += not ok
        print(f"  {'ok ' if ok else 'FALLA'}  {'DETIENE' if ok else 'PASA   '}  archivo de más de 10 MB")
    for texto, debe, desc in [('Arreglo del filtro', False, 'mensaje normal'),
                              ('x\n\nCo-Authored-By: Claude <noreply' + '@' + 'anthropic.com>', True, 'Co-Authored-By de IA'),
                              ('x\n\nGenerated with Claude Code', True, '"Generated with"'),
                              ('x\n\nCo-Authored-By: Haz <haz@example.com>', False, 'coautor humano')]:
        ok = bool(revisar_mensaje(texto)) == debe
        fallos += not ok
        print(f"  {'ok ' if ok else 'FALLA'}  {'DETIENE' if debe else 'PASA   '}  {desc}")
    # modo hibrido: material de la empresa y firma no se revisan; secretos y datos sí
    with tempfile.TemporaryDirectory() as t:
        git('init', '-q', raiz=t)
        git('config', 'user.email', 'prueba@example.com', raiz=t)
        git('config', 'user.name', 'prueba', raiz=t)
        Path(t, '.candado-modo').write_text('hibrido   # trabajo y notas personales\n', encoding='utf-8')
        git('add', '.candado-modo', raiz=t)
        git('commit', '-q', '-m', 'base', raiz=t)
        Path(t, 'x.py').write_text('import os\n', encoding='utf-8')
        Path(t, 'y.csv').write_text('a\n1\n', encoding='utf-8')
        git('add', 'x.py', 'y.csv', raiz=t)
        bloqueos, avisos = revisar_stage(t)
        for ok, desc in [(not any('sin firma' in a for a in avisos), 'híbrido: no avisa firma'),
                         (any(b.startswith('y.csv') for b in bloqueos), 'híbrido: sigue deteniendo datos sin contrato')]:
            fallos += not ok
            print(f"  {'ok ' if ok else 'FALLA'}  {desc}")
    # excepciones demasiado amplias o que cubren al candado: no cuentan
    with tempfile.TemporaryDirectory() as t:
        git('init', '-q', raiz=t)
        git('config', 'user.email', 'prueba@example.com', raiz=t)
        git('config', 'user.name', 'prueba', raiz=t)
        Path(t, '.candado-permitidos').write_text('*   # todo\n**/*   # todo\n.candado-*   # yo mismo\n',
                                                  encoding='utf-8')
        git('add', '.candado-permitidos', raiz=t)
        git('commit', '-q', '-m', 'base', raiz=t)
        Path(t, 'z.csv').write_text('a\n1\n', encoding='utf-8')
        git('add', 'z.csv', raiz=t)
        bloqueos, avisos = revisar_stage(t)
        casos_config = [(any(b.startswith('z.csv') for b in bloqueos), 'permitidos con "*" no apaga el candado'),
                        (sum('demasiado amplio' in a for a in avisos) == 3, 'avisa los 3 patrones ignorados')]
        # cambiar la configuración en el stage: no vale en ese commit y se detiene sin la confirmación de Haz
        Path(t, '.candado-permitidos').write_text('z.csv   # metido en el mismo commit\n', encoding='utf-8')
        git('add', '.candado-permitidos', raiz=t)
        anterior = os.environ.pop(VAR_CAMBIO_CONFIG, None)
        bloqueos, _ = revisar_stage(t)
        casos_config += [(any(b.startswith('.candado-permitidos') for b in bloqueos),
                          'cambio de configuración sin confirmar se detiene'),
                         (any(b.startswith('z.csv') for b in bloqueos),
                          'la excepción nueva no vale en el mismo commit')]
        os.environ[VAR_CAMBIO_CONFIG] = '1'
        bloqueos, _ = revisar_stage(t)
        casos_config.append((not any(b.startswith('.candado-permitidos') for b in bloqueos),
                             f'con {VAR_CAMBIO_CONFIG}=1 el cambio pasa'))
        os.environ.pop(VAR_CAMBIO_CONFIG)
        if anterior is not None:
            os.environ[VAR_CAMBIO_CONFIG] = anterior
        for ok, desc in casos_config:
            fallos += not ok
            print(f"  {'ok ' if ok else 'FALLA'}  {desc}")
    # clase de caracteres y configuración cambiada solo en disco
    with tempfile.TemporaryDirectory() as t:
        git('init', '-q', raiz=t)
        git('config', 'user.email', 'prueba@example.com', raiz=t)
        git('config', 'user.name', 'prueba', raiz=t)
        Path(t, '.candado-permitidos').write_text('[!.]*   # todo lo que no empiece con punto\n'
                                                  '[!zc.]*   # esquiva las sondas\n[d-y]*   # rango\n',
                                                  encoding='utf-8')
        git('add', '.candado-permitidos', raiz=t)
        git('commit', '-q', '-m', 'base', raiz=t)
        Path(t, 'w.csv').write_text('a\n1\n', encoding='utf-8')
        git('add', 'w.csv', raiz=t)
        ok = any(b.startswith('w.csv') for b in revisar_stage(t)[0])
        fallos += not ok
        print(f"  {'ok ' if ok else 'FALLA'}  clases de caracteres ([!.]*, [!zc.]*, [d-y]*) no apagan el candado")
        Path(t, '.candado-permitidos').write_text('w.csv   # metido solo en disco\n', encoding='utf-8')
        Path(t, '.candado-modo').write_text('hibrido   # solo en disco\n', encoding='utf-8')
        bloqueos, avisos = revisar_stage(t)
        for ok, desc in [(any(b.startswith('w.csv') for b in bloqueos), 'excepción solo en disco no cuenta'),
                         (sum('no coincide con la del último commit' in a for a in avisos) == 2,
                          'avisa la configuración cambiada en disco')]:
            fallos += not ok
            print(f"  {'ok ' if ok else 'FALLA'}  {desc}")
    total = len(casos) + 15
    print(f"\n{'los ' + str(total) + ' casos pasaron' if not fallos else str(fallos) + ' casos FALLARON'}")
    return 1 if fallos else 0

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if '--self-test' in sys.argv:
        return self_test()
    modo = sys.argv[1] if len(sys.argv) > 1 else 'pre-commit'
    if modo == 'commit-msg':
        texto = Path(sys.argv[2]).read_text(encoding='utf-8', errors='replace')
        return reportar(revisar_mensaje(texto), [], 'el commit')
    raiz = git('rev-parse', '--show-toplevel').strip()
    return reportar(*revisar_stage(raiz), 'el commit')

if __name__ == '__main__':
    sys.exit(main())
