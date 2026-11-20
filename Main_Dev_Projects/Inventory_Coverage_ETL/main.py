# ===============================================
# Inventory_Coverage_ETL
# Author: Haz
# ===============================================
# Reads three extracts (inventory snapshot, weekly demand forecast, open supply orders), validates
# their schema, removes duplicates, and builds one row per item and site with days of coverage,
# projected shortage date and a status. Every dropped or doubtful row is counted in a quality report.
# Standard library only; writes Parquet too when pyarrow is installed.

import csv
import json
import logging
import re
from collections import defaultdict
from datetime import date, datetime, timedelta

import config

# ===============================================
# Logging
# ===============================================
config.OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler(config.LOG_FILE, encoding='utf-8'), logging.StreamHandler()])
log = logging.getLogger('Inventory_Coverage_ETL')

OUTPUT_COLUMNS = ['item_id', 'site', 'on_hand', 'safety_stock', 'avg_daily_demand', 'days_of_coverage',
                  'open_supply_in_horizon', 'projected_shortage_date', 'status', 'extract_date']


# ===============================================
# Read
# ===============================================
def latest_file(prefix):
    """Newest file for a prefix, chosen by the YYYYMMDD in its name (never by today's date)."""
    candidates = []
    for path in config.SOURCE_FOLDER.glob(f'{prefix}*.csv'):
        match = re.search(r'(\d{8})', path.stem)
        if match:
            candidates.append((match.group(1), path))
    if not candidates:
        raise FileNotFoundError(f'No {prefix}YYYYMMDD.csv file in {config.SOURCE_FOLDER}')
    stamp, path = max(candidates)
    return path, datetime.strptime(stamp, '%Y%m%d').date()


def read_source(name):
    spec = config.SOURCES[name]
    path, extract_date = latest_file(spec['prefix'])
    try:
        with path.open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            missing = [c for c in spec['columns'] if c not in (reader.fieldnames or [])]
            if missing:
                raise ValueError(f'{path.name} is missing columns: {missing}')
            rows = list(reader)
    except OSError as error:
        raise OSError(f'Could not read {path}: {error}') from error
    log.info('Read %s: %d rows (extract date %s)', path.name, len(rows), extract_date)
    return rows, extract_date


# ===============================================
# Clean
# ===============================================
def clean(rows, name, numeric, dates, quality):
    """Drops malformed rows, exact duplicates, blank keys and bad numbers/dates; counts each reason."""
    columns = config.SOURCES[name]['columns']
    seen = set()
    kept = []
    for row in rows:
        # DictReader puts extra cells under the key None and fills missing cells with None.
        if None in row or any(row.get(c) is None for c in columns):
            quality[f'{name}_malformed_rows'] += 1
            continue
        key = tuple(row[c].strip() for c in columns)
        if key in seen:
            quality[f'{name}_duplicates'] += 1
            continue
        seen.add(key)
        if not row['item_id'].strip() or not row['site'].strip():
            quality[f'{name}_blank_keys'] += 1
            continue
        try:
            for column in numeric:
                row[column] = float(row[column])
                if row[column] < 0:
                    raise ValueError('negative')
            for column in dates:
                row[column] = date.fromisoformat(row[column].strip())
        except ValueError:
            quality[f'{name}_invalid_values'] += 1
            continue
        row['item_id'] = row['item_id'].strip()
        row['site'] = row['site'].strip()
        kept.append(row)
    return kept


def drop_key_conflicts(rows, name, key_columns, quality):
    """Keeps the first row per business key and counts the others (same key, different values)."""
    seen = set()
    kept = []
    for row in rows:
        key = tuple(row[c] for c in key_columns)
        if key in seen:
            quality[f'{name}_key_conflicts'] += 1
            continue
        seen.add(key)
        kept.append(row)
    return kept


# ===============================================
# Transform
# ===============================================
def daily_demand(forecast, start):
    """Spreads each weekly forecast evenly over its 7 days -> {(item, site): {day: qty}}."""
    demand = defaultdict(lambda: defaultdict(float))
    for row in forecast:
        for offset in range(7):
            day = row['week_start'] + timedelta(days=offset)
            if day >= start:
                demand[(row['item_id'], row['site'])][day] += row['forecast_qty'] / 7
    return demand


def build(inventory, demand, orders, extract_date, quality):
    supply = defaultdict(lambda: defaultdict(float))
    for row in orders:
        # Overdue orders are still open: count them as arriving on the extract date.
        due = row['due_date']
        if due < extract_date:
            quality['orders_overdue'] += 1
            due = extract_date
        supply[(row['item_id'], row['site'])][due] += row['open_qty']

    known = {(r['item_id'], r['site']) for r in inventory}
    quality['forecast_items_without_inventory'] = len(set(demand) - known)

    horizon_end = extract_date + timedelta(days=config.HORIZON_DAYS)
    output = []
    for row in sorted(inventory, key=lambda r: (r['site'], r['item_id'])):
        key = (row['item_id'], row['site'])
        window = [demand[key].get(extract_date + timedelta(days=d), 0.0) for d in range(config.DEMAND_WINDOW_DAYS)]
        avg = sum(window) / config.DEMAND_WINDOW_DAYS
        projected = row['on_hand']
        shortage = None
        day = extract_date
        while day < horizon_end:
            projected += supply[key].get(day, 0.0) - demand[key].get(day, 0.0)
            if projected < 0 and shortage is None:
                shortage = day
            day += timedelta(days=1)
        in_horizon = sum(q for d, q in supply[key].items() if extract_date <= d < horizon_end)
        # Priority: a projected shortage always wins, even when the next 28 days have no demand.
        # Coverage is undefined (empty, never 0 or infinite) when there is no demand in the window.
        coverage = round(row['on_hand'] / avg, 1) if avg else None
        if shortage:
            status = 'SHORTAGE'
        elif avg == 0:
            status = 'NO_DEMAND'
        elif row['on_hand'] < row['safety_stock']:
            status = 'BELOW_SAFETY'
        else:
            status = 'OK'
        output.append({
            'item_id': row['item_id'], 'site': row['site'], 'on_hand': row['on_hand'],
            'safety_stock': row['safety_stock'], 'avg_daily_demand': round(avg, 2), 'days_of_coverage': coverage,
            'open_supply_in_horizon': in_horizon,
            'projected_shortage_date': shortage.isoformat() if shortage else None,
            'status': status, 'extract_date': extract_date.isoformat(),
        })
    return output


# ===============================================
# Export
# ===============================================
def csv_safe(value):
    """Prefixes text that a spreadsheet would run as a formula (=, +, -, @)."""
    if isinstance(value, str) and value[:1] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + value
    return value


def export(rows, quality):
    csv_path = config.OUTPUT_FOLDER / 'inventory_coverage.csv'
    with csv_path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows({k: csv_safe(v) for k, v in row.items()} for row in rows)
    log.info('Wrote %s', csv_path.name)
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        log.warning('pyarrow is not installed: Parquet skipped, CSV written. Install requirements.txt for Parquet.')
    else:
        table = pa.Table.from_pylist(rows)
        pq.write_table(table, config.OUTPUT_FOLDER / 'inventory_coverage.parquet')
        log.info('Wrote inventory_coverage.parquet')
    report = config.OUTPUT_FOLDER / 'quality_report.json'
    report.write_text(json.dumps(dict(sorted(quality.items())), indent=2), encoding='utf-8')
    log.info('Quality report: %s', dict(sorted(quality.items())))


def main():
    # ===============================================
    # Read Source Files
    # ===============================================
    quality = defaultdict(int)
    inventory, extract_date = read_source('inventory')
    forecast, forecast_date = read_source('forecast')
    orders, orders_date = read_source('orders')
    dates = {'inventory': extract_date, 'forecast': forecast_date, 'orders': orders_date}
    quality.update({f'extract_date_{k}': v.isoformat() for k, v in dates.items()})
    if len(set(dates.values())) > 1:
        log.warning('Extract dates differ: %s. Coverage uses the inventory date %s.', dates, extract_date)
    # ===============================================
    # Clean and Transform
    # ===============================================
    inventory = clean(inventory, 'inventory', ['on_hand', 'safety_stock'], [], quality)
    forecast = clean(forecast, 'forecast', ['forecast_qty'], ['week_start'], quality)
    orders = clean(orders, 'orders', ['open_qty'], ['due_date'], quality)
    inventory = drop_key_conflicts(inventory, 'inventory', ['item_id', 'site'], quality)
    forecast = drop_key_conflicts(forecast, 'forecast', ['item_id', 'site', 'week_start'], quality)
    rows = build(inventory, daily_demand(forecast, extract_date), orders, extract_date, quality)
    for status in ('SHORTAGE', 'BELOW_SAFETY', 'OK', 'NO_DEMAND'):
        quality[f'status_{status.lower()}'] = sum(r['status'] == status for r in rows)
    # ===============================================
    # Export
    # ===============================================
    export(rows, quality)
    log.info('Completed: %d item-site rows exported to %s', len(rows), config.OUTPUT_FOLDER)


if __name__ == '__main__':
    main()
