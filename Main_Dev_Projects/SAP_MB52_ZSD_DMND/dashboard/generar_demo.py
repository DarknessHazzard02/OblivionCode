# Author: Haz
# Genera datos INVENTADOS para el tablero SAP_MB52_ZSD_DMND y arma data/ con ellos.
#
# Escribe demo/source/MB52_Report.csv y demo/source/ZSD_DMND_Report.csv con las mismas columnas
# que dejan las actividades Copy del pipeline, y luego corre generar_datos.py sobre esa carpeta.
# Nada de aqui sale de SAP: materiales DEMO-xxxxx, clientes "Cliente Demo", cantidades al azar
# con semilla fija. Las fechas se recorren al dia de hoy en cada corrida.
#
# Uso:  python generar_demo.py

import csv
import random
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
OUT = AQUI / 'demo' / 'source'
SEED = 20261020
N_MATERIALS = 300
N_DEMAND_ONLY = 8   # materiales con demanda y sin renglon en MB52

MB52_COLUMNS = [
    'Material', 'Material_Description', 'Base_Unit', 'Plant', 'Storage_Location',
    'Storage_Location_Description', 'Unrestricted', 'Value_Unrestricted', 'Quality_Inspection',
    'Value_Quality_Inspection', 'Blocked', 'Value_Blocked', 'Stock_In_Transfer', 'Value_In_Transfer',
    'Returns', 'Material_Type', 'Material_Group', 'FILE_DATE', 'LOAD_DATE', 'SOURCE_FILE',
]
SD48_COLUMNS = [
    'Plant', 'Material', 'Parent_Material', 'Necessity_Type', 'Qty', 'Remain_Qty', 'CN',
    'Object_Number', 'Object_Flag', 'Item', 'Obj_Type', 'Date', 'Goods_Issue_Date', 'Shipping_Date',
    'Customer_Name', 'MRP', 'Material_Group', 'Section', 'Qty_Truncada', 'Qty_Valor',
    'Qty_Reconstruida', 'FILE_DATE', 'LOAD_DATE', 'SOURCE_FILE',
]

# Almacenes de BASE_ROWS (generar_datos.py) con su peso para repartir inventario.
SLOCS = [('ZLD1', 'Direct Material', 60), ('ZLFG', 'Finished Goods', 8), ('ZLMN', 'Production Mini', 8),
         ('ZLMD', 'Production Midi', 5), ('ZLEW', 'Ext-Warehouse', 6), ('ZLTD', 'Quality TDAs', 3),
         ('ZLBL', 'Blocked Material', 3), ('ZLSC', 'Scrap', 2), ('ZLIA', 'Inv. Adjustments', 2),
         ('ZZ99', 'Demo sin mapear', 1)]
PARTS = ['Motor housing', 'Stator core', 'Rotor shaft', 'Bearing', 'End shield', 'Fan blade',
         'Control board', 'Wire harness', 'Terminal box', 'Capacitor', 'Magnet', 'Bracket']
TYPES = [('ROH', 'PC'), ('HALB', 'PC'), ('FERT', 'EA')]
GROUPS = ['DEMO-G1', 'DEMO-G2', 'DEMO-G3', 'DEMO-G4']
MRPS = ['D01', 'D02', 'D03', 'D04', 'D05']
CUSTOMERS = ['Cliente Demo A', 'Cliente Demo B', 'Cliente Demo C', 'Cliente Demo D', 'Cliente Demo E']
RECEIPTS = ['ShipNt', 'PchOrd', 'PurRqs', 'PlOrd', 'PrdOrd']
# Reparto de escenarios para que salgan los cuatro estatus del tablero.
SCENARIOS = [('sin_demanda', 25), ('faltante', 15), ('bajo', 25), ('cubierto', 35)]

rng = random.Random(SEED)
today = date.today()
load_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
mb52_file = f'MB52_DEMO_{today.isoformat()}.txt'
sd48_file = f'ZSD_DMND_DEMO_{today.isoformat()}.txt'


def pick(weighted):
    return rng.choices([w[0] for w in weighted], weights=[w[-1] for w in weighted])[0]


def demand_rows(material, mrp, group, total):
    """Reparte `total` en requerimientos negativos dentro de 3 meses, mas algunas recepciones."""
    rows, left, n = [], total, rng.randint(3, 12)
    for i in range(n):
        qty = left if i == n - 1 else round(total * rng.uniform(0.05, 0.25))
        qty = max(min(qty, left), 0)
        left -= qty
        if qty == 0:
            continue
        day = today + timedelta(days=rng.randint(-10, 88))
        rows.append(sd48_row(material, mrp, group, day, -qty, 'IndReq', rng.choice(CUSTOMERS)))
    for _ in range(rng.randint(0, 3)):
        day = today + timedelta(days=rng.randint(0, 88))
        rows.append(sd48_row(material, mrp, group, day, round(total * rng.uniform(0.1, 0.4)) + 1,
                             rng.choice(RECEIPTS), None))
    return rows


def sd48_row(material, mrp, group, day, qty, obj_type, customer):
    return {
        'Plant': 'US90', 'Material': material, 'Parent_Material': None,
        'Necessity_Type': 'Requirement' if qty < 0 else 'Receipt', 'Qty': abs(qty), 'Remain_Qty': abs(qty),
        'CN': None, 'Object_Number': f'D{rng.randint(1000000, 9999999)}', 'Object_Flag': None,
        'Item': rng.randint(1, 40) * 10, 'Obj_Type': obj_type, 'Date': day.isoformat(),
        'Goods_Issue_Date': day.isoformat() if qty < 0 else None,
        'Shipping_Date': (day + timedelta(days=1)).isoformat() if qty < 0 else None,
        'Customer_Name': customer, 'MRP': mrp, 'Material_Group': group, 'Section': 'DEMO',
        'Qty_Truncada': qty, 'Qty_Valor': qty, 'Qty_Reconstruida': qty,
        'FILE_DATE': today.isoformat(), 'LOAD_DATE': load_stamp, 'SOURCE_FILE': sd48_file,
    }


mb52, sd48 = [], []
for i in range(1, N_MATERIALS + N_DEMAND_ONLY + 1):
    material = f'DEMO-{i:05d}'
    mat_type, unit = rng.choice(TYPES)
    group, mrp = rng.choice(GROUPS), rng.choice(MRPS)
    description = f'{rng.choice(PARTS)} demo {i}'
    scenario = 'faltante' if i > N_MATERIALS else pick(SCENARIOS)
    demand = 0 if scenario == 'sin_demanda' else rng.randint(50, 20000)
    inventory = {'sin_demanda': rng.randint(0, 5000), 'faltante': 0,
                 'bajo': round(demand * rng.uniform(0.25, 0.85)),
                 'cubierto': round(demand * rng.uniform(1.1, 3.0))}[scenario]
    if scenario == 'faltante' and rng.random() < 0.5:
        inventory = round(demand * rng.uniform(0.01, 0.08))   # poco inventario y demanda vencida
    if demand:
        sd48.extend(demand_rows(material, mrp, group, demand))
        if scenario == 'faltante' and inventory:
            sd48.append(sd48_row(material, mrp, group, today - timedelta(days=5), -(inventory + 1),
                                 'IndReq', rng.choice(CUSTOMERS)))
    if i > N_MATERIALS:
        continue
    price = round(rng.uniform(0.5, 120), 2)
    slocs = rng.sample(SLOCS, rng.randint(1, 3))
    if not any(s[0] == 'ZLD1' for s in slocs) and rng.random() < 0.7:
        slocs[0] = SLOCS[0]
    weights = [rng.random() + (2 if s[0] == 'ZLD1' else 0) for s in slocs]
    for (sloc, sloc_desc, _), w in zip(slocs, weights):
        unrestricted = round(inventory * w / sum(weights))
        quality = rng.choice([0, 0, 0, rng.randint(1, 200)])
        blocked = rng.choice([0, 0, 0, 0, rng.randint(1, 100)])
        mb52.append({
            'Material': material, 'Material_Description': description, 'Base_Unit': unit,
            'Plant': 'US90', 'Storage_Location': sloc, 'Storage_Location_Description': sloc_desc,
            'Unrestricted': unrestricted, 'Value_Unrestricted': round(unrestricted * price, 2),
            'Quality_Inspection': quality, 'Value_Quality_Inspection': round(quality * price, 2),
            'Blocked': blocked, 'Value_Blocked': round(blocked * price, 2),
            'Stock_In_Transfer': 0, 'Value_In_Transfer': 0, 'Returns': 0,
            'Material_Type': mat_type, 'Material_Group': group,
            'FILE_DATE': today.isoformat(), 'LOAD_DATE': load_stamp, 'SOURCE_FILE': mb52_file,
        })


def write(path, columns, rows):
    # Mismo dialecto que las actividades Copy: coma, comilla doble y escape con diagonal invertida.
    with open(path, 'w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, delimiter=',', quotechar='"', escapechar='\\', doublequote=False)
        writer.writerow(columns)
        for row in rows:
            writer.writerow(['' if row.get(c) is None else row[c] for c in columns])


OUT.mkdir(parents=True, exist_ok=True)
write(OUT / 'MB52_Report.csv', MB52_COLUMNS, mb52)
write(OUT / 'ZSD_DMND_Report.csv', SD48_COLUMNS, sd48)
print(f'Demo MB52: {len(mb52):,} renglones  ZSD_DMND: {len(sd48):,} renglones  ->  {OUT}')

subprocess.run([sys.executable, str(AQUI / 'generar_datos.py'), str(OUT)], check=True)
