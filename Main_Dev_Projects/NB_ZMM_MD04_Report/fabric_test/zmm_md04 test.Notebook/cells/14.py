
from pyspark.sql import functions as F
lin = spark.table("sap_zmm_pgi_pgt_lineas")
sf = lin.filter(F.col("cubeta") == "LA · con referencia, sin factura en PGI")

sf.select("ref_key",
    F.when(F.col("ref_key").rlike("^[0-9]+$"), "solo dígitos")
     .when(F.col("ref_key").rlike("^1Z"), "guía UPS")
     .when(F.col("ref_key").rlike("^[A-Z]{1,4}[- ]?[0-9]+$"), "serie-folio")
     .otherwise("otra cosa").alias("forma"),
    F.col("Fecha_creación_OC")
).groupBy("forma").agg(
    F.count("*").alias("n"),
    F.min("Fecha_creación_OC").alias("OC_mas_vieja"),
    F.max("Fecha_creación_OC").alias("OC_mas_nueva")
).show(truncate=False)

sf.select("ref_key", "Proveedor", "Pedido", "Fecha_creación_OC").show(25, False)

