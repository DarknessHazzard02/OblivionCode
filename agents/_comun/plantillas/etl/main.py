# ===============================================
# <Proyecto> ETL
# Author: Haz
# ===============================================
"""Lee las fuentes, valida el esquema, transforma y exporta a parquet."""
import logging
import sys

import pandas as pd

import config

# ===============================================
# Configuration
# ===============================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ===============================================
# Read Source Files
# ===============================================
def read_sources(source_dir):
    files = sorted(source_dir.glob(f"{config.SOURCE_PREFIX}*.csv"))
    if not files:
        raise FileNotFoundError(f"No source files with prefix {config.SOURCE_PREFIX!r} in {source_dir}")
    frames, failed = [], []
    for path in files:
        try:
            frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
            frame["_SOURCE_FILE"] = path.name
            frames.append(frame)
        except (OSError, pd.errors.ParserError) as error:
            log.error("Could not read %s: %s", path.name, error)
            failed.append(path.name)
    if failed and not config.CONTINUE_ON_BAD_FILE:
        raise RuntimeError(f"Unreadable files: {failed}")
    if not frames:
        raise RuntimeError("No file could be read")
    return pd.concat(frames, ignore_index=True), len(files), failed


# ===============================================
# Validate Schema
# ===============================================
def validate_schema(df):
    missing = [c for c in config.EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")


# ===============================================
# Transform
# ===============================================
def transform(df):
    df = df[config.EXPECTED_COLUMNS + ["_SOURCE_FILE"]].copy()
    for column in config.NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    for column, fmt in config.DATE_COLUMNS.items():
        df[column] = pd.to_datetime(df[column], format=fmt, errors="coerce")
    before = len(df)
    df = df.drop_duplicates(subset=config.KEY_COLUMNS, keep="last")
    return df, before - len(df)


# ===============================================
# Export
# ===============================================
def export(df):
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    target = config.OUTPUT_DIR / f"{config.OUTPUT_NAME}.parquet"
    df.to_parquet(target, index=False, engine="pyarrow")
    return target


# ===============================================
# Main
# ===============================================
def main():
    source_dir = config.source_dir()
    df, file_count, failed = read_sources(source_dir)
    validate_schema(df)
    df, duplicates = transform(df)
    nulls = df[config.NUMERIC_COLUMNS + list(config.DATE_COLUMNS)].isna().sum()
    for column, count in nulls[nulls > 0].items():
        log.warning("%s: %d values could not be parsed", column, count)
    target = export(df)
    log.info("ETL completado: %d filas, %d archivos, %d descartados, %d duplicados -> %s",
             len(df), file_count, len(failed), duplicates, target)


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        log.error(str(error))
        sys.exit(1)
