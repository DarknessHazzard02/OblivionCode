# ===============================================
# <Proyecto> Demo Data
# Author: Haz
# ===============================================
"""Genera datos inventados con semilla fija en demo/source/."""
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)
OUT = Path(__file__).resolve().parent / "demo" / "source"
OUT.mkdir(parents=True, exist_ok=True)
BASE = date(2026, 1, 5)
rows = []
for day in range(5):
    for plant in ["Plant_A", "Plant_B", "Plant_C"]:
        for item in range(1, 21):
            rows.append({"Plant": plant, "Material": f"MAT-{item:05d}",
                         "OnHand": max(0, int(random.lognormvariate(5, 0.8))),
                         "DailyDemand": round(random.uniform(1, 40), 2),
                         "SnapshotDate": (BASE + timedelta(days=day)).isoformat()})
pd.DataFrame(rows).to_csv(OUT / "inventory_demo.csv", index=False, encoding="utf-8-sig")
print(f"{len(rows)} filas inventadas en {OUT}")
