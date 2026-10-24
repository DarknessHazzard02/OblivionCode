
# Resumen final y salida para el pipeline / correo.
# notebookutils.notebook.exit() entrega este JSON al pipeline en
# @activity('<nombre actividad>').output.result.exitValue

con_error = [r for r in resultados if r["status"] == "ERROR"]
if not resultados:
    status_global = "SIN_PENDIENTES"
elif con_error:
    status_global = "ERROR"
else:
    status_global = "OK"

resumen = {
    "status_global": status_global,
    "tabla": target_table,
    "modo": write_mode,
    "incluir_stock_negativo": incluir_stock_negativo,
    "archivos_procesados": len(resultados),
    "archivos_con_error": len(con_error),
    "filas_cargadas_total": sum(r["filas_cargadas"] for r in resultados),
    "filas_rechazadas_total": sum(r["filas_rechazadas"] for r in resultados),
    "stock_negativos_total": sum(r["stock_negativos"] for r in resultados),
    "duracion_segundos": round(time.time() - inicio, 1),
    "corrida": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "detalle": resultados,
}
# Campo "summary" legible: el estándar de pipelines del equipo lo usa en el
# cuerpo del correo (json(...exitValue).summary)
resumen["summary"] = (f"{status_global}: {len(resultados)} archivo(s) procesados, "
                      f"{resumen['filas_cargadas_total']} filas cargadas, "
                      f"{resumen['filas_rechazadas_total']} rechazadas (cuarentena), "
                      f"{resumen['stock_negativos_total']} con stock negativo, "
                      f"{resumen['duracion_segundos']} s")
log("RESUMEN DE LA CORRIDA:")
print(json.dumps(resumen, indent=2, ensure_ascii=False))

notebookutils.notebook.exit(json.dumps(resumen, ensure_ascii=False))

