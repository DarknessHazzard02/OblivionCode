# Author: Haz
"""
generar_demo.py — escribe fuentes INVENTADAS en demo/source/ (mismas columnas que las reales) y arma data/.

Nada de aquí viene de Oracle, AX ni del Excel: clientes, órdenes, items y montos son aleatorios
con semilla fija. Ver demo/CONTRATO.md.

    python generar_demo.py
"""
import csv
import datetime as dt
import os
import random
import sys

import generar_datos as gd

AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(AQUI, "demo", "source")
MAN = os.path.join(SRC, "manual")
rnd = random.Random(20261020)

CORTE = dt.date.today()
N_LINEAS = 1600

DIVS = [("DIV-IMD", "IMD", "1", 0.48), ("DIV-HVACR", "HVACR", "1", 0.37), ("DIV-GMS", "GMS", "0", 0.10),
        ("DIV-ELIM", "Eliminations", "0", 0.05)]
ORGS = [("C71", 0.14), ("C74", 0.14), ("C75", 0.12), ("C78", 0.07), ("C79", 0.12), ("RVT-MS", 0.18), ("D72", 0.10),
        ("C72", 0.03), ("C76", 0.05), ("H05", 0.02), ("C80", 0.03)]
PRODLINES = ["N56.63 Misc", "N56.63 4P", "N48.55 4P", "N48.3Ph 4/6P", "N56.VSPD", "N48.55 Jet Pump", "VSPD.Gen3",
             "PART.Prt P2", "PART.Prt", "NEMA.Demo 140T", "NEMA.Demo 180T", "MISC.Fan", "MISC.Capacitor",
             "DRIVES.Demo", "COMPRESSOR.Demo", "IHP.Demo", "ROTOR.Demo", ""]
PLANNERS = ["Northgate Planner A", "Planta Norte Planner B", "Planner Demo C", "Planner Demo D", ""]
RESP_ORIGEN = ["CMS IO Plant Northgate", "CMS IO Plant Valle Alto", "CMS IO Plant PLT1", "CMS IO Plant Asia",
               "CMS IO Distribution Riverton", "FG Items Purchased by CMC", "AMS IO Plant Rio Claro", "Buyout", ""]
GRUPOS = [("HVAC OEM", 0.3), ("HVAC Tier1 OEM", 0.05), ("Distribution", 0.3), ("Industrial OEM", 0.25), ("Pool & Spa", 0.1)]
ESTATUS = [("AWAITING_SHIPPING", 0.62), ("BOOKED", 0.18), ("AWAITING_FULFILLMENT", 0.06), ("ENTERED", 0.04),
           ("INVOICE_HOLD", 0.03), ("PICKED", 0.07)]
CLIENTES = [f"Cliente Demo {i:02d}" for i in range(1, 41)]
HOLDS = ["CTR Credit Check Hold - Manual", "CTR Line Pick & Ship Hold(CMS)", "CTR Quality Hold (CMS)",
         "CTR Test Apvl Engineering(CMS)", "CTR Pre-Ship Requirements", "CTR Price Approval Hold (CMS)",
         "CTR Hold For Customer Approval", "CTR 1000 LB Ship Line Hold", "Credit Check Failure"]
CPU_METODOS = ["CUSTOMER PICKUP-LTL-STD SERVICE", "CUSTOMER PICKUP-Parcel-STD SERVICE", "CUSTOMER PICKUP-Truck-STD SERVICE"]
PICK = ["Backordered", "Ready to Release", "Released to Warehouse", "Staged/Pick Confirmed"]

# Columnas del Open Orders (detailtab A:BA, sin Cost) — mismas que el archivo real
OO_COLS = ["Mkt DIV", "Org", "Group", "Reporting Market Class", "Market Class", "Market Class Descr", "Market Channel",
           "Market Channel Descr", "Sub Market", "Sub Market Descr", "Market Manager", "Market Manager Descr", "Customer #",
           "Customer", "Ship To Location", "Ship To Cty St Zip Ctry", "SalesChannel", "Business Unit", "Division",
           "Request Date", "Schedule Ship Date", "PERIOD", "MONTH", "MONTH Requested", "Promise Date", "Date Ordered",
           "OrderStatus", "Order Type", "Category", "Order", "LineNo", "Cust PO", "Item", "Item Number", "Item Desc",
           "Discount Symbol", "Ordered Quantity", "Unit Selling Price", "Total $", "Planner", "ProdLine", "POM (sales)",
           "FHP/IHP", "ProdLine (sales)", "Ecom Channel", "Site Number", "Salesman Code", "Salesperson", "Delivery",
           "Carrier", "Shipment Method"]


def elegir(pares):
    x, acum = rnd.random(), 0.0
    for v, p in pares:
        acum += p
        if x <= acum:
            return v
    return pares[-1][0]


def escribir(nombre, cab, filas):
    ruta = os.path.join(SRC, nombre)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cab)
        w.writerows(filas)


def periodo(ssd):
    if ssd < CORTE.replace(day=1):
        return "PAST DUE_PRIORMONTH"
    if ssd < CORTE:
        return "PAST DUE_CURRENT"
    return "CURRENT" if ssd.month == CORTE.month else "FUTURE"


def item_demo(pl):
    r = rnd.random()
    if r < 0.05:
        return f"X63-DEMO-{rnd.randint(100, 999)}"
    if r < 0.10:
        return f"2023{rnd.randint(1000, 9999)}-100"
    if r < 0.16:
        return str(rnd.randint(700000, 799999))
    return f"DEMO-{rnd.randint(1000, 1400)}"


def lineas():
    out = []
    orden_n = 7100000
    while len(out) < N_LINEAS:
        orden_n += rnd.randint(1, 40)
        org = elegir(ORGS)
        div = elegir([((d, n), p) for d, n, _i, p in DIVS])
        cliente = rnd.choice(CLIENTES)
        orden = f"SO-{orden_n}" if org == "RVT-MS" else str(orden_n)
        for ln in range(1, rnd.choice([1, 1, 1, 2, 3]) + 1):
            pl = rnd.choice(PRODLINES)
            ssd = CORTE + dt.timedelta(days=rnd.randint(-75, 110))
            req = ssd + dt.timedelta(days=rnd.randint(-12, 15))
            prom = ssd + dt.timedelta(days=rnd.randint(-5, 5)) if rnd.random() < 0.7 else None
            qty = rnd.choice([1, 2, 5, 10, 20, 40, 60, 100, 150])
            precio = round(rnd.uniform(25, 950), 2)
            item = item_demo(pl)
            out.append({
                "Mkt DIV": div[0], "Org": org, "Group": elegir(GRUPOS), "Customer #": f"D{abs(hash(cliente)) % 90000:05d}",
                "Customer": cliente, "Division": rnd.choice(["FSD", "IMD"]), "Request Date": req.isoformat(),
                "Schedule Ship Date": ssd.isoformat(), "PERIOD": periodo(ssd), "MONTH": ssd.strftime("%b-%y"),
                "Promise Date": prom.isoformat() if prom else "",
                "Date Ordered": (ssd - dt.timedelta(days=rnd.randint(3, 60))).isoformat(),
                "OrderStatus": elegir(ESTATUS), "Order Type": "Standard", "Order": orden, "LineNo": str(ln),
                "Item": item, "Item Number": item, "Item Desc": f"Motor demo {item[-4:]}",
                "Ordered Quantity": qty, "Unit Selling Price": precio, "Total $": round(qty * precio, 2),
                "Planner": rnd.choice(PLANNERS), "ProdLine": pl, "POM (sales)": rnd.choice(RESP_ORIGEN),
                "FHP/IHP": rnd.choice(["FHP", "IHP"]), "ProdLine (sales)": (pl.split(" ")[0] or "000.UNK"),
                "Delivery": f"DLV{rnd.randint(10000, 99999)}" if rnd.random() < 0.4 else "",
                "Shipment Method": rnd.choice(["LTL", "Parcel", "Truck"]),
            })
    return out[:N_LINEAS]


def main():
    os.makedirs(MAN, exist_ok=True)
    oo = lineas()
    escribir("Open_Orders.csv", OO_COLS, [[r.get(c, "") for c in OO_COLS] for r in oo])

    pares = sorted({(r["Org"], r["Item Number"]) for r in oo})
    oh = [(o, i, rnd.choice([0, 0, 5, 20, 60, 150, 400])) for o, i in pares if rnd.random() < 0.55 and o != "RVT-MS"]
    mitad = len(oh) // 2
    cab_oh = ["ORGANIZATION_CODE", "XXCT_ITEM_NUMBER", "ONHAND", "EXTRACT_DATE", "SUBINVENTORY_NAME", "ITEM_TYPE", "INVENTORY_ITEM_STATUS_CODE"]
    escribir("On_Hand_P_FG.csv", cab_oh, [[o, i, q, CORTE.isoformat(), "FG", "FG", "Active"] for o, i, q in oh[:mitad]])
    escribir("On_Hand_TFR_FG.csv", cab_oh, [[o, i, q, CORTE.isoformat(), "TFR", "FG", "Active"] for o, i, q in oh[mitad:]])
    escribir("OnHand_D72_FG.csv", ["ORGANIZATION_CODE", "XXCT_ITEM_NUMBER", "ON_HAND", "EXTRACT_DATE", "SUBINVENTORY_NAME", "ITEM_TYPE", "INVENTORY_ITEM_STATUS_CODE"],
             [["D72", i, rnd.choice([10, 40, 120]), CORTE.isoformat(), "FG", "FG", "Active"] for o, i in pares if o == "D72" and rnd.random() < 0.4])
    escribir("Shipment_Status_On_Hand.csv", ["ORGANIZATION_CODE", "XXCT_ITEM_NUMBER", "ON_HAND", "EXTRACT_DATE", "SUBINVENTORY_NAME", "ITEM_TYPE", "INVENTORY_ITEM_STATUS_CODE"],
             [[o, i, rnd.choice([5, 10]), CORTE.isoformat(), "STAGE", "FG", "Active"] for o, i in pares if o == "C79" and rnd.random() < 0.2])
    escribir("AX_Inventory.csv", ["Item Number", "Posted Quantity", "Physical reserved", "Available physical"],
             [[i, rnd.choice([20, 80, 300]), "", ""] for o, i in pares if o == "RVT-MS" and rnd.random() < 0.5])

    escribir("In_Transit.csv", ["TO_ORGANIZATION_CODE", "XXCT_ITEM_NUMBER", "QUANTITY_SUM", "EXPECTED_DELIVERY_DATE", "SUPPLY_TYPE_CODE"],
             [[o, i, rnd.choice([10, 50, 200]), (CORTE + dt.timedelta(days=rnd.randint(2, 20))).isoformat(), "SHIPMENT"]
              for o, i in pares if o in ("C79", "C80", "C78") and rnd.random() < 0.25])
    escribir("AX_In_Transit.csv", ["ORGANIZATION_CODE", "XXCT_ITEM_NUMBER", "ONHAND", "EXTRACT_DATE", "ITEM_TYPE", "SUBINVENTORY_NAME", "INVENTORY_ITEM_STATUS_CODE"],
             [["RVT-MS", i, rnd.choice([10, 60]), CORTE.isoformat(), "FG", "TRANSIT", "Active"] for o, i in pares if o == "RVT-MS" and rnd.random() < 0.15])

    no_sth = [r for r in oo if r["Org"] != "RVT-MS"]
    escribir("Shipment_Status.csv", ["ORDER_LINE_SHIPMENT", "ORDER_NUMBER", "LINE_SHIPMENT2", "SCHEDULE_STATUS", "STATUS", "PICK_STATUS", "ACTUAL_SHIPMENT_DATE"],
             [[f'{r["Order"]}|{r["LineNo"]}', r["Order"], f'{r["LineNo"]}.1', "SCHEDULED", "Open", rnd.choice(PICK), ""]
              for r in no_sth if rnd.random() < 0.7])
    sth = sorted({r["Order"] for r in oo if r["Org"] == "RVT-MS"})
    escribir("Open_Shipment.csv", ["Shipment #", "Ship to City", "Order #", "Status", "Customer PO #", "ITEMID", "Customer Item / Catalog",
                                   "Qty Released to Ship", "Picked Qty", "Shipment Value", "Days in Process"],
             [[f"SH{rnd.randint(1000, 9999)}", "Ciudad Demo", o, rnd.choice(["Open", "Picked", "In process"]), "", "", "", 1, 0, 0, rnd.randint(0, 9)]
              for o in sth if rnd.random() < 0.5])
    escribir("AX_SO_On_Hold.csv", ["Sales order", "Created date", "Name", "Hold reason code", "On hold", "CSR Comments"],
             [[o, CORTE.isoformat(), "Cliente demo", rnd.choice(["Credit hold", "CSR review", "Pricing"]), "", ""]
              for o in sth if rnd.random() < 0.12])
    ordenes = sorted({(r["Order"], r["LineNo"], r["Customer"]) for r in no_sth})
    escribir("CTR_Order_Holds.csv", ["Warehouse", "Order Number", "Line Number", "Order Type", "Customer Name", "Hold Type", "Extended Price"],
             [["W-DEMO", o, l, "Standard", c, rnd.choice(HOLDS), 0] for o, l, c in ordenes if rnd.random() < 0.08])
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
             [["Org demo", r["Item Number"], r["Order"], r["LineNo"], r["Org"],
               rnd.choice(["Customer Pick Up", "1000 LB Hold", "Prepay & Add", "Third Party Billing"])]
              for r in no_sth if r["Org"] in ("C74", "C75") and rnd.random() < 0.15])

    # ---- Captura manual (lo que en el Excel vive en Sheet2, Executive Summary Reference y Bridge)
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
    items = sorted({r["Item Number"] for r in oo if r["Item Number"].startswith("DEMO-")})
    escribir("manual/item_responsabilidad.csv", ["item", "responsabilidad"],
             [[i, rnd.choice(["CMS IO Plant Northgate", "CMS IO Plant PLT1", "CMS IO Plant Valle Alto"])] for i in rnd.sample(items, 12)])
    pd_lineas = [r for r in oo if r["PERIOD"].startswith("PAST DUE")]
    muestra = rnd.sample(pd_lineas, 14)
    aprob = ["Aprobador Demo 1", "Aprobador Demo 2"]
    motivos = ["Canadá: responsabilidad asignada por el equipo de Canadá", "Planta: proveedor asignado por el cliente",
               "Planta: no se puede embarcar desde Mesa Verde", "Modelo phase-out: responsabilidad del cliente"]
    ajustes = [[r["Order"], r["LineNo"], r["Item Number"], rnd.choice(["Customer/Commercial", "Intransit/Logistic", "CMS IO Plant Valle Alto"]),
                rnd.choice(motivos), rnd.choice(aprob), (CORTE - dt.timedelta(days=rnd.randint(0, 20))).isoformat()] for r in muestra[:10]]
    ajustes.append(["9999999", "1", "DEMO-0000", "Customer/Commercial", "Línea que ya no existe (prueba del aviso)", aprob[0], CORTE.isoformat()])
    escribir("manual/ajustes_responsabilidad.csv", ["order", "line", "item", "responsabilidad", "motivo", "aprobado_por", "fecha"], ajustes)
    escribir("manual/d12_intransit_manual.csv", ["item", "cantidad"],
             [[i, rnd.choice([10, 30])] for o, i in pares if o == "D72" and rnd.random() < 0.15])
    escribir("manual/razon_sitio.csv", ["order", "line", "razon", "comentario"],
             [[r["Order"], r["LineNo"], "WITNESS", "Prueba testigo con el cliente"] for r in muestra[10:14]])

    # Primera pasada: con el corte calculado se arman el Bridge y el historial inventados
    escribir("manual/bridge_manual.csv", ["concepto", "division", "monto", "nota"], [])
    escribir("manual/historial.csv", ["fecha", "division", "past_due", "un_dia"], [])
    filas, *_ = gd.calcular(SRC, CORTE)
    bruto, limpio = {}, {}
    for f in filas:
        if f["incluida"]:
            if f["pd_origen"] != gd.NO_PD:
                bruto[f["division"]] = bruto.get(f["division"], 0) + f["total"]
            if f["pd"] in gd.PD_SET:
                limpio[f["division"]] = limpio.get(f["division"], 0) + f["total"]
    bridge = []
    for div, b in sorted(bruto.items()):
        bridge.append(["MARKETING", div, round(b * rnd.uniform(1.01, 1.04), 2), "Número de Daily Sales Management (inventado)"])
        bridge.append(["AFILIADAS_MX", div, round(-b * rnd.uniform(0.004, 0.01), 2), "Afiliadas México (inventado)"])
    escribir("manual/bridge_manual.csv", ["concepto", "division", "monto", "nota"], bridge)

    # Caminata hacia atrás desde el corte de hoy: el historial termina donde empieza el dato calculado
    hist, d = [], CORTE - dt.timedelta(days=1)
    nivel = dict(limpio)
    while d > CORTE - dt.timedelta(days=150):
        if d.weekday() < 5:
            for div in sorted(nivel):
                nivel[div] = max(0, nivel[div] * rnd.uniform(0.965, 1.035))
                hist.append([d.isoformat(), div, round(nivel[div], 2), round(nivel[div] * rnd.uniform(0.01, 0.04), 2)])
        d -= dt.timedelta(days=1)
    hist.sort()
    escribir("manual/historial.csv", ["fecha", "division", "past_due", "un_dia"], hist)

    return gd.main(["--source", SRC, "--fecha", CORTE.isoformat(), "--out", os.path.join(AQUI, "data")])


if __name__ == "__main__":
    sys.exit(main())
