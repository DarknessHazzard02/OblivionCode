
# ===============================================
# SAP ZMM_MD04 Full Load Notebook (sap_zmm_md04_vigente)
# Updated by Haz
# ===============================================

# Celda de parámetros: en deployment pipelines / actividad de Notebook estos valores
# se sobreescriben por etapa (Dev/Test/Prod) o desde el pipeline.
workspace_id = "<workspace-id>"
lakehouse_id = "<lakehouse-id>"
source_folder = "Files/SAP/ZMM_MD04/ZMM_MD04 RAW"
# Destino: tabla propia, con TODAS las líneas del archivo. No apunta ni a
# SAP_ZMM_MD04 (la del dataflow, que sigue corriendo) ni a su _TEST.
# El criterio, decidido el 2026-08-06: la ingesta trae el archivo completo y
# el filtrado se hace después, en el tablero, donde se ve lo que se está
# quitando.
target_table = "sap_zmm_md04_vigente"
log_table = "SAP_ZMM_MD04_LOG"       # bitácora de archivos procesados
date_format_in = "M/d/yyyy"          # confirmado con archivo real (MM/DD/YYYY)

# Modo de escritura (ambos idempotentes: correr N veces no duplica filas):
#   "snapshot": la tabla siempre contiene SOLO el archivo más reciente (igual que el
#               dataflow). Los archivos intermedios no cargados quedan obsoletos.
#   "history":  acumula ejecuciones (una por día, vía replaceWhere por EXECUTION_DATE)
#               y hace CATCH-UP: si no corrió por N días, carga los archivos faltantes.
write_mode = "snapshot"

# Solo aplica en modo "history": fecha mínima (yyyy-MM-dd) desde la cual hacer
# catch-up de archivos pendientes. La carpeta tiene archivos desde 2023, así que
# vacío ("") = cargar TODO el histórico (~387 archivos) — hacerlo solo a propósito.
history_desde = "2026-07-01"

# Switch de negativos: el dataflow original DESCARTABA las filas con stock negativo
# formato SAP ("676.000-", ~345 filas por archivo).
#   True  = se conservan con su valor negativo real (recomendado)
#   False = se excluyen, replicando el comportamiento del dataflow
incluir_stock_negativo = True

# True = reprocesa los archivos aunque ya estén en la bitácora (útil tras corregir algo)
force_reload = False

# Exclusiones de proveedores y materiales. El dataflow original las aplicaba, y
# este notebook las replicaba para dar los mismos números.
#
# APAGADAS por decisión del equipo (2026-08-06): la tabla debe traer TODAS las
# líneas y el filtro se hace en el tablero, no aquí. Un filtro escondido en la
# ingesta es imposible de notar después: los renglones simplemente no están y
# nadie sabe que faltan.
#
# En True se recupera el comportamiento del dataflow, para poder comparar
# conteos contra el reporte viejo.
aplicar_exclusiones = False

# Tablas que este notebook NO debe escribir nunca. SAP_ZMM_MD04 la mantiene hoy
# el Dataflow Gen2 y la consume el equipo: si este notebook la escribiera en
# modo snapshot, sus 406 fotos (2.4 millones de filas) se irían de un golpe.
# Para hacer el cambio a producción hay que apagar el dataflow primero, y
# entonces sí quitar la tabla de esta lista, a conciencia.
tablas_intocables = ["SAP_ZMM_MD04", "SAP_ZMM_MD04_TEST"]

# Red de seguridad adicional: en modo snapshot se sobreescribe la tabla
# completa. Si la tabla destino ya tiene varias fotos acumuladas, escribir
# borraría todas menos una. Con esto en False, el notebook se detiene y avisa
# en vez de hacerlo.
permitir_perder_historia = False

# Cuántas filas de stock negativo imprimir como muestra, para poder ir a
# verificarlas en SAP. 0 = no imprimir ninguna.
mostrar_muestra_negativos = 10

# Fechas como texto "M/d/yyyy" (True) o como DATE (False).
#
# El dataflow las escribía como texto y el modelo de Power BI que lee
# SAP_ZMM_MD04 depende de ese formato. Si algún día este notebook apunta a esa
# tabla, hay que poner True. Para sap_zmm_md04_vigente va en False: en texto,
# ordenar por fecha ordena alfabéticamente y "12/4/2024" queda antes que
# "9/4/2025".
fechas_como_texto = False

