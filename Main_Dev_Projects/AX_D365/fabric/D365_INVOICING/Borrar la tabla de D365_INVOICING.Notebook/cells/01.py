
# ===============================================
# Drop Table - D365_INVOICING
# Updated by Haz
# ===============================================
# Drops the Delta table; the next load recreates it. Any error stops the run.

spark.sql("DROP TABLE IF EXISTS D365_INVOICING")
print("Table dropped: D365_INVOICING")

