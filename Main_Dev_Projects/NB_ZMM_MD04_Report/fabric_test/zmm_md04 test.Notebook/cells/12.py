
from pyspark.sql import functions as F
lin = spark.table("sap_zmm_pgi_pgt_lineas")
fac = spark.table("pgi_raw_facturas_por_estatus")

sin_fac = lin.filter(F.col("cubeta") == "LA · con referencia, sin factura en PGI")
folios = fac.select(F.upper(F.regexp_replace(F.trim(F.col("Folio")), "['\"]", "")).alias("f")).distinct()

# ¿La referencia existe como folio en ALGUNA factura, sin exigir PO+línea?
existe = sin_fac.join(folios, F.col("ref_key") == F.col("f"), "inner").count()
print(f"de las 191 sin factura, su referencia SÍ es un folio conocido: {existe}")
print(f"  -> esas fallan por PO+línea, no por ventana de fechas")
print(f"no aparece en ninguna factura: {sin_fac.count() - existe}")
print(f"  -> esas son factura fuera de la ventana, o referencia que no es factura")

