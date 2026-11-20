# ===============================================
# SOP_Star_Schema: verification
# Author: Haz
# ===============================================
# Loads sql/schema.sql and demo/seed.sql into an in-memory SQLite database, runs every query in
# sql/kpi_queries.sql, prints the results and checks that each KPI stays in a sane range.

import logging
import re
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger('SOP_Star_Schema')


def load_queries(path):
    text = path.read_text(encoding='utf-8')
    parts = re.split(r'^-- name: (\w+)\s*$', text, flags=re.MULTILINE)
    return dict(zip(parts[1::2], (q.strip().rstrip(';') for q in parts[2::2])))


def main():
    seed = HERE / 'demo' / 'seed.sql'
    if not seed.is_file():
        raise FileNotFoundError(f'{seed} not found: run python generar_demo.py first')
    db = sqlite3.connect(':memory:')
    db.execute('PRAGMA foreign_keys = ON')
    db.executescript((HERE / 'sql' / 'schema.sql').read_text(encoding='utf-8'))
    db.executescript(seed.read_text(encoding='utf-8'))
    for table in ('dim_date', 'dim_line', 'dim_item', 'fact_production', 'fact_inventory'):
        log.info('%-16s %4d rows', table, db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0])

    problems = []
    for name, sql in load_queries(HERE / 'sql' / 'kpi_queries.sql').items():
        cursor = db.execute(sql)
        columns = [c[0] for c in cursor.description]
        rows = cursor.fetchall()
        log.info('Query %s: %d rows', name, len(rows))
        print('  ' + ' | '.join(columns))
        for row in rows[:6]:
            print('  ' + ' | '.join('' if v is None else str(v) for v in row))
        if not rows:
            problems.append(f'{name} returned no rows')
        for row in rows:
            record = dict(zip(columns, row))
            for kpi in ('availability', 'performance', 'quality', 'oee', 'schedule_adherence'):
                if kpi in record and not 0 < record[kpi] <= 1:
                    problems.append(f'{name}: {kpi} = {record[kpi]} is outside (0, 1]')
            if record.get('coverage_status') == 'NO_DEMAND' and record.get('days_of_coverage') is not None:
                problems.append(f'{name}: NO_DEMAND row has a coverage value')
    if problems:
        raise ValueError('KPI checks failed: ' + '; '.join(problems))
    log.info('Completed: all KPI queries ran and every value is in range.')


if __name__ == '__main__':
    main()
