# ===============================================
# Inventory_Coverage_ETL: invented demo extracts
# Author: Haz
# ===============================================
# Writes demo/source/*.csv with a fixed seed: same columns as a real extract, no real values.
# Items are SKU-0001.., sites Site_A / Site_B. A few rows are broken on purpose (duplicate,
# blank key, negative quantity, bad date) so the quality report has something to count.

import csv
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'demo' / 'source'
EXTRACT = date(2026, 1, 5)          # fixed extract date, also used in the file names
STAMP = EXTRACT.strftime('%Y%m%d')


def write(name, header, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f'{name}_{STAMP}.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    rng = random.Random(20260105)
    items = [(f'SKU-{n:04d}', site) for n in range(1, 21) for site in ('Site_A', 'Site_B')]
    inventory, forecast, orders = [], [], []
    for item, site in items:
        weekly = rng.choice([0, 0, 35, 70, 140, 210, 350])
        on_hand = rng.randint(0, 14) * max(weekly, 20)
        inventory.append([item, site, on_hand, max(weekly, 10)])
        for week in range(8):
            forecast.append([item, site, (EXTRACT + timedelta(weeks=week)).isoformat(), weekly])
        if weekly and rng.random() < 0.5:
            orders.append([item, site, (EXTRACT + timedelta(days=rng.randint(3, 40))).isoformat(), weekly * 2])
    inventory.append(inventory[0])                              # duplicate
    inventory.append(['', 'Site_A', 10, 5])                     # blank key
    inventory.append(['SKU-0001', 'Site_A', 10, 5, 'extra'])    # malformed: one cell too many
    inventory.append(['SKU-0002', 'Site_A', 999, 10])           # key conflict: same item and site, other values
    forecast.append(['SKU-0002', 'Site_A', 'not-a-date', 10])   # bad date
    orders.append(['SKU-0003', 'Site_B', EXTRACT.isoformat(), -5])  # negative quantity
    forecast.append(['SKU-9999', 'Site_A', EXTRACT.isoformat(), 70])  # forecast without inventory
    write('inventory_snapshot', ['item_id', 'site', 'on_hand', 'safety_stock'], inventory)
    write('demand_forecast', ['item_id', 'site', 'week_start', 'forecast_qty'], forecast)
    write('open_orders', ['item_id', 'site', 'due_date', 'open_qty'], orders)
    print(f'Wrote 3 demo extracts dated {STAMP} to {OUT}')


if __name__ == '__main__':
    main()
