
# ===============================================
# Delete All Rows - D365_ON_HAND_MONTH_CLOSURE
# Updated by Haz
# ===============================================
# Empties the Delta table before a full reload. Any error stops the run:
# a failed delete must not let the pipeline append on top of old rows.

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("delete_rows")

TABLE_NAME = "D365_ON_HAND_MONTH_CLOSURE"

log.info("Deleting all rows from %s", TABLE_NAME)
spark.sql(f"DELETE FROM {TABLE_NAME}")
log.info("All rows deleted from %s", TABLE_NAME)

