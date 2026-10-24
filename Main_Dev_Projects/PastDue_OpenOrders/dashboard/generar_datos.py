# Author: Haz
"""
generar_datos.py — Past Due Open Orders

Reproduce el archivo "Past Due Open Orders" (pestaña detailtab + macro Orgs_Assignment /
Customerr / ovrwrite / Not_PD + pasos manuales del SOP) y escribe meta.json y dashboard.json
para el tablero. Python estándar, sin pandas.

De dónde lee (en este orden): argumento --source → variable PASTDUE_SOURCE → config.local.json
→ demo/source. Con datos reales escribe en data_real/ (ignorada por git); con demo, en data/.

    python generar_datos.py                    # corte de hoy
    python generar_datos.py --fecha 2026-09-24 # corte de un día concreto
    python generar_datos.py --guardar-historial  # además agrega el día a manual/historial.csv
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
DEMO_SOURCE = os.path.join(AQUI, "demo", "source")

# ============================================================
# REGLAS FIJAS (las que vienen del archivo y de la macro)
# ============================================================
PD_ACTUAL, PD_PREVIO = "PAST DUE CURRENT MONTH", "PAST DUE PRIOR MONTH"
D72_ACTUAL, D72_PREVIO = "D72 PAST DUE CURRENT MONTH", "D72 PAST DUE PRIOR MONTH"
UN_DIA, NO_PD = "1 DAY PAST DUE", "NOT PAST DUE"
PD_SET = {PD_ACTUAL, PD_PREVIO, D72_ACTUAL, D72_PREVIO}

# Responsabilidad (POM sales) -> renglón del Executive Summary
SITIO = {
    "CMS IO Plant Northgate": "Northgate", "CMS IO Plant Valle Alto": "Planta Norte", "CMS IO Plant PLT1": "PLT1",
    "CMS IO Plant PLT2": "PLT2", "CMS IO Plant Asia": "PLT3", "CMS IO Distribution Mesa Verde": "Mesa Verde",
    "CMS IO Plant NLA": "NLA", "CMS IO Distribution Riverton": "RVT", "Intransit/Logistic": "Intransit",
    "Buyout": "Buyout", "Customer/Commercial": "Customer/Commercial", "S&OP": "S&OP",
}
ORDEN_SITIOS = ["Northgate", "Planta Norte", "PLT1", "PLT2", "PLT3", "Mesa Verde", "NLA", "RVT", "Intransit",
                "Buyout", "Customer/Commercial", "S&OP", "Otro", "Sin asignar"]
PLANTAS = {"CMS IO Plant Asia", "CMS IO Plant PLT1", "CMS IO Plant PLT2", "CMS IO Plant Valle Alto", "CMS IO Plant Northgate"}

# Sheet2!Y:Z — días de atraso (sobre Schedule Ship Date) -> rango
RANGOS = [(0, 0, ""), (1, 1, "1"), (2, 5, "2-5"), (6, 15, "6-15"), (16, 30, "16-30"),
          (31, 60, "31-60"), (61, 90, "61-90"), (91, 180, "91-180")]

# Día de gracia: el archivo tiene dos reglas que no coinciden (BL resta 1 día fijo; CE mira la
# fecha de orden con 1-2 días según el día de la semana). Se usa la que explicó el proceso:
# 1 día HÁBIL sobre Schedule Ship Date (si el corte es lunes, cubre viernes, sábado y domingo).
DIAS_GRACIA_HABILES = 1

PRODLINE_PLT2 = {"PART.Prt P2", "VSPD.Cont", "VSPD.Gen3"}
PRODLINE_MTY = {"N56.63 Misc", "N56.63 4/6P", "N56.63 Haz Loc", "N56.63 3Ph 4P", "N56.63 4P",
                "N56.63 3Ph 2P", "N48.55 4P", "N48.3Ph 2P"}
PRODLINE_PLT1 = {"N48.3Ph 2P 2Sp Rtr", "N48.3Ph 4/6P", "N56.VSPD", "N48.55 Jet Pump", "N48.55 2Sp Jet Pump",
                 "N56.63 2P 1Sp", "N56.63 2P 2Sp", "N56.63 2P 2Sp-Timer", "N48.55 Jet Pump Rtr",
                 "VSPD.Gen3 Neptune", "VSPD.Gen3 Neptune H", "DRAFT_IND.CMD"}
PRODLINE_BUYOUT_PREF = ("37", "COMPRESSOR", "CONDENSING", "DRIVES", "PANELS")
PRODLINE_BUYOUT = {"DRAFT_IND.Purch", "VSPD.Kit", "MISC.100mm ECM", "MISC.100 Series BLDC", "MISC.300 Series BLDC",
                   "MISC.700 Series BLDC", "MISC.82mm ECM", "MISC.Avtron", "MISC.Capacitor", "MISC.Compressor",
                   "MISC.ECT", "MISC.Fan", "MISC.Hurst", "MISC.Inverter", "MISC.Jiamusi", "MISC.LSomer",
                   "MISC.Misc", "MISC.Protector", "MISC.Purch", "MISC.Relay"}

# ============================================================
# FUENTES — archivo, nombre, sistema y si es captura manual
# ============================================================
FUENTES = [
    # clave, archivo, es, en, sistema, manual, requerido
    ("open_orders", "Open_Orders.csv", "Open Orders (detailtab)", "Open Orders (detailtab)", "Oracle / AX", False, True),
    ("ship_status", "Shipment_Status.csv", "Shipment Status", "Shipment Status", "Oracle", False, True),
    ("in_transit", "In_Transit.csv", "Intransit", "Intransit", "Oracle", False, True),
    ("ax_in_transit", "AX_In_Transit.csv", "AX Intransit", "AX Intransit", "AX", False, False),
    ("cpu", "Customer_Pick_Up.csv", "Customer Pick Up", "Customer Pick Up", "Oracle", False, True),
    ("override", "Override_SO.csv", "Override SO", "Override SO", "Oracle", False, False),
    ("oh_p", "On_Hand_P_FG.csv", "On-Hand P_FG", "On-Hand P_FG", "Oracle", False, True),
    ("oh_tfr", "On_Hand_TFR_FG.csv", "On-Hand TFR_FG", "On-Hand TFR_FG", "Oracle", False, False),
    ("oh_d12", "OnHand_D72_FG.csv", "On-Hand D72_FG", "On-Hand D72_FG", "Oracle", False, False),
    ("oh_ship", "Shipment_Status_On_Hand.csv", "On-Hand (Shipment Status)", "On-Hand (Shipment Status)", "Oracle", False, False),
    ("ax_inv", "AX_Inventory.csv", "AX Inventory (correo)", "AX Inventory (email)", "AX", False, False),
    ("ax_ship", "Open_Shipment.csv", "AX Shipment Status (Open Shipment)", "AX Shipment Status (Open Shipment)", "AX", False, False),
    ("ax_hold", "AX_SO_On_Hold.csv", "AX Hold (AX SO ON HOLD)", "AX Hold (AX SO ON HOLD)", "AX", False, False),
    ("holds", "CTR_Order_Holds.csv", "Order Holds (CTR)", "Order Holds (CTR)", "Oracle", False, True),
    ("mepd", "MEPD.csv", "MEPD (Sales Orders with Inventory)", "MEPD (Sales Orders with Inventory)", "Oracle", False, False),
    # Captura manual: lo que en el Excel vive en Sheet2, Executive Summary Reference y Bridge
    ("divisiones", "manual/divisiones.csv", "Divisiones de mercado", "Market divisions", "Manual", True, True),
    ("razones", "manual/razones_categoria.csv", "Razón → categoría", "Reason → category", "Manual", True, True),
    ("freight", "manual/freight_terms.csv", "Freight terms → responsabilidad", "Freight terms → responsibility", "Manual", True, False),
    ("cc", "manual/clientes_customer_commercial.csv", "Clientes Customer/Commercial", "Customer/Commercial customers", "Manual", True, False),
    ("especiales", "manual/clientes_especiales.csv", "Clientes especiales", "Special customers", "Manual", True, False),
    ("item_resp", "manual/item_responsabilidad.csv", "Responsabilidad por item (Sheet2)", "Responsibility by item (Sheet2)", "Manual", True, False),
    ("ajustes", "manual/ajustes_responsabilidad.csv", "Ajustes de responsabilidad (Canadá / plantas)", "Responsibility adjustments (Canada / plants)", "Manual", True, False),
    ("d12_transit", "manual/d12_intransit_manual.csv", "D72 tránsito manual", "D72 manual in-transit", "Manual", True, False),
    ("razon_sitio", "manual/razon_sitio.csv", "Razón capturada por sitio", "Reason filled by site", "Manual", True, False),
    ("bridge", "manual/bridge_manual.csv", "Bridge (número de marketing)", "Bridge (marketing number)", "Manual", True, False),
    ("historial", "manual/historial.csv", "Historial diario", "Daily history", "Manual", True, False),
]


# ============================================================
# LECTURA
# ============================================================
def resolver_source(arg):
    if arg:
        return arg, "argumento"
    if os.environ.get("PASTDUE_SOURCE"):
        return os.environ["PASTDUE_SOURCE"], "PASTDUE_SOURCE"
    cfg = os.path.join(AQUI, "config.local.json")
    if os.path.exists(cfg):
        with open(cfg, encoding="utf-8") as f:
            src = json.load(f).get("source")
        if src:
            return src, "config.local.json"
    return DEMO_SOURCE, "demo"


def leer_csv(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


def col(r, *nombres):
    """Primer encabezado que exista (las extracciones no siempre usan el mismo nombre)."""
    for n in nombres:
        if n in r and r[n] != "":
            return r[n]
    return ""


def num(v):
    if v is None:
        return 0.0
    s = str(v).strip().replace(",", "").replace("$", "")
    if not s or s.upper() in ("NULL", "#N/A", "N/A"):
        return 0.0
    neg = (s.startswith("(") and s.endswith(")")) or s.endswith("-") or s.startswith("-")
    s = s.strip("()-")   # SAP/Oracle: (1,234.50) o 1,234.50- o -1234.50
    try:
        n = float(s)
    except ValueError:
        return 0.0
    return -n if neg else n


FORMATOS_FECHA = ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%b-%Y", "%d-%b-%y", "%Y/%m/%d")


def fecha(v):
    s = (v or "").strip()
    if not s or s.upper() == "NULL":
        return None
    s = s.split(" ")[0].split("T")[0]
    for fmt in FORMATOS_FECHA:
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def iso(d):
    return d.isoformat() if d else None


def dia_habil_anterior(d):
    d -= dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def rango(dias):
    for a, b, txt in RANGOS:
        if a <= dias <= b:
            return txt
    return "181+"


def es_numero(s):
    return bool(re.fullmatch(r"\d+(\.\d+)?", s or ""))


# ============================================================
# CÁLCULO
# ============================================================
def calcular(src, corte):
    falta, filas_fuente, leidas = {}, {}, {}
    for clave, archivo, *_resto in FUENTES:
        requerido = _resto[-1]
        ruta = os.path.join(src, archivo)
        if os.path.exists(ruta):
            leidas[clave] = leer_csv(ruta)
            falta[clave] = False
        else:
            leidas[clave] = []
            falta[clave] = requerido
        filas_fuente[clave] = len(leidas[clave])
    if not leidas["open_orders"]:
        raise SystemExit(f"No hay Open_Orders.csv en {src}: sin eso no hay tablero.")

    # --- catálogos manuales
    divisiones = {r["mkt_div"]: r for r in leidas["divisiones"]}
    incluidas = {k for k, r in divisiones.items() if r.get("incluir_en_pd", "").upper() in ("1", "SI", "SÍ", "YES", "Y")}
    nombre_div = {k: r.get("division") or k for k, r in divisiones.items()}
    razon_cat = {r["razon"]: r["categoria"] for r in leidas["razones"]}
    freight_resp = {r["freight_terms"]: r["responsabilidad"] for r in leidas["freight"]}
    clientes_cc = {r["customer"] for r in leidas["cc"]}
    especiales = {r["customer"] for r in leidas["especiales"]}
    item_resp = {r["item"]: r["responsabilidad"] for r in leidas["item_resp"]}

    # --- On-Hand: Oracle (4 queries) + AX (RVT-MS), por organización e item
    onhand = defaultdict(float)
    for clave in ("oh_p", "oh_tfr", "oh_d12", "oh_ship"):
        for r in leidas[clave]:
            onhand[(col(r, "ORGANIZATION_CODE", "Organization Code"), col(r, "XXCT_ITEM_NUMBER", "Xxinv Item Number"))] += \
                num(col(r, "ONHAND", "ON_HAND", "On-Hand"))
    for r in leidas["ax_inv"]:
        posted = col(r, "Posted Quantity")
        total = num(posted) if posted else num(col(r, "Physical reserved")) + num(col(r, "Available physical"))
        if total:
            onhand[("RVT-MS", col(r, "Item Number"))] += total
    oh_item = defaultdict(float)
    for (_, item), q in onhand.items():
        oh_item[item] += q

    # --- Tránsito: Oracle (destino) + AX (RVT-MS) + D72 manual
    transito = defaultdict(float)
    for r in leidas["in_transit"]:
        transito[(col(r, "TO_ORGANIZATION_CODE", "To Organization Code"), col(r, "XXCT_ITEM_NUMBER", "Item Number"))] += \
            num(col(r, "QUANTITY_SUM", "In Transit Qty"))
    for r in leidas["ax_in_transit"]:
        transito[("RVT-MS", col(r, "XXCT_ITEM_NUMBER", "Xxinv Item Number"))] += num(col(r, "ONHAND", "In Transit Qty"))
    for r in leidas["d12_transit"]:
        transito[("D72", r.get("item", ""))] += num(r.get("cantidad"))

    # --- Estatus de embarque, holds, pick up, override, MEPD
    ship = {col(r, "ORDER_LINE_SHIPMENT", "Order Line Shipment"): col(r, "PICK_STATUS", "Pick Status") for r in leidas["ship_status"]}
    ax_ship = {}
    for r in leidas["ax_ship"]:
        ax_ship.setdefault(col(r, "Order #"), col(r, "Status"))
    holds, holds_linea = {}, set()
    for r in leidas["holds"]:
        o = col(r, "Order Number")
        holds.setdefault(o, col(r, "Hold Type"))
        holds_linea.add((o, col(r, "Line Number")))
    ax_hold = {}
    for r in leidas["ax_hold"]:
        etiqueta = col(r, "On hold", "On Hold")
        if not etiqueta:   # SOP: "Credit hold" en el código -> CREDIT HOLD; lo demás -> CSR HOLD
            etiqueta = "CREDIT HOLD" if "credit" in col(r, "Hold reason code").lower() else "CSR HOLD"
        ax_hold.setdefault(col(r, "Sales order"), etiqueta)
    cpu = {}
    for r in leidas["cpu"]:
        cpu.setdefault(col(r, "ORDER_LINE_SHIPMENT3", "Order Line Shipment3"), col(r, "SHIPPING_METHOD", "Shipping Method"))
    override = {f'{col(r, "ORDER_NUMBER", "Order Number")}|{col(r, "LINE_NUMBER", "Line")}' for r in leidas["override"]}
    mepd = {}
    for r in leidas["mepd"]:
        clave = col(r, "Order Number") + col(r, "Line Number") + col(r, "Ordered Item")
        mepd.setdefault(clave, freight_resp.get(col(r, "Freight Terms"), ""))

    ajustes = {}
    for r in leidas["ajustes"]:
        ajustes[(r.get("order", ""), r.get("line", ""), r.get("item", ""))] = r
    razon_sitio = {(r.get("order", ""), r.get("line", "")): r for r in leidas["razon_sitio"]}

    gracia_desde = corte
    for _ in range(DIAS_GRACIA_HABILES):
        gracia_desde = dia_habil_anterior(gracia_desde)

    # --- Paso 1: columnas del Open Orders + fórmulas AZ..CE de detailtab
    filas = []
    for r in leidas["open_orders"]:
        f = {
            "mktdiv": col(r, "Mkt DIV"), "org": col(r, "Org"), "grupo": col(r, "Group"),
            "cliente": col(r, "Customer"), "orden": col(r, "Order"), "linea": col(r, "LineNo"),
            "item": col(r, "Item Number"), "desc": col(r, "Item Desc"), "prodline": col(r, "ProdLine"),
            "prodline_sales": col(r, "ProdLine (sales)"), "planner": col(r, "Planner"),
            "periodo": col(r, "PERIOD"), "estatus_orden": col(r, "OrderStatus"), "fhp": col(r, "FHP/IHP"),
            "division_neg": col(r, "Division"),
            "ssd": fecha(col(r, "Schedule Ship Date")), "req": fecha(col(r, "Request Date")),
            "prom": fecha(col(r, "Promise Date")), "ordenada": fecha(col(r, "Date Ordered")),
            "qty": num(col(r, "Ordered Quantity")), "total": num(col(r, "Total $")),
            "resp_origen": col(r, "POM (sales)"), "delivery": col(r, "Delivery"),
        }
        f["division"] = nombre_div.get(f["mktdiv"], f["mktdiv"])
        f["incluida"] = f["mktdiv"] in incluidas
        p = f["periodo"].upper()
        f["pd_origen"] = (PD_PREVIO if p.startswith("PAST DUE_PRIOR") else PD_ACTUAL) if p.startswith("PAST DUE") else NO_PD
        filas.append(f)

    # BD: inventario de la org menos lo que piden las líneas con SSD anterior (mismo org + item)
    grupos = defaultdict(list)
    for f in filas:
        grupos[(f["org"], f["item"])].append(f)
    for (org, item), fs in grupos.items():
        fs_ord = sorted(fs, key=lambda x: x["ssd"] or dt.date.max)
        acum, previo, i = 0.0, None, 0
        while i < len(fs_ord):
            j, ssd = i, fs_ord[i]["ssd"]
            while j < len(fs_ord) and fs_ord[j]["ssd"] == ssd:
                j += 1
            for k in range(i, j):
                fs_ord[k]["oh_ship"] = onhand.get((org, item), 0.0)
                fs_ord[k]["disp"] = fs_ord[k]["oh_ship"] - acum
            acum += sum(x["qty"] for x in fs_ord[i:j])
            i = j

    for f in filas:
        o, l, item, org = f["orden"], f["linea"], f["item"], f["org"]
        f["oh_all"] = oh_item.get(item, 0.0)
        f["fill"] = min(1.0, f["disp"] / f["qty"]) if f["qty"] else 0.0
        f["oh"] = "YES" if f["fill"] >= 1 else "NO"
        f["ship_status"] = (ax_ship.get(o, "Open") if org == "RVT-MS" else ship.get(f"{o}|{l}", "Ready to Release"))
        f["ax_hold"] = ax_hold.get(o, "")
        f["holds"] = holds.get(o, f["ax_hold"])
        f["on_hold"] = "ON HOLD" if (o in holds or (o, l) in holds_linea or o in ax_hold) else "NOT ON HOLD"
        f["transito_qty"] = transito.get((org, item), 0.0)
        f["transito"] = "NO" if (f["transito_qty"] == 0 and f["qty"] == 0) else ("YES" if f["transito_qty"] >= f["qty"] else "NO")
        # BP contra Request Date; BO contra Promise Date (sin promesa, toma BP)
        f["pd_crd"] = "PAST DUE" if (f["req"] and f["req"] < corte) else "NOT PAST DUE"
        if not f["prom"]:
            f["pd_prom"] = f["pd_crd"]
        else:
            f["pd_prom"] = "PAST DUE" if (f["prom"] < corte and (f["req"] is None or f["prom"] >= f["req"])) else "NOT PAST DUE"
        f["cpu"] = cpu.get(f"{o}|{l}", "")
        f["override"] = "Override SO" if f"{o}|{l}" in override else ""
        f["freight"] = mepd.get(o + l + item, "")
        f["especial"] = f["cliente"] if f["cliente"] in especiales else ""
        f["dias"] = (corte - f["ssd"]).days if (f["ssd"] and f["ssd"] < corte) else 0
        f["rango"] = rango(f["dias"])
        f["oh_int_qty"] = f["disp"] + f["transito_qty"]
        f["oh_int"] = "NO" if (f["oh_int_qty"] == 0 and f["qty"] == 0) else ("YES" if f["oh_int_qty"] >= f["qty"] else "NO")
        f["un_dia"] = bool(f["ssd"] and gracia_desde <= f["ssd"] < corte)
        f["resp"], f["pd"], f["motivo"], f["manual"], f["comentario"] = f["resp_origen"], f["pd_origen"], "", "", ""

    # --- Paso 2: la macro, en el mismo orden que CommandButton1_Click
    for f in filas:
        orgs_assignment(f, item_resp, razon_cat)
    for f in filas:
        customerr(f, incluidas)
    for f in filas:
        ovrwrite(f, clientes_cc)
    for f in filas:
        not_pd(f)

    # --- Paso 3: ajustes manuales (Sheet2 de Canadá/plantas y razón capturada por sitio)
    usados = set()
    for f in filas:
        a = ajustes.get((f["orden"], f["linea"], f["item"]))
        if a:
            usados.add((f["orden"], f["linea"], f["item"]))
            f["resp"] = a.get("responsabilidad") or f["resp"]
            f["manual"] = "ajuste"
            f["comentario"] = a.get("motivo", "")
        rs = razon_sitio.get((f["orden"], f["linea"]))
        if rs and rs.get("razon"):
            f["razon_sitio"] = rs["razon"].upper()
            f["manual"] = f["manual"] or "razon"
            f["comentario"] = f["comentario"] or rs.get("comentario", "")
        f["sitio"] = SITIO.get(f["resp"], "Otro") if f["resp"] else "Sin asignar"

    ajustes_lista = []
    for k, a in ajustes.items():
        ajustes_lista.append([a.get("order"), a.get("line"), a.get("item"), a.get("responsabilidad"), a.get("motivo"),
                              a.get("aprobado_por"), a.get("fecha"), k in usados])

    qc = {
        "filas": len(filas),
        "sin_ssd": sum(1 for f in filas if not f["ssd"]),
        "razon_undefined": sum(1 for f in filas if f["pd"] in PD_SET and f["categoria"] == "Undefined" and f["razon"]),
        "resp_vacia_pd": sum(1 for f in filas if f["pd"] in PD_SET and not f["resp"] and f["incluida"]),
        "mktdiv_sin_catalogo": sorted({f["mktdiv"] for f in filas if f["mktdiv"] not in divisiones}),
        "ajustes_sin_match": sum(1 for k in ajustes if k not in usados),
        "sitio_otro_pd": sum(1 for f in filas if f["pd"] in PD_SET and f["sitio"] in ("Otro", "Sin asignar") and f["incluida"]),
    }
    return filas, leidas, falta, filas_fuente, ajustes_lista, qc


def orgs_assignment(f, item_resp, razon_cat):
    """Module1.Orgs_Assignment, renglón por renglón. f['resp'] es la columna 42 (POM sales)."""
    org, item, pl, plan = f["org"], f["item"], f["prodline"], f["planner"]
    if pl in PRODLINE_PLT2:
        f["resp"] = "CMS IO Plant PLT2"
    if f["resp"] == "CMS IO Plant PLT2" and org == "C71":
        f["org"] = org = "C71-2"
    if pl in PRODLINE_MTY:
        f["resp"] = "CMS IO Plant Valle Alto"
    if pl in PRODLINE_PLT1:
        f["resp"] = "CMS IO Plant PLT1"
    if pl.startswith(PRODLINE_BUYOUT_PREF) or pl in PRODLINE_BUYOUT:
        f["resp"] = "Buyout"
    if item in item_resp:
        f["resp"] = item_resp[item]
    if item.startswith(("X63", "X83", "Z04", "Z05")):
        f["resp"] = "CMS IO Plant Valle Alto"
    if plan.startswith("Northgate"):
        f["resp"] = "CMS IO Plant Northgate"
    if plan.startswith("Planta Norte"):
        f["resp"] = "CMS IO Plant Valle Alto"
    if f["resp"] != "CMS IO Plant Northgate" and "-" in item and pl == "PART.Prt":
        f["resp"] = "CMS IO Plant Valle Alto"
    if org != "C74" and item.startswith(("2020", "2021", "2022", "2023", "2024", "2025", "2026")):
        f["resp"] = "CMS IO Plant Northgate"
    if f["estatus_orden"] == "AWAITING_FULFILLMENT":
        f["resp"] = "CMS IO Distribution Riverton"
    por_org = {"C71": "CMS IO Plant PLT1", "C72": "CMS IO Plant NLA", "C74": "CMS IO Plant Valle Alto",
               "C75": "CMS IO Plant Northgate", "C76": "Buyout"}
    if not f["resp"] and org in por_org:
        f["resp"] = por_org[org]
    if not f["resp"] and pl:   # en la macro la condición de H05/R01 siempre es verdadera (Or); se limpia más abajo
        f["resp"] = "CMS IO Plant Valle Alto" if pl.startswith("NEMA") else "Buyout"
    if not f["resp"] and org not in ("H05", "R01"):
        f["resp"] = "Buyout" if es_numero(item) else "CMS IO Distribution Riverton"
    if org in por_org:
        f["resp"] = por_org[org]
    f["resp"] = {"CMS IO Plant CMD": "CMS IO Plant PLT1", "AMS IO Plant Rio Claro": "Buyout",
                 "FG Items Purchased by CMC": "CMS IO Distribution Riverton"}.get(f["resp"], f["resp"])
    if org in ("H05", "R01"):
        f["resp"] = ""
    if org == "C78" and f["oh"] == "YES":
        f["resp"] = "CMS IO Distribution Mesa Verde"
    if org not in ("C71", "C71-2", "C72", "C74", "C75", "C76", "C78", "RVT-MS") and f["oh"] == "YES":
        f["resp"] = "CMS IO Distribution Riverton"
    if org == "RVT-MS" and f["oh"] == "YES":
        f["resp"] = "CMS IO Distribution Riverton" if f["delivery"] else "S&OP"   # columna 49 = Delivery
    if f["oh"] == "NO" and f["transito"] == "YES":
        f["resp"] = "Intransit/Logistic"
    if org == "D72" and f["pd"] == PD_PREVIO:
        f["pd"] = D72_PREVIO
    if org == "D72" and f["pd"] == PD_ACTUAL:
        f["pd"] = D72_ACTUAL
    if f["estatus_orden"] == "ENTERED" and f["pd"] != NO_PD:
        f["pd"], f["motivo"] = NO_PD, "ENTERED"
    if f["estatus_orden"] == "INVOICE_HOLD":
        f["holds"], f["on_hold"] = "CREDIT HOLD", "ON HOLD"
    # BQ / BR: razón y categoría (fórmulas; ya con el hold de facturación aplicado)
    f["razon"] = f["holds"] or f["cpu"] or (f["freight"] if f["freight"] == "Customer/Commercial" else "") or \
        ("NO" if f["oh"] == "NO" else "")
    f["categoria"] = razon_cat.get(f["razon"], "Undefined")
    f["razon_sitio"] = "CUSTOMER RELATED" if f["categoria"] == "Customer" else "PLANT PAST DUE"
    if f["override"] == "Override SO" and f["division"] == "HVACR":
        f["resp"] = "Customer/Commercial"


def customerr(f, incluidas):
    if f["mktdiv"] not in incluidas:
        return
    if f["razon_sitio"] == "CUSTOMER RELATED" and f["oh"] == "YES":
        f["resp"] = "Customer/Commercial"
    if f["holds"] != "CTR Test Apvl Engineering(CMS)" and f["on_hold"] == "ON HOLD" and f["oh"] == "YES":
        f["resp"] = "Customer/Commercial"


def ovrwrite(f, clientes_cc):
    if f["org"] == "C71-2":
        f["resp"] = "CMS IO Plant PLT2"
    if f["pd"].startswith("PAST DUE") and f["oh"] == "YES" and f["cliente"] in clientes_cc:
        f["resp"] = "Customer/Commercial"
    if f["org"] not in ("C73", "C71", "C71-2", "C74", "C75", "RVT-RET"):
        if f["oh_int"] == "YES" and f["pd"].startswith("PAST DUE") and f["resp"] in PLANTAS:
            f["resp"] = "Intransit/Logistic"


def not_pd(f):
    if f["un_dia"] and f["pd"] in PD_SET:
        f["pd"], f["motivo"] = UN_DIA, "UN_DIA"
    if f["resp"] == "CMS IO Plant NLA" and f["pd"].startswith("PAST DUE"):
        f["pd"], f["motivo"] = NO_PD, "NLA"
    if f["grupo"] == "HVAC Tier1 OEM" and f["pd"].startswith("PAST DUE"):
        f["pd"], f["motivo"] = NO_PD, "HVAC_TIER1"
    if f["estatus_orden"] == "INVOICE_HOLD" and f["pd"].startswith("PAST DUE"):
        f["pd"], f["motivo"] = NO_PD, "INVOICE_HOLD"


# ============================================================
# SALIDA
# ============================================================
COLUMNAS = [
    ("division", "division"), ("mktdiv", "mktdiv"), ("org", "org"), ("grupo", "grupo"), ("cliente", "cliente"),
    ("orden", "orden"), ("linea", "linea"), ("item", "item"), ("desc", "desc"), ("prodline", "prodline"),
    ("prodline_sales", "prodline_sales"), ("ssd", "ssd"), ("req", "req"), ("prom", "prom"), ("ordenada", "ordenada"),
    ("estatus_orden", "estatus_orden"), ("qty", "qty"), ("total", "total"), ("resp_origen", "resp_origen"),
    ("resp", "resp"), ("sitio", "sitio"), ("pd_origen", "pd_origen"), ("pd", "pd"), ("motivo", "motivo"),
    ("pd_crd", "pd_crd"), ("pd_prom", "pd_prom"), ("dias", "dias"), ("rango", "rango"), ("ship_status", "ship_status"),
    ("oh_ship", "oh_ship"), ("oh_all", "oh_all"), ("disp", "disp"), ("oh", "oh"), ("transito_qty", "transito_qty"),
    ("transito", "transito"), ("oh_int", "oh_int"), ("holds", "holds"), ("on_hold", "on_hold"), ("cpu", "cpu"),
    ("override", "override"), ("freight", "freight"), ("razon", "razon"), ("categoria", "categoria"),
    ("razon_sitio", "razon_sitio"), ("especial", "especial"), ("manual", "manual"), ("comentario", "comentario"),
    ("incluida", "incluida"),
]


def valor(v):
    if isinstance(v, dt.date):
        return v.isoformat()
    if isinstance(v, float):
        return round(v, 2)
    return v


def armar(src, modo, corte, guardar_historial):
    filas, leidas, falta, filas_fuente, ajustes_lista, qc = calcular(src, corte)
    ahora = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Historial diario: lo capturado + el punto de este corte (calculado, sin escribir salvo --guardar-historial)
    hist = {}
    for r in leidas["historial"]:
        hist[(r["fecha"], r["division"])] = [r["fecha"], r["division"], num(r.get("past_due")), num(r.get("un_dia"))]
    hoy = defaultdict(lambda: [0.0, 0.0])
    for f in filas:
        if not f["incluida"]:
            continue
        if f["pd"] in PD_SET:
            hoy[f["division"]][0] += f["total"]
        if f["pd"] == UN_DIA:
            hoy[f["division"]][1] += f["total"]
    for div, (pd_, ud) in hoy.items():
        hist[(corte.isoformat(), div)] = [corte.isoformat(), div, round(pd_, 2), round(ud, 2)]
    historial = sorted(hist.values())
    if guardar_historial:
        ruta = os.path.join(src, "manual", "historial.csv")
        with open(ruta, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["fecha", "division", "past_due", "un_dia"])
            w.writerows(historial)
        print(f"  historial actualizado: {ruta}")

    bridge = [[r.get("concepto"), r.get("division"), num(r.get("monto")), r.get("nota", "")] for r in leidas["bridge"]]

    dashboard = {
        "detalle": {"columns": [c for c, _ in COLUMNAS], "rows": [[valor(f.get(k)) for _, k in COLUMNAS] for f in filas]},
        "historial": historial,
        "bridge": bridge,
        "ajustes": ajustes_lista,
    }
    extraidos = []
    fuentes = []
    for clave, archivo, es, en, sistema, manual, _req in FUENTES:
        ruta = os.path.join(src, archivo)
        ext = dt.date.fromtimestamp(os.path.getmtime(ruta)).isoformat() if os.path.exists(ruta) else None
        if ext and not manual:
            extraidos.append(ext)
        fuentes.append({"clave": clave, "nombre": es, "nombre_en": en, "sistema": sistema, "archivo": archivo,
                        "manual": manual, "extraido_el": ext, "filas": filas_fuente[clave], "falta": falta[clave],
                        "existe": os.path.exists(ruta)})
    meta = {
        "generated_at": ahora,
        "demo": modo == "demo",
        "fuente": "datos inventados (generar_demo.py)" if modo == "demo" else f"{modo}",
        "fecha_corte": corte.isoformat(),
        "gracia": {"dias_habiles": DIAS_GRACIA_HABILES, "desde": None},
        "pd_set": sorted(PD_SET),
        "sitios": ORDEN_SITIOS,
        "fuentes": fuentes,
        "qc": qc,
    }
    g = corte
    for _ in range(DIAS_GRACIA_HABILES):
        g = dia_habil_anterior(g)
    meta["gracia"]["desde"] = g.isoformat()
    return meta, dashboard


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source")
    ap.add_argument("--fecha", help="fecha de corte YYYY-MM-DD (default: hoy)")
    ap.add_argument("--out", help="carpeta de salida (default: data/ con demo, data_real/ con datos reales)")
    ap.add_argument("--guardar-historial", action="store_true")
    a = ap.parse_args(argv)
    src, de_donde = resolver_source(a.source)
    modo = "demo" if os.path.abspath(src) == os.path.abspath(DEMO_SOURCE) else "real"
    corte = dt.date.fromisoformat(a.fecha) if a.fecha else dt.date.today()
    out = a.out or os.path.join(AQUI, "data" if modo == "demo" else "data_real")
    print(f"MODO {modo.upper()} · fuente: {src} ({de_donde}) · corte {corte.isoformat()}")
    meta, dashboard = armar(src, modo, corte, a.guardar_historial)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "dashboard.json"), "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, separators=(",", ":"))
    q = meta["qc"]
    print(f"  {q['filas']:,} líneas · escrito en {out}")
    faltan = [x["archivo"] for x in meta["fuentes"] if x["falta"]]
    if faltan:
        print(f"  AVISO: faltan fuentes requeridas: {', '.join(faltan)}")
    if q["ajustes_sin_match"]:
        print(f"  AVISO: {q['ajustes_sin_match']} ajustes manuales no encontraron su línea (orden + línea + item)")
    if q["mktdiv_sin_catalogo"]:
        print(f"  AVISO: Mkt DIV sin renglón en manual/divisiones.csv: {', '.join(q['mktdiv_sin_catalogo'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
