"""
verificar_notebook.py — prueba el notebook de Fabric SIN Fabric.

El notebook `sap_carga_01_archivos` tiene dos mitades: uno que necesita Spark
(leer del lakehouse, escribir Delta) y otro que es Python puro (configuración,
parser, mapeo de nombres, conversión de números). Esta segunda mitad es donde
vive el riesgo real, y se puede probar aquí contra `Sample files/`.

Sirve para tres cosas:
  1. Detectar errores de sintaxis antes de subir el notebook a Fabric.
  2. Confirmar que el parser del notebook da los MISMOS conteos que el de
     `sap_parser.py`, que ya se validó. Las dos copias se separan con el tiempo.
  3. Verificar la conversión de números y de FILE_DATE con datos reales.

Uso:  python verificar_notebook.py
"""

import re
import sys
from pathlib import Path

BASE = Path(__file__).parent
NOTEBOOK = (BASE / "fabric" / "SAP_TRANSACIONES" / "_COMUN" /
            "sap_carga_01_archivos.Notebook" / "notebook-content.py")
MUESTRAS = BASE / "Sample files"

ARCHIVOS = {
    "MB52": "SDDnnn_MATERIAL_LIST_MB52_2026-08-13_02-25-59.csv",
    "ZSD49N": "SDDnnn_PD_REPORT_2026-08-13_12-56-13AM.csv",
    "COOIS_HEADERS": "COOIS_Headers_08.13.2026.xlsx",
    "COOIS_COMPONENTS": "COOIS_Components_08.13.2026.xlsx",
}

# Conteos confirmados con `perfilar_fuentes.py`. Si el parser
# cambia y estos números se mueven, se rompe la prueba a propósito.
ESPERADO = {
    "MB52": {"filas": 13377, "columnas": 17, "encabezados": 227},
    "ZSD49N": {"filas": 17250, "columnas": 56, "encabezados": 314},
}

def celdas_de_codigo(texto):
    """Extrae las celdas de código del notebook de Fabric, junto con su tipo.

    La PARAMETERS CELL se devuelve marcada para poder saltarla: define
    `fuente = "MB52"` como default y, si se ejecuta, pisa la fuente que esta
    prueba quiere probar. En Fabric ese default lo sobreescribe el pipeline.
    """
    trozos = re.split(r"^# (CELL|PARAMETERS CELL|MARKDOWN|METADATA) \*+\s*$",
                      texto, flags=re.M)
    celdas = []
    for i in range(1, len(trozos) - 1, 2):
        tipo, cuerpo = trozos[i], trozos[i + 1]
        if tipo in ("METADATA", "MARKDOWN") or not cuerpo.strip():
            continue
        celdas.append((tipo, cuerpo))
    return celdas

def main():
    if not NOTEBOOK.exists():
        sys.exit(f"No encuentro el notebook: {NOTEBOOK}")

    texto = NOTEBOOK.read_text(encoding="utf-8")
    celdas = celdas_de_codigo(texto)
    print(f"Notebook: {len(texto):,} chars, {len(celdas)} celdas de código")

    fallos = []

    for fuente, nombre_archivo in ARCHIVOS.items():
        print("=" * 74)
        print(fuente)

        # Namespace con lo mínimo para que corran las celdas puras. Las celdas
        # que tocan Spark se saltan: aquí solo se prueba el parser.
        ns = {"fuente": fuente, "force_reload": False, "recrear_tabla": True,
              "__name__": "notebook"}
        try:
            exec("import json, re, unicodedata\nfrom datetime import datetime", ns)
            ns["log"] = lambda m: None
            ns["TOLERANCIA_PIPES"] = 3
            for tipo, celda in celdas:
                # La celda de parámetros define fuente="MB52" como default y
                # pisaría la fuente que se está probando.
                if tipo == "PARAMETERS CELL":
                    continue
                # Solo las que no necesitan Spark ni notebookutils.
                if any(t in celda for t in ("mssparkutils", "spark.", "F.lit",
                                            "StructType", "import pandas")):
                    continue
                exec(celda, ns)
        except Exception as e:
            fallos.append(f"{fuente}: la celda no ejecuta — {type(e).__name__}: {e}")
            print(f"  FALLO al ejecutar: {type(e).__name__}: {e}")
            continue

        cfg = ns["FUENTES"][fuente]
        ruta = MUESTRAS / nombre_archivo

        # FILE_DATE
        fecha = ns["fecha_de_archivo"](nombre_archivo)
        print(f"  FILE_DATE: {fecha}")
        if fecha is None:
            fallos.append(f"{fuente}: el patrón de fecha no casó con {nombre_archivo}")

        if cfg["formato"] != "alv":
            print("  (XLSX: el parser vive en pandas, se prueba en Fabric)")
            continue

        # Parser ALV
        texto_archivo = ruta.read_text(encoding="utf-8-sig", errors="replace")
        columnas, filas, diag, cuarentena = ns["parsear_alv"](texto_archivo)
        esp = ESPERADO[fuente]
        print(f"  filas: {len(filas):,} (esperado {esp['filas']:,})")
        print(f"  columnas: {len(columnas)} (esperado {esp['columnas']})")
        print(f"  encabezados repetidos: {diag['encabezados_repetidos']} "
              f"(esperado {esp['encabezados']})")
        print(f"  cuarentena: {len(cuarentena)}")

        if len(filas) != esp["filas"]:
            fallos.append(f"{fuente}: {len(filas)} filas, se esperaban {esp['filas']}")
        if len(columnas) != esp["columnas"]:
            fallos.append(f"{fuente}: {len(columnas)} columnas, se esperaban {esp['columnas']}")
        if cuarentena:
            fallos.append(f"{fuente}: {len(cuarentena)} filas en cuarentena")

        # Nombres finales
        finales, repes = ns["nombres_finales"](columnas)
        if repes:
            fallos.append(f"{fuente}: nombres duplicados tras el mapeo: {repes}")
        print(f"  nombres duplicados tras el mapeo: {repes or 'ninguno'}")

        # Conversión de números sobre la columna declarada
        numericas = ns["COLUMNAS_NUMERICAS"][fuente]
        for col in numericas[:2]:
            j = finales.index(col)
            crudos = [f[j] for f in filas if str(f[j]).strip()][:400]
            malos = [c for c in crudos if ns["num_europeo"](c) is None]
            muestra = [(c, ns["num_europeo"](c)) for c in crudos[:3]]
            print(f"  {col}: {muestra}  ilegibles en 400: {len(malos)}")
            if malos:
                fallos.append(f"{fuente}.{col}: {len(malos)} valores no parsean, ej {malos[:3]}")

    print("=" * 74)
    if fallos:
        print(f"FALLOS ({len(fallos)}):")
        for f in fallos:
            print(f"  - {f}")
        sys.exit(1)
    print("TODO OK — el parser del notebook coincide con lo medido.")

if __name__ == "__main__":
    main()
