"""Sube los items de Fabric a una rama nueva usando la Git Data API.

No se usa un clon local a propósito: el repo tiene nombres de item que Windows
no puede crear (espacios al final, `&#32;`), el checkout queda incompleto y un
`git add -A` en ese estado borraría cientos de archivos. La API trabaja sobre
el árbol de git directamente, sin working tree.
"""

import sys as _sys
_sys.exit("push_items.py es OBSOLETO: usa la Git Data API (404 ), apunta a "
          "repo-fabric-anterior (ya no existe) y a una carpeta de otra maquina. Usa push_git.py.")

import base64
import json
import subprocess
import sys
from pathlib import Path

REPO = "<org>/<repo-fabric>"
BASE_BRANCH = "fabric"
NUEVA_RAMA = "ingesta-sap-mb52-zsd49n-coois"
ORIGEN = Path(r"<carpeta del proyecto>")

def gh(*args, entrada=None):
    r = subprocess.run(["gh", *args], capture_output=True, text=True,
                       encoding="utf-8", input=entrada, shell=True)
    if r.returncode:
        sys.exit(f"ERROR gh {' '.join(args[:3])}\n{r.stderr[:600]}")
    return json.loads(r.stdout) if r.stdout.strip().startswith(("{", "[")) else r.stdout

# 1. Punta de la rama base
ref = gh("api", f"repos/{REPO}/git/ref/heads/{BASE_BRANCH}")
base_sha = ref["object"]["sha"]
commit = gh("api", f"repos/{REPO}/git/commits/{base_sha}")
base_tree = commit["tree"]["sha"]
print(f"{BASE_BRANCH} esta en {base_sha[:7]}, arbol {base_tree[:7]}")

# 2. Un blob por archivo
archivos = sorted(p for p in ORIGEN.rglob("*") if p.is_file())
print(f"{len(archivos)} archivos a subir")

entradas = []
for p in archivos:
    contenido = p.read_bytes()
    # Por stdin, no como argumento: en Windows la linea de comandos se corta
    # y el notebook base64 pasa de 30 KB.
    blob = gh("api", "-X", "POST", f"repos/{REPO}/git/blobs", "--input", "-",
              entrada=json.dumps({
                  "content": base64.b64encode(contenido).decode(),
                  "encoding": "base64",
              }))
    ruta = p.relative_to(ORIGEN).as_posix()
    entradas.append({"path": ruta, "mode": "100644", "type": "blob",
                     "sha": blob["sha"]})
    print(f"  {blob['sha'][:7]}  {ruta}")

# 3. Árbol nuevo sobre el existente: solo agrega, no toca lo demás
tree = gh("api", "-X", "POST", f"repos/{REPO}/git/trees", "--input", "-",
          entrada=json.dumps({"base_tree": base_tree, "tree": entradas}))
print(f"arbol nuevo {tree['sha'][:7]}")

MENSAJE = """Ingesta SAP a Fabric: MB52, ZSD49N y COOIS

Copy Job (on-prem -> OneLake) + notebook cargador comun + un pipeline por
fuente, clonados de ZMM_MD04_PIPELINE_CI.

Que resuelve:
- MB52 recupera las columnas Blocked y Value BlockedStock, que la ingesta
  actual (SAP_MB52_CI_NB) descarta en su select de 19 columnas.
- ZSD49N y COOIS entran a Fabric por primera vez con esta cadena.

Los archivos SDDnnn y SDDnnn no son CSV: son listas ALV de ancho fijo con marco
de pipes, paginadas, que repiten el encabezado 227 y 314 veces. El parser se
hereda de sap_zmm_md04, incluida la realineacion de filas corridas.

Decisiones:
- Copy Jobs en Binary, no DelimitedText: el parser depende de la posicion
  exacta de los pipes y un round-trip de texto delimitado puede moverla; un
  XLSX pasado por DelimitedText se corrompe.
- Columnas numericas declaradas a mano. La deteccion automatica proponia
  convertir Cust Nr = 0000305439, que quedaria en 305439.
- Valor ilegible -> NULL y contado, nunca cero.
- Las tablas se recrean cada dia (DROP + CREATE), por decision del negocio.
- Calendarios apagados hasta validar la primera corrida.

Pendiente: 8 columnas de ZSD49N truncadas por SAP siguen sin confirmarse; el
notebook las reporta en cada corrida.
"""

# 4. Commit y rama
nuevo = gh("api", "-X", "POST", f"repos/{REPO}/git/commits", "--input", "-",
           entrada=json.dumps({"message": MENSAJE, "tree": tree["sha"],
                               "parents": [base_sha]}))
print(f"commit {nuevo['sha'][:7]}")

gh("api", "-X", "POST", f"repos/{REPO}/git/refs", "--input", "-",
   entrada=json.dumps({"ref": f"refs/heads/{NUEVA_RAMA}", "sha": nuevo["sha"]}))
print(f"rama {NUEVA_RAMA} creada")
