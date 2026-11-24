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
    carpeta (o una de arriba) tenga CONTRATO.md; lo mismo con .txt/.dat/.prn/.xml que tengan forma de export
    (lista ALV, tabla con separador, XML de hoja), también en UTF-16; cualquier cosa en data_real/ o config.local.json;
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
from collections import Counter
from pathlib import Path

MB = 1024 * 1024
LIMITE_DURO, LIMITE_AVISO = 10 * MB, 2 * MB
REGLAS_PRIVADAS = Path(os.environ.get('CANDADO_REGLAS') or Path.home() / '.claude' / 'hooks' / 'copiar_skills_reglas.json')

EXT_DATOS = ('.xlsx', '.xls', '.xlsm', '.xlsb', '.csv', '.tsv', '.parquet', '.avro', '.feather', '.pbix',
             '.accdb', '.mdb', '.db', '.sqlite', '.sqlite3', '.zip', '.7z', '.rar', '.gz', '.tar', '.prn')
# Texto que a veces es un export (ALV de SAP, "Texto Unicode" de Excel, XML de hoja): se revisa el contenido
EXT_TEXTO_DATOS = ('.txt', '.dat', '.xml', '.htm', '.html', '.rtf')
# Campo de export: número (europeo, con signo al final, moneda o %) o fecha con hora opcional. Con una sola coma
# por renglón separa una tabla de 2 columnas de la prosa, que trae una coma por renglón seguido.
CAMPO_DATO = re.compile(r'[$€]?\s?-?(?=[\d.,]*\d)[\d.,]+-?\s?%?|\d{1,4}[/.-]\d{1,2}[/.-]\d{1,4}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?')
# Un solo ; por renglón que NO es columna: comentario después (`//`, `/*`, `# x`, `-- x`) o marcador de entorno
# de requirements. `--` pegado a texto solo es comentario en un renglón de SQL; `;--`, `;--N/A` o `;--4521` son
# valores de un export.
PYC_NO_COLUMNA = re.compile(r';\s*(//|/\*|--\s+\S|#\s)|;\s*(python_version|python_full_version|sys_platform|'
                            r'platform_\w+|os_name|implementation_\w+|extra)\b')
SQL_COMENTARIO = re.compile(r'^\s*(select|insert|update|delete|drop|create|alter|exec|with|merge)\b.*;\s*--[a-z]',
                            re.I)
# El ; al final cierra una sentencia solo si el renglón trae algo de código: operador (`=`, `+`, `:`, llaves,
# `<>`) o una llamada (`f(`). `M00001;` o `Tornillo (M6);` (última columna vacía) siguen siendo export.
PYC_FIN = re.compile(r';\s*$')
CODIGO_EN_RENGLON = re.compile(r'[=*{}<>]|\+\+|--;|:\s+[a-z]|\w\(|^\s*(return|using|import|export)\b')
ANCHO_FIJO = re.compile(r'\S {2,}(?=\S)')
HTML_FILA = re.compile(r'<tr\b', re.I)
RTF_FILA = re.compile(r'\\row\b')
RTF_RENGLON = re.compile(r'\\(par|line)\b ?')
RTF_COLUMNA = re.compile(r'\\(tab|cell)\b ?')
RTF_HEX = re.compile(r"\\'[0-9a-f]{2}", re.I)                 # \'e9 = é: un solo carácter, no tres
RTF_CONTROL = re.compile(r'\\[a-z]+-?\d* ?|\\[^a-z]', re.I)
MIN_FILAS_TABLA = 20
XML_HOJA = re.compile(r'urn:schemas-microsoft-com:office:spreadsheet|<(ss:)?Workbook\b', re.I)
XML_FILA = re.compile(r'<(ss:)?Row\b|<(row|record|item)\b', re.I)
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

def decodificar(contenido):
    """Texto del archivo, o None si es binario. Reconoce UTF-16 (con BOM o con un byte nulo de cada dos),
    que es como Excel guarda "Texto Unicode" y como salen algunos exports: no se salta como binario."""
    muestra = contenido[:8000]
    if muestra.startswith((b'\xff\xfe', b'\xfe\xff')):
        return contenido.decode('utf-16', 'replace')
    if b'\0' in muestra:
        pares, impares = muestra[0::2], muestra[1::2]
        if impares and impares.count(0) > 0.9 * len(impares) and pares.count(0) < 0.1 * len(pares):
            return contenido.decode('utf-16-le', 'replace')
        if pares and pares.count(0) > 0.9 * len(pares) and impares.count(0) < 0.1 * len(impares):
            return contenido.decode('utf-16-be', 'replace')
        return None
    return contenido.decode('utf-8', 'replace')

def parece_tabla(texto, ruta):
    """True si el texto tiene forma de export: XML de hoja de Excel o con muchas filas repetidas, o al menos
    MIN_FILAS_TABLA renglones donde la mayoría trae el mismo número de separadores (| o tabulador al menos una
    vez; ; o coma, dos o más, o uno solo con una columna de números o fechas), o columnas de ancho fijo (spool de SAP sin barras): 3 o más columnas que empiezan
    en la misma posición en la mayoría de los renglones. El código alineado y la salida de --help alinean una o
    dos columnas, no tres. HTML y RTF de una descarga se miden por sus filas de tabla."""
    if ruta.endswith('.xml'):
        return bool(XML_HOJA.search(texto)) or len(XML_FILA.findall(texto)) >= MIN_FILAS_TABLA
    if ruta.endswith(('.htm', '.html')):
        return len(HTML_FILA.findall(texto)) >= MIN_FILAS_TABLA
    if ruta.endswith('.rtf'):
        if len(RTF_FILA.findall(texto)) >= MIN_FILAS_TABLA:
            return True
        texto = RTF_HEX.sub('?', RTF_COLUMNA.sub('\t', RTF_RENGLON.sub('\n', texto)))
        texto = RTF_CONTROL.sub('', texto).replace('{', '').replace('}', '')
    lineas = [l for l in texto.splitlines() if l.strip()]
    if len(lineas) < MIN_FILAS_TABLA:
        return False
    minimo = 0.6 * len(lineas)
    # Mismo número de separadores en casi todos los renglones = columnas. Con un solo separador (2 columnas):
    # el ; cuenta salvo que cierre la sentencia (JS) o abra un marcador de entorno (requirements), porque un
    # export de texto puro (`Nombre;Correo`) también es dato; la coma pide además una columna de número o
    # fecha, porque la prosa trae una coma por renglón seguido.
    for sep in ('|', '\t', ';', ','):
        cuentas = [l.strip().count(sep) for l in lineas]
        moda = max(set(cuentas), key=cuentas.count)
        if sum(1 for c in cuentas if c >= 3) >= minimo:
            return True
        if moda < 1 or cuentas.count(moda) < 0.8 * len(lineas):
            continue
        if moda >= 2 or sep in '|\t':
            return True
        unicos = [l.strip() for l in lineas if l.strip().count(sep) == 1]
        if sep == ';' and sum(1 for l in unicos if not es_sentencia(l)) >= 0.8 * len(lineas):
            return True
        if sep == ',' and dos_columnas_con_dato(unicos, sep):
            return True
    inicios = Counter(m.end() for l in lineas for m in ANCHO_FIJO.finditer(l.rstrip()))
    return sum(1 for n in inicios.values() if n >= minimo) >= 3

def es_sentencia(linea):
    """True si el único ; del renglón es código y no un separador de columnas."""
    return bool(PYC_NO_COLUMNA.search(linea) or SQL_COMENTARIO.search(linea)
                or (PYC_FIN.search(linea) and CODIGO_EN_RENGLON.search(linea)))

def es_numeracion(valores, otra):
    """True si la columna es una lista numerada (1, 2, 3...) de texto: enteros sin ceros a la izquierda que
    empiezan en 0 o 1 y suben de uno en uno, junto a renglones de 3 palabras o más sin correos. Un ID
    autoincremental (1000, 1001...) o con relleno (00001) junto a un nombre sigue siendo export."""
    if not all(re.fullmatch(r'0|[1-9]\d*', v, re.ASCII) for v in valores):
        return False
    numeros = [int(v) for v in valores]
    if numeros[0] not in (0, 1) or any(b != a + 1 for a, b in zip(numeros, numeros[1:])):
        return False
    # Prosa: 3 palabras o más, sin correo y con alguna en minúscula. `Juan Perez Lopez` es un nombre, no un paso
    return sum(1 for t in otra if len(t.split()) >= 3 and '@' not in t
               and any(w[:1].islower() for w in t.split())) >= 0.8 * len(otra)

def dos_columnas_con_dato(unicos, sep):
    """True si en el 80 % de los renglones (con un solo `sep`) alguna de las dos columnas es número o fecha.
    Una columna que solo numera los renglones (`1, paso`) no cuenta: es una lista, no un dato."""
    partes = [[c.strip().strip('"') for c in l.split(sep)] for l in unicos]
    if not partes:
        return False
    for i in (0, 1):
        valores, otra = [p[i] for p in partes], [p[1 - i] for p in partes]
        if sum(1 for v in valores if CAMPO_DATO.fullmatch(v)) >= 0.8 * len(partes) and not es_numeracion(valores, otra):
            return True
    return False

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
        texto = decodificar(contenido)
        if texto is None:
            continue                                          # binario: ya se revisó por tipo y tamaño
        utf16 = b'\0' in contenido[:8000]                     # git lo ve binario: su diff no trae líneas
        if bajo.endswith(EXT_TEXTO_DATOS) and not contrato and parece_tabla(texto, bajo):
            bloqueos.append(f'{ruta}: parece un export de datos (tabla, lista ALV o XML de Excel) '
                            f'sin CONTRATO.md que diga que son inventados')
            continue
        if VENDOR.search('/' + bajo):
            continue                                          # librería de terceros minificada: sus IDs y su código dan falsos positivos
        agregadas = texto.splitlines() if ruta in nuevos or utf16 else lineas_agregadas(raiz, ruta)
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
            if not FIRMA.search(texto):
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
        ('export/mb52.txt', ''.join(f'|M{i:05d} |Product A |UN |PL01|  {i} |\n' for i in range(30)), True,
         'lista ALV en .txt sin contrato'),
        ('export/ventas.dat', ''.join(f'{i};A;B;{i * 2}\n' for i in range(30)), True, '.dat con ; sin contrato'),
        ('export/hoja.xml', '<?xml version="1.0"?>\n<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet">'
         '</Workbook>\n', True, 'XML de hoja de Excel'),
        ('proyecto/demo/source/alv.txt', ''.join(f'|M{i} |A |B |C |\n' for i in range(30)), False,
         'lista ALV con contrato'),
        ('app/requirements.txt', 'pandas==2.2.3\npyarrow==17.0.0\n', False, 'requirements.txt'),
        ('export/spool.txt', ''.join(f'M{i:05d}    Product A      UN    PL01      {i:>6}\n' for i in range(30)), True,
         'spool de ancho fijo en .txt'),
        ('export/hoja.prn', 'M1    A    1\n', True, '.prn sin contrato'),
        ('export/dos_cols.txt', ''.join(f'M{i}\t{i}\n' for i in range(30)), True, 'export de 2 columnas con tabulador'),
        ('export/tres_cols.txt', ''.join(f'M{i};A;{i}\n' for i in range(30)), True, 'export de 3 columnas con ;'),
        ('export/comas.txt', ''.join(f'M{i},A,{i}\n' for i in range(30)), True, 'export de 3 columnas con coma'),
        ('export/lista.htm', '<table>' + ''.join(f'<tr><td>M{i}</td><td>{i}</td></tr>' for i in range(30)) + '</table>',
         True, 'descarga HTML con tabla'),
        ('export/lista.rtf', '{\\rtf1 ' + ''.join(f'M{i:05d}    Product A      UN    PL01\\par ' for i in range(30)) + '}',
         True, 'descarga RTF de ancho fijo'),
        ('export/tabs.rtf', '{\\rtf1 ' + ''.join(f'M{i}\\tab Product A\\tab UN\\tab {i}\\par ' for i in range(30)) + '}',
         True, 'descarga RTF con \\tab'),
        ('export/acentos.rtf', '{\\rtf1 ' + ''.join(
            f'M{i:05d}    {"Pi\\\'f1on    " if i % 2 else "Product A"}      UN    PL01\\par ' for i in range(30)) + '}',
         True, "descarga RTF con acentos (\\'f1)"),
        ('docs/codigo.txt', ''.join(f'valor_{i:02d}  = {i}    # comentario\n' for i in range(30)), False,
         'código alineado en .txt'),
        ('docs/ayuda.txt', ''.join(f'  --opcion-{i:02d}    hace la cosa {i}\n' for i in range(30)), False,
         'salida de --help en .txt'),
        ('docs/prosa.txt', ''.join(f'Renglón {i}{", y algo más" * (i % 3)} aquí.\n' for i in range(30)), False,
         'prosa con comas variables'),
        ('docs/notas.txt',''.join(f'renglón {i} de notas, con una coma\n' for i in range(30)), False,
         'notas de texto con comas sueltas'),
        ('export/dos_comas.txt', ''.join(f'M{i:05d},{i * 3}\n' for i in range(30)), True, 'export de 2 columnas con coma'),
        ('export/dos_pyc.txt', ''.join(f'Product {i};{i},50-\n' for i in range(30)), True,
         'export de 2 columnas con ; y número europeo'),
        ('export/fechas.txt', ''.join(f'M{i},2026-11-{i % 28 + 1:02d}\n' for i in range(30)), True,
         'export de 2 columnas con fecha'),
        ('export/contactos.txt', ''.join(f'Persona {i};persona{i}@example.com\n' for i in range(30)), True,
         'export de 2 columnas de texto con ;'),
        ('export/montos.txt', ''.join(f'Pedido {i},${i}.50\n' for i in range(30)), True,
         'export de 2 columnas con coma y moneda'),
        ('export/comillas.txt', ''.join(f'"M{i}","{i * 3}"\n' for i in range(30)), True,
         'export de 2 columnas con coma y comillas'),
        ('export/folios.txt', ''.join(f'Cliente {i};#{4500 + i}\n' for i in range(30)), True,
         'export de 2 columnas con folio #'),
        ('export/una_col.txt', ''.join(f'M{i:05d};\n' for i in range(30)), True,
         'export con la última columna vacía (M00001;)'),
        ('export/guiones.txt', ''.join(f'Cliente {i};--{4500 + i}\n' for i in range(30)), True,
         'export de 2 columnas con -- y número'),
        ('docs/pasos.txt', ''.join(f'{i}, paso del proceso número {i}\n' for i in range(1, 31)), False,
         'lista numerada con coma'),
        ('docs/sql.txt', ''.join(f'SELECT {i}; --nota {i}\n' for i in range(30)), False,
         'SQL con comentario pegado al --'),
        ('export/ids.txt', ''.join(f'{1000 + i}, Cliente {i}\n' for i in range(30)), True,
         'export con ID autoincremental y nombre'),
        ('export/relleno.txt', ''.join(f'{i + 1:05d}, Juan {i}\n' for i in range(30)), True,
         'export con ID con ceros a la izquierda'),
        ('export/correos.txt', ''.join(f'{i + 1},persona{i}@correo.com\n' for i in range(30)), True,
         'export con numeración y correo'),
        ('export/vacios.txt', ''.join(f'Cliente {i};--\n' for i in range(30)), True, 'export con -- como vacío'),
        ('export/parentesis.txt', ''.join(f'Tornillo (M{i});\n' for i in range(30)), True,
         'export con paréntesis y ; final'),
        ('export/empleados.txt', ''.join(f'{i + 1}, Juan Perez Lopez {i}\n' for i in range(30)), True,
         'lista numerada de nombres completos'),
        ('export/horas.txt', ''.join(f'2026-01-05 08:{i:02d};\n' for i in range(30)), True,
         'export de una columna con hora y ; final'),
        ('docs/using.txt', ''.join(f'using System.Mod{i};\n' for i in range(30)), False, 'bloque de using en C#'),
        ('docs/js.txt', ''.join(f'x{i}++;\n' for i in range(30)), False, 'JS x++;'),
        ('docs/css.txt', ''.join(f'color: red{i};\n' for i in range(30)), False, 'CSS con ; final'),
        ('docs/sql_fin.txt', ''.join(f'UPDATE t SET x = {i};\n' for i in range(30)), False,
         'SQL con ; al final'),
        ('docs/capitulos.txt', ''.join(f'Capitulo {i}, ...\n' for i in range(30)), False,
         'texto con coma y puntos suspensivos'),
        ('docs/comentado.txt', ''.join(f'x{i} = {i}; // nota {i}\n' for i in range(30)), False,
         'JS con comentario después del ;'),
        ('docs/script.txt', ''.join(f'const valor{i} = calcula({i});\n' for i in range(30)), False,
         'JS con un ; por renglón'),
        ('docs/reqs.txt', ''.join(f'paquete{i}==1.{i}; python_version < "3.12"\n' for i in range(30)), False,
         'requirements con marcadores'),
        ('export/lista.html', '<!-- Made by: Hazzard --><table>' + ''.join(
            f'<tr><td>M{i}</td><td>{i}</td></tr>' for i in range(30)) + '</table>', True, 'descarga guardada como .html'),
        ('web/index.html', '<!-- Made by: Hazzard --><table><tr><td>KPI</td></tr></table>', False, 'tablero .html'),
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
        # "Texto Unicode" de Excel (UTF-16 con tabuladores) y un secreto en UTF-16 sin BOM: no se saltan como binario
        for ruta, datos, desc in [
                ('export/unicode.txt', ''.join(f'M{i}\tA\tB\t{i}\n' for i in range(30)).encode('utf-16'),
                 'Texto Unicode de Excel (UTF-16)'),
                ('app/clave16.txt', ('API_KEY = "sk-' + '9f8e7d6c5b4a3210"\n').encode('utf-16-le'),
                 'secreto en UTF-16 sin BOM')]:
            git('reset', '-q', raiz=t)
            p = Path(t, ruta)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(datos)
            git('add', '-f', ruta, raiz=t)
            ok = any(b.startswith(ruta) for b in revisar_stage(t)[0])
            fallos += not ok
            print(f"  {'ok ' if ok else 'FALLA'}  {'DETIENE' if ok else 'PASA   '}  {desc}")
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
    total = len(casos) + 17
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
