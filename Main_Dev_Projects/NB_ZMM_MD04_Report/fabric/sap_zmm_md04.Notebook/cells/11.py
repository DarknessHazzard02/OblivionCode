
# ── Validación (opcional, para la fase de pruebas): distribuciones de la tabla ──
try:
    out = spark.read.format("delta").load(table_path)
except Exception:
    print(f"{target_table} no existe. Si la borraste, vuelve a correr la celda "
          f"anterior: ahora detecta la tabla ausente e ignora la bitácora.")
else:
    print(f"Filas totales en {target_table}: {out.count()}")
    if "Fila_Realineada" in out.columns:
        realineadas = out.filter(F.col("Fila_Realineada") == "Sí").count()
        print(f"Filas recuperadas por alineación: {realineadas}")
    display(out.groupBy("EXECUTION_DATE", "EXECUTION_TIME").count().orderBy("EXECUTION_DATE"))
    display(out.groupBy("Status").count().orderBy("Status"))
    display(out.groupBy("Excepción").count().orderBy("Excepción"))

