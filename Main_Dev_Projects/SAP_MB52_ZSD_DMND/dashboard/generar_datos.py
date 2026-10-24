# Author: Haz
# Genera data/dashboard.json y data/meta.json para el tablero SAP_MB52_ZSD_DMND.
#
# Port local, con la libreria estandar de Python, de las celdas 4-8 del notebook
# NB_MB52_ZSD_DMND.py (PL_MB52_ZSD_DMND / Merge_File). La logica es la misma salvo
# la regla de demanda (DEMAND_RULE, CELL 6): aqui solo cuentan los requerimientos.
# Con DEMAND_RULE = 'neto_abs' reproduce el Excel del notebook sin diferencias.
#
# Uso:  python generar_datos.py [carpeta_con_los_csv]
#
# La carpeta de origen se busca en este orden:
#   1. el argumento
#   2. la variable de entorno MB52_SD48_SOURCE
#   3. config.local.json -> {"source": "..."}  (ignorado por git; ahi va la ruta de OneLake)
#   4. ./demo/source  (datos inventados, versionados)
# Con datos reales escribe en ./data_real (ignorada por git); con los demo, en ./data.

import csv
import json
import math
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DEMO_SOURCE = AQUI / 'demo' / 'source'


def resolve_source():
    if len(sys.argv) > 1:
        return Path(sys.argv[1]), 'argumento'
    if os.environ.get('MB52_SD48_SOURCE'):
        return Path(os.environ['MB52_SD48_SOURCE']), 'MB52_SD48_SOURCE'
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
MB52_FILE_NAME = 'MB52_Report.csv'
SD48_FILE_NAME = 'ZSD_DMND_Report.csv'
ANALYSIS_DATE_OVERRIDE = None  # Ejemplo: '2026-10-06'
WAREHOUSE_RESUME = 'Almacen'

# Igual que BASE_ROWS del notebook.
BASE_ROWS = [
    ('US90', 'ZLFG', 'Finished Goods', 'Finish Good', 'FG Almacen', 'Validate'),
    ('US90', 'ZLD1', 'Direct Material', 'Almacen', 'Almacen', 'Main'),
    ('US90', 'ZLMN', 'Production Mini', 'Piso Prod', 'Piso Prod', 'Validate'),
    ('US90', 'ZXCU', 'Production CDU', 'Piso Prod(CDU)', 'Piso Prod', 'Validate'),
    ('US90', 'ZLIA', 'Inv. Adjustments', 'Inv Adjustment', 'Inv Adjustment', 'Validate'),
    ('US90', None, None, 'Blank', 'Blank', 'Validate'),
    ('US90', 'ZLBL', 'Blocked Material', 'Blocked Material', 'Blocked Material', 'Validate'),
    ('US90', 'ZLEW', 'Ext-Warehouse', 'External WHS', 'Ext Almacen', 'Validate'),
    ('US90', 'ZLSC', 'Scrap', 'Scrap', 'Scrap', 'Validate'),
    ('US90', 'ZLLA', 'R&D Samples', 'R&D Samples', 'R&D Samples', 'Validate'),
    ('US90', 'ZLWA', 'Inv. under anály', 'Inv Adjustment', 'Inv Adjustment', 'Validate'),
    ('US90', 'ZLMD', 'Production Midi', 'Piso Prod(Midi)', 'Piso Prod', 'Validate'),
    ('US90', 'ZLTD', 'Quality TDAs', 'Quality', 'Quality', 'Validate'),
    ('US90', 'ZLQA', 'Quality Samples', 'Quality Samples', 'Quality', 'Validate'),
    ('US90', 'ZWET', 'Prd Rotor WET', 'Piso Prod(Rotor)', 'Piso Prod', 'Validate'),
    ('US90', 'ZFAN', 'Prd ECM FAN', 'Piso Prod(Fan)', 'Piso Prod', 'Validate'),
    ('US90', 'ZXEL', 'Prd Electronicos', 'Piso Prod(Elect)', 'Piso Prod', 'Validate'),
    ('US90', None, 'Blank', 'Blank', 'Blank', 'Validate'),
]


# --- Helpers (equivalentes a la CELL 2 del notebook) -------------------------

def canonical(value):
    return re.sub(r'[^a-z0-9]', '', str(value).lower())


def resolve_column(columns, candidates, required=True):
    available = {canonical(c): c for c in columns}
    for candidate in candidates:
        key = canonical(candidate)
        if key in available:
            return available[key]
    if required:
        raise KeyError(f'Missing expected column. Candidates: {candidates}. Available: {list(columns)}')
    return None


def text(value):
    # Spark lee el campo vacio como null.
    if value is None:
        return None
    value = value.strip()
    return value if value != '' else None


def normalize_material(value):
    value = text(value)
    return re.sub(r'\.0$', '', value) if value is not None else None


def numeric(value):
    # pd.to_numeric(errors='coerce').fillna(0.0)
    try:
        number = float(value)
        return number if math.isfinite(number) else 0.0
    except (TypeError, ValueError):
        return 0.0


def parse_date(value):
    # pd.to_datetime(errors='coerce').dt.normalize(); formatos que traen estos CSV.
    value = text(value)
    if value is None:
        return None
    for fmt, size in (('%Y-%m-%d', 10), ('%m/%d/%Y', 10)):
        try:
            return datetime.strptime(value[:size], fmt).date()
        except ValueError:
            pass
    return None


def add_months(day, months):
    # relativedelta(months=n): mismo dia, topado al fin de mes.
    month = day.month - 1 + months
    year = day.year + month // 12
    month = month % 12 + 1
    last = [31, 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28,
            31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
    return date(year, month, min(day.day, last))


def sunday_only_workdays(start, end, inclusive_end=True):
    if start is None or end is None or end < start:
        return 0
    end_value = end if inclusive_end else end - timedelta(days=1)
    count, day = 0, start
    while day <= end_value:
        if day.weekday() != 6:
            count += 1
        day += timedelta(days=1)
    return count


def stockout_date(group, inventory, analysis_date, horizon_end):
    # group: lista [(Date, Abs)] ordenada por fecha.
    if not group or inventory <= 0:
        return analysis_date
    past_due = sum(a for d, a in group if d < analysis_date)
    if past_due >= inventory:
        return analysis_date
    future = [(d, a) for d, a in group if analysis_date <= d < horizon_end]
    if not future:
        return None
    running = past_due
    for d, a in future:
        running += a
        if running >= inventory:
            return d
    return None


def read_csv(path):
    # Mismas opciones que load_fabric_csv: comillas dobles y escape con diagonal invertida.
    with open(path, encoding='utf-8-sig', newline='') as handle:
        reader = csv.reader(handle, delimiter=',', quotechar='"', escapechar='\\', doublequote=False)
        header = [c.strip() for c in next(reader)]
        rows = []
        for line, values in enumerate(reader, start=2):
            if len(values) != len(header):
                raise ValueError(f'{path.name}, renglon {line}: {len(values)} columnas, se esperaban {len(header)}.')
            rows.append({h: (v if v != '' else None) for h, v in zip(header, values)})
    return header, rows


def date_from_source_file(name):
    match = re.search(r'(\d{4}-\d{2}-\d{2})', name or '')
    return match.group(1) if match else None


def iso(value):
    return value.isoformat() if value else None


def r4(value):
    return round(value, 4)


# --- Carga ------------------------------------------------------------------

mb52_path = SOURCE / MB52_FILE_NAME
sd48_path = SOURCE / SD48_FILE_NAME
missing = [str(p) for p in (mb52_path, sd48_path) if not p.exists()]
if missing:
    raise SystemExit('Faltan archivos de origen: ' + ', '.join(missing))

mb52_cols, mb52_raw = read_csv(mb52_path)
sd48_cols, sd48_raw = read_csv(sd48_path)
print(f'MB52 rows: {len(mb52_raw):,}  ZSD_DMND rows: {len(sd48_raw):,}')


# --- CELL 4: Normalize MB52 -------------------------------------------------

def mapper(columns, spec):
    return {target: resolve_column(columns, candidates, required) for target, (candidates, required) in spec.items()}


mb52_map = mapper(mb52_cols, {
    'Material': (['Material'], True),
    'Material_Description': (['Material_Description', 'Material Description', 'Description'], True),
    'Plant': (['Plant'], True),
    'Storage_Location': (['Storage_Location', 'Storage Location', 'SLoc'], True),
    'Unrestricted': (['Unrestricted', 'Unrestricted Stock'], True),
    'Quality_Inspection': (['Quality_Inspection', 'Quality Inspection'], False),
    'Blocked': (['Blocked'], False),
    'Material_Type': (['Material_Type', 'Material Type'], False),
    'Material_Group': (['Material_Group', 'Material Group'], False),
    'FILE_DATE': (['FILE_DATE', 'File Date'], False),
    'LOAD_DATE': (['LOAD_DATE', 'Load Date'], False),
    'SOURCE_FILE': (['SOURCE_FILE', 'Source File'], False),
})


def get(row, mapping, key):
    source = mapping[key]
    return row.get(source) if source else None


resume_by_key = {}
for plant, sloc, _desc, _loc, resume, _note in BASE_ROWS:
    resume_by_key.setdefault((plant, sloc), resume)  # drop_duplicates(keep='first')

mb52 = []
for row in mb52_raw:
    unrestricted = numeric(get(row, mb52_map, 'Unrestricted'))
    quality = numeric(get(row, mb52_map, 'Quality_Inspection'))
    blocked = numeric(get(row, mb52_map, 'Blocked'))
    plant = text(get(row, mb52_map, 'Plant'))
    sloc = text(get(row, mb52_map, 'Storage_Location'))
    mb52.append({
        'Material': normalize_material(get(row, mb52_map, 'Material')),
        'Material_Description': text(get(row, mb52_map, 'Material_Description')),
        'Plant': plant,
        'Storage_Location': sloc,
        'Resume_Location': resume_by_key.get((plant, sloc), 'Blank'),
        'Available': unrestricted,
        'Total Inv': unrestricted + quality + blocked,
        'Material_Type': text(get(row, mb52_map, 'Material_Type')),
        'Material_Group': text(get(row, mb52_map, 'Material_Group')),
        'FILE_DATE': parse_date(get(row, mb52_map, 'FILE_DATE')),
        'LOAD_DATE': text(get(row, mb52_map, 'LOAD_DATE')),
        'SOURCE_FILE': text(get(row, mb52_map, 'SOURCE_FILE')),
    })

if ANALYSIS_DATE_OVERRIDE:
    analysis_date = date.fromisoformat(ANALYSIS_DATE_OVERRIDE)
else:
    file_dates = [r['FILE_DATE'] for r in mb52 if r['FILE_DATE']]
    if not file_dates:
        raise SystemExit('Analysis date could not be derived. Set ANALYSIS_DATE_OVERRIDE.')
    analysis_date = max(file_dates)
period_1_end = add_months(analysis_date, 1)
period_2_end = add_months(analysis_date, 2)
period_3_end = add_months(analysis_date, 3)
workable_days = sunday_only_workdays(analysis_date, period_3_end, inclusive_end=False)
print(f'Analysis date: {analysis_date}  3M workable days: {workable_days}')


# --- CELL 5: Normalize ZSD_DMND ----------------------------------------------

sd48_map = mapper(sd48_cols, {
    'Material': (['Material', 'Material Number'], True),
    'Date': (['Date', 'Requirement Date', 'Basic Date'], True),
    'Qty_Valor': (['Qty_Valor', 'Qty Valor', 'Quantity Value', 'Quantity'], True),
    'MRP': (['MRP'], False),
    'FILE_DATE': (['FILE_DATE', 'File Date'], False),
    'LOAD_DATE': (['LOAD_DATE', 'Load Date'], False),
    'SOURCE_FILE': (['SOURCE_FILE', 'Source File'], False),
})

sd48 = []
sd48_meta = {'file_dates': set(), 'load_dates': set(), 'source_files': set()}
mrp_by_material = {}
for row in sd48_raw:
    for key, bucket in (('FILE_DATE', 'file_dates'), ('LOAD_DATE', 'load_dates'), ('SOURCE_FILE', 'source_files')):
        value = text(get(row, sd48_map, key))
        if value:
            sd48_meta[bucket].add(value)
    material = normalize_material(get(row, sd48_map, 'Material'))
    day = parse_date(get(row, sd48_map, 'Date'))
    if material is None or day is None:
        continue
    sd48.append((material, day, numeric(get(row, sd48_map, 'Qty_Valor'))))
    mrp = text(get(row, sd48_map, 'MRP'))
    if mrp and material not in mrp_by_material:
        mrp_by_material[material] = mrp


# --- CELL 6: ZSD_DMND_P ------------------------------------------------------
# Regla de demanda: solo REQUERIMIENTOS (Qty_Valor negativo). Las recepciones de
# ZSD_DMND (ShipNt, PchOrd, PurRqs, PlOrd, PrdOrd, QM lot) vienen en positivo; el
# notebook original sumaba todo y tomaba el absoluto, asi que una recepcion sola
# en una fecha contaba como demanda. 'neto_abs' reproduce el Excel original.
DEMAND_RULE = 'requerimientos'   # 'requerimientos' | 'neto_abs'

sums = defaultdict(float)
for material, day, qty in sd48:
    if DEMAND_RULE == 'requerimientos':
        sums[(material, day)] += -qty if qty < 0 else 0.0
    else:
        sums[(material, day)] += qty
demand_groups = defaultdict(list)
for (material, day), qty in sums.items():
    demand_groups[material].append((day, abs(qty)))
for group in demand_groups.values():
    group.sort()


# --- CELL 7: MB52_P ---------------------------------------------------------

mb52_p = {}
location_inventory = defaultdict(lambda: defaultdict(float))
for r in mb52:
    m = r['Material']
    item = mb52_p.setdefault(m, {'Unrestricted': 0.0, 'Total_Inventory': 0.0, 'Warehouse': 0.0,
                                 'Material_Description': None, 'Material_Type': None, 'Material_Group': None})
    item['Unrestricted'] += r['Available']
    item['Total_Inventory'] += r['Total Inv']
    if r['Resume_Location'] == WAREHOUSE_RESUME:
        item['Warehouse'] += r['Available']
    for key in ('Material_Description', 'Material_Type', 'Material_Group'):
        if item[key] is None and r[key] is not None:
            item[key] = r[key]
    location_inventory[m][r['Resume_Location']] += r['Available']


# --- CELL 8: Final ----------------------------------------------------------

materials = list(dict.fromkeys([m for m in mb52_p if m is not None] + [m for m in demand_groups if m is not None]))


def status(exposure, inventory, stockout):
    if exposure == 0:
        return 'No Demand'
    if inventory <= 0 or stockout == analysis_date:
        return 'Immediate Shortage'
    if inventory < exposure:
        return 'Below Rolling 3M Coverage'
    return 'Covered Rolling 3M'


final = []
for m in materials:
    inv = mb52_p.get(m, {})
    group = demand_groups.get(m, [])
    p1 = sum(a for d, a in group if d < period_1_end)
    p2 = sum(a for d, a in group if period_1_end <= d < period_2_end)
    p3 = sum(a for d, a in group if period_2_end <= d < period_3_end)
    unrestricted = inv.get('Unrestricted', 0.0)
    total_inv = inv.get('Total_Inventory', 0.0)
    warehouse = inv.get('Warehouse', 0.0)
    exposure = p1 + p2 + p3
    daily = exposure / workable_days if exposure != 0 else 0.0

    def coverage_days(value):
        return int(min(max(math.floor(value / daily), 0), workable_days)) if daily > 0 else 0

    def coverage_pct(value):
        return min(value / exposure, 1.01) if exposure > 0 else 1.0

    un_stockout = None if exposure == 0 else stockout_date(group, unrestricted, analysis_date, period_3_end)
    tot_stockout = None if exposure == 0 else stockout_date(group, total_inv, analysis_date, period_3_end)
    final.append({
        'Material': m,
        'Material_Description': inv.get('Material_Description'),
        'Warehouse Available Inventory': warehouse,
        'Unrestricted': unrestricted,
        'Total_Inventory': total_inv,
        'Warehouse Share of Available Inventory': warehouse / unrestricted if unrestricted != 0 else 0.0,
        'Non-Warehouse Available Inventory': unrestricted - warehouse,
        'Past_Due_+_Period_1_Demand': p1,
        'Period_2_Demand': p2,
        'Period_3_Demand': p3,
        'Total_Demand_Exposure': exposure,
        'Average_Daily_Demand': daily,
        'Warehouse Average Coverage Days': coverage_days(warehouse),
        'Available_Average_Days_Coverage': coverage_days(unrestricted),
        'Total_Average_Days_Coverage': coverage_days(total_inv),
        'Warehouse Demand Coverage %': coverage_pct(warehouse),
        'Available_Demand_Coverage_%': coverage_pct(unrestricted),
        'Total_Demand_Coverage_%': coverage_pct(total_inv),
        'Unrestricted_Stockout_Date': un_stockout,
        'Total_Inventory_Stockout_Date': tot_stockout,
        'Available_SAP_Days_Coverage': max(0, sunday_only_workdays(analysis_date, un_stockout) - 1) if un_stockout else 0,
        'Total_SAP_Days_Coverage': max(0, sunday_only_workdays(analysis_date, tot_stockout) - 1) if tot_stockout else 0,
        'Unrestricted_Status': status(exposure, unrestricted, un_stockout),
        'Total_Inventory_Status': status(exposure, total_inv, tot_stockout),
        # Campos que agrega el tablero (no estan en la hoja Final del Excel), solo para filtrar.
        'Material_Type': inv.get('Material_Type'),
        'Material_Group': inv.get('Material_Group'),
        'MRP': mrp_by_material.get(m),
    })
final.sort(key=lambda r: (r['Warehouse Share of Available Inventory'], r['Material']))


# --- CELL 9: Quality checks (los mismos avisos, ahora llegan al tablero) -----

unmapped = {(r['Plant'], r['Storage_Location']) for r in mb52 if r['Resume_Location'] == 'Blank'}
total_below_unrestricted = sum(1 for r in final if r['Total_Inventory'] < r['Unrestricted'])
if any(r['Material'] is None for r in final):
    raise SystemExit('Final output contains null materials.')

status_counts = defaultdict(lambda: defaultdict(int))
for r in final:
    status_counts['Unrestricted'][r['Unrestricted_Status']] += 1
    status_counts['Total_Inventory'][r['Total_Inventory_Status']] += 1
print('Final materials:', f'{len(final):,}')
for basis, counts in status_counts.items():
    print(basis, dict(counts))


# --- Salida -----------------------------------------------------------------

FINAL_COLUMNS = list(final[0].keys())
DATE_COLUMNS = {'Unrestricted_Stockout_Date', 'Total_Inventory_Stockout_Date'}


def cell(column, value):
    if column in DATE_COLUMNS:
        return iso(value)
    if isinstance(value, float):
        return r4(value)
    return value


demand = {}
for m, group in demand_groups.items():
    demand[m] = [[iso(d), r4(a)] for d, a in group if d < period_3_end and a != 0]

locations = sorted({loc for per in location_inventory.values() for loc in per})
location_rows = {m: {loc: r4(v) for loc, v in per.items() if v != 0} for m, per in location_inventory.items()}

OUT.mkdir(exist_ok=True)
dashboard = {
    'final': {'columns': FINAL_COLUMNS, 'rows': [[cell(c, r[c]) for c in FINAL_COLUMNS] for r in final]},
    'demanda': demand,
    'ubicaciones': location_rows,
}
(OUT / 'dashboard.json').write_text(json.dumps(dashboard, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

mb52_files = sorted({r['SOURCE_FILE'] for r in mb52 if r['SOURCE_FILE']})
mb52_loads = sorted({r['LOAD_DATE'] for r in mb52 if r['LOAD_DATE']})
oldest = lambda names: min((date_from_source_file(n) for n in names if date_from_source_file(n)), default=None)

meta = {
    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
    'demo': DEMO,
    'fuente': ('datos inventados (generar_demo.py)' if DEMO else
               'generar_datos.py (port local de NB_MB52_ZSD_DMND · PL_MB52_ZSD_DMND / Merge_File)'),
    'regla_demanda': DEMAND_RULE,
    'analysis_date': iso(analysis_date),
    'workable_days_3m': workable_days,
    'periodos': {'p1_fin': iso(period_1_end), 'p2_fin': iso(period_2_end), 'p3_fin': iso(period_3_end)},
    'counts': {
        'mb52_filas': len(mb52),
        'sd48_filas': len(sd48_raw),
        'sd48_filas_con_fecha': len(sd48),
        'sd48_p_filas': sum(len(g) for g in demand_groups.values()),
        'materiales': len(final),
        'status': {basis: dict(counts) for basis, counts in status_counts.items()},
    },
    'avisos': {
        'ubicaciones_sin_mapear': len(unmapped),
        'total_menor_que_unrestricted': total_below_unrestricted,
    },
    'filters': {
        'status': [
            {'valor': 'Immediate Shortage', 'rol': 'critical', 'es': 'Faltante Inmediato', 'en': 'Immediate Shortage'},
            {'valor': 'Below Rolling 3M Coverage', 'rol': 'warn', 'es': 'Bajo Cobertura 3M', 'en': 'Below Rolling 3M Coverage'},
            {'valor': 'Covered Rolling 3M', 'rol': 'ok', 'es': 'Cubierto 3M', 'en': 'Covered Rolling 3M'},
            {'valor': 'No Demand', 'rol': 'neutral', 'es': 'Sin Demanda', 'en': 'No Demand'},
        ],
        'ubicaciones': locations,
    },
    'fuentes': [
        {'nombre': 'MB52 · inventario por almacén', 'nombre_en': 'MB52 · stock by storage location',
         'sistema': 'SAP', 'tabla': 'Files/MB52_ZSD_DMND/' + MB52_FILE_NAME,
         'archivo': ', '.join(mb52_files),
         'extraido_el': oldest(mb52_files),
         'actualizado': (mb52_loads[-1][:16] if mb52_loads else None),
         'dato_al': iso(analysis_date), 'filas': len(mb52), 'falta': False},
        {'nombre': 'ZSD_DMND · demanda', 'nombre_en': 'ZSD_DMND · demand',
         'sistema': 'SAP', 'tabla': 'Files/MB52_ZSD_DMND/' + SD48_FILE_NAME,
         'archivo': ', '.join(sorted(sd48_meta['source_files'])),
         'extraido_el': oldest(sd48_meta['source_files']),
         'actualizado': (max(sd48_meta['load_dates'])[:16] if sd48_meta['load_dates'] else None),
         'dato_al': max(sd48_meta['file_dates']) if sd48_meta['file_dates'] else None,
         'filas': len(sd48_raw), 'falta': False},
    ],
    'pestanas_sin_actualizar': {},
}
(OUT / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'Escrito: {OUT / "dashboard.json"} ({(OUT / "dashboard.json").stat().st_size:,} bytes)')
print(f'Escrito: {OUT / "meta.json"}')
