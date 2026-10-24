# Author: Haz
"""
generar_contrato.py — arma el contrato del tablero para el Portal BI con datos 100 % INVENTADOS desde cero.

1. Escribe en una carpeta temporal las fuentes del tablero (mismas columnas que las reales) con
   valores al azar y semilla fija: clientes ficticios (FABRIKAM HVAC SYSTEMS...), items CM-000001, órdenes,
   montos, planeadores y aprobadores inventados. Nada parte de un corte real. Lo único que se
   conserva son las reglas del cálculo: códigos de org, divisiones, product lines y holds.
2. Corre sobre ellas el cálculo del tablero (calculo.py en el portal; ../generar_datos.py en local).
3. Escribe meta.json y dashboard.json sin nombres de archivos de origen.

    python build/generar_contrato.py [carpeta_salida]
    (salida por default: data/dashboard/ en el portal, data_portal/ en local)
"""
import csv
import datetime as dt
import importlib
import json
import os
import random
import shutil
import sys
import tempfile

BUILD = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(BUILD)
EN_PORTAL = os.path.exists(os.path.join(BUILD, "calculo.py"))
CALCULO = os.path.join(BUILD, "calculo.py") if EN_PORTAL else os.path.join(RAIZ, "generar_datos.py")
SALIDA = sys.argv[1] if len(sys.argv) > 1 else (
    os.path.join(RAIZ, "data", "dashboard") if EN_PORTAL else os.path.join(RAIZ, "data_portal"))

rnd = random.Random(20261022)
CORTE = dt.date.today()
N_LINEAS = 1600

# Catálogos que usa el cálculo para asignar responsabilidad y sitio: son reglas, no datos de clientes
DIVS = [("DIV-IMD", "IMD", "1", 0.48), ("DIV-HVACR", "HVACR", "1", 0.37), ("DIV-GMS", "GMS", "0", 0.10),
        ("DIV-ELIM", "Eliminations", "0", 0.05)]
ORGS = [("C71", 0.14), ("C74", 0.14), ("C75", 0.12), ("C78", 0.07), ("C79", 0.12), ("RVT-MS", 0.18), ("D72", 0.10),
        ("C72", 0.03), ("C76", 0.05), ("H05", 0.02), ("C80", 0.03)]
PRODLINES = ["N56.63 Misc", "N56.63 4P", "N48.55 4P", "N48.3Ph 4/6P", "N56.VSPD", "N48.55 Jet Pump", "VSPD.Gen3",
             "PART.Prt P2", "PART.Prt", "NEMA.Std 140T", "NEMA.Std 180T", "MISC.Fan", "MISC.Capacitor",
             "DRIVES.Std", "COMPRESSOR.Std", "IHP.Std", "ROTOR.Std", ""]
# El cálculo lee el sitio del inicio del nombre del planeador ("Northgate…", "Planta Norte…")
PLANEADORES = ["Northgate Laura Mendez", "Planta Norte Daniel Ortiz", "Sofia Rivas", "Marco Salas", ""]
RESP_ORIGEN = ["CMS IO Plant Northgate", "CMS IO Plant Valle Alto", "CMS IO Plant PLT1", "CMS IO Plant Asia",
               "CMS IO Distribution Riverton", "FG Items Purchased by CMC", "AMS IO Plant Rio Claro", "Buyout", ""]
GRUPOS = [("HVAC OEM", 0.3), ("HVAC Tier1 OEM", 0.05), ("Distribution", 0.3), ("Industrial OEM", 0.25), ("Pool & Spa", 0.1)]
ESTATUS = [("AWAITING_SHIPPING", 0.62), ("BOOKED", 0.18), ("AWAITING_FULFILLMENT", 0.06), ("ENTERED", 0.04),
           ("INVOICE_HOLD", 0.03), ("PICKED", 0.07)]
CLIENTES = ["FABRIKAM HVAC SYSTEMS", "NORTHWIND AIR SOLUTIONS", "ADVENTURE WORKS PUMPS", "TAILSPIN FLUID POWER", "WIDE WORLD COMPRESSORS", "LITWARE INDUSTRIAL", "PROSEWARE CONTROLS", "ALPINE SKI HOUSE EQUIPMENT", "LUCERNE CLIMATE", "TREY RESEARCH LABS", "FOURTH COFFEE EQUIPMENT", "BLUE YONDER AERO", "WINGTIP MOTION", "SOUTHRIDGE POOL & SPA", "HUMONGOUS MACHINES", "CONSOLIDATED FANS", "RELECLOUD COOLING", "VANARSDEL APPLIANCES", "A. DATUM AUTOMATION", "MUNSON REFRIGERATION", "LAMNA MEDICAL DEVICES", "TAILWIND TRADERS", "GRAPHIC MOTION WORKS", "WOODGROVE WATER", "COHO AGRITECH", "MARGIE AIR MOVERS", "BELLOWS VENTILATION", "FABRIKAM RESIDENCES HVAC", "NORTHWIND DISTRIBUTION", "CONTOSO SPARE PARTS", "ADATUM POOL SYSTEMS", "PROSEWARE DRIVES", "LITWARE BLOWERS", "WIDE WORLD FANS", "TAILSPIN CHILLERS", "LUCERNE HEAT PUMPS", "TREY INDUSTRIAL OEM", "BLUE YONDER MOTORS", "WINGTIP ROOFTOP UNITS", "SOUTHRIDGE PUMPS"]
HOLDS = ["CTR Credit Check Hold - Manual", "CTR Line Pick & Ship Hold(CMS)", "CTR Quality Hold (CMS)",
         "CTR Test Apvl Engineering(CMS)", "CTR Pre-Ship Requirements", "CTR Price Approval Hold (CMS)",
         "CTR Hold For Customer Approval", "CTR 1000 LB Ship Line Hold", "Credit Check Failure"]
CPU_METODOS = ["CUSTOMER PICKUP-LTL-STD SERVICE", "CUSTOMER PICKUP-Parcel-STD SERVICE", "CUSTOMER PICKUP-Truck-STD SERVICE"]
PICK = ["Backordered", "Ready to Release", "Released to Warehouse", "Staged/Pick Confirmed"]

OO_COLS = ["Mkt DIV", "Org", "Group", "Reporting Market Class", "Market Class", "Market Class Descr", "Market Channel",
           "Market Channel Descr", "Sub Market", "Sub Market Descr", "Market Manager", "Market Manager Descr", "Customer #",
           "Customer", "Ship To Location", "Ship To Cty St Zip Ctry", "SalesChannel", "Business Unit", "Division",
           "Request Date", "Schedule Ship Date", "PERIOD", "MONTH", "MONTH Requested", "Promise Date", "Date Ordered",
           "OrderStatus", "Order Type", "Category", "Order", "LineNo", "Cust PO", "Item", "Item Number", "Item Desc",
           "Discount Symbol", "Ordered Quantity", "Unit Selling Price", "Total $", "Planner", "ProdLine", "POM (sales)",
           "FHP/IHP", "ProdLine (sales)", "Ecom Channel", "Site Number", "Salesman Code", "Salesperson", "Delivery",
           "Carrier", "Shipment Method"]
CAB_OH = ["ORGANIZATION_CODE", "XXCT_ITEM_NUMBER", "ONHAND", "EXTRACT_DATE", "SUBINVENTORY_NAME", "ITEM_TYPE",
          "INVENTORY_ITEM_STATUS_CODE"]
CAB_OH2 = ["ORGANIZATION_CODE", "XXCT_ITEM_NUMBER", "ON_HAND", "EXTRACT_DATE", "SUBINVENTORY_NAME", "ITEM_TYPE",
           "INVENTORY_ITEM_STATUS_CODE"]


def elegir(pares):
    x, acum = rnd.random(), 0.0
    for v, p in pares:
        acum += p
        if x <= acum:
            return v
    return pares[-1][0]


def periodo(ssd):
    if ssd < CORTE.replace(day=1):
        return "PAST DUE_PRIORMONTH"
    if ssd < CORTE:
        return "PAST DUE_CURRENT"
    return "CURRENT" if ssd.month == CORTE.month else "FUTURE"


def item_demo():
    # Las formas de item que el cálculo distingue: prefijo X63, año al inicio, número puro y el resto
    r = rnd.random()
    if r < 0.05:
        return f"X63-CM-{rnd.randint(100, 999)}"
    if r < 0.10:
        return f"2023{rnd.randint(1000, 9999)}-100"
    if r < 0.16:
        return str(rnd.randint(900000, 999999))
    return f"CM-{rnd.randint(1, 400):06d}"


def lineas():
    out, orden_n = [], 9100000
    while len(out) < N_LINEAS:
        orden_n += rnd.randint(1, 40)
        org = elegir(ORGS)
        div = elegir([((d, n), p) for d, n, _i, p in DIVS])
        n_cliente = rnd.randrange(len(CLIENTES))
        orden = f"SO-{orden_n}" if org == "RVT-MS" else str(orden_n)
        for ln in range(1, rnd.choice([1, 1, 1, 2, 3]) + 1):
            pl = rnd.choice(PRODLINES)
            ssd = CORTE + dt.timedelta(days=rnd.randint(-75, 110))
            req = ssd + dt.timedelta(days=rnd.randint(-12, 15))
            prom = ssd + dt.timedelta(days=rnd.randint(-5, 5)) if rnd.random() < 0.7 else None
            qty = rnd.choice([1, 2, 5, 10, 20, 40, 60, 100, 150])
            precio = round(rnd.uniform(25, 950), 2)
            item = item_demo()
            out.append({
                "Mkt DIV": div[0], "Org": org, "Group": elegir(GRUPOS), "Customer #": f"C{n_cliente + 1:05d}",
                "Customer": CLIENTES[n_cliente], "Division": rnd.choice(["FSD", "IMD"]), "Request Date": req.isoformat(),
                "Schedule Ship Date": ssd.isoformat(), "PERIOD": periodo(ssd), "MONTH": ssd.strftime("%b-%y"),
                "Promise Date": prom.isoformat() if prom else "",
                "Date Ordered": (ssd - dt.timedelta(days=rnd.randint(3, 60))).isoformat(),
                "OrderStatus": elegir(ESTATUS), "Order Type": "Standard", "Order": orden, "LineNo": str(ln),
                "Item": item, "Item Number": item, "Item Desc": f"Motor MO-{item[-4:]}",
                "Ordered Quantity": qty, "Unit Selling Price": precio, "Total $": round(qty * precio, 2),
                "Planner": rnd.choice(PLANEADORES), "ProdLine": pl, "POM (sales)": rnd.choice(RESP_ORIGEN),
                "FHP/IHP": rnd.choice(["FHP", "IHP"]), "ProdLine (sales)": (pl.split(" ")[0] or "000.UNK"),
                "Delivery": f"DLV-{rnd.randint(10000, 99999)}" if rnd.random() < 0.4 else "",
                "Shipment Method": rnd.choice(["LTL", "Parcel", "Truck"]),
            })
    return out[:N_LINEAS]


def fuentes(src, gd):
    def escribir(nombre, cab, filas):
        ruta = os.path.join(src, nombre)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(cab)
            w.writerows(filas)

    # Los nombres de archivo son los que busca el cálculo; viven solo en la carpeta temporal.
    oo = lineas()
    escribir("Open_Orders.csv", OO_COLS, [[r.get(c, "") for c in OO_COLS] for r in oo])

    pares = sorted({(r["Org"], r["Item Number"]) for r in oo})
    oh = [(o, i, rnd.choice([0, 0, 5, 20, 60, 150, 400])) for o, i in pares if rnd.random() < 0.55 and o != "RVT-MS"]
    mitad = len(oh) // 2
    escribir("On_Hand_P_FG.csv", CAB_OH, [[o, i, q, CORTE.isoformat(), "FG", "FG", "Active"] for o, i, q in oh[:mitad]])
    escribir("On_Hand_TFR_FG.csv", CAB_OH, [[o, i, q, CORTE.isoformat(), "TFR", "FG", "Active"] for o, i, q in oh[mitad:]])
    escribir("OnHand_D72_FG.csv", CAB_OH2,
             [["D72", i, rnd.choice([10, 40, 120]), CORTE.isoformat(), "FG", "FG", "Active"]
              for o, i in pares if o == "D72" and rnd.random() < 0.4])
    escribir("Shipment_Status_On_Hand.csv", CAB_OH2,
             [[o, i, rnd.choice([5, 10]), CORTE.isoformat(), "STAGE", "FG", "Active"]
              for o, i in pares if o == "C79" and rnd.random() < 0.2])
    escribir("AX_Inventory.csv", ["Item Number", "Posted Quantity", "Physical reserved", "Available physical"],
             [[i, rnd.choice([20, 80, 300]), "", ""] for o, i in pares if o == "RVT-MS" and rnd.random() < 0.5])
    escribir("In_Transit.csv", ["TO_ORGANIZATION_CODE", "XXCT_ITEM_NUMBER", "QUANTITY_SUM", "EXPECTED_DELIVERY_DATE", "SUPPLY_TYPE_CODE"],
             [[o, i, rnd.choice([10, 50, 200]), (CORTE + dt.timedelta(days=rnd.randint(2, 20))).isoformat(), "SHIPMENT"]
              for o, i in pares if o in ("C79", "C80", "C78") and rnd.random() < 0.25])
    escribir("AX_In_Transit.csv", ["ORGANIZATION_CODE", "XXCT_ITEM_NUMBER", "ONHAND", "EXTRACT_DATE", "ITEM_TYPE", "SUBINVENTORY_NAME", "INVENTORY_ITEM_STATUS_CODE"],
             [["RVT-MS", i, rnd.choice([10, 60]), CORTE.isoformat(), "FG", "TRANSIT", "Active"]
              for o, i in pares if o == "RVT-MS" and rnd.random() < 0.15])

    no_sth = [r for r in oo if r["Org"] != "RVT-MS"]
    escribir("Shipment_Status.csv", ["ORDER_LINE_SHIPMENT", "ORDER_NUMBER", "LINE_SHIPMENT2", "SCHEDULE_STATUS", "STATUS", "PICK_STATUS", "ACTUAL_SHIPMENT_DATE"],
             [[f'{r["Order"]}|{r["LineNo"]}', r["Order"], f'{r["LineNo"]}.1', "SCHEDULED", "Open", rnd.choice(PICK), ""]
              for r in no_sth if rnd.random() < 0.7])
    sth = sorted({r["Order"] for r in oo if r["Org"] == "RVT-MS"})
    escribir("Open_Shipment.csv", ["Shipment #", "Ship to City", "Order #", "Status", "Customer PO #", "ITEMID", "Customer Item / Catalog",
                                   "Qty Released to Ship", "Picked Qty", "Shipment Value", "Days in Process"],
             [[f"SH-{rnd.randint(1000, 9999)}", "RIVERTON", o, rnd.choice(["Open", "Picked", "In process"]), "", "", "", 1, 0, 0,
               rnd.randint(0, 9)] for o in sth if rnd.random() < 0.5])
    escribir("AX_SO_On_Hold.csv", ["Sales order", "Created date", "Name", "Hold reason code", "On hold", "CSR Comments"],
             [[o, CORTE.isoformat(), CLIENTES[0], rnd.choice(["Credit hold", "CSR review", "Pricing"]), "", ""]
              for o in sth if rnd.random() < 0.12])
    ordenes = sorted({(r["Order"], r["LineNo"], r["Customer"]) for r in no_sth})
    escribir("CTR_Order_Holds.csv", ["Warehouse", "Order Number", "Line Number", "Order Type", "Customer Name", "Hold Type", "Extended Price"],
             [["ALMACEN-EJ", o, l, "Standard", c, rnd.choice(HOLDS), 0] for o, l, c in ordenes if rnd.random() < 0.08])
    escribir("Customer_Pick_Up.csv", ["ORDER_LINE_SHIPMENT3", "ORGANIZATION_CODE", "ORDER_NUMBER", "LINE_SHIPMENT3", "SCHEDULE_SHIP_DATE",
                                      "ORDERED_ITEM", "ORDERED_QUANTITY", "STATUS", "SHIPPING_METHOD", "CUSTOMER", "ORDER_TYPE",
                                      "CATEGORY_NAME", "CATEGORY_TYPE_NAME"],
             [[f'{r["Order"]}|{r["LineNo"]}', r["Org"], r["Order"], r["LineNo"], r["Schedule Ship Date"], r["Item Number"],
               r["Ordered Quantity"], "Open", rnd.choice(CPU_METODOS), r["Customer"], "Standard", "", ""]
              for r in no_sth if rnd.random() < 0.05])
    escribir("Override_SO.csv", ["ORDER_NUMBER", "LINE_NUMBER", "ORDERED_QUANTITY_SUM", "STATUS", "CUSTOMER", "OVERRIDE_ATP_DATE_CODE",
                                 "REQUEST_DATE", "SCHEDULE_SHIP_DATE", "PRODUCTION_LINE", "ORGANIZATION_CODE", "ITEM_NAME"],
             [[r["Order"], r["LineNo"], r["Ordered Quantity"], "Open", r["Customer"], "Y", r["Request Date"], r["Schedule Ship Date"],
               "", r["Org"], r["Item Number"]] for r in no_sth if rnd.random() < 0.02])
    escribir("MEPD.csv", ["Org Name", "Ordered Item", "Order Number", "Line Number", "Ship From Org", "Freight Terms"],
             [["ORG C71", r["Item Number"], r["Order"], r["LineNo"], r["Org"],
               rnd.choice(["Customer Pick Up", "1000 LB Hold", "Prepay & Add", "Third Party Billing"])]
              for r in no_sth if r["Org"] in ("C74", "C75") and rnd.random() < 0.15])

    # ---- Captura manual (catálogos, ajustes aprobados, Bridge e historial)
    escribir("manual/divisiones.csv", ["mkt_div", "division", "incluir_en_pd"], [[d, n, i] for d, n, i, _ in DIVS])
    razones = [(h, "Plant Past Due" if any(x in h for x in ("Quality", "Engineering", "1000 LB")) else "Customer") for h in HOLDS]
    razones += [(m, "Customer") for m in CPU_METODOS]
    razones += [("CREDIT HOLD", "Customer"), ("CSR HOLD", "Customer"), ("Customer/Commercial", "Customer"),
                ("NO", "Plant Past Due"), ("Witness Testing", "Witness"), ("In Stock - waiting on Release", "Others")]
    escribir("manual/razones_categoria.csv", ["razon", "categoria"], razones)
    escribir("manual/freight_terms.csv", ["freight_terms", "responsabilidad"],
             [["Customer Pick Up", "Customer/Commercial"], ["1000 LB Hold", "Plant"], ["Prepay & Add", "Plant"],
              ["Fixed Freight Terms", "Customer/Commercial"], ["Third Party Billing", "Customer/Commercial"]])
    escribir("manual/clientes_customer_commercial.csv", ["customer"], [[c] for c in CLIENTES[:6]])
    escribir("manual/clientes_especiales.csv", ["customer"], [[c] for c in CLIENTES[6:9]])
    items = sorted({r["Item Number"] for r in oo if r["Item Number"].startswith("CM-")})
    escribir("manual/item_responsabilidad.csv", ["item", "responsabilidad"],
             [[i, rnd.choice(["CMS IO Plant Northgate", "CMS IO Plant PLT1", "CMS IO Plant Valle Alto"])] for i in rnd.sample(items, 12)])
    pd_lineas = [r for r in oo if r["PERIOD"].startswith("PAST DUE")]
    muestra = rnd.sample(pd_lineas, 14)
    aprob = ["Paula Herrera", "Jorge Castillo"]
    motivos = ["Responsabilidad asignada por otro equipo", "Planta: proveedor asignado por el cliente",
               "Planta: no se puede embarcar desde ese sitio", "Modelo phase-out: responsabilidad del cliente"]
    ajustes = [[r["Order"], r["LineNo"], r["Item Number"], rnd.choice(["Customer/Commercial", "Intransit/Logistic", "CMS IO Plant Valle Alto"]),
                rnd.choice(motivos), rnd.choice(aprob), (CORTE - dt.timedelta(days=rnd.randint(0, 20))).isoformat()] for r in muestra[:10]]
    ajustes.append(["9999999", "1", "CM-000000", "Customer/Commercial", "Línea que ya no existe (prueba del aviso)", aprob[0], CORTE.isoformat()])
    escribir("manual/ajustes_responsabilidad.csv", ["order", "line", "item", "responsabilidad", "motivo", "aprobado_por", "fecha"], ajustes)
    escribir("manual/d12_intransit_manual.csv", ["item", "cantidad"],
             [[i, rnd.choice([10, 30])] for o, i in pares if o == "D72" and rnd.random() < 0.15])
    escribir("manual/razon_sitio.csv", ["order", "line", "razon", "comentario"],
             [[r["Order"], r["LineNo"], "WITNESS", "Prueba testigo con el cliente"] for r in muestra[10:14]])

    # Primera pasada: con el corte calculado se arman el Bridge y el historial inventados
    escribir("manual/bridge_manual.csv", ["concepto", "division", "monto", "nota"], [])
    escribir("manual/historial.csv", ["fecha", "division", "past_due", "un_dia"], [])
    filas, *_ = gd.calcular(src, CORTE)
    bruto, limpio = {}, {}
    for f in filas:
        if f["incluida"]:
            if f["pd_origen"] != gd.NO_PD:
                bruto[f["division"]] = bruto.get(f["division"], 0) + f["total"]
            if f["pd"] in gd.PD_SET:
                limpio[f["division"]] = limpio.get(f["division"], 0) + f["total"]
    bridge = []
    for div, b in sorted(bruto.items()):
        bridge.append(["MARKETING", div, round(b * rnd.uniform(1.01, 1.04), 2), "Número de ventas diarias (inventado)"])
        bridge.append(["AFILIADAS_MX", div, round(-b * rnd.uniform(0.004, 0.01), 2), "Afiliadas (inventado)"])
    escribir("manual/bridge_manual.csv", ["concepto", "division", "monto", "nota"], bridge)

    # Caminata hacia atrás desde el corte: el historial termina donde empieza el dato calculado
    hist, d, nivel = [], CORTE - dt.timedelta(days=1), dict(limpio)
    while d > CORTE - dt.timedelta(days=150):
        if d.weekday() < 5:
            for div in sorted(nivel):
                nivel[div] = max(0, nivel[div] * rnd.uniform(0.965, 1.035))
                hist.append([d.isoformat(), div, round(nivel[div], 2), round(nivel[div] * rnd.uniform(0.01, 0.04), 2)])
        d -= dt.timedelta(days=1)
    hist.sort()
    escribir("manual/historial.csv", ["fecha", "division", "past_due", "un_dia"], hist)
    return len(oo)


# Nombre genérico de cada fuente (clave del cálculo → es, en), sin nombres de extractos ni pestañas
NOMBRES = {
    "open_orders": ("Órdenes abiertas", "Open orders"), "ship_status": ("Estatus de embarque", "Shipment status"),
    "in_transit": ("Tránsito", "In transit"), "ax_in_transit": ("Tránsito (AX)", "In transit (AX)"),
    "cpu": ("Recoge el cliente", "Customer pick up"), "override": ("Fecha forzada", "Date override"),
    "oh_p": ("Inventario FG (P)", "FG on hand (P)"), "oh_tfr": ("Inventario FG (TFR)", "FG on hand (TFR)"),
    "oh_d12": ("Inventario FG (D72)", "FG on hand (D72)"), "oh_ship": ("Inventario en embarque", "On hand in shipping"),
    "ax_inv": ("Inventario (AX)", "On hand (AX)"), "ax_ship": ("Estatus de embarque (AX)", "Shipment status (AX)"),
    "ax_hold": ("Órdenes en hold (AX)", "Orders on hold (AX)"), "holds": ("Holds de órdenes", "Order holds"),
    "mepd": ("Órdenes con términos de flete", "Orders with freight terms"),
    "item_resp": ("Responsabilidad por item", "Responsibility by item"),
    "ajustes": ("Ajustes de responsabilidad", "Responsibility adjustments"),
    "bridge": ("Bridge", "Bridge"),
}


def limpiar_meta(meta):
    """Sin nombres de archivos de origen: cada fuente queda con un nombre genérico y su clave."""
    meta["fuente"] = "datos inventados (build/generar_contrato.py)"
    meta.pop("semi", None)
    for f in meta["fuentes"]:
        f["nombre"], f["nombre_en"] = NOMBRES.get(f["clave"], (f["nombre"], f["nombre_en"]))
        f["archivo"] = f'{f["clave"]}_demo.csv'
    return meta


def main():
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "demo", "source")
        os.makedirs(os.path.join(src, "manual"))
        # Con la copia junto a demo/source, el cálculo corre en modo demo
        shutil.copy(CALCULO, os.path.join(tmp, "generar_datos.py"))
        sys.path.insert(0, tmp)
        gd = importlib.import_module("generar_datos")
        n = fuentes(src, gd)
        salida_tmp = os.path.join(tmp, "data")
        gd.main(["--source", src, "--fecha", CORTE.isoformat(), "--out", salida_tmp])
        with open(os.path.join(salida_tmp, "meta.json"), encoding="utf-8") as fh:
            meta = limpiar_meta(json.load(fh))
        os.makedirs(SALIDA, exist_ok=True)
        shutil.copy(os.path.join(salida_tmp, "dashboard.json"), os.path.join(SALIDA, "dashboard.json"))
        with open(os.path.join(SALIDA, "meta.json"), "w", encoding="utf-8") as fh:
            json.dump(meta, fh, ensure_ascii=False, indent=1)
        sys.path.remove(tmp)
        sys.modules.pop("generar_datos", None)
    print(f"Inventadas: {n:,} líneas de órdenes -> {SALIDA}")


if __name__ == "__main__":
    main()
