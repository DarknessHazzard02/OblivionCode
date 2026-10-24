
# ===============================================
# SAP ZMM_MD04 Load Notebook (dataflow replica, SAP_ZMM_MD04_TEST)
# Updated by Haz
# ===============================================

# Celda de parámetros: en deployment pipelines / actividad de Notebook estos valores
# se sobreescriben por etapa (Dev/Test/Prod) o desde el pipeline.
workspace_id = "<workspace-id>"
lakehouse_id = "<lakehouse-id>"
source_folder = "Files/SAP/ZMM_MD04/ZMM_MD04 RAW"
target_table = "SAP_ZMM_MD04_TEST"   # cambiar a "SAP_ZMM_MD04" al validar
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

