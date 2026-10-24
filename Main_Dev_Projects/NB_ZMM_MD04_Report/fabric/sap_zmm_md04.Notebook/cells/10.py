
# Proceso principal: parsear -> transformar -> escribir -> registrar en bitácora
#
# Idempotencia: la escritura Delta es atómica (si el job falla a medias, la tabla
# queda en la versión anterior) y la bitácora evita recargar archivos ya procesados.
#
# columnMapping "name" permite nombres de columna con espacios/acentos/puntos,
# igual que los produce un Dataflow Gen2.
spark.conf.set("spark.databricks.delta.properties.defaults.minReaderVersion", "2")
spark.conf.set("spark.databricks.delta.properties.defaults.minWriterVersion", "5")
spark.conf.set("spark.databricks.delta.properties.defaults.columnMapping.mode", "name")

inicio = time.time()
resultados = []

for file_info in pendientes:
    exec_date, exec_time = timestamp_de_archivo(file_info)
    r = {"archivo": file_info.name, "execution_date": exec_date,
         "execution_time": exec_time, "status": "OK", "error": None,
         "filas_cargadas": 0, "filas_rechazadas": 0, "stock_negativos": 0}
    log("-" * 70)
    log(f"Procesando {file_info.name} (ejecución SAP: {exec_date} {exec_time})")
    try:
        df_crudo, r["filas_rechazadas"] = parsear_archivo(file_info, exec_date)
        df_final, stats = transformar(df_crudo, exec_date, exec_time)
        r["stock_negativos"] = stats["stock_negativos"]
        r["filas_cargadas"] = df_final.count()
        log(f"  Filas finales a cargar: {r['filas_cargadas']}")

        if write_mode == "history":
            # Delete-insert por fecha de ejecución en una sola transacción:
            # re-correr el mismo día reemplaza en lugar de duplicar
            log(f"  Escribiendo (history, replaceWhere EXECUTION_DATE = '{exec_date}')...")
            (a_nombres_delta(df_final).write.format("delta")
                .mode("overwrite")
                .option("replaceWhere", f"EXECUTION_DATE = '{exec_date}'")
                .save(table_path))
        else:
            log("  Escribiendo (snapshot, overwrite de tabla completa)...")
            (a_nombres_delta(df_final).write.format("delta")
                .mode("overwrite")
                .option("overwriteSchema", "true")
                .save(table_path))
        log(f"  OK: {file_info.name} cargado en {target_table}")
    except Exception as e:
        r["status"] = "ERROR"
        r["error"] = str(e)[:500]
        log(f"  ERROR con {file_info.name}: {r['error']}")

    # Registrar en bitácora (una fila por archivo procesado)
    fila_log = [(file_info.name, r["execution_date"], r["execution_time"], write_mode,
                 target_table, r["filas_cargadas"], r["filas_rechazadas"],
                 r["stock_negativos"], incluir_stock_negativo, r["status"],
                 r["error"] or "", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))]
    cols_log = ["file_name", "execution_date", "execution_time", "write_mode",
                "target_table", "filas_cargadas", "filas_rechazadas",
                "stock_negativos", "incluir_stock_negativo", "status",
                "mensaje_error", "procesado_en"]
    spark.createDataFrame(fila_log, cols_log).write.format("delta") \
        .mode("append").option("mergeSchema", "true").save(log_path)

    resultados.append(r)

log("-" * 70)
log(f"Proceso terminado en {round(time.time() - inicio, 1)} s")

