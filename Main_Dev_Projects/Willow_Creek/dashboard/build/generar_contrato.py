# Author: Haz
# Arma el contrato del tablero para el Portal BI con datos 100 % INVENTADOS desde cero.
#
# 1. Escribe en una carpeta temporal fuentes inventadas con la misma forma que las del tablero:
#    reportes diarios de Willow Creek (formato viejo hasta el 2026-07-24, nuevo despues, y un
#    consolidado el 2026-09-30 para probar la marca), ordenes abiertas de SAP, clientes y el job de
#    seguimiento. Nada parte de un corte real: clientes ficticios (FABRIKAM HVAC SYSTEMS...), materiales CM-000001,
#    correos @example.com y usuarios ficticios (LMENDEZ...), con semilla fija.
# 2. Corre sobre ellas el calculo del tablero (calculo.py en el portal; ../generar_datos.py en local).
# 3. Escribe meta.json y dashboard.json sin nombres de archivos de origen.
#
# Uso:  python build/generar_contrato.py [carpeta_salida]
#       salida por default: data/dashboard/ en el portal, data_portal/ en local

import csv
import json
import random
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

BUILD = Path(__file__).resolve().parent
RAIZ = BUILD.parent
EN_PORTAL = (BUILD / 'calculo.py').exists()
CALCULO = BUILD / 'calculo.py' if EN_PORTAL else RAIZ / 'generar_datos.py'
SALIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else (RAIZ / 'data' / 'dashboard' if EN_PORTAL else RAIZ / 'data_portal')

rnd = random.Random(20261022)
HOY = date(2026, 10, 21)
INICIO = date(2026, 7, 19)

OMS = [f'om.{i:02d}@example.com' for i in range(1, 5)]
_NOMBRES = [["900001", "FABRIKAM HVAC SYSTEMS", "@FABRIKAMHVACSY.EXAMPLE"], ["900002", "NORTHWIND AIR SOLUTIONS", "@NORTHWINDAIRSO.EXAMPLE"], ["900003", "ADVENTURE WORKS PUMPS", "@ADVENTUREWORKS.EXAMPLE"], ["900004", "TAILSPIN FLUID POWER", "@TAILSPINFLUIDP.EXAMPLE"], ["900005", "WIDE WORLD COMPRESSORS", "@WIDEWORLDCOMPR.EXAMPLE"], ["900006", "LITWARE INDUSTRIAL", "@LITWAREINDUSTR.EXAMPLE"]]
CLIENTES = [(_NOMBRES[i - 1][0], _NOMBRES[i - 1][1], _NOMBRES[i - 1][2], OMS[(i - 1) % 4])
            for i in range(1, 7)]   # (customer, nombre, dominio, om)
OTRO_CLIENTE = ('900099', 'A. DATUM AUTOMATION')   # Sold-To fuera del catalogo de clientes
USUARIO_WC, USUARIO_OM, USUARIO_EDI, USUARIO_OTRO = 'LMENDEZ', 'DORTIZ', 'EDI_BATCH', 'SRIVAS'

CAB_VIEJA = ['PO Number', 'Received Date', 'Order Date', 'Sold To Name', 'Sold To ID', 'Ship To Name', 'Ship To ID',
             'Order Manager', 'Sender', 'WC Status', 'Review Status', 'SAP Status', 'Note', 'Subject', 'ID']
CAB_NUEVA = CAB_VIEJA + ['SO Number', 'SAP Submit Timestamp', 'Review Available', 'Review Completed']
CAB_SAP = ['SOrg.', 'Sales Doc.', 'POtyp', 'Purchase Order Number', 'Created On', 'Created By', 'Sold-To Pt',
           'Sold-To Party', 'Req.dlv.dt', 'Item', 'Dv', 'Plnt', 'Material', 'Order Quantity', 'SU', 'DB',
           'Schedule line blocked for delivery']

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


def ts(d, h, m=0):
    return datetime(d.year, d.month, d.day, h, m).strftime('%Y-%m-%dT%H:%M:%SZ')


def envios_y_sap():
    """Cada envio a Willow Creek con su desenlace, y las ordenes que termina habiendo en SAP."""
    so_seq = iter(range(110300000, 110400000))
    envios, sap = [], []
    dia, n = INICIO, 0
    while dia <= HOY:
        for _ in range(rnd.choice([0, 1, 2, 2, 3, 4])):
            n += 1
            c = rnd.choice(CLIENTES)
            if rnd.random() < 0.03:
                c = OTRO_CLIENTE + ('', OMS[2])
            po = rnd.choice(['PO', '', '4500', 'P0000']) + str(100000 + n * 7)
            _, wc, rev, sapst, nota, crea = rnd.choices(DESENLACES, weights=[d[0] for d in DESENLACES])[0]
            sold = '' if nota == "Can't Identify Sold-To Party" else c[0]
            om = '' if rnd.random() < 0.04 else (rnd.choice(OMS) if rnd.random() < 0.05 else c[3])
            so = str(next(so_seq)) if crea else ('0000000000' if sapst == 'Error' else '')
            e = {'PO Number': po, 'Received Date': ts(dia, rnd.randint(8, 20), rnd.randint(0, 59)),
                 'Order Date': (dia - timedelta(days=rnd.randint(0, 5))).isoformat(),
                 'Sold To Name': c[1].title(), 'Sold To ID': sold, 'Ship To Name': c[1].title(), 'Ship To ID': sold,
                 'Order Manager': om, 'Sender': om or OMS[0], 'WC Status': wc, 'Review Status': rev,
                 'SAP Status': sapst, 'Note': nota.format(po=po), 'Subject': f'[PO Intake] {c[1].title()} {po}',
                 'ID': f'wc-{n:05d}.1', 'SO Number': so,
                 'SAP Submit Timestamp': ts(dia, 21) if sapst != 'Not Submitted' else '',
                 'Review Available': ts(dia, 20), 'Review Completed': ts(dia, 21) if rev in ('Approved', 'Rejected') else '',
                 '_dia': dia, '_vida': 0 if wc == 'Success' else rnd.randint(1, 20)}
            envios.append(e)
            if crea:
                sap.append((so, c[0], c[1], po, dia, USUARIO_WC, ''))
            elif wc != 'In Progress' and rnd.random() < 0.8 and sold:
                # WC no la creo: alguien la captura a mano en SAP unos dias despues
                sap.append((str(next(so_seq)), c[0], c[1], po.replace('PO', ''), dia + timedelta(days=rnd.randint(1, 4)),
                            USUARIO_OM, ''))
            if rnd.random() < 0.06 and wc == 'Blocked':
                # reenvio del mismo PO que si entra
                e2 = dict(e, **{'ID': f'wc-{n:05d}.9', 'WC Status': 'Success', 'Review Status': 'Approved',
                                'SAP Status': 'Success', 'Note': 'Order Complete', 'SO Number': str(next(so_seq)),
                                'Received Date': ts(dia + timedelta(days=2), 9), '_dia': dia + timedelta(days=2), '_vida': 0})
                envios.append(e2)
                sap.append((e2['SO Number'], c[0], c[1], po, dia + timedelta(days=2), USUARIO_WC, ''))
        dia += timedelta(days=1)

    # Ordenes de SAP de clientes WC que nunca pasaron por WC
    for i in range(40):
        c = rnd.choice(CLIENTES)
        d = INICIO + timedelta(days=rnd.randint(0, (HOY - INICIO).days))
        sap.append((str(next(so_seq)), c[0], c[1], f'MAN{i:04d}', d, rnd.choice([USUARIO_OM, USUARIO_EDI]),
                    'DFUE' if rnd.random() < 0.3 else ''))
    return envios, sap, so_seq


def fuentes(src):
    envios, sap, so_seq = envios_y_sap()

    # --- Reportes diarios: tres al dia (formato viejo) hasta el 24-jul, luego uno a las 11 AM ---
    rep = src / 'Willow Creek Orders Report'   # el calculo busca los reportes en esta carpeta
    rep.mkdir(parents=True)
    previo, dia = None, INICIO
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
            with open(rep / f'{dia.isoformat()} {hora}.csv.csv', 'w', encoding='utf-8', newline='') as fh:
                w = csv.writer(fh)
                w.writerow(cab)
                w.writerows(filas)
            if filas:
                previo = (cab, filas)
        dia += timedelta(days=1)

    # --- SAP: ordenes abiertas, catalogo de clientes y job de seguimiento ---
    fu = []
    for so, cli, nom, po, d, por, potyp in sap:
        for it in range(rnd.randint(1, 4)):
            bloq = rnd.random() < 0.03
            fu.append(['0500', so, potyp, po, d.strftime('%m/%d/%Y'), por, cli, nom,
                       (d + timedelta(days=rnd.randint(20, 120))).strftime('%m/%d/%Y'), f'{(it + 1) * 100:06d}', '10',
                       'XX10', f'CM-{rnd.randint(1, 9999):06d}', rnd.choice([1, 2, 6, 12, 24, 48]), 'UN',
                       'ZG' if bloq else '', 'Blocked General' if bloq else ''])
    for i in range(60):   # ordenes abiertas de otros clientes (no WC)
        d = HOY - timedelta(days=rnd.randint(0, 200))
        fu.append(['0500', str(next(so_seq)), '', f'X{i:05d}', d.strftime('%m/%d/%Y'), USUARIO_OTRO, '800001',
                   'SOUTHRIDGE PUMPS', d.strftime('%m/%d/%Y'), '000100', '10', 'XX10', 'CM-000001', 5, 'UN', '', ''])
    cerradas = set(rnd.sample([s[0] for s in sap], k=len(sap) // 6))   # ya surtidas: salen de las abiertas
    fu = [f for f in fu if f[1] not in cerradas]
    # Los nombres siguen los patrones que busca el calculo; viven solo en la carpeta temporal.
    with open(src / 'WC_FOLLOWUP_20261021_090000.csv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh); w.writerow(CAB_SAP); w.writerows(fu)

    with open(src / 'ZWCCUST_20261021_090000.csv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['SOrg.', 'Customer', 'Name', 'Del', 'Domain', 'E-Mail Address', 'E-Mail Address', 'Created',
                    'User Name', 'Last Chg', 'User Name'])
        for cli, nom, dom, om in CLIENTES:
            w.writerow(['0500', cli, nom, '', dom, om, '', '46062', USUARIO_OTRO, '46189', USUARIO_OTRO])

    octubre = [f for f in fu if f[6] in {c[0] for c in CLIENTES} and f[4] >= '10/01/2026']
    anchos = [5, 10, 5, 30, 10, 10, 10, 30, 10, 6, 2, 4, 16, 14, 2, 2, 34]
    fila = lambda vals: '|' + '|'.join(str(v).ljust(a)[:a] for v, a in zip(vals, anchos)) + '|'
    with open(src / 'SDD167_WILLOWCREEK_ENA_2026-10-21_08-00-00.csv', 'w', encoding='utf-8', newline='') as fh:
        fh.write(f'{HOY.strftime("%m/%d/%Y")}{"SEGUIMIENTO DE PO":>60}\n{"-" * 120}\n')
        fh.write(fila(CAB_SAP) + '\n|' + '-' * 118 + '|\n')
        for f in octubre:
            fh.write(fila(f) + '\n')
    return len(envios), len(fu)


# Los catalogos de hallazgos citan los extractos por su nombre: en el contrato van con uno generico
GENERICOS = [('Fuera de ZWCCUST', 'Fuera del Catálogo de Clientes'), ('Not in ZWCCUST', 'Not in the Customer Catalog'),
             ('Distinto a ZWCCUST', 'Distinto al del Catálogo'), ('Differs from ZWCCUST', 'Differs from the Catalog'),
             ('en ZWCCUST', 'en el catálogo de clientes'), ('in ZWCCUST', 'in the customer catalog'),
             ('en WC_FOLLOWUP', 'en las órdenes abiertas de SAP'), ('in WC_FOLLOWUP', 'in the SAP open orders')]


def limpiar_meta(meta):
    """Sin nombres de archivos ni rutas de origen: solo lo que el tablero necesita para dibujarse."""
    meta['fuente'] = 'datos inventados (build/generar_contrato.py)'
    meta.pop('semi', None)
    filtros = json.dumps(meta['filters'], ensure_ascii=False)
    for viejo, nuevo in GENERICOS:
        filtros = filtros.replace(viejo, nuevo)
    meta['filters'] = json.loads(filtros)
    nombres = [('Reportes diarios de Willow Creek', 'Willow Creek daily reports', 'reportes_demo/'),
               ('Órdenes abiertas de SAP', 'SAP open orders', 'ordenes_abiertas_demo.csv'),
               ('Seguimiento de PO (job diario)', 'PO follow-up (daily job)', 'seguimiento_demo.csv'),
               ('Clientes de Willow Creek', 'Willow Creek customers', 'clientes_demo.csv')]
    for f, (es, en, archivo) in zip(meta['fuentes'], nombres):
        f.update({'nombre': es, 'nombre_en': en, 'tabla': archivo,
                  'archivo': f'{f["filas"]:,} renglones de demo' if archivo.endswith('/') else archivo})
    return meta


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        src = tmp / 'demo' / 'source'
        n_envios, n_sap = fuentes(src)
        # Con la copia junto a demo/source, el calculo corre en modo demo y escribe en tmp/data.
        shutil.copy(CALCULO, tmp / 'generar_datos.py')
        subprocess.run([sys.executable, '-I', str(tmp / 'generar_datos.py'), str(src)], check=True,
                       stdout=subprocess.DEVNULL)
        meta = limpiar_meta(json.loads((tmp / 'data' / 'meta.json').read_text(encoding='utf-8')))
        SALIDA.mkdir(parents=True, exist_ok=True)
        shutil.copy(tmp / 'data' / 'dashboard.json', SALIDA / 'dashboard.json')
        (SALIDA / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'Inventados: {n_envios} envíos, {n_sap} renglones de SAP -> {SALIDA}')


if __name__ == '__main__':
    main()
