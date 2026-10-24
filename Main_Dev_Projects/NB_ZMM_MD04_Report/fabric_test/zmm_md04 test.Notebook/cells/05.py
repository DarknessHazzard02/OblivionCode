
from pyspark.sql import functions as F
nb = spark.table("sap_zmm_md04_vigente")

nb.filter(F.col("Material").isin("635731", "777676")).select(
    "Centro", "Proveedor", "Material",
    F.col("Pedido"), F.col("Pedido").isNull().alias("Pedido_es_null"),
    F.col("Posición"), F.col("Posición").isNull().alias("Posicion_es_null")
).show(5, False)

