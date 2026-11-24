# Made by: Hazzard
# Updated by Haz: ofuscado para portafolio
"""
sap_parser.py — núcleo de lectura de archivos SAP para la ingesta a Fabric.

Este módulo NO depende de Spark ni de Fabric: trabaja sobre texto y sobre
openpyxl. Así se prueba en local contra archivos de ejemplo inventados antes de
desplegar nada.

El mismo código se pega en el notebook cargador.

Hereda de un notebook de referencia (Fabric) el parser de listas ALV: los reportes de SAP
son de ancho fijo con marco de pipes, y las líneas que se desalinean no traen
un pipe adentro sino la línea corrida unos caracteres. Ver `alinear_por_posicion`.
"""

import re
import unicodedata
from datetime import datetime

# Cuántos caracteres puede correrse un pipe respecto al encabezado antes de
# darse por perdido. Heredado de un notebook de referencia.
TOLERANCIA_PIPES = 3

# ---------------------------------------------------------------------------
# Configuración por fuente
# ---------------------------------------------------------------------------
# `patron_fecha` saca FILE_DATE del NOMBRE del archivo, no de su contenido.
# Cada fuente trae el suyo porque no coinciden entre sí.
FUENTES = {
    # Ejemplo con una transacción estándar. Cada fuente nueva agrega su bloque.
    "MB52": {
        "carpeta": "Files/SAP/MB52",
        "tabla": "SAP_MB52",
        "formato": "alv",
        "encabezado_empieza": "|Material",
        # MATERIAL_LIST_MB52_2026-08-13_02-25-59.csv
        "patron_fecha": r"_(\d{4})-(\d{2})-(\d{2})_",
        "orden_fecha": ("Y", "M", "D"),
        "extensiones": (".csv", ".txt"),
    },
    "COOIS_HEADERS": {
        "carpeta": "Files/SAP/COOIS/Headers",
        "tabla": "SAP_COOIS_HEADERS",
        "formato": "xlsx",
        # COOIS_Headers_08.13.2026.xlsx  ->  MM.DD.YYYY
        "patron_fecha": r"_(\d{2})\.(\d{2})\.(\d{4})",
        "orden_fecha": ("M", "D", "Y"),
        "extensiones": (".xlsx", ".xls"),
    },
}

# ---------------------------------------------------------------------------
# Nombres de columna
# ---------------------------------------------------------------------------
# SAP corta los encabezados al ancho de la columna. El mapeo es EXPLÍCITO: lo
# que no está aquí conserva su nombre (saneado para Delta) y el cargador lo
# reporta, para que el diccionario se complete a propósito y no por descuido.
MAPEO_COLUMNAS = {
    "MB52": {
        "Plnt": "Plant",
        "SLoc": "Storage_Location",
        "BUn": "Base_Unit",
        "MTyp": "Material_Type",
        "Matl Grou": "Material_Group",          # truncado de "Matl Group"
        "Qual.Insp.": "Quality_Inspection",
        "Value in QualInsp.": "Value_Quality_Inspection",
        "Value BlockedStock": "Value_Blocked",
        "Stock in tfr": "Stock_In_Transfer",
        "Value in Stock Tfr": "Value_In_Transfer",
    },
    "COOIS_HEADERS": {},      # los XLSX ya traen nombres completos
}

# Un nombre repetido en dos columnas se desambigua por POSICIÓN (lo único estable).
# Ejemplo: {"<FUENTE>": {17: "Confirmed_quantity", 18: "Confirmed_flag"}}
DUPLICADOS_POR_POSICION = {}

# Nombres de SAP que ya están completos y correctos: así "sin mapear" queda solo
# con lo que nadie ha revisado todavía.
NOMBRE_YA_CORRECTO = {
    "MB52": {"Material", "Material Description", "Unrestricted", "Value Unrestricted",
             "Blocked", "Returns"},
    "COOIS_HEADERS": {"Plant", "Order", "Material Number", "Description",
                      "Basic start date", "Basic finish date"},
}

# Truncados sin resolver: se cargan con su nombre y se reportan en cada corrida.
# Ejemplo: {"<FUENTE>": {"Planned Pr": "el encabezado sugiere 'Price' pero trae fechas"}}
POR_CONFIRMAR = {}

# ---------------------------------------------------------------------------
# Qué columnas se convierten a número
# ---------------------------------------------------------------------------
# DECLARADO A MANO: se convierte lo que se SUMA (cantidades y valores). Lo que
# identifica algo se queda como texto aunque parezca número (`0000305439` como
# número deja de casar con SAP). Solo aplica a `alv`: los XLSX ya traen tipos.
COLUMNAS_NUMERICAS = {
    "MB52": [
        "Unrestricted", "Value_Unrestricted",
        "Quality_Inspection", "Value_Quality_Inspection",
        "Blocked", "Value_Blocked",
        "Stock_In_Transfer", "Value_In_Transfer",
        "Returns",
    ],
    "COOIS_HEADERS": [],
}

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def a_nombre_delta(nombre):
    """Delta rechaza espacios, puntos y otros signos al CREAR una tabla.
    Misma convención que ya usan las demás tablas del lakehouse."""
    limpio = unicodedata.normalize("NFKD", str(nombre))
    limpio = re.sub(r"[ ,;{}()\n\t=.\[\]#/-]+", "_", limpio)
    return re.sub(r"_+", "_", limpio).strip("_")

def fecha_de_archivo(nombre, cfg):
    """FILE_DATE sale del NOMBRE del archivo. None si no coincide el patrón —
    nunca se sustituye por la fecha de hoy: un archivo cuyo nombre no se puede
    leer es un problema que hay que ver, no que rellenar."""
    m = re.search(cfg["patron_fecha"], nombre)
    if not m:
        return None
    partes = dict(zip(cfg["orden_fecha"], m.groups()))
    try:
        return datetime(int(partes["Y"]), int(partes["M"]), int(partes["D"])).date()
    except ValueError:
        return None

RE_NUMERO_EU = re.compile(r"^-?\d{1,3}(\.\d{3})*(,\d+)?-?$|^-?\d+(,\d+)?-?$")

def num_europeo(valor):
    """'2.450,14' -> 2450.14 · '676.000-' -> -676.0 · '946' -> 946.0

    Punto de miles, coma decimal, y el signo negativo AL FINAL (formato SAP).
    Devuelve None si no parsea. Nunca 0: un valor ilegible que se vuelve cero
    se suma a los totales y nadie se entera.
    """
    if valor is None:
        return None
    s = str(valor).strip()
    if not s or not RE_NUMERO_EU.match(s):
        return None
    negativo = s.endswith("-")
    s = s.rstrip("-").lstrip("-")
    if negativo is False and str(valor).strip().startswith("-"):
        negativo = True
    s = s.replace(".", "").replace(",", ".")
    try:
        n = float(s)
    except ValueError:
        return None
    return -n if negativo else n

def es_columna_numerica(valores, umbral=0.95):
    """True si al menos `umbral` de los valores no vacíos parsean como número.

    Solo se usa para PROPONER qué columnas convertir; la lista final se declara
    explícitamente por fuente. Detectar tipos en silencio es adivinar.
    """
    llenos = [v for v in valores if str(v).strip()]
    if not llenos:
        return False
    ok = sum(1 for v in llenos if num_europeo(v) is not None)
    return ok / len(llenos) >= umbral

# ---------------------------------------------------------------------------
# Parser de listas ALV (MB52, ZXX_SALES)
# ---------------------------------------------------------------------------
def posiciones_pipes(linea):
    return [i for i, ch in enumerate(linea) if ch == "|"]

def alinear_por_posicion(linea, pos_enc, tol=TOLERANCIA_PIPES):
    """Recupera una línea cuyos pipes no coinciden en número con el encabezado.

    El reporte es de ancho fijo: en las líneas sanas los pipes caen en las
    mismas posiciones que en el encabezado. Las que se desalinean no traen un
    pipe dentro del texto — traen la línea corrida unos caracteres. Cada corte
    del encabezado se empareja con el pipe más cercano dentro de la tolerancia.

    Si algún corte no encuentra pareja, o dos cortes caen en el mismo pipe, se
    devuelve None y la fila va a cuarentena: es preferible perderla, y contarla,
    a meterla con las columnas recorridas.

    Devuelve (campos, recuperada).
    """
    pos = posiciones_pipes(linea)
    if len(pos) == len(pos_enc):
        return [linea[a + 1:b].strip() for a, b in zip(pos, pos[1:])], False

    cortes = []
    for p in pos_enc:
        cercanos = [q for q in pos if abs(q - p) <= tol]
        if not cercanos:
            return None, False
        cortes.append(min(cercanos, key=lambda q: abs(q - p)))
    if len(set(cortes)) != len(cortes):
        return None, False

    return [linea[a + 1:b].strip() for a, b in zip(cortes, cortes[1:])], True

def _es_separador(linea):
    s = linea.strip()
    return len(s) > 20 and set(s) <= set("-|+")

def parsear_alv(texto, cfg):
    """Convierte una lista ALV en (columnas, filas, diagnostico).

    SAP pagina el reporte y repite el encabezado en cada página — SDDnnn lo
    repite cientos de veces en un archivo grande. Todas esas repeticiones, los títulos de
    página y los separadores se descartan aquí.
    """
    lineas = texto.split("\n")
    prefijo = cfg["encabezado_empieza"]

    idx_enc = [i for i, l in enumerate(lineas) if l.startswith(prefijo)]
    if not idx_enc:
        raise ValueError(
            f"No encontré el encabezado que empieza con {prefijo!r}. "
            f"Primeras líneas del archivo: {lineas[:3]}"
        )

    linea_enc = lineas[idx_enc[0]]
    pos_enc = posiciones_pipes(linea_enc)
    columnas = [c.strip() for c in linea_enc.split("|")[1:-1]]
    repetidos = set(idx_enc)

    filas, cuarentena, recuperadas = [], [], 0
    for i, linea in enumerate(lineas):
        if i in repetidos or not linea.startswith("|") or _es_separador(linea):
            continue
        campos, recup = alinear_por_posicion(linea, pos_enc)
        if campos is None or len(campos) != len(columnas):
            cuarentena.append((i + 1, linea[:120]))
            continue
        if recup:
            recuperadas += 1
        filas.append(campos)

    diagnostico = {
        "lineas_totales": len(lineas),
        "encabezados_repetidos": len(idx_enc),
        "filas_datos": len(filas),
        "filas_recuperadas": recuperadas,
        "filas_cuarentena": len(cuarentena),
        "muestra_cuarentena": cuarentena[:5],
    }
    return columnas, filas, diagnostico

# ---------------------------------------------------------------------------
# Nombres finales de columna
# ---------------------------------------------------------------------------
def nombres_finales(columnas, fuente):
    """Aplica el mapeo explícito, desambigua duplicados por posición y sanea
    para Delta. Devuelve (nombres, sin_mapear)."""
    mapeo = MAPEO_COLUMNAS.get(fuente, {})
    por_pos = DUPLICADOS_POR_POSICION.get(fuente, {})
    ya_correcto = NOMBRE_YA_CORRECTO.get(fuente, set())
    pendientes = POR_CONFIRMAR.get(fuente, {})

    finales, sin_mapear = [], []
    for i, col in enumerate(columnas):
        if i in por_pos:
            finales.append(por_pos[i])
            continue
        if col in mapeo:
            finales.append(mapeo[col])
            continue
        finales.append(a_nombre_delta(col))
        # Solo se reporta lo que nadie ha mirado: ni mapeado, ni marcado como
        # ya correcto, ni anotado como pendiente de confirmar.
        if col.strip() and col not in ya_correcto and col not in pendientes:
            sin_mapear.append(col)

    # Un duplicado que se cuele después del mapeo rompería la escritura en
    # Delta. Se reporta con su posición en vez de renombrarlo en silencio.
    vistos, repes = set(), []
    for i, n in enumerate(finales):
        if n in vistos:
            repes.append((i, n))
        vistos.add(n)

    return finales, sin_mapear, repes
