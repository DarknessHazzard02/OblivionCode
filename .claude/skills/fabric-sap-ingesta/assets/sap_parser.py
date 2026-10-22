"""
sap_parser.py — núcleo de lectura de archivos SAP para la ingesta a Fabric.

Este módulo NO depende de Spark ni de Fabric: trabaja sobre texto y sobre
openpyxl. Así se prueba en local contra `Sample files/` antes de desplegar
nada, que es la Fase 1 del playbook (`COMO-HACER-UN-TABLERO.md`).

El mismo código se pega en el notebook `sap_carga_01_archivos`.

Hereda de `sap_zmm_md04` (Fabric) el parser de listas ALV: los reportes de SAP
son de ancho fijo con marco de pipes, y las líneas que se desalinean no traen
un pipe adentro sino la línea corrida unos caracteres. Ver `alinear_por_posicion`.
"""

import re
import unicodedata
from datetime import datetime

# Cuántos caracteres puede correrse un pipe respecto al encabezado antes de
# darse por perdido. Heredado de sap_zmm_md04.
TOLERANCIA_PIPES = 3

# ---------------------------------------------------------------------------
# Configuración por fuente
# ---------------------------------------------------------------------------
# `patron_fecha` saca FILE_DATE del NOMBRE del archivo, no de su contenido.
# Cada fuente trae el suyo porque no coinciden entre sí.
FUENTES = {
    "MB52": {
        "carpeta": "Files/SAP/MB52/MB52_CopyJob",
        "tabla": "SAP_MB52",
        "formato": "alv",
        "encabezado_empieza": "|Material",
        # SDDnnn_MATERIAL_LIST_MB52_2026-08-13_02-25-59.csv
        "patron_fecha": r"_(\d{4})-(\d{2})-(\d{2})_",
        "orden_fecha": ("Y", "M", "D"),
        "extensiones": (".csv", ".txt"),
    },
    "ZSD49N": {
        "carpeta": "Files/SAP/ZSD49N/ZSD49N_CopyJob",
        "tabla": "SAP_ZSD49N",
        "formato": "alv",
        "encabezado_empieza": "|  Reason for",
        # SDDnnn_PD_REPORT_2026-08-13_12-56-13AM.csv
        "patron_fecha": r"_(\d{4})-(\d{2})-(\d{2})_",
        "orden_fecha": ("Y", "M", "D"),
        "extensiones": (".csv", ".txt"),
    },
    "COOIS_HEADERS": {
        "carpeta": "Files/SAP/COOIS/COOIS Header",
        "tabla": "SAP_COOIS_HEADERS",
        "formato": "xlsx",
        # COOIS_Headers_08.13.2026.xlsx  ->  MM.DD.YYYY
        "patron_fecha": r"_(\d{2})\.(\d{2})\.(\d{4})",
        "orden_fecha": ("M", "D", "Y"),
        "extensiones": (".xlsx", ".xls"),
    },
    "COOIS_COMPONENTS": {
        "carpeta": "Files/SAP/COOIS/COOIS Components",
        "tabla": "SAP_COOIS_COMPONENTS",
        "formato": "xlsx",
        "patron_fecha": r"_(\d{2})\.(\d{2})\.(\d{4})",
        "orden_fecha": ("M", "D", "Y"),
        "extensiones": (".xlsx", ".xls"),
    },
}

# ---------------------------------------------------------------------------
# Nombres de columna
# ---------------------------------------------------------------------------
# SAP corta los encabezados al ancho de la columna, así que muchos llegan
# mutilados. El mapeo es EXPLÍCITO: lo que no está aquí conserva su nombre de
# SAP (solo saneado para Delta) y el cargador lo reporta al final, para que el
# diccionario se complete a propósito y no por descuido.
#
# Los marcados MEDIDO salieron de mirar el contenido real, no de interpretar el
# encabezado. Los marcados POR CONFIRMAR siguen pendientes de validar en SAP.
MAPEO_COLUMNAS = {
    "MB52": {
        "Plnt": "Plant",
        "SLoc": "Storage_Location",
        "Description": "Storage_Location_Description",
        "BUn": "Base_Unit",
        "MTyp": "Material_Type",
        "Matl Grou": "Material_Group",          # truncado de "Matl Group"
        "Qual.Insp.": "Quality_Inspection",
        "Value in QualInsp.": "Value_Quality_Inspection",
        "Value BlockedStock": "Value_Blocked",
        "Stock in tfr": "Stock_In_Transfer",
        "Value in Stock Tfr": "Value_In_Transfer",
        # `Unrestricted` y `Blocked` se quedan igual: ya se llaman como deben.
        # Blocked es la columna que la ingesta anterior descartaba.
    },
    "ZSD49N": {
        "Sales Orde": "Sales_Order_Date",       # MEDIDO: trae fechas (01.08.2025)
        "Custom.nic": "Customer_Nickname",
        "Ordered qt": "Ordered_Quantity",
        # `Planned Pr` parece "Planned Price" por el encabezado, pero MEDIDO
        # trae FECHAS. Se queda con el nombre truncado en vez de asignarle uno
        # que contradice su contenido: un nombre equivocado es peor que uno feo.
        "Billing da": "Billing_Date",
        "Prog Expor": "Prog_Export",
        "Depart.por": "Departure_Port",
        "Actual Dep": "Actual_Departure",
        "Cust. Requ": "Customer_Requested_Date",
        "Deliv.crea": "Delivery_Created",
        "Delivery q": "Delivery_Quantity",
        "Distr.chan": "Distribution_Channel",
        "Good issue": "Goods_Issue",
        "Invoiced q": "Invoiced_Quantity",
        "Price Tota": "Price_Total",
        "Ship-to pa": "Ship_To_Party",
        "ETA Whouse": "ETA_Warehouse",
        "Hierachy 1": "Hierarchy_1",            # el typo es de SAP
        "Hierachy 2": "Hierarchy_2",
    },
    "COOIS_HEADERS": {},      # los XLSX ya traen nombres completos
    "COOIS_COMPONENTS": {},
}

# ZSD49N repite el nombre `Confirmed` en dos columnas. Se desambiguan por
# POSICIÓN, que es lo único estable: un mapeo por nombre renombraría las dos.
# MEDIDO: la 17 trae cantidades (3.500,000) y la 18 una bandera X.
# PENDIENTE de verificar contra el layout de ZSD49N en SAP.
DUPLICADOS_POR_POSICION = {
    "ZSD49N": {17: "Confirmed_quantity", 18: "Confirmed_flag"},
}

# Columnas que NO están en el mapeo porque su nombre de SAP ya está completo y
# es correcto. Se listan a propósito: así "sin mapear" queda solo con lo que
# nadie ha mirado todavía, en vez de repetir 36 nombres que ya están bien.
NOMBRE_YA_CORRECTO = {
    "MB52": {"Material", "Material Description", "Unrestricted", "Value Unrestricted",
             "Blocked", "Returns"},
    "ZSD49N": {"Reason for", "Credit stat.", "Cust Nr", "Plant", "Customer PO#",
               "Custom.part number", "Delivery Block", "Note", "Order", "Item",
               "Family", "Model", "Material", "Invoice#", "Delivery", "Incoterms",
               "Incoterm2 of SO", "Booking", "Vessel", "Container", "ETD",
               "ETA Port", "Dest. port", "Custom. Name", "Date", "Deliv.status",
               "Invoice Block", "Price List"},
    "COOIS_HEADERS": {"Plant", "Order", "Material Number", "Description",
                      "Actual start time", "Firming indicator",
                      "Order quantity (GMEIN)", "Quantity Delivered (GMEIN)",
                      "Confirmed quantity (GMEIN)", "Basic start date",
                      "Basic finish date", "Start date (sched)",
                      "Scheduled finish date", "Confirmed finish date",
                      "Actual finish date", "Deletion flag", "Family", "Entered by"},
    "COOIS_COMPONENTS": {"Requirement date", "Order", "Pegged requirement", "Material",
                         "Material Description", "Shortage (EINHEIT)",
                         "Open Quantity (EINHEIT)", "Confirmed quantity (EINHEIT)",
                         "Vendor", "Requirement Quantity (ERFME)", "Item ID",
                         "Intra material", "Supplier", "Planned order", "Backflush",
                         "Alternative BOM", "Bill of material", "Item component list",
                         "Requirement Quantity (EINHEIT)", "Quantity withdrawn (EINHEIT)",
                         "Plant", "Storage Location", "Assembly", "Reservation item"},
}

# Columnas truncadas por SAP que siguen SIN resolver: el nombre está cortado y
# todavía no se ha confirmado qué son. Se cargan con su nombre truncado y el
# cargador las reporta en cada corrida hasta que alguien las cierre.
POR_CONFIRMAR = {
    "ZSD49N": {
        "Planned Pr": "el encabezado sugiere 'Price' pero MEDIDO trae fechas",
        "Deadline D": "truncado; 100% vacía en el extracto",
        "Deadline C": "truncado; 100% vacía en el extracto",
        "Actual pre": "truncado; MEDIDO trae fechas",
        "Customer P": "truncado; MEDIDO trae números tipo identificador",
        "Customer r": "truncado; MEDIDO trae fechas",
        "Shipping b": "truncado",
        "Shipping d": "truncado",
    },
}

# ---------------------------------------------------------------------------
# Qué columnas se convierten a número
# ---------------------------------------------------------------------------
# DECLARADO A MANO a propósito. La detección automática de `es_columna_numerica`
# solo sirve para PROPONER: al correrla sobre ZSD49N propuso convertir `Cust Nr`,
# `Order`, `Item`, `Delivery` y `Price List`, que son identificadores. Convertir
# `0000305439` a número lo deja en `305439` y deja de casar con SAP.
#
# La regla: se convierte lo que se SUMA (cantidades y valores). Todo lo que
# identifica algo se queda como texto, aunque parezca número.
#
# Solo aplica al formato `alv`: los XLSX ya llegan con sus tipos desde openpyxl.
COLUMNAS_NUMERICAS = {
    "MB52": [
        "Unrestricted", "Value_Unrestricted",
        "Quality_Inspection", "Value_Quality_Inspection",
        "Blocked", "Value_Blocked",              # las que la ingesta vieja tiraba
        "Stock_In_Transfer", "Value_In_Transfer",
        "Returns",
    ],
    "ZSD49N": [
        "Ordered_Quantity", "Confirmed_quantity",
        "Delivery_Quantity", "Invoiced_Quantity",
        "Price_Total",
    ],
    "COOIS_HEADERS": [],        # XLSX: openpyxl ya entrega números
    "COOIS_COMPONENTS": [],
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
# Parser de listas ALV (MB52, ZSD49N)
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
    repite 227 veces y SDDnnn 320. Todas esas repeticiones, los títulos de
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
