
dfw = spark.table("SAP_ZMM_MD04").filter(F.col("EXECUTION_DATE") == "2026-08-06")
excl_mat = ["77233554","77269668","77049219","77637835","77437336","77887719"]  # muestra
print("filas del notebook con materiales que el dataflow excluye:",
      nb.filter(F.col("Material").isin(excl_mat)).count())
print("las mismas en el dataflow (deberían ser 0):",
      dfw.filter(F.col("Material").isin(excl_mat)).count())

