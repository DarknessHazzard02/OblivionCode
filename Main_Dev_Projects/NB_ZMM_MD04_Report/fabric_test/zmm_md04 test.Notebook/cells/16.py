
from pyspark.sql import functions as F

z = spark.table("sap_zmm_md04_vigente")
z = z.withColumn("_por", F.when(F.col("Por").isNull() | (F.col("Por") == 0), F.lit(1.0)).otherwise(F.col("Por")))
z = z.withColumn("_monto_hoy", F.col("Cantidad") * F.col("Precio_Neto") / F.col("_por"))

par = z.filter(F.col("Tipo_Confirmacion").isin(["LA", "LA+"]))
par = par.withColumn("u_po", F.upper(F.trim(F.col("Unidad_Med"))))
par = par.withColumn("u_precio", F.upper(F.trim(F.col("Unidad_Precio"))))

print("--- pares donde las unidades DIFIEREN (aqui hace falta factor) ---")
d = par.filter(F.col("u_po") != F.col("u_precio"))
d.groupBy("u_po", "u_precio").agg(
    F.count("*").alias("lineas"),
    F.countDistinct("Material").alias("materiales"),
    F.round(F.sum("_monto_hoy"), 0).alias("monto_hoy_inflado")
).orderBy(F.desc("monto_hoy_inflado")).show(50, False)

print("--- materiales que mas pesan ---")
d.groupBy("Material", "u_po", "u_precio").agg(
    F.round(F.sum("_monto_hoy"), 0).alias("monto_hoy"),
    F.countDistinct("Nombre_del_Proveedor").alias("n_proveedores")
).orderBy(F.desc("monto_hoy")).show(30, False)

print("iguales:", par.filter(F.col("u_po") == F.col("u_precio")).count(),
      "| diferentes:", d.count())

