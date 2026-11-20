# ===============================================
# Inventory_Coverage_ETL: configuration
# Author: Haz
# ===============================================
# Real paths never live here: they come from config.local.json (ignored by git) or an
# environment variable. Without either, the ETL reads the invented demo files.

import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
_local = HERE / 'config.local.json'
_cfg = json.loads(_local.read_text(encoding='utf-8-sig')) if _local.is_file() else {}

SOURCE_FOLDER = Path(os.environ.get('INVENTORY_COVERAGE_ETL_SOURCE', _cfg.get('source', HERE / 'demo' / 'source')))
OUTPUT_FOLDER = Path(_cfg.get('output', HERE / 'Output'))
LOG_FILE = OUTPUT_FOLDER / 'Inventory_Coverage_ETL.log'

# One entry per extract: file prefix (the date YYYYMMDD follows it) and the columns it must have.
SOURCES = {
    'inventory': {'prefix': 'inventory_snapshot_', 'columns': ['item_id', 'site', 'on_hand', 'safety_stock']},
    'forecast': {'prefix': 'demand_forecast_', 'columns': ['item_id', 'site', 'week_start', 'forecast_qty']},
    'orders': {'prefix': 'open_orders_', 'columns': ['item_id', 'site', 'due_date', 'open_qty']},
}

HORIZON_DAYS = 56          # 8 weeks of projection
DEMAND_WINDOW_DAYS = 28    # average daily demand is taken from the next 4 weeks of forecast
