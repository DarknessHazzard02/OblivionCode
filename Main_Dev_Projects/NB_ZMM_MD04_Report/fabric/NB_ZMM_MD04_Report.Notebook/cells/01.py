
# ===============================================
# SAP Open PO Standardization Notebook
# Author: Haz
# ===============================================

import logging

from notebookutils import mssparkutils
from pyspark.sql.functions import col, current_date, date_format, substring, to_date

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("sap_open_po_report")

# ===============================================
# Configuration
# ===============================================

CONFIG = {
    "source_file": "Files/PO_Report/OpenPO_Report_SAP.csv",
    "temp_folder": "Files/PO_Report/OpenPO_Report_SAP_Temp",
    "final_file": "Files/PO_Report/OpenPO_Report_SAP.csv",
    "sap_date_format": "yyyy-MM-dd",
    "report_date_format": "MM/dd/yyyy",
}

# Columns with accents can arrive mis-decoded (UTF-8 read as Latin-1): accept both spellings
POSITION_CANDIDATES = ["Posición", "PosiciÃ³n"]
CREATION_DATE_CANDIDATES = ["Fecha_creación_OC", "Fecha_creaciÃ³n_OC"]

REQUIRED_COLUMNS = [
    "Pedido", "Proveedor", "Nombre_del_Proveedor", "Centro", "Material",
    "Material_Description", "Material_Proveedor", "Cantidad", "Unidad_Med",
    "Fecha_Embarque_AB", "Fecha_Embarque_LA", "Tipo_Confirmacion", "Referencia",
    "EXECUTION_DATE",
]

# ===============================================
# Read Source File
# ===============================================

sap_source = (
    spark.read
    .option("header", "true")
    .option("encoding", "UTF-8")
    .csv(CONFIG["source_file"])
)

# ===============================================
# Validate Source Columns
# ===============================================

def resolve_column(candidates):
    found = next((name for name in candidates if name in sap_source.columns), None)
    if found is None:
        raise ValueError(f"Column not found. Expected one of: {candidates}")
    return found

position_column = resolve_column(POSITION_CANDIDATES)
creation_date_column = resolve_column(CREATION_DATE_CANDIDATES)

missing_columns = [name for name in REQUIRED_COLUMNS if name not in sap_source.columns]
if missing_columns:
    raise ValueError(f"Missing SAP source columns: {missing_columns}")

# ===============================================
# Filter Current Execution Date
# ===============================================

def to_sap_date(column_name):
    return to_date(substring(col(column_name), 1, 10), CONFIG["sap_date_format"])

def to_report_date(column_name):
    return date_format(to_sap_date(column_name), CONFIG["report_date_format"])

sap_filtered = sap_source.filter(to_sap_date("EXECUTION_DATE") == current_date())

source_rows = sap_source.count()
filtered_rows = sap_filtered.count()
if filtered_rows == 0:
    raise ValueError(f"No SAP records found for today's EXECUTION_DATE ({source_rows} rows in source).")

# ===============================================
# Standardize SAP Output
# ===============================================

final_output = sap_filtered.select(
    col("Pedido").alias("Order No (PO)"),
    col(position_column).alias("Seq"),
    col("Proveedor").alias("Vendor Code"),
    col("Nombre_del_Proveedor").alias("Vendor Name"),
    col("Centro").alias("Ship to Code"),
    col("Centro").alias("DC Destination (Header)"),
    col("Material").alias("Style"),
    col("Material_Description").alias("Item Description"),
    col("Material_Proveedor").alias("SKU"),
    col("Cantidad").alias("Qty"),
    col("Unidad_Med").alias("UOM"),
    to_report_date("Fecha_Embarque_AB").alias("Start date Ship Window"),
    to_report_date("Fecha_Embarque_LA").alias("End date Ship Window"),
    col("Cantidad").alias("Ordered Qty"),
    to_report_date(creation_date_column).alias("PO Creation Date"),
    col("Tipo_Confirmacion").alias("Confirmation Type"),
    col("Referencia").alias("Reference"),
)

log.info("SAP rows - source: %s | today: %s", source_rows, filtered_rows)
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

log.info("SAP Open PO standardization completed: %s rows", filtered_rows)

