"""Arma (o rehace) la copia local del Portal BI para ver un cambio antes de aprobarlo.

La copia vive en C:\\<servidor>\<carpeta> sin .git (no se puede
subir nada desde ahi), con su propio venv. Se rehace desde el repo
repo-portal y luego se le montan encima los tableros que todavia NO estan
en el repo (los de _local/tableros.json): sus archivos, su lista blanca, sus
rutas en app.py y su tarjeta en el portal.

Ademas aplica los REEMPLAZOS de _local/reemplazos/: paginas del portal cambiadas
solo en local (por ejemplo, una seccion nueva o el boton de idioma), con la misma
ruta que en el repo. _local/reemplazos.json guarda la huella de la version del
repo de la que salio cada una; si el repo cambio ese archivo, el script se
detiene en vez de tapar el cambio del repo con una version vieja.

Uso:
    python portal_local.py                     # copia desde el arbol de trabajo del repo
    python portal_local.py --rama <rama>       # copia desde una rama (git archive; no hace checkout)
    python portal_local.py --reales            # datos reales de los tableros montados (ver SKILL.md)
    python portal_local.py --servir            # al terminar, levanta el portal en :8080
    python portal_local.py --sin-reemplazos    # el portal tal cual esta en el repo
    python portal_local.py --rebasar <ruta>    # el reemplazo ya se ajusto al repo nuevo: actualiza su huella
    python portal_local.py --sin-zip           # sin rearmar Documents\\Portal-Local.zip
    python portal_local.py --zip <ruta.zip>    # el zip en otro lugar

Cada corrida (salvo --reales o --sin-zip) rearma Documents\\Portal-Local.zip y
sobreescribe el anterior: un zip portable, solo con datos inventados.

Cada corrida deja en la copia iniciar_portal.cmd: levanta el portal en cualquier
equipo Windows con Python, desde la carpeta (o desde el zip descomprimido).

El repo solo se lee. Lo que se rehace es la copia: se borra lo que no venga del
repo, salvo venv/ y _local/.
"""
import argparse
import hashlib
import io
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(r"C:\Users\<usuario>\Documents\GitHub\repo-portal")
COPIA = Path(r"C:\Users\<usuario>\Documents\Portal-Local")
CONSERVAR = {"venv", "_local"}
TABLEROS = COPIA / "_local" / "tableros.json"
REEMPLAZOS = COPIA / "_local" / "reemplazos"
HUELLAS = COPIA / "_local" / "reemplazos.json"
LANZADOR = Path(__file__).resolve().parent.parent / "plantillas" / "iniciar_portal.cmd"
# Lo que nunca va en el zip: venv no sirve en otro equipo (rutas absolutas) y
# _local trae rutas de este usuario. data_real/config.local.json no deberian
# existir en la copia; si aparecen, el zip no se arma.
FUERA_DEL_ZIP = {"venv", "_local", "__pycache__", ".env"}
PROHIBIDOS_EN_ZIP = {"data_real", "config.local.json"}
ZIP = COPIA.parent / f"{COPIA.name}.zip"

# Donde se inserta cada pieza. Si el portal cambia y un ancla ya no aparece, el
# script se detiene: montar a medias da un portal que "carga" sin el tablero.
ANCLA_APP = "# ══════════════════════════════════════════════════════════════\n# SHARED STATIC"
ANCLA_TARJETA = "\n];\n\n/* ═══════════════════════════════════════════════\n   RENDER DASHBOARDS"

BLOQUE_APP = '''# ══════════════════════════════════════════════════════════════
# {slug} — montado por portal_local.py (solo en la copia local; NO esta en el repo)
# Mismo patron que ATP Rule: lista fija, ETag desde meta.json.
# ══════════════════════════════════════════════════════════════
{var}_DIR = os.path.join(BASE, "{slug}")
{var}_DATA = os.path.join({var}_DIR, "data", "dashboard")
{var}_ARCHIVOS = {archivos!r}
TABLEROS_SIN_ATRIBUTOS.add("{slug}")
TABLEROS_ESTRICTOS.add("{slug}")

def _{fn}_crudo_sellado(nombre, sello):
    return _leer_datos_crudo_sellado(
        archivo_datos=f"{slug}/{{nombre}}",
        local_fallback_path=os.path.join({var}_DATA, nombre),
        sello=sello,
    )

@app.route("/{slug}/")
@app.route("/{slug}/index.html")
def {fn}_index():
    return _no_cache(make_response(send_from_directory({var}_DIR, "index.html")))

@app.route("/api/{slug}/<nombre>")
def {fn}_data(nombre):
    if nombre not in {var}_ARCHIVOS:
        from flask import abort
        abort(404)
    meta = _leer_datos_json(archivo_datos="{slug}/meta.json",
                            local_fallback_path=os.path.join({var}_DATA, "meta.json"))
    sello = (meta or {{}}).get("generated_at")
    return _responder_datos(sello, lambda: _{fn}_crudo_sellado(nombre, sello), comprimir=True)

@app.route("/{slug}/<path:filename>")
def {fn}_static(filename):
    return _send_cached({var}_DIR, filename)

'''

def git(*args, binario=False):
    r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, check=True)
    return r.stdout if binario else r.stdout.decode("utf-8").strip()

def limpiar_copia():
    COPIA.mkdir(parents=True, exist_ok=True)
    for hijo in COPIA.iterdir():
        if hijo.name in CONSERVAR:
            continue
        shutil.rmtree(hijo) if hijo.is_dir() else hijo.unlink()

def copiar_arbol():
    """El arbol de trabajo tal cual (incluye cambios sin commitear), sin .git ni secretos."""
    ignorar = shutil.ignore_patterns(".git", "venv", "__pycache__", ".env", "*.env")
    for hijo in REPO.iterdir():
        if hijo.name in {".git", "venv", "__pycache__", ".env"}:
            continue
        destino = COPIA / hijo.name
        if hijo.is_dir():
            shutil.copytree(hijo, destino, ignore=ignorar)
        else:
            shutil.copy2(hijo, destino)

def copiar_rama(rama):
    """Lo que tiene la rama en git, sin hacer checkout (el repo no se toca)."""
    zip_bytes = git("archive", "--format=zip", rama, binario=True)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        z.extractall(COPIA)

def huella(ruta):
    # Sin importar CRLF/LF: git puede entregar cualquiera de los dos.
    datos = ruta.read_bytes().replace(bytes([13, 10]), bytes([10]))
    return hashlib.sha256(datos).hexdigest()[:16]

def aplicar_reemplazos(rebasar):
    if not REEMPLAZOS.is_dir():
        return []
    huellas = json.loads(HUELLAS.read_text(encoding="utf-8")) if HUELLAS.exists() else {}
    aplicados, viejos = [], []
    for local in sorted(p for p in REEMPLAZOS.rglob("*") if p.is_file()):
        rel = local.relative_to(REEMPLAZOS).as_posix()
        del_repo = COPIA / rel
        if not del_repo.is_file():
            raise SystemExit(f"Reemplazo {rel}: ese archivo ya no existe en el repo.")
        actual = huella(del_repo)
        if rel not in huellas or rel in rebasar:
            huellas[rel] = actual
        elif huellas[rel] != actual:
            viejos.append(rel)
            continue
        shutil.copy2(local, del_repo)
        aplicados.append(rel)
    HUELLAS.write_text(json.dumps(huellas, indent=1), encoding="utf-8")
    if viejos:
        raise SystemExit(
            "El repo cambio estos archivos desde que se hizo su reemplazo local: " + ", ".join(viejos) +
            ".\nSi se aplicara, el cambio del repo no se veria. Lleva ese cambio al archivo de "
            "_local/reemplazos/ y corre con --rebasar <ruta>, o usa --sin-reemplazos.")
    return aplicados

def elegir_datos(tablero, reales):
    origen = Path(tablero["origen"])
    carpetas = (tablero.get("datos_reales", []) if reales else []) + tablero["datos_demo"]
    for carpeta in carpetas:
        d = origen / carpeta
        if all((d / a).is_file() for a in tablero["archivos"]):
            return d, carpeta in tablero.get("datos_reales", [])
    raise SystemExit(f"{tablero['slug']}: ninguna carpeta de datos trae {tablero['archivos']} ({carpetas})")

def montar(tablero, reales):
    slug, origen = tablero["slug"], Path(tablero["origen"])
    if (COPIA / slug).exists():
        raise SystemExit(f"{slug}: el repo ya trae esa carpeta. Quitalo de _local/tableros.json: ya no es local.")
    destino = COPIA / slug
    (destino / "data" / "dashboard").mkdir(parents=True)
    for archivo in tablero["codigo"]:
        shutil.copy2(origen / archivo, destino / archivo)
    carpeta, son_reales = elegir_datos(tablero, reales)
    for archivo in tablero["archivos"]:
        shutil.copy2(carpeta / archivo, destino / "data" / "dashboard" / archivo)

    var = "LOCAL_" + slug.upper().replace("-", "_")
    fn = "local_" + slug.replace("-", "_")
    app_py = COPIA / "app.py"
    texto = app_py.read_text(encoding="utf-8")
    if texto.count(ANCLA_APP) != 1:
        raise SystemExit("app.py cambio: no encuentro el bloque SHARED STATIC para montar las rutas.")
    bloque = BLOQUE_APP.format(slug=slug, var=var, fn=fn, archivos=set(tablero["archivos"]))
    app_py.write_text(texto.replace(ANCLA_APP, bloque + ANCLA_APP), encoding="utf-8", newline="")

    portal = COPIA / tablero["portal"] / "index.html"
    html = portal.read_text(encoding="utf-8")
    if html.count(ANCLA_TARJETA) != 1:
        raise SystemExit(f"{portal}: no encuentro el final de la lista de tableros para poner la tarjeta.")
    tarjeta = ",\n  " + json.dumps(tablero["tarjeta"], ensure_ascii=False, indent=4).replace("\n", "\n  ")
    portal.write_text(html.replace(ANCLA_TARJETA, tarjeta + ANCLA_TARJETA), encoding="utf-8", newline="")
    return "REALES" if son_reales else "inventados", carpeta

def escribir_lanzador():
    # CRLF: cmd.exe se confunde con las etiquetas (goto) en un .cmd con solo LF.
    texto = LANZADOR.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\n", "\r\n")
    (COPIA / "iniciar_portal.cmd").write_bytes(texto.encode("ascii"))

def armar_zip(destino, tableros):
    """Zip de la copia lista para otro equipo. Solo con datos inventados."""
    for t in tableros:
        meta = json.loads((COPIA / t["slug"] / "data" / "dashboard" / "meta.json").read_text(encoding="utf-8-sig"))
        if meta.get("demo") is not True:
            raise SystemExit(f"Zip cancelado: /{t['slug']}/ no trae \"demo\": true en su meta.json. "
                             "El zip solo lleva datos inventados.")
    archivos = []
    for ruta in sorted(COPIA.rglob("*")):
        rel = ruta.relative_to(COPIA)
        if rel.parts[0] in FUERA_DEL_ZIP or "__pycache__" in rel.parts or ruta.suffix == ".pyc":
            continue
        if PROHIBIDOS_EN_ZIP & set(rel.parts):
            raise SystemExit(f"Zip cancelado: apareció {rel} en la copia. No se empaquetan datos reales.")
        if ruta.is_file():
            archivos.append((ruta, rel))
    destino.parent.mkdir(parents=True, exist_ok=True)
    # Se arma aparte y se reemplaza al final: si algo truena a medias, el zip
    # anterior sigue completo en vez de quedar uno roto con el mismo nombre.
    temporal = destino.with_name(destino.name + ".tmp")
    with zipfile.ZipFile(temporal, "w", zipfile.ZIP_DEFLATED) as z:
        for ruta, rel in archivos:
            z.write(ruta, (Path(COPIA.name) / rel).as_posix())
    temporal.replace(destino)
    mb = destino.stat().st_size / 1_048_576
    print(f"Zip: {destino}  ({len(archivos)} archivos, {mb:.1f} MB, datos inventados)")

def asegurar_venv():
    py = COPIA / "venv" / "Scripts" / "python.exe"
    if not py.exists():
        subprocess.run([sys.executable, "-m", "venv", str(COPIA / "venv")], check=True)
    # Versiones fijas del requirements.txt del portal; si ya estan, pip no baja nada.
    subprocess.run([str(py), "-m", "pip", "install", "-q", "--disable-pip-version-check",
                    "-r", str(COPIA / "requirements.txt")], check=True)
    return py

def probar(py, slugs):
    """Lo mismo que se revisa a mano: el portal, cada tablero montado, su API y la lista blanca."""
    pruebas = [("/logistics/", 200), ("/sop/", 200)]
    for s in slugs:
        pruebas += [(f"/{s}/", 200), (f"/api/{s}/meta.json", 200),
                    (f"/api/{s}/..%2F..%2Fapp.py", 404), (f"/{s}/data/dashboard/meta.json", 404)]
    codigo = ("import sys, logging; sys.path.insert(0, r'%s'); logging.disable(logging.WARNING)\n"
              "from app import app\nc = app.test_client()\nmal = 0\n"
              "for url, esperado in %r:\n"
              "    r = c.get(url); ok = r.status_code == esperado; mal += not ok\n"
              "    print('  OK ' if ok else '  MAL', r.status_code, url)\n"
              "sys.exit(1 if mal else 0)\n") % (COPIA, pruebas)
    return subprocess.run([str(py), "-c", codigo], cwd=COPIA).returncode == 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rama", help="rama del repo del portal a copiar (default: arbol de trabajo)")
    ap.add_argument("--reales", action="store_true", help="datos reales de los tableros montados")
    ap.add_argument("--servir", action="store_true", help="levantar el portal al terminar")
    ap.add_argument("--sin-reemplazos", action="store_true", help="no aplicar _local/reemplazos/")
    ap.add_argument("--rebasar", nargs="+", default=[], metavar="RUTA",
                    help="reemplazos ya ajustados al repo nuevo: se toma su huella actual")
    ap.add_argument("--zip", metavar="RUTA.zip", default=str(ZIP),
                    help=f"donde va el zip (default: {ZIP}); se sobreescribe en cada corrida")
    ap.add_argument("--sin-zip", action="store_true", help="no rearmar el zip esta vez")
    args = ap.parse_args()

    tableros = json.loads(TABLEROS.read_text(encoding="utf-8-sig")) if TABLEROS.exists() else []
    origen = f"rama {args.rama} ({git('rev-parse', '--short', args.rama)})" if args.rama else \
        f"arbol de trabajo, rama {git('branch', '--show-current')} ({git('rev-parse', '--short', 'HEAD')})"
    sucio = git("status", "--porcelain")
    print(f"Portal desde: {origen}")
    if not args.rama and sucio:
        print("  ojo: el arbol de trabajo tiene cambios sin commitear; van incluidos en la copia")

    limpiar_copia()
    copiar_rama(args.rama) if args.rama else copiar_arbol()
    if not args.sin_reemplazos:
        for rel in aplicar_reemplazos(set(args.rebasar)):
            print(f"Reemplazo local: {rel}")
    for t in tableros:
        tipo, carpeta = montar(t, args.reales)
        print(f"Montado: /{t['slug']}/  datos {tipo}  ({carpeta})")
    escribir_lanzador()

    py = asegurar_venv()
    ok = probar(py, [t["slug"] for t in tableros])
    print("Pruebas: todo bien" if ok else "Pruebas: HAY FALLAS (arriba)")
    if not ok:
        sys.exit(1)
    # El zip se rearma en cada corrida (mismo nombre, se sobreescribe), salvo con
    # datos reales: ese zip nunca se arma, y el que ya existe se queda como estaba.
    if args.reales:
        print(f"Zip: NO se rearmo (--reales). {Path(args.zip).name} sigue con la version anterior, con datos inventados.")
    elif not args.sin_zip:
        armar_zip(Path(args.zip), tableros)
    if args.servir:
        print("Portal local -> http://127.0.0.1:8080/   (Ctrl+C para parar)")
        subprocess.run([str(py), "servir.py"], cwd=COPIA)

if __name__ == "__main__":
    main()
