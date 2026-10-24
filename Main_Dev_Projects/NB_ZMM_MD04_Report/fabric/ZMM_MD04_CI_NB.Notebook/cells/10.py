
# ── Validación (opcional, para la fase de pruebas): distribuciones de la tabla ──
out = spark.read.format("delta").load(table_path)

print(f"Filas totales en {target_table}: {out.count()}")
display(out.groupBy("EXECUTION_DATE", "EXECUTION_TIME").count().orderBy("EXECUTION_DATE"))
display(out.groupBy("Status").count().orderBy("Status"))
display(out.groupBy("Excepción").count().orderBy("Excepción"))

