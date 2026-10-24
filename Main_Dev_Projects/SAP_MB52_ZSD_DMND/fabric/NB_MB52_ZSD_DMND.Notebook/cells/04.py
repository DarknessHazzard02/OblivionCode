
# ===============================================
# Check Default Lakehouse and Load CSV Files
# ===============================================
def load_fabric_csv(spark_path, file_label):
    log.info("%s: reading from %s", file_label, spark_path)
    try:
        spark_dataframe = (spark.read
            .format("csv")
            .option("header", "true")
            .option("inferSchema", "false")
            .option("encoding", "UTF-8")
            .option("delimiter", ",")
            .option("quote", chr(34))
            .option("escape", chr(92))
            .option("multiLine", "true")
            .option("mode", "FAILFAST")
            .option("unescapedQuoteHandling", "STOP_AT_DELIMITER")
            .load(spark_path))
        if not spark_dataframe.columns:
            raise ValueError(f"{file_label} returned no columns from {spark_path}.")
        row_count = spark_dataframe.count()
        if row_count == 0:
            raise ValueError(f"{file_label} file is empty: {spark_path}.")
        log.info("%s: %s rows, %s columns", file_label, f"{row_count:,}", len(spark_dataframe.columns))
        log.debug("%s columns: %s", file_label, spark_dataframe.columns)
        return spark_dataframe
    except Exception as error:
        raise RuntimeError(
            f"Unable to parse {file_label} from {spark_path}. "
            "Verify delimiter, quote, escape, and multiline settings in the upstream Copy activity."
        ) from error

log.info("Default Lakehouse mounted: %s | Files folder: %s | Project folder %s: %s",
         DEFAULT_LAKEHOUSE.exists(), DEFAULT_FILES.exists(), ROOT, ROOT.exists())
if not DEFAULT_LAKEHOUSE.exists():
    raise RuntimeError(
        "The notebook does not have a default Lakehouse attached. "
        "Attach the pipeline Lakehouse and pin it as the notebook default."
    )
if ROOT.exists():
    for item in ROOT.iterdir():
        log.info("Project file: %s (%s bytes)", item.name, f"{item.stat().st_size:,}")
mb52_spark = load_fabric_csv(MB52_SPARK_PATH, "MB52")
sd48_spark = load_fabric_csv(SD48_SPARK_PATH, "ZSD_DMND")
mb52_raw = mb52_spark.toPandas()
sd48_raw = sd48_spark.toPandas()
mb52_raw.columns = [str(column).strip() for column in mb52_raw.columns]
sd48_raw.columns = [str(column).strip() for column in sd48_raw.columns]
log.info("Pandas rows - MB52: %s | ZSD_DMND: %s", f"{len(mb52_raw):,}", f"{len(sd48_raw):,}")


