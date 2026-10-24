
z = spark.table("sap_zmm_md04_vigente")
z.groupBy("Por").count().orderBy(F.desc("count")).show(10)
z.select("Cantidad", "Precio_Neto", "Por", "Mon",
         (F.col("Cantidad")*F.col("Precio_Neto")).alias("actual"),
         (F.col("Cantidad")*F.col("Precio_Neto")/F.col("Por")).alias("con_Por")
).orderBy(F.desc("actual")).show(10, False)

