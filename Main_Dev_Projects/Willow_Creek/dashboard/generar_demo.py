# Author: Haz
# Escribe datos INVENTADOS en demo/source/ con la misma forma que la carpeta real de
# Willow Creek y arma data/ con ellos (llama a generar_datos.py sobre demo/source).
#
# Nada de aqui sale de SAP ni de Willow Creek: clientes, PO, SO, correos y materiales son
# inventados. Ver demo/CONTRATO.md.
#
# Uso:  python generar_demo.py

import csv
import random
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SRC = AQUI / 'demo' / 'source'
REP = SRC / 'Willow Creek Orders Report'
rnd = random.Random(20261021)

HOY = date(2026, 10, 21)
INICIO = date(2026, 7, 19)

OMS = ['om.uno@example.com', 'om.dos@example.com', 'om.tres@example.com', 'om.cuatro@example.com']
CLIENTES = [  # (customer, nombre, dominio, om)
    ('900001', 'ACME REFRIGERATION', '@ACME-REF.EXAMPLE', OMS[0]),
    ('900002', 'POLAR COOLING CO', '@POLAR.EXAMPLE', OMS[1]),
    ('900003', 'NORTHWIND FOODSERVICE', '@NORTHWIND.EXAMPLE', OMS[2]),
    ('900004', 'BLUE ICE SYSTEMS', '@BLUEICE.EXAMPLE', OMS[0]),
    ('900005', 'CONTOSO COLD CHAIN', '@CONTOSO.EXAMPLE', OMS[3]),
    ('900006', 'FABRIKAM APPLIANCES', '@FABRIKAM.EXAMPLE', OMS[1]),
]
OTRO_CLIENTE = ('900099', 'TAILSPIN NOT IN ZWCCUST')   # Sold-To fuera del catalogo

CAB_VIEJA = ['PO Number', 'Received Date', 'Order Date', 'Sold To Name', 'Sold To ID', 'Ship To Name', 'Ship To ID',
             'Order Manager', 'Sender', 'WC Status', 'Review Status', 'SAP Status', 'Note', 'Subject', 'ID']
CAB_NUEVA = CAB_VIEJA + ['SO Number', 'SAP Submit Timestamp', 'Review Available', 'Review Completed']

# Desenlaces posibles de un envio: (peso, WC, Review, SAP, Nota, crea_SO)
DESENLACES = [
    (60, 'Success', 'Approved', 'Success', 'Order Complete', True),
    (6, 'Success', 'Approved', 'Success', 'PO: {po}', True),
    (6, 'Success', 'Approved', 'Warnings', 'Order Complete', True),
    (6, 'Success', 'Approved', 'Error', 'Order Complete', False),
    (3, 'Success', 'Approved', 'Success', 'Order Complete', False),          # exito sin SO
    (8, 'Blocked', 'Not Started', 'Not Submitted', "Can't Match Material ID", False),
    (3, 'Blocked', 'Not Started', 'Not Submitted', "Can't Identify Sold-To Party", False),
    (2, 'Blocked', 'Not Started', 'Not Submitted', 'Date Format Parsing Error', False),
    (2, 'Review Rejected', 'Rejected', 'Not Submitted', 'Order Parsed', False),
    (1, 'Internal Error', 'Approved', 'Submitted', 'Willow Creek Computer Error', False),
    (1, 'In Progress', 'Approved', 'No Response', 'Order Parsed', False),
    (2, 'In Progress', 'Awaiting Review', 'Not Submitted', 'Order Parsed', False),
]

so_seq = iter(range(110300000, 110400000))
envios, sap = [], []


def ts(d, h, m=0):
    return datetime(d.year, d.month, d.day, h, m).strftime('%Y-%m-%dT%H:%M:%SZ')


dia, n = INICIO, 0
while dia <= HOY:
    for _ in range(rnd.choice([0, 1, 2, 2, 3, 4])):
        n += 1
        c = rnd.choice(CLIENTES)
        if rnd.random() < 0.03:
            c = OTRO_CLIENTE + ('', OMS[2])
        po = rnd.choice(['PO', '', '4500', 'P0000']) + str(100000 + n * 7)
        peso = [d[0] for d in DESENLACES]
        _, wc, rev, sapst, nota, crea = rnd.choices(DESENLACES, weights=peso)[0]
        sold = '' if nota == "Can't Identify Sold-To Party" else c[0]
        om = '' if rnd.random() < 0.04 else (rnd.choice(OMS) if rnd.random() < 0.05 else c[3])
        so = str(next(so_seq)) if crea else ('0000000000' if sapst == 'Error' else '')
        e = {'PO Number': po, 'Received Date': ts(dia, rnd.randint(8, 20), rnd.randint(0, 59)),
             'Order Date': (dia - timedelta(days=rnd.randint(0, 5))).isoformat(),
             'Sold To Name': c[1].title(), 'Sold To ID': sold, 'Ship To Name': c[1].title(), 'Ship To ID': sold,
             'Order Manager': om, 'Sender': om or OMS[0], 'WC Status': wc, 'Review Status': rev,
             'SAP Status': sapst, 'Note': nota.format(po=po), 'Subject': f'[demo-order] {c[1].split()[0].title()} {po}',
             'ID': f'demo-{n:05d}.1', 'SO Number': so,
             'SAP Submit Timestamp': ts(dia, 21) if sapst != 'Not Submitted' else '',
             'Review Available': ts(dia, 20), 'Review Completed': ts(dia, 21) if rev in ('Approved', 'Rejected') else '',
             '_dia': dia, '_vida': 0 if wc == 'Success' else rnd.randint(1, 20)}
        envios.append(e)
        if crea:
            sap.append((so, c[0], c[1], po, dia, 'ITJOBS_DEMO', ''))
        elif wc != 'In Progress' and rnd.random() < 0.8 and sold:
            # WC no la creo: alguien la captura a mano en SAP unos dias despues
            sap.append((str(next(so_seq)), c[0], c[1], po.replace('PO', ''), dia + timedelta(days=rnd.randint(1, 4)), 'OM_DEMO', ''))
        if rnd.random() < 0.06 and wc == 'Blocked':
            # reenvio del mismo PO que si entra
            e2 = dict(e, **{'ID': f'demo-{n:05d}.9', 'WC Status': 'Success', 'Review Status': 'Approved', 'SAP Status': 'Success',
                            'Note': 'Order Complete', 'SO Number': str(next(so_seq)), 'Received Date': ts(dia + timedelta(days=2), 9),
                            '_dia': dia + timedelta(days=2), '_vida': 0})
            envios.append(e2)
            sap.append((e2['SO Number'], c[0], c[1], po, dia + timedelta(days=2), 'ITJOBS_DEMO', ''))
    dia += timedelta(days=1)

# Ordenes de SAP de clientes WC que nunca pasaron por WC
for i in range(40):
    c = rnd.choice(CLIENTES)
    d = INICIO + timedelta(days=rnd.randint(0, (HOY - INICIO).days))
    sap.append((str(next(so_seq)), c[0], c[1], f'MAN{i:04d}', d, rnd.choice(['OM_DEMO', 'EDI_DEMO']),
                'DFUE' if rnd.random() < 0.3 else ''))

# --- Reportes diarios: tres al dia (formato viejo) hasta el 24-jul, luego uno a las 11 AM ---
if SRC.exists():
    shutil.rmtree(SRC)
REP.mkdir(parents=True)
previo = None
dia = INICIO
while dia <= HOY:
    horas = ['06 AM', '10 AM', '02 PM'] if dia <= date(2026, 7, 24) else ['11 AM']
    for hora in horas:
        cab = CAB_VIEJA if dia <= date(2026, 7, 24) else CAB_NUEVA
        vivos = [e for e in envios if e['_dia'] <= dia <= e['_dia'] + timedelta(days=max(1, e['_vida']))]
        if dia == date(2026, 9, 30):
            vivos = [e for e in envios if e['_dia'] <= dia]       # un consolidado, para probar la marca
        filas = [[e.get(k, '') for k in cab] for e in vivos]
        if not filas and previo and previo[0] == cab:
            filas = previo[1]                                      # dias sin movimiento: el mismo archivo
        with open(REP / f'{dia.isoformat()} {hora}.csv.csv', 'w', encoding='utf-8', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(cab)
            w.writerows(filas)
        if filas:
            previo = (cab, filas)
    dia += timedelta(days=1)

# --- SAP: WC_FOLLOWUP (CSV en vez de Excel), ZWCCUST y SDD167 ---
fu_cab = ['SOrg.', 'Sales Doc.', 'POtyp', 'Purchase Order Number', 'Created On', 'Created By', 'Sold-To Pt',
          'Sold-To Party', 'Req.dlv.dt', 'Item', 'Dv', 'Plnt', 'Material', 'Order Quantity', 'SU', 'DB',
          'Schedule line blocked for delivery']
fu_filas = []
for so, cli, nom, po, d, por, potyp in sap:
    for it in range(rnd.randint(1, 4)):
        bloq = rnd.random() < 0.03
        fu_filas.append(['0500', so, potyp, po, d.strftime('%m/%d/%Y'), por, cli, nom,
                         (d + timedelta(days=rnd.randint(20, 120))).strftime('%m/%d/%Y'), f'{(it + 1) * 100:06d}', '10', 'XX10',
                         f'DEMO-{rnd.randint(1000, 9999)}', rnd.choice([1, 2, 6, 12, 24, 48]), 'UN',
                         'ZG' if bloq else '', 'Blocked General' if bloq else ''])
# ordenes abiertas de otros clientes (no WC)
for i in range(60):
    d = HOY - timedelta(days=rnd.randint(0, 200))
    fu_filas.append(['0500', str(next(so_seq)), '', f'X{i:05d}', d.strftime('%m/%d/%Y'), 'OTRO_DEMO', '800001',
                     'OTHER CUSTOMER DEMO', d.strftime('%m/%d/%Y'), '000100', '10', 'XX10', 'DEMO-0001', 5, 'UN', '', ''])
# algunas ya surtidas: salen de las abiertas
cerradas = set(rnd.sample([s[0] for s in sap], k=len(sap) // 6))
fu_filas = [f for f in fu_filas if f[1] not in cerradas]
with open(SRC / 'WC_FOLLOWUP_20261021_090000.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh); w.writerow(fu_cab); w.writerows(fu_filas)

with open(SRC / 'ZWCCUST_20261021_090000.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['SOrg.', 'Customer', 'Name', 'Del', 'Domain', 'E-Mail Address', 'E-Mail Address', 'Created', 'User Name', 'Last Chg', 'User Name'])
    for cli, nom, dom, om in CLIENTES:
        w.writerow(['0500', cli, nom, '', dom, om, '', '46062', 'DEMO', '46189', 'DEMO'])

oct_filas = [f for f in fu_filas if f[6] in {c[0] for c in CLIENTES} and f[4] >= '10/01/2026']
anchos = [5, 10, 5, 30, 10, 10, 10, 30, 10, 6, 2, 4, 16, 14, 2, 2, 34]
fila = lambda vals: '|' + '|'.join(str(v).ljust(a)[:a] for v, a in zip(vals, anchos)) + '|'
with open(SRC / 'SDD167_WILLOWCREEK_ENA_2026-10-21_08-00-00.csv', 'w', encoding='utf-8', newline='') as fh:
    fh.write(f'{HOY.strftime("%m/%d/%Y")}{"WILLOWCREEK PO FOLLOW UP":>60}\n{"-" * 120}\n')
    fh.write(fila(fu_cab) + '\n|' + '-' * 118 + '|\n')
    for f in oct_filas:
        fh.write(fila(f) + '\n')

print(f'Inventados: {len(envios)} envíos, {len(list(REP.glob("*.csv")))} reportes, {len(fu_filas)} renglones de WC_FOLLOWUP')
sys.exit(subprocess.call([sys.executable, '-I', str(AQUI / 'generar_datos.py'), str(SRC)]))
