# ===============================================
# <Proyecto> Configuration
# Author: Haz
# ===============================================
"""Rutas y columnas. La ruta real vive en config.local.json (ignorado por git)."""
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "Output"
OUTPUT_NAME = "inventory_coverage"
SOURCE_PREFIX = "inventory_"
EXPECTED_COLUMNS = ["Plant", "Material", "OnHand", "DailyDemand", "SnapshotDate"]
NUMERIC_COLUMNS = ["OnHand", "DailyDemand"]
DATE_COLUMNS = {"SnapshotDate": "%Y-%m-%d"}
KEY_COLUMNS = ["Plant", "Material", "SnapshotDate"]
CONTINUE_ON_BAD_FILE = False


def source_dir():
    """config.local.json -> variable SOURCE_DIR -> demo/source. Falla si ninguna existe."""
    tried = []
    local = BASE_DIR / "config.local.json"
    if local.is_file():
        path = Path(json.loads(local.read_text(encoding="utf-8"))["source"])
        tried.append(str(path))
        if path.is_dir():
            return path
    if os.environ.get("SOURCE_DIR"):
        path = Path(os.environ["SOURCE_DIR"])
        tried.append(str(path))
        if path.is_dir():
            return path
    demo = BASE_DIR / "demo" / "source"
    tried.append(str(demo))
    if demo.is_dir():
        return demo
    raise FileNotFoundError(f"No source folder found. Tried: {tried}")
