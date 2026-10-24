
# ===============================================
# Publish Portal JSON (Inventory Coverage vs Demand)
# ===============================================
# Writes meta.json and dashboard.json to Files/dashboard/sap-mb52-zsd-dmnd/.
# The pipeline activity "Publicar a PORTAL-BI" copies them through the gateway
# to PORTAL-DATA\sap-mb52-zsd-dmnd\, where the Portal BI reads them.
#
# Same contract and logic as dashboard/generar_datos.py. Demand rule differs
# from the workbook on purpose: only requirements (negative Qty_Valor) count.
# The calculation core below uses plain Python only, so it can be tested
# locally without pandas; the adapter at the end feeds it from cells 04-06.
# Made by: Hazzard
import json
import logging
import math
from collections import defaultdict
from datetime import date, datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

if 'log' not in globals():   # the original notebook prints instead of logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    log = logging.getLogger('mb52_zsd_dmnd')

PORTAL_FOLDER = 'sap-mb52-zsd-dmnd'
PORTAL_ROOT = DEFAULT_FILES / 'dashboard' / PORTAL_FOLDER
SITE_TIMEZONE = 'America/Chicago'   # Fabric runs in UTC
DEMAND_RULE = 'requerimientos'   # 'requerimientos' | 'neto_abs'
STATUS_FILTERS = [
    {'valor': 'Immediate Shortage', 'rol': 'critical', 'es': 'Faltante Inmediato', 'en': 'Immediate Shortage'},
    {'valor': 'Below Rolling 3M Coverage', 'rol': 'warn', 'es': 'Bajo Cobertura 3M', 'en': 'Below Rolling 3M Coverage'},
    {'valor': 'Covered Rolling 3M', 'rol': 'ok', 'es': 'Cubierto 3M', 'en': 'Covered Rolling 3M'},
    {'valor': 'No Demand', 'rol': 'neutral', 'es': 'Sin Demanda', 'en': 'No Demand'},
]
DATE_COLUMNS = {'Unrestricted_Stockout_Date', 'Total_Inventory_Stockout_Date'}


def portal_workdays(start: date, end: Optional[date], inclusive_end: bool = True) -> int:
    if end is None or end < start:
        return 0
    last = end if inclusive_end else date.fromordinal(end.toordinal() - 1)
    return sum(1 for ordinal in range(start.toordinal(), last.toordinal() + 1)
               if date.fromordinal(ordinal).weekday() != 6)


def portal_stockout(group: list, inventory: float, analysis_day: date, horizon_end: date) -> Optional[date]:
    if not group or inventory <= 0:
        return analysis_day
    running = sum(amount for day, amount in group if day < analysis_day)
    if running >= inventory:
        return analysis_day
    for day, amount in group:
        if analysis_day <= day < horizon_end:
            running += amount
            if running >= inventory:
                return day
    return None


def portal_iso(value: Optional[date]) -> Optional[str]:
    return value.isoformat() if value else None


def portal_r4(value: float) -> float:
    return round(value, 4)


def portal_oldest_file_date(names: list) -> Optional[str]:
    found = [m.group(1) for m in (re.search(r'(\d{4}-\d{2}-\d{2})', n) for n in names) if m]
    return min(found, default=None)


def build_portal_payload(mb52_records: list, sd48_records: list, sd48_raw_info: dict,
                         analysis_day: date, generated_at: str) -> tuple:
    """Returns (dashboard, meta). Records are dicts with plain Python values."""
    period_ends = [portal_add_months(analysis_day, months) for months in (1, 2, 3)]
    period_1_end, period_2_end, period_3_end = period_ends
    workdays_3m = portal_workdays(analysis_day, period_3_end, inclusive_end=False)
    # Demand by material and date (ZSD_DMND_P)
    mrp_by_material: dict = {}
    sums: dict = defaultdict(float)
    for row in sd48_records:
        qty = row['Qty_Valor']
        if DEMAND_RULE == 'requerimientos':
            sums[(row['Material'], row['Date'])] += -qty if qty < 0 else 0.0
        else:
            sums[(row['Material'], row['Date'])] += qty
        if row['MRP'] and row['Material'] not in mrp_by_material:
            mrp_by_material[row['Material']] = row['MRP']
    demand_groups: dict = defaultdict(list)
    for (material, day), qty in sums.items():
        demand_groups[material].append((day, abs(qty)))
    for group in demand_groups.values():
        group.sort()
    # Inventory by material (MB52_P) and by resume location
    inventory: dict = {}
    by_location: dict = defaultdict(lambda: defaultdict(float))
    for row in mb52_records:
        item = inventory.setdefault(row['Material'], {
            'Unrestricted': 0.0, 'Total_Inventory': 0.0, 'Warehouse': 0.0,
            'Material_Description': None, 'Material_Type': None, 'Material_Group': None})
        item['Unrestricted'] += row['Available']
        item['Total_Inventory'] += row['Total Inv']
        if row['Resume_Location'] == WAREHOUSE_RESUME:
            item['Warehouse'] += row['Available']
        for key in ('Material_Description', 'Material_Type', 'Material_Group'):
            if item[key] is None and row[key] is not None:
                item[key] = row[key]
        by_location[row['Material']][row['Resume_Location']] += row['Available']
    # Final coverage model
    def row_status(exposure: float, stock: float, stockout: Optional[date]) -> str:
        if exposure == 0:
            return 'No Demand'
        if stock <= 0 or stockout == analysis_day:
            return 'Immediate Shortage'
        if stock < exposure:
            return 'Below Rolling 3M Coverage'
        return 'Covered Rolling 3M'
    materials = list(dict.fromkeys([m for m in inventory if m is not None] + [m for m in demand_groups if m is not None]))
    final_rows = []
    for material in materials:
        inv = inventory.get(material, {})
        group = demand_groups.get(material, [])
        p1 = sum(a for d, a in group if d < period_1_end)
        p2 = sum(a for d, a in group if period_1_end <= d < period_2_end)
        p3 = sum(a for d, a in group if period_2_end <= d < period_3_end)
        unrestricted = inv.get('Unrestricted', 0.0)
        total_inv = inv.get('Total_Inventory', 0.0)
        warehouse = inv.get('Warehouse', 0.0)
        exposure = p1 + p2 + p3
        daily = exposure / workdays_3m if exposure != 0 else 0.0
        def coverage_days(value: float) -> int:
            return int(min(max(math.floor(value / daily), 0), workdays_3m)) if daily > 0 else 0
        def coverage_pct(value: float) -> float:
            return min(value / exposure, 1.01) if exposure > 0 else 1.0
        un_stockout = None if exposure == 0 else portal_stockout(group, unrestricted, analysis_day, period_3_end)
        tot_stockout = None if exposure == 0 else portal_stockout(group, total_inv, analysis_day, period_3_end)
        final_rows.append({
            'Material': material,
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
            'Available_SAP_Days_Coverage': max(0, portal_workdays(analysis_day, un_stockout) - 1) if un_stockout else 0,
            'Total_SAP_Days_Coverage': max(0, portal_workdays(analysis_day, tot_stockout) - 1) if tot_stockout else 0,
            'Unrestricted_Status': row_status(exposure, unrestricted, un_stockout),
            'Total_Inventory_Status': row_status(exposure, total_inv, tot_stockout),
            'Material_Type': inv.get('Material_Type'),
            'Material_Group': inv.get('Material_Group'),
            'MRP': mrp_by_material.get(material),
        })
    if not final_rows:
        raise ValueError('Portal JSON: no materials to publish. The previous files in PORTAL-DATA stay untouched.')
    final_rows.sort(key=lambda r: (r['Warehouse Share of Available Inventory'], r['Material']))
    # Payload
    def cell(column: str, value: Any) -> Any:
        if column in DATE_COLUMNS:
            return portal_iso(value)
        return portal_r4(value) if isinstance(value, float) else value
    columns = list(final_rows[0].keys())
    status_counts: dict = defaultdict(lambda: defaultdict(int))
    for r in final_rows:
        status_counts['Unrestricted'][r['Unrestricted_Status']] += 1
        status_counts['Total_Inventory'][r['Total_Inventory_Status']] += 1
    dashboard = {
        'final': {'columns': columns, 'rows': [[cell(c, r[c]) for c in columns] for r in final_rows]},
        'demanda': {m: [[portal_iso(d), portal_r4(a)] for d, a in g if d < period_3_end and a != 0]
                    for m, g in demand_groups.items()},
        'ubicaciones': {m: {loc: portal_r4(v) for loc, v in per.items() if v != 0} for m, per in by_location.items()},
    }
    mb52_files = sorted({r['SOURCE_FILE'] for r in mb52_records if r['SOURCE_FILE']})
    mb52_loads = sorted({r['LOAD_DATE'] for r in mb52_records if r['LOAD_DATE']})
    unmapped_locations = {(r['Plant'], r['Storage_Location']) for r in mb52_records if r['Resume_Location'] == 'Blank'}
    meta = {
        'generated_at': generated_at,
        'demo': False,
        'fuente': 'NB_MB52_ZSD_DMND · PL_MB52_ZSD_DMND / Merge_File',
        'regla_demanda': DEMAND_RULE,
        'analysis_date': portal_iso(analysis_day),
        'workable_days_3m': workdays_3m,
        'periodos': {'p1_fin': portal_iso(period_1_end), 'p2_fin': portal_iso(period_2_end), 'p3_fin': portal_iso(period_3_end)},
        'counts': {
            'mb52_filas': len(mb52_records),
            'sd48_filas': sd48_raw_info['rows'],
            'sd48_filas_con_fecha': len(sd48_records),
            'sd48_p_filas': sum(len(g) for g in demand_groups.values()),
            'materiales': len(final_rows),
            'status': {basis: dict(counts) for basis, counts in status_counts.items()},
        },
        'avisos': {
            'ubicaciones_sin_mapear': len(unmapped_locations),
            'total_menor_que_unrestricted': sum(1 for r in final_rows if r['Total_Inventory'] < r['Unrestricted']),
        },
        'filters': {
            'status': STATUS_FILTERS,
            'ubicaciones': sorted({loc for per in by_location.values() for loc in per}),
        },
        'fuentes': [
            {'nombre': 'MB52 · inventario por almacén', 'nombre_en': 'MB52 · stock by storage location',
             'sistema': 'SAP', 'tabla': 'Files/MB52_ZSD_DMND/' + MB52_FILE_NAME,
             'archivo': ', '.join(mb52_files),
             'extraido_el': portal_oldest_file_date(mb52_files),
             'actualizado': (mb52_loads[-1][:16] if mb52_loads else None),
             'dato_al': portal_iso(analysis_day), 'filas': len(mb52_records), 'falta': False},
            {'nombre': 'ZSD_DMND · demanda', 'nombre_en': 'ZSD_DMND · demand',
             'sistema': 'SAP', 'tabla': 'Files/MB52_ZSD_DMND/' + SD48_FILE_NAME,
             'archivo': ', '.join(sorted(sd48_raw_info['source_files'])),
             'extraido_el': portal_oldest_file_date(sorted(sd48_raw_info['source_files'])),
             'actualizado': (max(sd48_raw_info['load_dates'])[:16] if sd48_raw_info['load_dates'] else None),
             'dato_al': max(sd48_raw_info['file_dates']) if sd48_raw_info['file_dates'] else None,
             'filas': sd48_raw_info['rows'], 'falta': False},
        ],
        'pestanas_sin_actualizar': {},
    }
    return dashboard, meta


def portal_add_months(day: date, months: int) -> date:
    month_index = day.month - 1 + months
    year, month = day.year + month_index // 12, month_index % 12 + 1
    next_month = date(year + (month == 12), month % 12 + 1, 1)
    last = date.fromordinal(next_month.toordinal() - 1).day
    return date(year, month, min(day.day, last))


def write_portal_files(dashboard: dict, meta: dict) -> None:
    PORTAL_ROOT.mkdir(parents=True, exist_ok=True)
    payloads = {
        'dashboard.json': json.dumps(dashboard, ensure_ascii=False, separators=(',', ':')),
        'meta.json': json.dumps(meta, ensure_ascii=False, indent=1),
    }
    for name, content in payloads.items():
        target = PORTAL_ROOT / name
        target.write_text(content, encoding='utf-8')
        log.info('Portal JSON written: %s (%s bytes)', target, f'{target.stat().st_size:,}')


# --- Adapter: notebook DataFrames -> plain records -----------------------------

def _clean_text(value: Any) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    text_value = str(value).strip()
    return text_value or None


def _clean_day(value: Any) -> Optional[date]:
    return None if value is None or pd.isna(value) else pd.Timestamp(value).date()


def _raw_text_set(column: Optional[str]) -> set:
    if column is None:
        return set()
    return {v for v in (_clean_text(x) for x in sd48_raw[column]) if v}


def notebook_records() -> tuple:
    mb52_records = [{
        'Material': _clean_text(r['Material']),
        'Material_Description': _clean_text(r['Material_Description']),
        'Plant': _clean_text(r['Plant']),
        'Storage_Location': _clean_text(r['Storage_Location']),
        'Resume_Location': r['Resume_Location'],
        'Available': float(r['Available']),
        'Total Inv': float(r['Total Inv']),
        'Material_Type': _clean_text(r['Material_Type']),
        'Material_Group': _clean_text(r['Material_Group']),
        'LOAD_DATE': None if pd.isna(r['LOAD_DATE']) else pd.Timestamp(r['LOAD_DATE']).strftime('%Y-%m-%d %H:%M'),
        'SOURCE_FILE': _clean_text(r['SOURCE_FILE']),
    } for r in mb52.to_dict('records')]
    sd48_records = [{
        'Material': _clean_text(r['Material']),
        'Date': _clean_day(r['Date']),
        'Qty_Valor': float(r['Qty_Valor']),
        'MRP': _clean_text(r['MRP']),
    } for r in sd48.to_dict('records')]
    sd48_records = [r for r in sd48_records if r['Material'] and r['Date']]
    sd48_raw_info = {
        'rows': len(sd48_raw),
        'file_dates': _raw_text_set(sd48_map['FILE_DATE']),
        'load_dates': _raw_text_set(sd48_map['LOAD_DATE']),
        'source_files': _raw_text_set(sd48_map['SOURCE_FILE']),
    }
    return mb52_records, sd48_records, sd48_raw_info


if __name__ == '__main__':
    if 'mb52' not in globals() or 'sd48' not in globals():
        raise RuntimeError('Portal JSON: run the previous cells first (mb52 / sd48 not found).')
    portal_mb52, portal_sd48, portal_sd48_info = notebook_records()
    portal_dashboard, portal_meta = build_portal_payload(
        portal_mb52, portal_sd48, portal_sd48_info,
        analysis_date.date(), datetime.now(ZoneInfo(SITE_TIMEZONE)).strftime('%Y-%m-%d %H:%M'))
    write_portal_files(portal_dashboard, portal_meta)
    log.info('Portal JSON completed: %s materials | status %s',
             f"{portal_meta['counts']['materiales']:,}", portal_meta['counts']['status']['Unrestricted'])
