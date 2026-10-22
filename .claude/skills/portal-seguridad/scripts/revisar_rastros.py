"""Busca rastros de herramientas de desarrollo en un repo de git.

Uso:
    python revisar_rastros.py RUTA-DEL-REPO [--base origin/main]

Revisa, contra ../assets/firmas.txt:
  1. el CONTENIDO de todos los archivos versionados (lo que hay en HEAD);
  2. los NOMBRES y RUTAS de esos archivos (carpetas de configuracion, rutas
     personales);
  3. los MENSAJES de los commits de la rama (desde --base; sin --base, solo
     el ultimo commit).
Y en contenido y mensajes, los CARACTERES INVISIBLES (ancho cero, controles
bidi, etiquetas Unicode) que no tienen uso legitimo.

Sale con codigo 1 si encuentra algo. No corrige nada: cada hallazgo se revisa
a mano, porque hay falsos positivos legitimos (un nombre propio dentro de un
JSON de datos, por ejemplo) que se reportan en vez de esconderse.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

LISTA = Path(__file__).resolve().parent.parent / "assets" / "firmas.txt"

# Caracteres invisibles: la MISMA lista que validar-antes-de-entregar/scripts/validar_entregable.py.
# Si cambia alla, se cambia aqui.
INVISIBLES = [(0x00AD, 0x00AD), (0x034F, 0x034F), (0x061C, 0x061C), (0x115F, 0x1160), (0x17B4, 0x17B5),
              (0x180E, 0x180E), (0x200B, 0x200F), (0x202A, 0x202E), (0x2060, 0x2064), (0x2066, 0x206F),
              (0x2800, 0x2800), (0x3164, 0x3164), (0xFE00, 0xFE0F), (0xFEFF, 0xFEFF), (0xFFA0, 0xFFA0),
              (0xE0000, 0xE007F), (0xE0100, 0xE01EF)]

def _es_emoji(ch):
    import unicodedata
    cp = ord(ch)
    return cp >= 0x1F000 or 0x2100 <= cp <= 0x2BFF or unicodedata.category(ch).startswith("S")

def invisibles(texto):
    """[(linea, columna, 'U+XXXX NOMBRE')], sin los usos legitimos: BOM al inicio y emojis compuestos."""
    import unicodedata
    salida = []
    linea, col = 1, 0
    for i, ch in enumerate(texto):
        if ch == "\n":
            linea, col = linea + 1, 0
            continue
        col += 1
        cp = ord(ch)
        if cp < 0xAD or not any(a <= cp <= b for a, b in INVISIBLES):
            continue
        previo = texto[i - 1] if i else ""
        siguiente = texto[i + 1] if i + 1 < len(texto) else ""
        if cp == 0xFEFF and (i == 0 or (previo and previo in "'\"`,")):
            continue  # BOM al inicio, o escrito a proposito en un literal ('﻿' + csv)
        if cp in (0xFE0E, 0xFE0F) and previo and (_es_emoji(previo) or previo in "#*0123456789"):
            continue
        if cp == 0x200D and previo and siguiente and (_es_emoji(previo) or ord(previo) == 0xFE0F) \
                and _es_emoji(siguiente):
            continue
        salida.append((linea, col, "U+%04X %s" % (cp, unicodedata.name(ch, "?"))))
    return salida

def cargar():
    terminos = [t.strip() for t in LISTA.read_text(encoding="utf-8").splitlines()
                if t.strip() and not t.lstrip().startswith("#")]
    return re.compile("|".join(re.escape(t) for t in terminos), re.I)

def git(repo, *args, binario=False):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)
    return r.stdout if binario else r.stdout.decode("utf-8", errors="replace")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--base", help="rama contra la que se comparan los commits (ej. origin/main)")
    a = ap.parse_args()
    patron = cargar()
    hallazgos = []

    for rel in git(a.repo, "ls-files", "-z").split("\0"):
        if not rel:
            continue
        m = patron.search(rel)
        if m:
            hallazgos.append(f"RUTA     {rel}  ->  {m.group(0)}")
        try:
            datos = git(a.repo, "show", f"HEAD:{rel}", binario=True)
        except subprocess.CalledProcessError:
            continue
        texto = datos.decode("utf-8", errors="ignore")
        for m in patron.finditer(texto):
            linea = texto.count("\n", 0, m.start()) + 1
            # El texto de alrededor, no el inicio del renglon: en un archivo
            # minificado el renglon es el archivo entero.
            contexto = texto[max(0, m.start() - 45):m.end() + 45].replace("\n", " ").strip()
            hallazgos.append(f"ARCHIVO  {rel}:{linea}  ->  {contexto}")
        if b"\0" not in datos[:8000]:  # solo archivos de texto
            inv = invisibles(texto)
            if inv:
                ejemplos = ", ".join(f"{l}:{c} {n}" for l, c, n in inv[:3])
                hallazgos.append(f"INVISIBLE {rel}  ->  {len(inv)} caracter(es): {ejemplos}"
                                 + (" ..." if len(inv) > 3 else ""))

    rango = f"{a.base}..HEAD" if a.base else "-1"
    for bloque in git(a.repo, "log", rango, "--format=%h%x00%an <%ae>%x00%B%x01").split("\x01"):
        if not bloque.strip():
            continue
        sha, autor, cuerpo = (bloque.strip("\n").split("\0") + ["", ""])[:3]
        for m in patron.finditer(autor + "\n" + cuerpo):
            hallazgos.append(f"COMMIT   {sha}  ->  {m.group(0)}")
        for l, c, n in invisibles(cuerpo)[:3]:
            hallazgos.append(f"COMMIT   {sha}  ->  caracter invisible en el mensaje, {l}:{c} {n}")

    if hallazgos:
        print(f"{len(hallazgos)} hallazgo(s) en {a.repo}:\n")
        print("\n".join(hallazgos))
        sys.exit(1)
    print(f"Sin rastros en {a.repo} (archivos, rutas y commits {rango}).")

if __name__ == "__main__":
    main()
