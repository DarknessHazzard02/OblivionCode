
# Detección de archivos pendientes (catch-up)
# La bitácora SAP_ZMM_MD04_LOG registra cada archivo cargado con éxito; los archivos
# que no estén en ella son "pendientes". Si el notebook no corre por N días, aquí
# aparecen todos los archivos faltantes.

log("=" * 70)
log(f"Inicio de carga ZMM_MD04 | tabla destino: {target_table} | modo: {write_mode} | "
    f"incluir_stock_negativo: {incluir_stock_negativo} | force_reload: {force_reload}")
log("Detección de pendientes: v2.1 (fix snapshot: solo el archivo más reciente)")
log("=" * 70)

archivos = [f for f in notebookutils.fs.ls(folder_path) if not f.isDir]
if not archivos:
    raise FileNotFoundError(f"No hay archivos en {folder_path}")

# Orden cronológico por timestamp de ejecución (del nombre del archivo)
archivos = sorted(archivos, key=timestamp_de_archivo)
log(f"Archivos en la carpeta: {len(archivos)} "
    f"(del {timestamp_de_archivo(archivos[0])[0]} al {timestamp_de_archivo(archivos[-1])[0]})")

# Archivos ya procesados según la bitácora (por tabla destino, para que las corridas
# de prueba no interfieran con producción)
procesados = set()
if delta_exists(log_path):
    log_df = spark.read.format("delta").load(log_path)
    procesados = {r["file_name"] for r in
                  log_df.filter((F.col("status") == "OK") &
                                (F.col("target_table") == target_table))
                        .select("file_name").distinct().collect()}
    log(f"Bitácora {log_table}: {len(procesados)} archivos ya cargados en {target_table}")
else:
    log(f"Bitácora {log_table} aún no existe; se creará en esta corrida")

if force_reload:
    pendientes = list(archivos)
    log(f"force_reload = True: se reprocesarán TODOS los archivos ({len(pendientes)})")
else:
    pendientes = [f for f in archivos if f.name not in procesados]

if write_mode == "history" and history_desde:
    antes = len(pendientes)
    pendientes = [f for f in pendientes if timestamp_de_archivo(f)[0] >= history_desde]
    if antes - len(pendientes):
        log(f"Modo history: {antes - len(pendientes)} archivos anteriores a "
            f"{history_desde} omitidos (parámetro history_desde)")

if write_mode == "snapshot":
    # En snapshot el ÚNICO archivo relevante es el más reciente de la carpeta:
    # si ya está cargado no hay nada que hacer. Nunca se debe tomar "el más
    # reciente de los no procesados" — eso sobreescribiría la tabla con fotos
    # cada vez más viejas en corridas sucesivas.
    mas_reciente = archivos[-1]
    if force_reload or mas_reciente.name not in procesados:
        pendientes = [mas_reciente]
        log(f"Modo snapshot: se carga únicamente la foto más reciente "
            f"({mas_reciente.name}); usa modo 'history' si necesitas los días faltantes")
    else:
        pendientes = []
        log(f"Modo snapshot: la foto más reciente ({mas_reciente.name}) "
            f"ya está cargada; nada que hacer")

if pendientes:
    log(f"Archivos pendientes de cargar: {len(pendientes)}")
    for f in pendientes:
        log(f"  - {f.name}")
else:
    log("No hay archivos pendientes: la tabla ya está al día")

