
# Transformaciones (réplica de la lógica M) — devuelve (df_final, stats)

date_cols = ["Fecha Reprog", "Fecha creación OC", "Fecha entrega PO",
             "Fecha Embarque AB", "Fecha Embarque LA"]


def transformar(df, exec_date, exec_time):
    stats = {}

    # Trim general + quitar filas vacías y encabezados repetidos (Centro = "Centro")
    df = df.select([F.trim(c(x)).alias(x) for x in df.columns])
    df = df.filter(c("Centro").isNotNull() & (c("Centro") != "") & (c("Centro") != "Centro"))

    # Renombres (mismos alias que el dataflow); "Tipo Conf." se renombra desde ya
    # para evitar el punto en el nombre
    df = (df.withColumnRenamed("Fecha Pedido", "Fecha creación OC")
            .withColumnRenamed("Fecha Entrega Pedido", "Fecha entrega PO")
            .withColumnRenamed("Fecha Embarque", "Fecha Embarque AB")
            .withColumnRenamed("Fecha Planta TC", "Fecha Embarque LA")
            .withColumnRenamed("Excepcion", "Excepcion 1")
            .withColumnRenamed("Tipo Conf.", "Tipo Confirmacion"))

    # Fechas (locale en-US; valor no parseable -> null, igual que ReplaceErrorValues del M)
    for dcol in date_cols:
        df = df.withColumn(dcol, F.to_date(c(dcol), date_format_in))

    # Números: se quitan separadores de miles y se maneja el signo negativo al final
    # estilo SAP ("676.000-" -> -676.0), que el dataflow no sabía parsear.
    num_cols = ["Cantidad", "Precio Neto", "Por", "Stock Centro Disp",
                "ROP", "Plazo Entrega Previo", "Tiempo Tratamiento EM"]
    for ncol in num_cols:
        clean = F.regexp_replace(c(ncol), ",", "")
        clean = F.regexp_replace(clean, r"^(.+)-$", r"-$1")
        df = df.withColumn(ncol, clean.cast("double"))

    df = df.withColumn("Posición", F.regexp_replace(c("Posición"), ",", "").cast("long"))

    # Switch de negativos: reporte + filtro opcional (False = comportamiento del dataflow)
    stats["stock_negativos"] = df.filter(c("Stock Centro Disp") < 0).count()
    if incluir_stock_negativo:
        log(f"  Stock negativo: {stats['stock_negativos']} filas CONSERVADAS "
            f"(incluir_stock_negativo = True)")
    else:
        df = df.filter(F.coalesce(c("Stock Centro Disp") >= 0, F.lit(True)))
        log(f"  Stock negativo: {stats['stock_negativos']} filas EXCLUIDAS "
            f"(incluir_stock_negativo = False, igual que el dataflow)")

    # Tipo Confirmacion: quitar espacios; vacío -> "SC"
    df = df.withColumn("Tipo Confirmacion", F.regexp_replace(c("Tipo Confirmacion"), " ", ""))
    df = df.withColumn("Tipo Confirmacion",
                       F.when(c("Tipo Confirmacion").isNull() | (c("Tipo Confirmacion") == ""), "SC")
                        .otherwise(c("Tipo Confirmacion")))

    # Material: quitar espacios internos y filtrar materiales excluidos
    df = df.withColumn("Material", F.regexp_replace(c("Material"), " ", ""))
    df = df.filter(c("Material").isNotNull() & ~c("Material").isin(materiales_excluidos))

    # Proveedores excluidos (el M usa Text.Contains)
    df = df.filter(c("Proveedor").isNotNull())
    for prov in proveedores_excluidos:
        df = df.filter(~c("Proveedor").contains(prov))

    # Aging: días desde hoy contra la fecha que corresponde según el tipo de confirmación
    today = F.current_date()
    df = df.withColumn("Aging",
        F.when(c("Tipo Confirmacion") == "AB", F.datediff(today, c("Fecha Embarque AB")))
         .when(c("Tipo Confirmacion").isin("LA", "LA+"), F.datediff(today, c("Fecha Embarque LA")))
         .when(c("Proveedor").isin(proveedores_aging_po) & (c("Tipo Confirmacion") == "SC"),
               F.datediff(today, c("Fecha entrega PO")))
         .when(c("Tipo Confirmacion") == "SC", F.datediff(today, c("Fecha creación OC")))
         .otherwise(F.lit(None))
         .cast("long"))

    # Status
    df = df.withColumn("Status",
        F.when(c("Aging").isNull(), "Sin Clasificar")
         .when((c("Tipo Confirmacion") == "SC") & (c("Aging") > 10), "Delay")
         .when(c("Tipo Confirmacion").isin("AB", "LA", "LA+") & (c("Aging") > 0), "Delay")
         .otherwise("On time"))

    # Reschedule Days (valor absoluto) y bucket Reschedule (función "Aging" del M)
    df = df.withColumn("Reschedule Days",
                       F.abs(F.datediff(c("Fecha Reprog"), c("Fecha Embarque LA"))).cast("long"))

    rd = c("Reschedule Days")
    df = df.withColumn("Reschedule",
        F.when(rd.isNull(), F.lit(None).cast("string"))
         .when(rd >= 365, "i. More than 1 year")
         .when(rd >= 270, "h. More than 09 months")
         .when(rd >= 180, "g. More than 06 months")
         .when(rd >= 90, "f. More than 03 months")
         .when(rd >= 30, "e. More than 01 month")
         .when(rd >= 14, "d. More than 02 weeks")
         .when(rd >= 7, "c. More than 01 weeks")
         .when(rd >= 3, "b. More than 03 days")
         .otherwise("a. Less than 03 days"))

    # Excepción: categorización del texto de excepción de SAP
    exc = F.coalesce(c("Excepcion 1"), F.lit(""))
    df = df.withColumn("Excepción",
        F.when(exc.contains("Reschedule in"), "Reschedule in")
         .when(exc.contains("Reschedule out"), "Reschedule out")
         .when(exc.contains("Finish date in the past"), "Finish date in the past")
         .when(exc.contains("Cancel process"), "Cancel process")
         .otherwise("No Exception")).drop("Excepcion 1")

    # EXECUTION_DATE / EXECUTION_TIME: timestamp de ejecución de SAP (del nombre del archivo)
    df = (df.withColumn("EXECUTION_DATE", F.to_date(F.lit(exec_date), "yyyy-MM-dd"))
            .withColumn("EXECUTION_TIME", F.lit(exec_time))
            .withColumn("DATA_BASE", F.lit("SAP")))

    # Esquema final idéntico al del dataflow (fechas y Aging como TEXTO) para no
    # romper el modelo de Power BI actual.
    # Mejora futura: dejar tipos nativos (date / long) cuando se ajuste el modelo semántico.
    for dcol in date_cols:
        df = df.withColumn(dcol, F.date_format(c(dcol), "M/d/yyyy"))
    df = df.withColumn("Aging", c("Aging").cast("string"))

    # Orden final de columnas (igual al dataflow)
    final_cols = [
        "Centro", "Proveedor", "Nombre del Proveedor", "Planif. Nec", "Material",
        "Material Description", "Material Proveedor", "Ind. ABC", "Pedido", "Posición",
        "Unidad Med", "Tipo Confirmacion", "Referencia", "Fecha Reprog", "Estrategia Lib",
        "Fecha Entrada Necesidad", "Status Msg", "Fecha creación OC", "Fecha entrega PO",
        "Fecha Embarque AB", "Fecha Embarque LA", "Cantidad", "Precio Neto", "Por", "Mon",
        "Stock Centro Disp", "Ubicación", "Family", "ROP", "Plazo Entrega Previo",
        "Tiempo Tratamiento EM", "Aging", "Status", "Reschedule Days", "Reschedule",
        "Excepción", "EXECUTION_TIME", "EXECUTION_DATE", "DATA_BASE",
    ]
    df = df.select([c(x) for x in final_cols])

    # "" -> null en todas las columnas de texto (Replaced value del M)
    string_cols = [f.name for f in df.schema.fields if f.dataType.simpleString() == "string"]
    df = df.select([
        F.when(c(x) == "", None).otherwise(c(x)).alias(x) if x in string_cols else c(x)
        for x in df.columns
    ])

    return df, stats

