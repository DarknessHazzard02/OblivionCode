# Author: Haz
# Genera data/dashboard.json y data/meta.json para el tablero Willow_Creek.
#
# Cruza los reportes diarios de Willow Creek (Willow Creek Orders Report) contra SAP:
#   - WC_FOLLOWUP   todas las ordenes abiertas de SAP (Excel o CSV)
#   - SDD167        job de SAP con las ordenes de clientes WC (lista ALV)
#   - ZWCCUST       clientes dados de alta para WC, con su dominio y Order Manager
# y marca las ordenes de WC sin procesar, con error o mal capturadas.
# Solo libreria estandar de Python (el Excel se lee como zip).
#
# Uso:  python generar_datos.py [carpeta_de_origen]
#
# La carpeta de origen se busca en este orden:
#   1. el argumento
#   2. la variable de entorno WILLOWCREEK_SOURCE
#   3. config.local.json -> {"source": "..."}  (ignorado por git)
#   4. ./demo/source  (datos inventados, versionados)
# Con datos reales escribe en ./data_real (ignorada por git); con los demo, en ./data.

import csv
import hashlib
import json
import os
import re
import statistics
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DEMO_SOURCE = AQUI / 'demo' / 'source'


def resolve_source():
    if len(sys.argv) > 1:
        return Path(sys.argv[1]), 'argumento'
    if os.environ.get('WILLOWCREEK_SOURCE'):
        return Path(os.environ['WILLOWCREEK_SOURCE']), 'WILLOWCREEK_SOURCE'
    config = AQUI / 'config.local.json'
    if config.exists():
        source = json.loads(config.read_text(encoding='utf-8-sig')).get('source')
        if source:
            return Path(source), 'config.local.json'
    return DEMO_SOURCE, 'default'


SOURCE, SOURCE_FROM = resolve_source()
DEMO = SOURCE.resolve() == DEMO_SOURCE.resolve()
OUT = AQUI / ('data' if DEMO else 'data_real')
print(f'Modo: {"DEMO (datos inventados)" if DEMO else "REAL"}  Origen ({SOURCE_FROM}): {SOURCE}')
print(f'Salida: {OUT}')

REPORTS_DIR = 'Willow Creek Orders Report'
# Un archivo es "consolidado" si trae al menos esto de fechas de recepcion distintas.
CONSOLIDADO_MIN_DIAS = 15

# --- Catalogos de Reporting Notes (Basecamp, Jordan Blake, Apr 20) -----------

WC_STATUS_DOC = {'Blocked', 'In Progress', 'Invalid Request', 'Review Rejected', 'Starting', 'Success'}
NOTAS_DOC = {
    'Buyer Not Approved For Automation', "Can't Identify Ship-To Party", "Can't Identify Sold-To Party",
    "Can't Match Material ID", 'Duplicate PO FILE was rejected', 'Missing Price', 'Multiple Orders Submitted',
    'No Delivery Date on PO', 'No Order Submitted', 'Order Complete', 'Order Parsed', 'Price Mismatch',
}
PARES_DOC = {
    ('Blocked', "Can't Identify Ship-To Party"), ('Blocked', "Can't Identify Sold-To Party"),
    ('Blocked', "Can't Match Material ID"), ('Blocked', 'Missing Price'),
    ('In Progress', 'Order Parsed'),
    ('Invalid Request', 'Buyer Not Approved For Automation'), ('Invalid Request', 'Duplicate PO FILE was rejected'),
    ('Invalid Request', 'Missing Price'), ('Invalid Request', 'Multiple Orders Submitted'),
    ('Invalid Request', 'No Delivery Date on PO'), ('Invalid Request', 'No Order Submitted'),
    ('Invalid Request', 'Price Mismatch'),
    ('Review Rejected', 'Order Parsed'),
    ('Success', 'Order Complete'),
}

# Hallazgos: codigo -> rol. Las etiquetas viven en meta.filters.hallazgos.
HALLAZGOS = [
    ('BLOQ', 'critical', 'Bloqueada por WC', 'Blocked by WC',
     'WC Status = Blocked: WC no pudo procesarla (ver la nota).', 'WC Status = Blocked: WC could not process it (see the note).'),
    ('INVAL', 'critical', 'Solicitud Inválida', 'Invalid Request',
     'WC Status = Invalid Request: la frenó una regla de Contoso.', 'WC Status = Invalid Request: stopped by a Contoso rule.'),
    ('ERR_WC', 'critical', 'Error Interno de WC', 'WC Internal Error',
     'WC Status = Internal Error o nota Willow Creek Computer Error.', 'WC Status = Internal Error or note Willow Creek Computer Error.'),
    ('RECH', 'critical', 'Rechazada en Revisión', 'Rejected in Review',
     'El OM la rechazó (Review Rejected / Rejected).', 'The OM rejected it (Review Rejected / Rejected).'),
    ('ERR_SAP', 'critical', 'Error al Crear en SAP', 'SAP Creation Error',
     'SAP Status = Error: no se creó la orden de venta.', 'SAP Status = Error: the sales order was not created.'),
    ('SIN_RESP', 'critical', 'SAP sin Respuesta', 'No Response from SAP',
     'SAP Status = No Response: SAP no contestó en 30 minutos.', 'SAP Status = No Response: SAP did not answer within 30 minutes.'),
    ('EXITO_SIN_SO', 'critical', 'Éxito sin Número de SO', 'Success without SO Number',
     'WC y SAP dicen Success pero no hay número de orden de venta.', 'WC and SAP say Success but there is no sales order number.'),
    ('SOLD_VACIO', 'critical', 'Sin Sold-To', 'No Sold-To',
     'La orden llegó sin Sold To ID.', 'The order arrived without a Sold To ID.'),
    ('SOLD_DIF', 'critical', 'Sold-To en SAP Distinto', 'Different Sold-To in SAP',
     'El Sold-To de la orden de venta en SAP no es el que trae WC.', 'The SAP sales order Sold-To is not the one WC has.'),
    ('PEND_REV', 'warn', 'Pendiente de Revisión', 'Awaiting Review',
     'Review Status = Awaiting Review o Not Started, sin error.', 'Review Status = Awaiting Review or Not Started, with no error.'),
    ('EN_PROC', 'warn', 'En Proceso', 'In Progress',
     'WC Status = In Progress o Starting, sin error.', 'WC Status = In Progress or Starting, with no error.'),
    ('INCONS', 'warn', 'WC Success con SAP en Error', 'WC Success with SAP Error',
     'WC Status = Success pero SAP Status = Error: el estatus de WC no refleja la falla.', 'WC Status = Success but SAP Status = Error: the WC status hides the failure.'),
    ('ADV_SAP', 'warn', 'Advertencias de SAP', 'SAP Warnings',
     'SAP Status = Warnings: se creó, pero con advertencias.', 'SAP Status = Warnings: created, but with warnings.'),
    ('PO_DIF', 'warn', 'PO en SAP Distinto al de WC', 'SAP PO Differs from WC',
     'El PO capturado en la orden de venta no es igual al de WC.', 'The PO on the sales order is not the same as in WC.'),
    ('PO_MULTI_SO', 'warn', 'PO con Más de un SO', 'PO with More than One SO',
     'El mismo PO del cliente aparece en más de una orden de venta abierta.', 'The same customer PO appears on more than one open sales order.'),
    ('BLOQ_ENTREGA', 'warn', 'SO con Bloqueo de Entrega', 'SO with Delivery Block',
     'Alguna línea de la orden de venta tiene bloqueo de entrega en SAP.', 'A sales order line has a delivery block in SAP.'),
    ('SOLD_NO_CAT', 'warn', 'Sold-To Fuera de ZWCCUST', 'Sold-To Not in ZWCCUST',
     'El Sold To ID no está en el catálogo de clientes WC.', 'The Sold To ID is not in the WC customer catalog.'),
    ('OM_VACIO', 'warn', 'Sin Order Manager', 'No Order Manager',
     'La orden no trae Order Manager.', 'The order has no Order Manager.'),
    ('OM_DIF', 'warn', 'Order Manager Distinto a ZWCCUST', 'Order Manager Differs from ZWCCUST',
     'El Order Manager no es el asignado al cliente en ZWCCUST.', 'The Order Manager is not the one assigned to the customer in ZWCCUST.'),
    ('ESTATUS_NO_DOC', 'warn', 'Estatus No Documentado', 'Undocumented Status',
     'WC Status fuera de la lista de Reporting Notes.', 'WC Status outside the Reporting Notes list.'),
    ('NOTA_NO_DOC', 'neutral', 'Nota No Documentada', 'Undocumented Note',
     'Nota fuera de la lista de Reporting Notes (p. ej. "PO: n", Date Format Parsing Error).', 'Note outside the Reporting Notes list (e.g. "PO: n", Date Format Parsing Error).'),
    ('PAR_NO_DOC', 'neutral', 'Estatus y Nota sin Pareja Documentada', 'Status/Note Pair Not Documented',
     'La combinación WC Status + Nota no está en la tabla Matched Data Pairs.', 'The WC Status + Note combination is not in the Matched Data Pairs table.'),
    ('CAPTURADA_MANUAL', 'neutral', 'Capturada a Mano en SAP', 'Entered Manually in SAP',
     'WC no creó la orden, pero el mismo PO ya está en una orden abierta de SAP capturada fuera de WC.', 'WC did not create the order, but the same PO is on an open SAP order entered outside WC.'),
    ('SO_NO_ABIERTA', 'neutral', 'SO No Está Abierta en SAP', 'SO Not Open in SAP',
     'El SO no aparece en WC_FOLLOWUP: puede estar ya surtido o cerrado.', 'The SO is not in WC_FOLLOWUP: it may already be shipped or closed.'),
    ('REINTENTO', 'neutral', 'Reenviada', 'Resubmitted',
     'El mismo PO llegó en más de un envío a WC.', 'The same PO came in more than one WC submission.'),
]
ROL = {h[0]: h[1] for h in HALLAZGOS}
CRITICOS_PROCESO = {'BLOQ', 'INVAL', 'ERR_WC', 'RECH', 'ERR_SAP', 'SIN_RESP', 'EXITO_SIN_SO'}


# --- Lectores ------------------------------------------------------------------

def text(v):
    return '' if v is None else str(v).strip()


def leer_xlsx(path):
    """Primera hoja como lista de diccionarios (encabezado = primer renglon)."""
    z = zipfile.ZipFile(path)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        x = z.read('xl/sharedStrings.xml').decode('utf-8')
        for si in re.findall(r'<si>(.*?)</si>', x, re.S):
            ss.append(''.join(re.findall(r'<t[^>]*>([^<]*)</t>', si)))
    hojas = sorted(n for n in z.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml$', n))
    x = z.read(hojas[0]).decode('utf-8')
    filas = []
    for row in re.findall(r'<row[^>]*>(.*?)</row>', x, re.S):
        r = {}
        for attrs, body in re.findall(r'<c ([^>]*?)(?:/>|>(.*?)</c>)', row, re.S):
            col = re.search(r'r="([A-Z]+)', attrs).group(1)
            tipo = re.search(r't="(\w+)"', attrs)
            v = re.search(r'<v>(.*?)</v>', body or '')
            inline = re.search(r'<t[^>]*>(.*?)</t>', body or '')
            val = v.group(1) if v else (inline.group(1) if inline else '')
            if tipo and tipo.group(1) == 's' and val != '':
                val = ss[int(val)]
            r[col] = val.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&apos;', "'")
        filas.append(r)
    if not filas:
        return [], []
    cab = filas[0]
    cols = sorted(cab, key=lambda c: (len(c), c))
    nombres, vistos = [], Counter()
    for c in cols:   # encabezados repetidos (ZWCCUST trae dos "E-Mail Address") -> sufijo
        n = text(cab[c]); vistos[n] += 1
        nombres.append(n if vistos[n] == 1 else f'{n} {vistos[n]}')
    return nombres, [{n: text(f.get(c, '')) for c, n in zip(cols, nombres)} for f in filas[1:]]


def leer_csv(path):
    with open(path, encoding='utf-8-sig', newline='') as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return [], []
    cab, nombres, vistos = rows[0], [], Counter()
    for n in cab:
        n = text(n); vistos[n] += 1
        nombres.append(n if vistos[n] == 1 else f'{n} {vistos[n]}')
    return nombres, [{n: text(r[i]) if i < len(r) else '' for i, n in enumerate(nombres)} for r in rows[1:]]


def leer_tabla(path):
    return leer_xlsx(path) if path.suffix.lower() == '.xlsx' else leer_csv(path)


def leer_alv(path):
    """Lista ALV de SAP (SDD167): renglones con '|', encabezado repetido por pagina."""
    raw = path.read_bytes()
    try:
        txt = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        txt = raw.decode('latin-1')
    cab, filas = None, []
    for line in txt.splitlines():
        if not line.startswith('|') or line.startswith('|-'):
            continue
        celdas = [c.strip() for c in line.strip().strip('|').split('|')]
        if 'Sales Doc.' in celdas:
            cab = celdas
            continue
        if cab and len(celdas) == len(cab):
            filas.append(dict(zip(cab, celdas)))
    return cab or [], filas


def ultimo(patron):
    archivos = sorted(SOURCE.glob(patron))
    archivos = [a for a in archivos if a.suffix.lower() in ('.xlsx', '.csv')]
    return archivos[-1] if archivos else None


def fecha_de_nombre(nombre):
    m = re.search(r'(\d{4})-?(\d{2})-?(\d{2})', nombre)
    return f'{m.group(1)}-{m.group(2)}-{m.group(3)}' if m else None


def fecha_excel(v):
    """Serial de Excel, MM/DD/YYYY o ISO -> ISO. Lo que no se entiende sale vacio, no inventado."""
    v = text(v)
    if not v:
        return ''
    if re.fullmatch(r'\d+(\.0+)?', v):
        return (date(1899, 12, 30) + timedelta(days=int(float(v)))).isoformat()
    m = re.fullmatch(r'(\d{2})/(\d{2})/(\d{4})', v)
    if m:
        return f'{m.group(3)}-{m.group(1)}-{m.group(2)}'
    if re.match(r'\d{4}-\d{2}-\d{2}', v):
        return v[:10]
    return ''


def num(v):
    v = text(v).replace(',', '')
    try:
        return float(v)
    except ValueError:
        return None


def doc(v):
    """Numero de documento de SAP sin ceros a la izquierda; '0000000000' cuenta como vacio."""
    return text(v).lstrip('0')


def cliente(v):
    return text(v).lstrip('0')


def norm_po(v):
    return re.sub(r'\s+', '', text(v)).upper()


def po_suelto(v):
    """PO para buscarlo en SAP aunque se haya capturado distinto: solo letras y numeros, sin 'PO' al inicio."""
    return re.sub(r'^PO', '', re.sub(r'[^A-Z0-9]', '', text(v).upper()))


def iso_dt(v):
    v = text(v)
    return v[:16].replace('T', ' ') if v else ''


# --- 1. Reportes de Willow Creek --------------------------------------------------

RE_ARCHIVO = re.compile(r'(\d{4}-\d{2}-\d{2}) (\d{2}) (AM|PM)', re.I)


def corte_de(nombre):
    m = RE_ARCHIVO.search(nombre)
    if not m:
        return None
    h = int(m.group(2)) % 12 + (12 if m.group(3).upper() == 'PM' else 0)
    return f'{m.group(1)} {h:02d}:00'


dir_rep = SOURCE / REPORTS_DIR
reportes = sorted(dir_rep.glob('*.csv'), key=lambda p: (corte_de(p.name) or '', p.name)) if dir_rep.exists() else []
if not reportes:
    raise SystemExit(f'No hay reportes de Willow Creek en {dir_rep}: no se genera el tablero.')

archivos, envios = [], {}
hash_a_archivo, ids_vistos = {}, set()
for p in reportes:
    corte = corte_de(p.name)
    cab, filas = leer_csv(p)
    h = hashlib.md5(p.read_bytes()).hexdigest()
    recibidos = sorted({f.get('Received Date', '')[:10] for f in filas if f.get('Received Date')})
    nuevos = 0
    for f in filas:
        fid = f.get('ID') or f"{f.get('PO Number')}|{f.get('Received Date')}"
        if fid not in ids_vistos:
            nuevos += 1
            ids_vistos.add(fid)
        e = envios.setdefault(fid, {'primer_archivo': corte, 'veces': 0})
        e.update(f)
        e['ultimo_archivo'] = corte
        e['veces'] += 1
    archivos.append({
        'archivo': p.name, 'corte': corte or '', 'fecha': (corte or '')[:10],
        'columnas': len(cab), 'filas': len(filas), 'nuevos': nuevos,
        'recibido_min': recibidos[0] if recibidos else '', 'recibido_max': recibidos[-1] if recibidos else '',
        'dias_recibido': len(recibidos), 'bytes': p.stat().st_size,
        'identico_a': hash_a_archivo.get(h, ''),
        'sin_corte': corte is None,
    })
    hash_a_archivo.setdefault(h, p.name)

# Marcas por archivo: formato, repetidos, tamano fuera de lo normal, consolidado
mediana = statistics.median([a['filas'] for a in archivos]) or 1
formatos = Counter(a['columnas'] for a in archivos)
formato_actual = archivos[-1]['columnas']
por_dia = Counter(a['fecha'] for a in archivos)
for a in archivos:
    marcas = []
    if a['columnas'] != formato_actual:
        marcas.append('FORMATO_ANTERIOR')
    if a['identico_a']:
        marcas.append('IDENTICO')
    if a['filas'] == 0:
        marcas.append('VACIO')
    if a['filas'] >= 3 * mediana and a['filas'] >= 10:
        marcas.append('GRANDE')
    if a['dias_recibido'] >= CONSOLIDADO_MIN_DIAS:
        marcas.append('CONSOLIDADO')
    if por_dia[a['fecha']] > 1:
        marcas.append('VARIOS_POR_DIA')
    if a['sin_corte']:
        marcas.append('SIN_FECHA_EN_NOMBRE')
    a['marcas'] = marcas
consolidados = [a['archivo'] for a in archivos if 'CONSOLIDADO' in a['marcas']]
cambio_formato = next((a['fecha'] for a in archivos if a['columnas'] == formato_actual), '')
corte_final = archivos[-1]['corte']

# --- 2. SAP ---------------------------------------------------------------------

f_fu, f_cust = ultimo('WC_FOLLOWUP_*'), ultimo('ZWCCUST_*')
sdd_files = sorted(SOURCE.glob('SDD167_*.csv'))
f_sdd = sdd_files[-1] if sdd_files else None

_, fu = leer_tabla(f_fu) if f_fu else ([], [])
_, zwc = leer_tabla(f_cust) if f_cust else ([], [])
_, sdd = leer_alv(f_sdd) if f_sdd else ([], [])

CUST = {}
for r in zwc:
    c = cliente(r.get('Customer'))
    if c and not text(r.get('Del')):
        CUST[c] = {'nombre': text(r.get('Name')), 'dominio': text(r.get('Domain')).lower(),
                   'om': text(r.get('E-Mail Address')).lower(), 'om2': text(r.get('E-Mail Address 2')).lower()}

# Ordenes abiertas de SAP por documento
SO = defaultdict(lambda: {'lineas': 0, 'cantidad': 0.0, 'bloqueos': set(), 'po': '', 'sold': '', 'sold_nombre': '',
                          'creado': '', 'creado_por': '', 'potyp': '', 'sorg': '', 'entrega': ''})
for r in fu:
    d = doc(r.get('Sales Doc.'))
    if not d:
        continue
    s = SO[d]
    s['lineas'] += 1
    s['cantidad'] += num(r.get('Order Quantity')) or 0
    if text(r.get('Schedule line blocked for delivery')):
        s['bloqueos'].add(text(r.get('Schedule line blocked for delivery')))
    s['po'] = text(r.get('Purchase Order Number'))
    s['sold'] = cliente(r.get('Sold-To Pt'))
    s['sold_nombre'] = text(r.get('Sold-To Party'))
    s['creado'] = fecha_excel(r.get('Created On'))
    s['creado_por'] = text(r.get('Created By'))
    s['potyp'] = text(r.get('POtyp'))
    s['sorg'] = text(r.get('SOrg.'))
    e = fecha_excel(r.get('Req.dlv.dt'))
    s['entrega'] = min(filter(None, [s['entrega'], e]), default='')
SO = dict(SO)
po_a_so, suelto_a_so = defaultdict(set), defaultdict(set)
for d, s in SO.items():
    po_a_so[(s['sold'], norm_po(s['po']))].add(d)
    if po_suelto(s['po']):
        suelto_a_so[po_suelto(s['po'])].add(d)

sdd_docs = {doc(r.get('Sales Doc.')) for r in sdd if doc(r.get('Sales Doc.'))}
sdd_no_en_fu = sorted(sdd_docs - set(SO))

# --- 3. Ordenes de WC por PO: ultima actualizacion --------------------------------

por_po = defaultdict(list)
for fid, e in envios.items():
    e['_id'] = fid
    e['_so'] = doc(e.get('SO Number'))
    por_po[norm_po(e.get('PO Number')) or fid].append(e)


def orden_envio(e):
    return (e.get('ultimo_archivo') or '', e.get('Received Date') or '', e['_id'])


def resuelto(e):
    return e.get('WC Status') == 'Success' and e.get('SAP Status') in ('Success', 'Warnings') and e['_so']


ordenes, intentos = [], {}
wc_so = set()
for key, lista in por_po.items():
    lista.sort(key=orden_envio)
    ok = [e for e in lista if resuelto(e)]
    # Ultima actualizacion; si algun envio ya quedo creado en SAP, manda ese (un rechazo
    # posterior suele ser el duplicado del mismo PO y no deja la orden sin procesar).
    e = ok[-1] if ok else lista[-1]
    for x in lista:
        if x['_so']:
            wc_so.add(x['_so'])
    wc, rev, sap = e.get('WC Status', ''), e.get('Review Status', ''), e.get('SAP Status', '')
    nota = e.get('Note', '')
    nota_cat = 'PO: <n>' if nota.startswith('PO:') else nota
    sold = cliente(e.get('Sold To ID'))
    om = text(e.get('Order Manager')).lower()
    so = e['_so']
    h = []
    if wc == 'Blocked': h.append('BLOQ')
    if wc == 'Invalid Request': h.append('INVAL')
    if wc == 'Internal Error' or nota == 'Willow Creek Computer Error': h.append('ERR_WC')
    if wc == 'Review Rejected' or rev == 'Rejected': h.append('RECH')
    if sap == 'Error': h.append('ERR_SAP')
    if sap == 'No Response': h.append('SIN_RESP')
    if wc == 'Success' and sap == 'Success' and not so: h.append('EXITO_SIN_SO')
    if not sold: h.append('SOLD_VACIO')
    criticos = bool(set(h) & CRITICOS_PROCESO)
    if not criticos and rev in ('Awaiting Review', 'Not Started'): h.append('PEND_REV')
    if not criticos and wc in ('In Progress', 'Starting'): h.append('EN_PROC')
    if wc == 'Success' and sap == 'Error': h.append('INCONS')
    if sap == 'Warnings': h.append('ADV_SAP')
    s = SO.get(so) if so else None
    if so and s:
        if norm_po(s['po']) != norm_po(e.get('PO Number')): h.append('PO_DIF')
        if sold and s['sold'] != sold: h.append('SOLD_DIF')
        if s['bloqueos']: h.append('BLOQ_ENTREGA')
        if len(po_a_so.get((s['sold'], norm_po(s['po'])), ())) > 1: h.append('PO_MULTI_SO')
    elif so:
        h.append('SO_NO_ABIERTA')
    if sold and CUST and sold not in CUST: h.append('SOLD_NO_CAT')
    if not om: h.append('OM_VACIO')
    elif sold in CUST and CUST[sold]['om'] and om not in (CUST[sold]['om'], CUST[sold]['om2']): h.append('OM_DIF')
    if wc and wc not in WC_STATUS_DOC: h.append('ESTATUS_NO_DOC')
    if nota and nota not in NOTAS_DOC: h.append('NOTA_NO_DOC')
    elif wc and nota and (wc, nota) not in PARES_DOC: h.append('PAR_NO_DOC')
    if len(lista) > 1: h.append('REINTENTO')
    # Si WC no la creo, se busca el PO en SAP: muchas se capturan a mano despues.
    manual = []
    if not so:
        manual = sorted(d for d in suelto_a_so.get(po_suelto(e.get('PO Number')), ())
                        if not sold or SO[d]['sold'] == sold or SO[d]['sold'] in CUST)
        if manual: h.append('CAPTURADA_MANUAL')

    if criticos and manual:
        cat = 'MANUAL'
    elif criticos:
        cat = 'ERROR'
    elif 'PEND_REV' in h or 'EN_PROC' in h:
        cat = 'PENDIENTE'
    elif any(ROL[x] in ('critical', 'warn') for x in h):
        cat = 'OBSERVACIONES'
    else:
        cat = 'PROCESADA'
    recibido = (e.get('Received Date') or '')[:10]
    ordenes.append({
        'po': text(e.get('PO Number')), 'categoria': cat, 'hallazgos': h,
        'wc_status': wc, 'review_status': rev, 'sap_status': sap, 'nota': nota_cat, 'nota_txt': nota,
        'sold_id': sold, 'sold_nombre': text(e.get('Sold To Name')),
        'ship_id': cliente(e.get('Ship To ID')), 'ship_nombre': text(e.get('Ship To Name')),
        'om': om, 'om_zwccust': CUST.get(sold, {}).get('om', ''),
        'so': so, 'so_manual': ', '.join(manual), 'so_po': s['po'] if s else '', 'so_sold': s['sold'] if s else '',
        'so_lineas': s['lineas'] if s else None, 'so_entrega': s['entrega'] if s else '',
        'so_bloqueos': ', '.join(sorted(s['bloqueos'])) if s else '',
        'recibido': recibido, 'fecha_orden': text(e.get('Order Date'))[:10],
        'sap_enviado': iso_dt(e.get('SAP Submit Timestamp')),
        'revision_lista': iso_dt(e.get('Review Available')), 'revision_hecha': iso_dt(e.get('Review Completed')),
        'asunto': text(e.get('Subject')),
        'mes': recibido[:7],
        'dias': (date.fromisoformat(corte_final[:10]) - date.fromisoformat(recibido)).days if recibido and corte_final else None,
        'intentos': len(lista), 'ultimo_archivo': e.get('ultimo_archivo') or '',
    })
    intentos[text(e.get('PO Number'))] = [
        [x['_id'], (x.get('Received Date') or '')[:16].replace('T', ' '), x.get('primer_archivo') or '', x.get('ultimo_archivo') or '',
         x.get('WC Status', ''), x.get('Review Status', ''), x.get('SAP Status', ''), x.get('Note', ''), x['_so']]
        for x in lista]

# --- 4. Ordenes de SAP de clientes WC que no pasaron por WC -------------------------

desde = min((o['recibido'] for o in ordenes if o['recibido']), default='')
wc_por_po = defaultdict(list)
for o in ordenes:
    wc_por_po[po_suelto(o['po'])].append(o)
sap_sin_wc = []
for d, s in SO.items():
    if s['sold'] not in CUST or d in wc_so or (desde and s['creado'] and s['creado'] < desde):
        continue
    en_wc = wc_por_po.get(po_suelto(s['po']), []) if po_suelto(s['po']) else []
    if any(o['so'] for o in en_wc):
        tipo = 'DUPLICADO'          # WC ya creo una SO para ese PO y hay otra
    elif en_wc:
        tipo = 'MANUAL_TRAS_WC'     # fallo en WC y alguien la capturo a mano
    else:
        tipo = 'SIN_WC'
    sap_sin_wc.append({
        'so': d, 'tipo': tipo, 'po': s['po'], 'potyp': s['potyp'] or '', 'sorg': s['sorg'],
        'sold_id': s['sold'], 'sold_nombre': s['sold_nombre'] or CUST[s['sold']]['nombre'],
        'creado': s['creado'], 'creado_por': s['creado_por'], 'om_zwccust': CUST[s['sold']]['om'],
        'entrega': s['entrega'], 'lineas': s['lineas'], 'cantidad': round(s['cantidad'], 3),
        'bloqueos': ', '.join(sorted(s['bloqueos'])), 'en_sdd167': d in sdd_docs,
        'mes': s['creado'][:7],
    })

# --- 5. Salida --------------------------------------------------------------------

OUT.mkdir(parents=True, exist_ok=True)
dashboard = {'ordenes': ordenes, 'intentos': intentos, 'sap_sin_wc': sap_sin_wc, 'archivos': archivos}
(OUT / 'dashboard.json').write_text(json.dumps(dashboard, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

cat_counts = Counter(o['categoria'] for o in ordenes)
h_counts = Counter(x for o in ordenes for x in o['hallazgos'])
meta = {
    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
    'demo': DEMO,
    'fuente': 'datos inventados (generar_demo.py)' if DEMO else 'generar_datos.py (carpeta local de Willow Creek)',
    'corte_wc': corte_final,
    'counts': {
        'archivos': len(archivos), 'envios': len(envios), 'ordenes': len(ordenes),
        'categoria': dict(cat_counts), 'hallazgos': dict(h_counts),
        'sap_sin_wc': len(sap_sin_wc), 'wc_followup_filas': len(fu), 'wc_followup_so': len(SO),
        'zwccust': len(CUST), 'sdd167_filas': len(sdd), 'sdd167_so': len(sdd_docs),
    },
    'archivos_resumen': {
        'total': len(archivos), 'consolidados': consolidados, 'consolidado_min_dias': CONSOLIDADO_MIN_DIAS,
        'formatos': {str(k): v for k, v in formatos.items()}, 'formato_actual': formato_actual,
        'cambio_formato': cambio_formato,
        'identicos': sum(1 for a in archivos if a['identico_a']),
        'primero': archivos[0]['corte'], 'ultimo': corte_final,
        'mediana_filas': mediana, 'max_filas': max(a['filas'] for a in archivos),
    },
    'avisos': {
        'sdd167_no_en_wc_followup': len(sdd_no_en_fu),
        'sin_wc_followup': f_fu is None, 'sin_zwccust': f_cust is None, 'sin_sdd167': f_sdd is None,
    },
    'filters': {
        'categoria': [
            {'valor': 'ERROR', 'rol': 'critical', 'es': 'Con Error / Sin Procesar', 'en': 'Error / Not Processed'},
            {'valor': 'MANUAL', 'rol': 'manual', 'es': 'Error en WC, Capturada a Mano en SAP', 'en': 'WC Error, Entered Manually in SAP'},
            {'valor': 'PENDIENTE', 'rol': 'warn', 'es': 'Pendiente', 'en': 'Pending'},
            {'valor': 'OBSERVACIONES', 'rol': 'obs', 'es': 'Procesada con Observaciones', 'en': 'Processed with Findings'},
            {'valor': 'PROCESADA', 'rol': 'ok', 'es': 'Procesada', 'en': 'Processed'},
        ],
        'hallazgos': [{'valor': c, 'rol': r, 'es': es, 'en': en, 'desc_es': de, 'desc_en': dn}
                      for c, r, es, en, de, dn in HALLAZGOS],
        'tipo_sap': [
            {'valor': 'DUPLICADO', 'rol': 'critical', 'es': 'PO Ya Creado por WC en Otra SO (Posible Duplicado)', 'en': 'PO Already Created by WC on Another SO (Possible Duplicate)'},
            {'valor': 'MANUAL_TRAS_WC', 'rol': 'manual', 'es': 'Capturada a Mano tras Fallar en WC', 'en': 'Entered Manually After Failing in WC'},
            {'valor': 'SIN_WC', 'rol': 'warn', 'es': 'Sin Registro en WC', 'en': 'No WC Record'},
        ],
        'marcas_archivo': [
            {'valor': 'CONSOLIDADO', 'rol': 'critical', 'es': 'Parece Consolidado', 'en': 'Looks Consolidated'},
            {'valor': 'GRANDE', 'rol': 'warn', 'es': 'Mucho Más Grande que lo Normal', 'en': 'Much Larger than Usual'},
            {'valor': 'FORMATO_ANTERIOR', 'rol': 'warn', 'es': 'Formato Anterior (Menos Columnas)', 'en': 'Older Format (Fewer Columns)'},
            {'valor': 'IDENTICO', 'rol': 'neutral', 'es': 'Idéntico a Otro Archivo', 'en': 'Identical to Another File'},
            {'valor': 'VARIOS_POR_DIA', 'rol': 'neutral', 'es': 'Varios Archivos el Mismo Día', 'en': 'Several Files the Same Day'},
            {'valor': 'VACIO', 'rol': 'warn', 'es': 'Sin Renglones', 'en': 'No Rows'},
            {'valor': 'SIN_FECHA_EN_NOMBRE', 'rol': 'critical', 'es': 'Sin Fecha en el Nombre', 'en': 'No Date in the Name'},
        ],
    },
    'fuentes': [
        {'nombre': 'Willow Creek Orders Report · reportes diarios', 'nombre_en': 'Willow Creek Orders Report · daily reports',
         'sistema': 'Willow Creek', 'tabla': REPORTS_DIR + '/',
         'archivo': f'{len(archivos)} archivos ({archivos[0]["archivo"]} … {archivos[-1]["archivo"]})',
         'extraido_el': corte_final[:10], 'actualizado': corte_final,
         'dato_al': max((o['recibido'] for o in ordenes if o['recibido']), default=None),
         'filas': sum(a['filas'] for a in archivos), 'falta': False},
        {'nombre': 'WC_FOLLOWUP · órdenes abiertas de SAP', 'nombre_en': 'WC_FOLLOWUP · SAP open orders',
         'sistema': 'SAP', 'tabla': f_fu.name if f_fu else 'WC_FOLLOWUP_*', 'archivo': f_fu.name if f_fu else '',
         'extraido_el': fecha_de_nombre(f_fu.name) if f_fu else None, 'actualizado': None,
         'dato_al': max((s['creado'] for s in SO.values() if s['creado']), default=None),
         'filas': len(fu), 'falta': f_fu is None},
        {'nombre': 'SDD167 · job WC PO Follow Up', 'nombre_en': 'SDD167 · WC PO Follow Up job',
         'sistema': 'SAP', 'tabla': f_sdd.name if f_sdd else 'SDD167_*', 'archivo': f_sdd.name if f_sdd else '',
         'extraido_el': fecha_de_nombre(f_sdd.name) if f_sdd else None, 'actualizado': None,
         'dato_al': max((fecha_excel(r.get('Created On')) for r in sdd), default=None),
         'filas': len(sdd), 'falta': f_sdd is None},
        {'nombre': 'ZWCCUST · clientes WC', 'nombre_en': 'ZWCCUST · WC customers',
         'sistema': 'SAP', 'tabla': f_cust.name if f_cust else 'ZWCCUST_*', 'archivo': f_cust.name if f_cust else '',
         'extraido_el': fecha_de_nombre(f_cust.name) if f_cust else None, 'actualizado': None,
         'dato_al': None, 'filas': len(zwc), 'falta': f_cust is None, 'catalogo': True},
    ],
    'pestanas_sin_actualizar': {},
}
(OUT / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')

print(f'Reportes: {len(archivos)} · envíos: {len(envios)} · órdenes (PO): {len(ordenes)}')
print('Categorías: ' + ', '.join(f'{k} {v}' for k, v in cat_counts.most_common()))
print(f'SAP de clientes WC sin WC: {len(sap_sin_wc)} · SDD167 que no está en WC_FOLLOWUP: {len(sdd_no_en_fu)}')
print(f'Consolidado: {", ".join(consolidados) if consolidados else "ninguno"}')
print(f'Escrito: {OUT / "dashboard.json"} ({(OUT / "dashboard.json").stat().st_size:,} bytes)')
print(f'Escrito: {OUT / "meta.json"}')
