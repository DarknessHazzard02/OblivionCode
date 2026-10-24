
from pyspark.sql import functions as F

nb  = spark.table("sap_zmm_md04_vigente")
dfw = spark.table("SAP_ZMM_MD04").filter(F.col("EXECUTION_DATE") == "2026-08-06")

for m in ["635731", "777676"]:
    print(f"\n=== material {m} ===")
    print(f"  en el notebook: {nb.filter(F.col('Material') == m).count()}")
    print(f"  en el dataflow: {dfw.filter(F.col('Material') == m).count()}")
    dfw.filter(F.col("Material") == m).select(
        "Centro", "Proveedor", "Material", "Pedido", "Posición",
        "Tipo Confirmacion", "Cantidad").show(5, False)

