
# Funciones de apoyo: logging, parseo y transformación

import json
import re
import time
import notebookutils
from datetime import datetime
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType

base_path = f"abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id}"
folder_path = f"{base_path}/{source_folder}"
table_path = f"{base_path}/Tables/{target_table}"
log_path = f"{base_path}/Tables/{log_table}"

def delta_exists(path):
    """True si hay una tabla Delta en la ruta. Revisa el _delta_log en vez de
    atrapar cualquier error al leer: un error de permisos o de red no debe
    confundirse con "la tabla no existe"."""
    return notebookutils.fs.exists(f"{path}/_delta_log")


# Los nombres con punto ("Planif. Nec", "Ind. ABC") requieren backticks al referenciarlos
c = lambda name: F.col(f"`{name}`")


def log(msg):
    """Logging descriptivo con timestamp: todo lo que hace el notebook queda visible."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def timestamp_de_archivo(file_info):
    """Extrae fecha/hora de ejecución de SAP del nombre del archivo
    (ej. MMD142_USALL_ZMMMD04_2026-07-02_06-05-58.txt).
    Si el patrón no aparece, usa la fecha de modificación en OneLake."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})", file_info.name)
    if m:
        return m.group(1), m.group(2).replace("-", ":")
    dt = datetime.fromtimestamp(file_info.modifyTime / 1000)
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")


def split_row(line):
    """Divide por | y descarta los bordes vacíos del pipe inicial/final
    (Column1 y Column34 en el M)."""
    parts = [p.strip() for p in line.split("|")]
    return parts[1:-1] if len(parts) > 2 else parts


def parsear_archivo(file_info, exec_date):
    """Parsea el TXT con pipes (equivale a "Transform file" + PromoteHeaders del M).
    Devuelve (df_crudo, n_rechazadas). Las filas desalineadas por pipes en el
    contenido se cuarentenan en Files/.../rejects para auditoría."""
    log(f"  Leyendo archivo: {file_info.name}")
    lines = spark.sparkContext.textFile(file_info.path)

    # Table.Skip(1): quitar la primera línea (separador) + filtrar líneas de guiones
    body = (lines.zipWithIndex()
                 .filter(lambda t: t[1] > 0)
                 .map(lambda t: t[0])
                 .filter(lambda l: "-------" not in l))

    header_line = body.first()
    raw_names = split_row(header_line)
    n_cols = len(raw_names)
    log(f"  Layout detectado: {n_cols} columnas")

    # SAP repite el encabezado "Tiempo Tratamiento EM": la segunda es la unidad de
    # medida (UN/TO/KG) y se descarta después, igual que el Column34 del M.
    col_names, seen = [], {}
    for i, name in enumerate(raw_names):
        if name == "":
            name = f"Column{i + 2}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        col_names.append(name)

    parsed = (body.filter(lambda l: l != header_line)   # quita encabezados repetidos por página
                  .map(lambda l: (l, split_row(l))))
    data_rdd = parsed.filter(lambda t: len(t[1]) == n_cols).map(lambda t: t[1])
    reject_lines = parsed.filter(lambda t: len(t[1]) != n_cols).map(lambda t: t[0]).take(1000)

    if reject_lines:
        reject_path = f"{base_path}/Files/SAP/ZMM_MD04/rejects/{exec_date}_{file_info.name}"
        notebookutils.fs.put(reject_path, "\n".join(reject_lines), True)
        log(f"  AVISO: {len(reject_lines)} filas desalineadas (pipes en el contenido) "
            f"cuarentenadas en: {reject_path}")
    else:
        log("  Sin filas desalineadas")

    schema = StructType([StructField(x, StringType(), True) for x in col_names])
    df = spark.createDataFrame(data_rdd, schema)

    # Descartar la columna duplicada de unidad de medida (Column34 en el M)
    df = df.drop("Tiempo Tratamiento EM_1")

    # Validación temprana: si el layout del archivo cambió, fallar con mensaje claro
    required = ["Centro", "Planif. Nec", "Proveedor", "Nombre del Proveedor", "Material",
                "Material Description", "Material Proveedor", "Ind. ABC", "Pedido", "Posición",
                "Unidad Med", "Tipo Conf.", "Referencia", "Fecha Reprog", "Excepcion",
                "Estrategia Lib", "Fecha Entrada Necesidad", "Status Msg", "Fecha Pedido",
                "Fecha Entrega Pedido", "Fecha Embarque", "Fecha Planta TC", "Cantidad",
                "Precio Neto", "Por", "Mon", "Stock Centro Disp", "Ubicación", "Family",
                "ROP", "Plazo Entrega Previo", "Tiempo Tratamiento EM"]
    missing = [x for x in required if x not in df.columns]
    assert not missing, f"Columnas faltantes en el archivo: {missing}. Encontradas: {df.columns}"

    return df, len(reject_lines)

