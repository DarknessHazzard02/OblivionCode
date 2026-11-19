# ===============================================
# SOP_KPI_Dashboard: invented data for the dashboard
# Author: Haz
# ===============================================
# Writes data/dashboard.json (production rows + latest inventory) and data/meta.json with a fixed
# seed. Lines LINE_01..LINE_04, items ITM-001..ITM-012: nothing comes from a real system.

import json
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'data'
START = date(2026, 1, 5)
DAYS = 21


def main():
    rng = random.Random(20260105)
    lines = ['LINE_01', 'LINE_02', 'LINE_03', 'LINE_04']
    quality_bias = {'LINE_01': 0.985, 'LINE_02': 0.975, 'LINE_03': 0.96, 'LINE_04': 0.99}
    production = []
    for day in range(DAYS):
        d = START + timedelta(days=day)
        if d.weekday() >= 5:
            continue
        for line in lines:
            planned = rng.choice([400, 500, 600])
            actual = round(planned * rng.uniform(0.78, 1.06))
            good = round(actual * min(0.999, rng.gauss(quality_bias[line], 0.01)))
            run_min = round(450 * rng.uniform(0.76, 0.95), 1)
            cycle = round(run_min * 60 / actual * rng.uniform(0.78, 0.97), 2)
            production.append({'date': d.isoformat(), 'line': line, 'item': f'ITM-{rng.randint(1, 12):03d}',
                               'planned_qty': planned, 'actual_qty': actual, 'good_qty': good,
                               'planned_min': 450, 'run_min': run_min, 'ideal_cycle_sec': cycle})
    inventory = []
    for n in range(1, 13):
        demand = 0 if n == 12 else rng.choice([10, 20, 40])
        safety = rng.choice([50, 100, 200])
        inventory.append({'item': f'ITM-{n:03d}', 'family': ['Family_A', 'Family_B', 'Family_C'][n % 3],
                          'on_hand': rng.randint(0, 30) * max(demand, 5), 'forecast_daily': demand, 'safety_stock': safety})
    as_of = (START + timedelta(days=DAYS - 1)).isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'dashboard.json').write_text(json.dumps({'production': production, 'inventory': inventory}, indent=1), encoding='utf-8')
    (OUT / 'meta.json').write_text(json.dumps({'demo': True, 'source': 'Invented data (generar_demo.py)',
                                               'data_as_of': as_of, 'production_rows': len(production),
                                               'inventory_rows': len(inventory)}, indent=2), encoding='utf-8')
    print(f'Wrote {len(production)} production and {len(inventory)} inventory rows (as of {as_of}) to {OUT}')


if __name__ == '__main__':
    main()
