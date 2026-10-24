
# Detección de archivos pendientes (catch-up)
# La bitácora SAP_ZMM_MD04_LOG registra cada archivo cargado con éxito; los archivos
# que no estén en ella son "pendientes". Si el notebook no corre por N días, aquí
# aparecen todos los archivos faltantes.

# ── Guardas: se revisan ANTES de leer nada ────────────────────────────────
if target_table in tablas_intocables:
    raise SystemExit(
        f"'{target_table}' está en tablas_intocables y este notebook no la escribe. "
        f"Hoy la mantiene el Dataflow Gen2 y la consume el equipo: escribirla desde "
        f"aquí en modo snapshot borraría su histórico completo. Para pasar a "
        f"producción, primero apagar el dataflow y avisarle al equipo; recién "
        f"entonces quitarla de la lista, a conciencia.")

if write_mode == "snapshot" and not permitir_perder_historia:
    # Si la tabla no existe no hay nada que perder. Cualquier otro error al leerla
    # debe detener la corrida: tomarlo como "0 fotos" desarmaría esta red.
    _fotos = (spark.read.format("delta").load(table_path)
              .select("EXECUTION_DATE").distinct().count()) if delta_exists(table_path) else 0
    if _fotos > 1:
        raise SystemExit(
            f"'{target_table}' ya tiene {_fotos} fotos acumuladas y el modo es "
            f"'snapshot', que sobreescribe la tabla completa: quedaría 1 y se "
            f"perderían {_fotos - 1}. Si querías conservarlas, usa "
            f"write_mode = 'history'. Si de verdad quieres dejar solo la última, "
            f"pon permitir_perder_historia = True.")

log("=" * 70)
log(f"Inicio de carga ZMM_MD04 | tabla destino: {target_table} | modo: {write_mode} | "
    f"incluir_stock_negativo: {incluir_stock_negativo} | force_reload: {force_reload}")
log(f"Exclusiones de proveedores/materiales: "
    f"{'APLICADAS (como el dataflow)' if aplicar_exclusiones else 'APAGADAS — entran todas las líneas'}")
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
# ¿La tabla destino existe? La bitácora dice qué archivos se cargaron, pero si
# alguien borró la tabla, esa memoria queda mintiendo: el notebook no haría
# nada y la tabla se quedaría vacía para siempre. Pasó el 2026-08-06.
tabla_existe = delta_exists(table_path)
if not tabla_existe:
    log(f"La tabla {target_table} no existe (¿se borró?). Se ignora la bitácora "
        f"y se recarga desde cero.")

procesados = set()
if tabla_existe and delta_exists(log_path):
    log_df = spark.read.format("delta").load(log_path)
    procesados = {r["file_name"] for r in
                  log_df.filter((F.col("status") == "OK") &
                                (F.col("target_table") == target_table))
                        .select("file_name").distinct().collect()}
    log(f"Bitácora {log_table}: {len(procesados)} archivos ya cargados en {target_table}")
elif tabla_existe:
    log(f"Bitácora {log_table} aún no existe; se creará en esta corrida")

# Columnas que este notebook produce y que, si faltan en la tabla destino, quieren
# decir que la tabla se escribió con una versión anterior del código. En ese caso
# hay que recargar aunque la bitácora diga que el archivo ya se procesó: el archivo
# es el mismo, pero lo que sabemos extraerle cambió.
#
# Evita tener que acordarse de poner force_reload = True a mano después de cada
# cambio de esquema — que es justo lo que se olvida y deja la tabla a medias.
COLUMNAS_ESPERADAS = ["Unidad_Precio"]

# El tipo también cuenta, no solo el nombre. Cambiar las fechas de texto a DATE
# no agrega ni quita columnas, así que sin esta comprobación la tabla se
# quedaría con el esquema viejo hasta que alguien pusiera force_reload a mano.
TIPO_ESPERADO = {} if fechas_como_texto else {"Fecha_creación_OC": "date"}

recarga_por_esquema = False
if tabla_existe and not force_reload:
    try:
        esquema_actual = spark.read.format("delta").load(table_path).schema
        cols_actuales = {f.name: f.dataType.simpleString() for f in esquema_actual}
        faltantes = [x for x in COLUMNAS_ESPERADAS if x not in cols_actuales]
        distintas = [f"{k} es {cols_actuales.get(k)} y debería ser {v}"
                     for k, v in TIPO_ESPERADO.items()
                     if k in cols_actuales and cols_actuales[k] != v]
        if faltantes or distintas:
            recarga_por_esquema = True
            log(f"El esquema de {target_table} no corresponde a esta versión del "
                f"notebook; se recarga la foto más reciente.")
            if faltantes:
                log(f"  faltan columnas: {faltantes}")
            for d in distintas:
                log(f"  {d}")
    except Exception as e:
        log(f"No se pudo leer el esquema de {target_table} ({type(e).__name__}); "
            f"se sigue con la lógica normal de bitácora")

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
    if force_reload or recarga_por_esquema or mas_reciente.name not in procesados:
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

