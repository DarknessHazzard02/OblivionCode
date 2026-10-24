
# ===============================================
# Oracle Open PO Standardization Notebook
# Author: Haz
# ===============================================

import logging

from notebookutils import mssparkutils
from pyspark.sql.functions import col, date_format, substring, to_date

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("open_po_report")

# ===============================================
# Configuration
# ===============================================

CONFIG = {
    "source_file": "Files/PO_Report/OpenPO_Report_C.csv",
    "temp_folder": "Files/PO_Report/OpenPO_Report_Oracle_Temp",
    "final_file": "Files/PO_Report/OpenPOs_Report.csv",
    "oracle_date_format": "yyyy-MM-dd",
    "report_date_format": "MM/dd/yyyy",
}

# Oracle column -> report column, in report order
OUTPUT_COLUMNS = {
    "PO_NUM": "Order No (PO)",
    "VENDOR_NUM": "Vendor Code",
    "VENDOR_NAME": "Vendor Name",
    "SHIP_TO_LOCATION_ID": "Ship to Code",
    "LOCATION_CODE": "Ship to Name",
    "ORGANIZATION_CODE": "DC Destination (Header)",
    "ORG": "Destination (Header)",
    "ITEM_NUM": "Style",
    "LINE_NUM": "Seq",
    "DESCRIPTION": "Item Description",
    "QUANTITY_BALANCE": "Qty",
    "UNIT_MEAS_LOOKUP_CODE": "UOM",
    "NEED_BY_DATE": "Ready Date (=Exfcty date)",
    "AUTHORIZATION_STATUS": "Authorization Status",
    "VENDOR_SITE_CODE": "Vendor Site Code",
    "QUANTITY": "Ordered Qty",
    "QUANTITY_RECEIVED": "Received Qty",
    "QUANTITY_CANCELLED": "Cancelled Qty",
    "CREATION_DATE": "PO Creation Date",
}

DATE_COLUMNS = {"NEED_BY_DATE", "CREATION_DATE"}

# ===============================================
# Read Source File
# ===============================================

oracle_source = (
    spark.read
    .option("header", "true")
    .option("encoding", "UTF-8")
    .csv(CONFIG["source_file"])
)

# ===============================================
# Validate Source
# ===============================================

missing_columns = [name for name in OUTPUT_COLUMNS if name not in oracle_source.columns]
if missing_columns:
    raise ValueError(f"Missing Oracle source columns: {missing_columns}")

source_rows = oracle_source.count()
if source_rows == 0:
    raise ValueError(f"Oracle source file is empty: {CONFIG['source_file']}")

# ===============================================
# Standardize Oracle Output
# ===============================================

def to_report_date(column_name):
    return date_format(
        to_date(substring(col(column_name), 1, 10), CONFIG["oracle_date_format"]),
        CONFIG["report_date_format"],
    )

final_output = oracle_source.select([
    (to_report_date(source) if source in DATE_COLUMNS else col(source)).alias(target)
    for source, target in OUTPUT_COLUMNS.items()
])

log.info("Oracle source rows: %s", source_rows)
log.info("Report columns (%s): %s", len(final_output.columns), final_output.columns)
display(final_output.limit(20))

# ===============================================
# Export Single CSV
# ===============================================

temp_folder = CONFIG["temp_folder"]
if mssparkutils.fs.exists(temp_folder):
    mssparkutils.fs.rm(temp_folder, True)

try:
    (
        final_output
        .coalesce(1)
        .write
        .mode("overwrite")
        .option("header", "true")
        .option("encoding", "UTF-8")
        .csv(temp_folder)
    )
    generated_csv = next(
        (f.path for f in mssparkutils.fs.ls(temp_folder)
         if f.name.startswith("part-") and f.name.endswith(".csv")),
        None,
    )
    if generated_csv is None:
        raise RuntimeError(f"No CSV part file found in {temp_folder}")
    mssparkutils.fs.cp(generated_csv, CONFIG["final_file"], True)
    log.info("Final file created: %s", CONFIG["final_file"])
finally:
    if mssparkutils.fs.exists(temp_folder):
        mssparkutils.fs.rm(temp_folder, True)

# ===============================================
# Completion Message
# ===============================================

log.info("Oracle Open PO standardization completed: %s rows", source_rows)

