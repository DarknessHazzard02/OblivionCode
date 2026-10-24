
# ===============================================
# Drop Table - D365_ON_HAND_MONTH_CLOSURE
# Updated by Haz
# ===============================================
# Drops the Delta table; the next load recreates it. Any error stops the run.

spark.sql("DROP TABLE IF EXISTS D365_ON_HAND_MONTH_CLOSURE")
print("Table dropped: D365_ON_HAND_MONTH_CLOSURE")

