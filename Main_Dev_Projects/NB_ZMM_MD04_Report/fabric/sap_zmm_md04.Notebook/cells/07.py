
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

def delta_exists(path):
    """True si hay una tabla Delta en la ruta. Revisa el _delta_log en vez de
    atrapar cualquier error al leer: un error de permisos o de red no debe
    confundirse con "la tabla no existe"."""
    return notebookutils.fs.exists(f"{path}/_delta_log")

log_path = f"{base_path}/Tables/{log_table}"

# Los nombres con punto ("Planif. Nec", "Ind. ABC") requieren backticks al referenciarlos
c = lambda name: F.col(f"`{name}`")


def a_nombres_delta(df):
    """Delta rechaza espacios y puntos en los nombres de columna al CREAR una
    tabla ('Nombre del Proveedor' -> 'Nombre_del_Proveedor').

    El notebook original escribía con los nombres tal cual porque su destino,
    SAP_ZMM_MD04_TEST, ya existía con column mapping activado y los toleraba.
    Al apuntar a una tabla nueva la escritura truena.

    Se renombra en vez de activar column mapping: es la misma convención que
    ya siguen las demás tablas del lakehouse (pgi_raw_*), y no deja la tabla
    atada a una propiedad especial de Delta.
    """
    prohibidos = "[ ,;{}()" + chr(92) + "n" + chr(92) + "t=.]+"
    return df.toDF(*[re.sub(prohibidos, "_", x).strip("_") for x in df.columns])


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


# Tolerancia, en caracteres, para emparejar los pipes de una línea con los del
# encabezado. Ver alinear_por_posicion().
TOLERANCIA_PIPES = 3


def split_row(line):
    """Divide por | y descarta los bordes vacíos del pipe inicial/final
    (Column1 y Column34 en el M)."""
    parts = [p.strip() for p in line.split("|")]
    return parts[1:-1] if len(parts) > 2 else parts


def posiciones_pipes(line):
    return [i for i, ch in enumerate(line) if ch == "|"]


def alinear_por_posicion(line, pos_enc, tol=TOLERANCIA_PIPES):
    """Recupera una línea cuyos pipes no coinciden en número con el encabezado.

    El reporte de SAP es de ANCHO FIJO: en las líneas sanas los pipes caen en
    las mismas posiciones de carácter que en el encabezado. Las que se
    "desalinean" no traen un pipe dentro del texto, como parecía: traen la
    línea entera CORRIDA uno o dos caracteres a partir de cierto punto, porque
    el contenido tiene un tabulador que SAP contó con un ancho y escribió con
    otro.

    Ejemplo real (2026-08-06, material 77412093610.Q):
        encabezado:  ... 132, 168, 177, 188, 197, 208 ...
        la línea:    ... 133, 169, 178, 189, 198, 209 ...

    Como el desfase es de pocos caracteres, cada corte del encabezado se
    empareja con el pipe más cercano de la línea. Si alguno no tiene pareja
    dentro de la tolerancia, o dos cortes caen en el mismo pipe, se devuelve
    None y la fila se cuarentena como antes: es preferible perderla a meterla
    con las columnas recorridas.

    Devuelve (campos, recuperada) — recuperada = True si hubo que realinear.
    """
    pos = posiciones_pipes(line)

    # Si la línea trae el mismo NÚMERO de pipes que el encabezado, se parte por
    # los suyos y ya. No importa si están corridos: los cortes siguen cayendo
    # entre los mismos campos.
    #
    # (Exigir que las posiciones coincidieran exactamente mandó 39 filas sanas
    # a la cuarentena en la corrida del 2026-08-06. El número de campos es el
    # criterio bueno; la posición solo sirve para rescatar a las que fallan.)
    if len(pos) == len(pos_enc):
        return [line[a + 1:b].strip() for a, b in zip(pos, pos[1:])], False

    cortes = []
    for p in pos_enc:
        cercanos = [q for q in pos if abs(q - p) <= tol]
        if not cercanos:
            return None, False
        cortes.append(min(cercanos, key=lambda q: abs(q - p)))
    if len(set(cortes)) != len(cortes):
        return None, False

    return [line[a + 1:b].strip() for a, b in zip(cortes, cortes[1:])], True


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

    # SAP repite el encabezado "Tiempo Tratamiento EM". Es un error del reporte:
    # la PRIMERA sí es el tiempo de tratamiento en días, la SEGUNDA es la unidad
    # en que está expresado el Precio Neto (UN / TO / KG / ...).
    #
    # El M anterior la tiraba como "Column34" y por eso los montos salían
    # inflados: si la Cantidad viene en KG y el precio es por TO, hay que
    # dividir entre 1000 antes de multiplicar. Aquí se conserva como
    # `Unidad_Precio` (ver más abajo).
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

    # El archivo es de ANCHO FIJO: en las líneas sanas los pipes caen en las
    # mismas posiciones que en el encabezado. Las que no, suelen venir corridas
    # uno o dos caracteres (un tabulador en el contenido), y se pueden
    # recuperar emparejando cada corte con el pipe más cercano.
    pos_enc = posiciones_pipes(header_line)
    parsed = (body.filter(lambda l: l != header_line)   # quita encabezados repetidos por página
                  .map(lambda l: (l,) + alinear_por_posicion(l, pos_enc)))

    buenas = parsed.filter(lambda t: t[1] is not None and len(t[1]) == n_cols).cache()
    data_rdd = buenas.map(lambda t: t[1] + ["Sí" if t[2] else "No"])
    n_realineadas = buenas.filter(lambda t: t[2]).count()
    if n_realineadas:
        log(f"  {n_realineadas} filas venían corridas y se recuperaron alineando "
            f"por posición (quedan marcadas en Fila_Realineada)")

    reject_lines = (parsed.filter(lambda t: t[1] is None or len(t[1]) != n_cols)
                          .map(lambda t: t[0]).take(1000))

    if reject_lines:
        reject_path = f"{base_path}/Files/SAP/ZMM_MD04/rejects/{exec_date}_{file_info.name}"
        notebookutils.fs.put(reject_path, "\n".join(reject_lines), True)
        log(f"  AVISO: {len(reject_lines)} filas desalineadas (pipes en el contenido) "
            f"cuarentenadas en: {reject_path}")
    else:
        log("  Sin filas desalineadas")

    schema = StructType([StructField(x, StringType(), True)
                         for x in col_names + ["Fila_Realineada"]])
    df = spark.createDataFrame(data_rdd, schema)

    # La segunda "Tiempo Tratamiento EM" es la unidad del precio. NO se descarta:
    # sin ella no se puede valuar la línea cuando la unidad del PO es distinta.
    if "Tiempo Tratamiento EM_1" in df.columns:
        df = df.withColumnRenamed("Tiempo Tratamiento EM_1", "Unidad_Precio")
    else:
        # El reporte dejó de repetir el encabezado. Que no truene, pero que se vea.
        log("  AVISO: el encabezado ya no repite 'Tiempo Tratamiento EM'. "
            "Unidad_Precio queda vacía y los montos no se van a poder convertir.")
        df = df.withColumn("Unidad_Precio", F.lit(None).cast("string"))

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

