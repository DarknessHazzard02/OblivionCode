# ===============================================
# BOM Maquinados ETL: configuration
# Author: Haz
# ===============================================
# The real source folder and file prefix are NOT kept here: they come from config.local.json
# (ignored by git) or from environment variables, so the repo carries no company paths.

import json
import os
from pathlib import Path

_local = Path(__file__).resolve().parent / 'config.local.json'
_cfg = json.loads(_local.read_text(encoding='utf-8-sig')) if _local.is_file() else {}

SOURCE_FOLDER = Path(os.environ.get('BOM_SOURCE_FOLDER', _cfg.get('source', 'demo/source')))

FILE_PREFIX = os.environ.get('BOM_FILE_PREFIX', _cfg.get('file_prefix', 'Rpt_BOM_'))

OUTPUT_PARQUET = Path("Output/BOM_Maquinados.parquet")
OUTPUT_CSV = Path("Output/BOM_Maquinados.csv")

LOG_FILE = Path("Logs/process.log")
