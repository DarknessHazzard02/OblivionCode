#!/usr/bin/env python3
# Made by: Hazzard
# Candado de git para los repos personales: revisa lo que entra a cada commit.
"""
Candado personal: pre-commit y commit-msg para BI_DataNexus y OblivionCode.

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
    (~/.claude/hooks/copiar_skills_reglas.json), sus patrones "prohibido" sobre las líneas agregadas;
  - en el mensaje: firma de una herramienta de IA (Co-Authored-By de un asistente, "Generated with").

AVISA, sin detener:
  - archivos de código nuevos o modificados sin la firma personal (Made by: Hazzard / Author: Haz /
    Updated by Haz), con la forma de cada lenguaje;
  - archivos de más de 2 MB.

Excepciones a propósito: `.candado-permitidos` en la raíz del repo, una por renglón:
    ruta/o/patron/*.csv   # por qué se permite
Cada excepción lleva su motivo; sin motivo no cuenta.
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
REGLAS_PRIVADAS = Path.home() / '.claude' / 'hooks' / 'copiar_skills_reglas.json'

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
SIN_FIRMA_RUTAS = re.compile(r'(^|/)(\.claude|\.git|\.vscode|node_modules|venv|\.venv|demo|data|shared|vendor)/')
FIRMA_IA = re.compile(
    r'(?im)^\s*co-authored-by:.*\b(claude|anthropic|copilot|chatgpt|openai|gpt|gemini|cursor|codeium)\b'
    r'|generated (?:with|by) (?:\[?claude|ai\b|chatgpt|copilot)|🤖\s*generated')

def git(*args, raiz=None, binario=False):
    r = subprocess.run(['git', *args], cwd=raiz, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode('utf-8', 'replace').strip())
    return r.stdout if binario else r.stdout.decode('utf-8', 'replace')

def permitidos(raiz):
    """[(patron, motivo)] de .candado-permitidos; un renglón sin motivo no cuenta."""
    f = Path(raiz) / '.candado-permitidos'
    salida = []
    if f.is_file():
        for linea in f.read_text(encoding='utf-8').splitlines():
            patron, _, motivo = linea.partition('#')
            if patron.strip() and motivo.strip():
                salida.append((patron.strip(), motivo.strip()))
    return salida

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

def revisar_stage(raiz):
    """(bloqueos, avisos): listas de textos."""
    nombres = [n for n in git('diff', '--cached', '--name-only', '-z', '--diff-filter=ACMR', raiz=raiz).split('\0') if n]
    en_stage = set(nombres)
    nuevos = {n for n in git('diff', '--cached', '--name-only', '-z', '--diff-filter=A', raiz=raiz).split('\0') if n}
    excepciones = permitidos(raiz)
    privados = patrones_privados()
    bloqueos, avisos = [], []
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
        if ext in EXT_CODIGO and not SIN_FIRMA_RUTAS.search('/' + bajo):
            if not FIRMA.search(contenido.decode('utf-8', 'replace')):
                avisos.append(f'{ruta}: sin firma (Made by: Hazzard / Author: Haz / Updated by Haz)')
    if privados is None:
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
    total = len(casos) + 5
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
