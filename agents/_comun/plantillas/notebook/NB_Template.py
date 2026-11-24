# ===============================================
# NB_<Nombre> — archivos a Delta
# Author: Haz
# ===============================================
# Ver skills delta-lakehouse y sap-fabric-ingesta. Sin credenciales en el notebook.
from pyspark.sql import functions as F

# ===============================================
# Parameters
# ===============================================
SOURCE_PATH = "Files/<fuente>/"
RAW_TABLE = "<FUENTE>_RAW"
CLEAN_TABLE = "<FUENTE>_CLEAN"
EXPECTED_COLUMNS = ["Plant", "Material", "OnHand", "SnapshotDate"]

# ===============================================
# Read
# ===============================================
raw = (spark.read.option("header", True).csv(SOURCE_PATH)
       .withColumn("_SOURCE_FILE", F.input_file_name())
       .withColumn("_LOAD_TS", F.current_timestamp()))

# ===============================================
# Validate Schema
# ===============================================
missing = sorted(set(EXPECTED_COLUMNS) - set(raw.columns))
if missing:
    raise ValueError(f"Missing columns: {missing}")

# ===============================================
# Raw
# ===============================================
raw.write.mode("overwrite").format("delta").saveAsTable(RAW_TABLE)

# ===============================================
# Clean
# ===============================================
clean = (raw
         .withColumn("OnHand", F.expr("try_cast(OnHand AS DOUBLE)"))
         .withColumn("SnapshotDate", F.expr("try_to_date(SnapshotDate, 'yyyy-MM-dd')"))
         .dropDuplicates(["Plant", "Material", "SnapshotDate"]))
expected_count = clean.count()
bad_dates = clean.filter(F.col("SnapshotDate").isNull()).count()
clean.write.mode("overwrite").format("delta").saveAsTable(CLEAN_TABLE)

# ===============================================
# Validate Target
# ===============================================
target_count = spark.table(CLEAN_TABLE).count()
if target_count != expected_count:
    raise RuntimeError(f"Target count {target_count} does not match {expected_count}")
print(f"Carga completada: {target_count} filas, {bad_dates} fechas no parseadas")
