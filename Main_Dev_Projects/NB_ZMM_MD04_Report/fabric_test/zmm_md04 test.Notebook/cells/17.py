
from pyspark.sql import functions as F
z = spark.table("sap_zmm_md04_vigente")
z = z.withColumn("u_po", F.upper(F.trim(F.col("Unidad_Med"))))
z = z.withColumn("u_precio", F.upper(F.trim(F.col("Unidad_Precio"))))

print("--- centros en TODO el archivo ---")
z.groupBy("Centro").count().orderBy(F.desc("count")).show(30, False)

print("--- centros de las lineas con unidad cruzada ---")
d = z.filter(~F.col("u_po").eqNullSafe(F.col("u_precio")))
d.groupBy("Centro", "u_po", "u_precio").count().orderBy("Centro", F.desc("count")).show(60, False)

