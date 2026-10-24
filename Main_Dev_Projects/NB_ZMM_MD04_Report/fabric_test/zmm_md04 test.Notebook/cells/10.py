
from pyspark.sql import functions as F
v = spark.table("sap_zmm_md04_vigente")

v.filter(F.col("Fila_Realineada") == "Sí").select(
    "Centro", "Proveedor", "Material", "Material_Description",
    "Pedido", "Posición", "Tipo_Confirmacion", "Cantidad", "Precio_Neto", "Mon"
).show(11, False)

