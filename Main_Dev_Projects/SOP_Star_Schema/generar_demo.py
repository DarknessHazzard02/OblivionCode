# ===============================================
# SOP_Star_Schema: invented seed data
# Author: Haz
# ===============================================
# Writes demo/seed.sql with INSERTs for every table, fixed seed. Lines LINE_01..LINE_04,
# items ITM-001..ITM-012, 14 days of production and inventory. Nothing comes from a real system.

import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'demo' / 'seed.sql'
START = date(2026, 1, 5)
DAYS = 14


def main():
    rng = random.Random(20260105)
    lines = [(1, 'LINE_01', 'Assembly'), (2, 'LINE_02', 'Assembly'), (3, 'LINE_03', 'Machining'), (4, 'LINE_04', 'Packing')]
    items = [(n, f'ITM-{n:03d}', ['Family_A', 'Family_B', 'Family_C'][n % 3], rng.choice([50, 100, 200])) for n in range(1, 13)]
    statements = ['-- Made by: Hazzard', '-- Invented seed data written by generar_demo.py. Do not edit by hand.', '']

    for day in range(DAYS):
        d = START + timedelta(days=day)
        week = f'{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}'
        statements.append(f"INSERT INTO dim_date VALUES ({d:%Y%m%d}, '{d.isoformat()}', '{week}', '{d:%B}', {int(d.weekday() < 5)});")
    statements += [f"INSERT INTO dim_line VALUES ({k}, '{code}', '{area}');" for k, code, area in lines]
    statements += [f"INSERT INTO dim_item VALUES ({k}, '{code}', '{fam}', {ss});" for k, code, fam, ss in items]

    for day in range(DAYS):
        d = START + timedelta(days=day)
        if d.weekday() >= 5:
            continue
        for line_key, _, _ in lines:
            item_key = rng.randint(1, 12)
            planned = rng.choice([400, 500, 600])
            actual = round(planned * rng.uniform(0.80, 1.08))
            good = round(actual * rng.uniform(0.95, 0.995))
            planned_min = 450.0
            run_min = round(planned_min * rng.uniform(0.78, 0.95), 1)
            cycle = round(run_min * 60 / actual * rng.uniform(0.80, 0.97), 2)  # keeps performance <= 1
            statements.append(f'INSERT INTO fact_production VALUES ({d:%Y%m%d}, {line_key}, {item_key}, '
                              f'{planned}, {actual}, {good}, {planned_min}, {run_min}, {cycle});')

    for day in range(DAYS):
        d = START + timedelta(days=day)
        for item_key, _, _, safety in items:
            demand = 0 if item_key == 12 else rng.choice([10, 20, 40])
            on_hand = rng.randint(0, 30) * max(demand, 5)
            statements.append(f'INSERT INTO fact_inventory VALUES ({d:%Y%m%d}, {item_key}, {on_hand}, {demand});')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(statements) + '\n', encoding='utf-8')
    print(f'Wrote {len(statements) - 3} INSERTs to {OUT}')


if __name__ == '__main__':
    main()
