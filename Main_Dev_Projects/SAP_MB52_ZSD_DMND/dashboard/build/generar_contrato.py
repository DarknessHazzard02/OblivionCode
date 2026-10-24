# Author: Haz
# Arma el contrato del tablero para el Portal BI con datos 100 % INVENTADOS desde cero.
#
# 1. Escribe en una carpeta temporal dos fuentes inventadas con las mismas columnas que dejan las
#    actividades Copy del pipeline (inventario por almacen y demanda). Nada parte de un corte real:
#    materiales CM-000001, clientes ficticios (FABRIKAM HVAC SYSTEMS...), cantidades al azar con semilla fija y
#    fechas recorridas al dia en que se corre.
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

SEED = 20261022
N_MATERIALES = 300
N_SOLO_DEMANDA = 8   # materiales con demanda y sin renglon de inventario

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

# Almacenes del catalogo del calculo (BASE_ROWS), con su peso para repartir inventario.
SLOCS = [('ZLD1', 'Direct Material', 60), ('ZLFG', 'Finished Goods', 8), ('ZLMN', 'Production Mini', 8),
         ('ZLMD', 'Production Midi', 5), ('ZLEW', 'Ext-Warehouse', 6), ('ZLTD', 'Quality TDAs', 3),
         ('ZLBL', 'Blocked Material', 3), ('ZLSC', 'Scrap', 2), ('ZLIA', 'Inv. Adjustments', 2),
         ('ZZ99', 'Almacen sin mapear', 1)]
PIEZAS = ['Carcasa', 'Nucleo de estator', 'Flecha de rotor', 'Balero', 'Tapa', 'Aspa',
          'Tarjeta de control', 'Arnes', 'Caja de terminales', 'Capacitor', 'Iman', 'Soporte']
TIPOS = [('ROH', 'PC'), ('HALB', 'PC'), ('FERT', 'EA')]
GRUPOS = ['MG-101', 'MG-102', 'MG-103', 'MG-104']
MRPS = ['E01', 'E02', 'E03', 'E04', 'E05']
CLIENTES = ["FABRIKAM HVAC SYSTEMS", "NORTHWIND AIR SOLUTIONS", "ADVENTURE WORKS PUMPS", "TAILSPIN FLUID POWER", "WIDE WORLD COMPRESSORS"]
RECEPCIONES = ['ShipNt', 'PchOrd', 'PurRqs', 'PlOrd', 'PrdOrd']
# Reparto de escenarios para que salgan los cuatro estatus del tablero.
ESCENARIOS = [('sin_demanda', 25), ('faltante', 15), ('bajo', 25), ('cubierto', 35)]

rng = random.Random(SEED)
hoy = date.today()
carga = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
archivo_inv = f'INVENTARIO_{hoy.isoformat()}.txt'
archivo_dem = f'DEMANDA_{hoy.isoformat()}.txt'


def elegir(pesos):
    return rng.choices([w[0] for w in pesos], weights=[w[-1] for w in pesos])[0]


def renglon_demanda(material, mrp, grupo, dia, qty, obj_type, cliente):
    return {
        'Plant': 'US90', 'Material': material, 'Parent_Material': None,
        'Necessity_Type': 'Requirement' if qty < 0 else 'Receipt', 'Qty': abs(qty), 'Remain_Qty': abs(qty),
        'CN': None, 'Object_Number': f'OB{rng.randint(1000000, 9999999)}', 'Object_Flag': None,
        'Item': rng.randint(1, 40) * 10, 'Obj_Type': obj_type, 'Date': dia.isoformat(),
        'Goods_Issue_Date': dia.isoformat() if qty < 0 else None,
        'Shipping_Date': (dia + timedelta(days=1)).isoformat() if qty < 0 else None,
        'Customer_Name': cliente, 'MRP': mrp, 'Material_Group': grupo, 'Section': 'GENERAL',
        'Qty_Truncada': qty, 'Qty_Valor': qty, 'Qty_Reconstruida': qty,
        'FILE_DATE': hoy.isoformat(), 'LOAD_DATE': carga, 'SOURCE_FILE': archivo_dem,
    }


def demanda(material, mrp, grupo, total):
    """Reparte `total` en requerimientos negativos dentro de 3 meses, mas algunas recepciones."""
    filas, resta, n = [], total, rng.randint(3, 12)
    for i in range(n):
        qty = resta if i == n - 1 else round(total * rng.uniform(0.05, 0.25))
        qty = max(min(qty, resta), 0)
        resta -= qty
        if qty == 0:
            continue
        dia = hoy + timedelta(days=rng.randint(-10, 88))
        filas.append(renglon_demanda(material, mrp, grupo, dia, -qty, 'IndReq', rng.choice(CLIENTES)))
    for _ in range(rng.randint(0, 3)):
        dia = hoy + timedelta(days=rng.randint(0, 88))
        filas.append(renglon_demanda(material, mrp, grupo, dia, round(total * rng.uniform(0.1, 0.4)) + 1,
                                     rng.choice(RECEPCIONES), None))
    return filas


def fuentes():
    inv, dem = [], []
    for i in range(1, N_MATERIALES + N_SOLO_DEMANDA + 1):
        material = f'CM-{i:06d}'
        tipo, unidad = rng.choice(TIPOS)
        grupo, mrp = rng.choice(GRUPOS), rng.choice(MRPS)
        pieza = rng.choice(PIEZAS)
        sigla = ''.join(w[0] for w in pieza.split() if w not in ('de', 'del')).upper()
        sigla = sigla if len(sigla) > 1 else pieza[:2].upper()
        descripcion = f'{pieza} {sigla}-{i:04d}'
        escenario = 'faltante' if i > N_MATERIALES else elegir(ESCENARIOS)
        total = 0 if escenario == 'sin_demanda' else rng.randint(50, 20000)
        inventario = {'sin_demanda': rng.randint(0, 5000), 'faltante': 0,
                      'bajo': round(total * rng.uniform(0.25, 0.85)),
                      'cubierto': round(total * rng.uniform(1.1, 3.0))}[escenario]
        if escenario == 'faltante' and rng.random() < 0.5:
            inventario = round(total * rng.uniform(0.01, 0.08))   # poco inventario y demanda vencida
        if total:
            dem.extend(demanda(material, mrp, grupo, total))
            if escenario == 'faltante' and inventario:
                dem.append(renglon_demanda(material, mrp, grupo, hoy - timedelta(days=5), -(inventario + 1),
                                           'IndReq', rng.choice(CLIENTES)))
        if i > N_MATERIALES:
            continue
        precio = round(rng.uniform(0.5, 120), 2)
        slocs = rng.sample(SLOCS, rng.randint(1, 3))
        if not any(s[0] == 'ZLD1' for s in slocs) and rng.random() < 0.7:
            slocs[0] = SLOCS[0]
        pesos = [rng.random() + (2 if s[0] == 'ZLD1' else 0) for s in slocs]
        for (sloc, sloc_desc, _), w in zip(slocs, pesos):
            libre = round(inventario * w / sum(pesos))
            calidad = rng.choice([0, 0, 0, rng.randint(1, 200)])
            bloqueado = rng.choice([0, 0, 0, 0, rng.randint(1, 100)])
            inv.append({
                'Material': material, 'Material_Description': descripcion, 'Base_Unit': unidad,
                'Plant': 'US90', 'Storage_Location': sloc, 'Storage_Location_Description': sloc_desc,
                'Unrestricted': libre, 'Value_Unrestricted': round(libre * precio, 2),
                'Quality_Inspection': calidad, 'Value_Quality_Inspection': round(calidad * precio, 2),
                'Blocked': bloqueado, 'Value_Blocked': round(bloqueado * precio, 2),
                'Stock_In_Transfer': 0, 'Value_In_Transfer': 0, 'Returns': 0,
                'Material_Type': tipo, 'Material_Group': grupo,
                'FILE_DATE': hoy.isoformat(), 'LOAD_DATE': carga, 'SOURCE_FILE': archivo_inv,
            })
    return inv, dem


def escribir(ruta, columnas, filas):
    # Mismo dialecto que las actividades Copy: coma, comilla doble y escape con diagonal invertida.
    with open(ruta, 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter=',', quotechar='"', escapechar='\\', doublequote=False)
        w.writerow(columnas)
        for fila in filas:
            w.writerow(['' if fila.get(c) is None else fila[c] for c in columnas])


def limpiar_meta(meta):
    """Sin nombres de archivos ni rutas de origen: solo lo que el tablero necesita para dibujarse."""
    meta['fuente'] = 'datos inventados (build/generar_contrato.py)'
    meta.pop('semi', None)
    nombres = [('Inventario por almacén', 'Stock by storage location', 'inventario_demo.csv'),
               ('Demanda', 'Demand', 'demanda_demo.csv')]
    for f, (es, en, archivo) in zip(meta['fuentes'], nombres):
        f.update({'nombre': es, 'nombre_en': en, 'tabla': archivo, 'archivo': archivo})
    return meta


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        src = tmp / 'demo' / 'source'
        src.mkdir(parents=True)
        inv, dem = fuentes()
        # El calculo busca sus fuentes por estos nombres; se quedan en la carpeta temporal.
        escribir(src / 'MB52_Report.csv', MB52_COLUMNS, inv)
        escribir(src / 'ZSD_DMND_Report.csv', SD48_COLUMNS, dem)
        # Con la copia junto a demo/source, el calculo corre en modo demo y escribe en tmp/data.
        shutil.copy(CALCULO, tmp / 'generar_datos.py')
        subprocess.run([sys.executable, '-I', str(tmp / 'generar_datos.py'), str(src)], check=True,
                       stdout=subprocess.DEVNULL)
        meta = limpiar_meta(json.loads((tmp / 'data' / 'meta.json').read_text(encoding='utf-8')))
        SALIDA.mkdir(parents=True, exist_ok=True)
        shutil.copy(tmp / 'data' / 'dashboard.json', SALIDA / 'dashboard.json')
        (SALIDA / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'Inventados: {len(inv):,} renglones de inventario, {len(dem):,} de demanda -> {SALIDA}')


if __name__ == '__main__':
    main()
