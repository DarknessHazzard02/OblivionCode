
# ===============================================
# Drop Table - D365_INVENTORY_AGING
# Updated by Haz
# ===============================================
# Drops the Delta table; the next load recreates it. Any error stops the run.

spark.sql("DROP TABLE IF EXISTS D365_INVENTORY_AGING")
print("Table dropped: D365_INVENTORY_AGING")

