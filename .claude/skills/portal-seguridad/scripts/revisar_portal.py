#!/usr/bin/env python3
"""Barrido completo de un portal Flask con tableros HTML/JS.

Uso:
    python revisar_portal.py RUTA [--json salida.json] [--nombres "Haz,otra persona"]

Recorre TODOS los archivos de la carpeta (menos librerias de terceros y
carpetas de dependencias) y deja un inventario archivo:linea de lo que hay que
juzgar. No decide si algo es explotable: eso lo hace quien lo lee. Lo que
garantiza es que ningun tablero se quede sin revisar por muestreo.

## Por que existe

Una vez, el agente revisor-seguridad corrio sobre el paquete del portal
que ya habia auditado alguien mas. Encontro el XSS por datos de DataStage, que
la skill nombraba, y no vio el mismo patron en otros seis tableros que la skill
no nombraba. Un modelo que lee revisa por muestreo; un script no se salta
archivos. Aqui se mide, y el agente juzga lo medido.

## Que NO hace

- No lee el contenido de datos: los .json, .csv y Excel solo cuentan por
  nombre y tamano (Regla 5). Las lineas de mas de 5 000 caracteres (datos
  pegados en el HTML) no se analizan ni se imprimen: se reportan por tamano.
- No abre navegadores ni hace peticiones.
- No corrige nada.

Sale con codigo 1 si hay algun hallazgo de severidad Alta.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SALTAR_DIRS = {".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist",
               ".pytest_cache", ".mypy_cache", ".idea", ".vscode"}
VENDOR = ("shared/vendor/", "/vendor/", "/lib/", "/libs/")
EXT_FRONT = {".html", ".htm", ".js", ".mjs"}
EXT_BACK = {".py"}
EXT_DOCS = {".md", ".txt", ".bat", ".cmd", ".sh", ".ps1", ".cfg", ".ini", ".toml", ".yml",
            ".yaml", ".config", ".example"}
EXT_DATOS = {".json", ".csv", ".tsv", ".xlsx", ".xls", ".xlsm", ".xlsb", ".parquet", ".db",
             ".sqlite", ".zip", ".7z", ".rar", ".pbix"}
LINEA_LARGA = 5000

SEVERIDAD = {
    "XSS-PLANTILLA": "Alta", "XSS-CONCAT": "Alta", "XSS-SINK": "Alta",
    "XSS-HELPER": "Media", "XSS-VARIABLE": "Baja", "URL-FUENTE": "Info",
    "RUTA-SIN-FILTRO": "Alta", "FILTRO-WINDOWS": "Media", "HOST-TODAS": "Media",
    "DEBUG": "Alta", "CSP-UNSAFE": "Media", "CSP-EXTERNO": "Baja", "CACHE-API": "Baja",
    "SIN-BITACORA": "Baja", "CSV-SIN-NEUTRALIZAR": "Media", "DATOS-PEGADOS": "Alta",
    "DATOS-PERSONALES": "Alta", "EXTERNO": "Baja", "COMENTARIO-INTERNO": "Baja",
    "DEP-SIN-FIJAR": "Media", "DEPENDENCIAS": "Info",
    "JS-INLINE": "Info",
    # calidad: fallas que salen en verde
    "FETCH-SIN-OK": "Calidad", "FETCH-SIN-TIMEOUT": "Calidad", "CATCH-SILENCIOSO": "Calidad", "STORAGE-SIN-TRY": "Calidad",
    "FECHA-UTC": "Calidad", "ACTUALIZADO-NAVEGADOR": "Calidad", "CONFIG-CLAVE-FALTA": "Calidad",
    "COPIA-DIVERGENTE": "Calidad", "COPIA-IDENTICA": "Calidad", "RESPALDO-SILENCIOSO": "Calidad",
    "REGEX-PERMISIVA": "Baja", "GLOBAL-SIN-LOCK": "Calidad", "ETAG-DUPLICADO": "Calidad",
    "ETAG-LEE-ANTES": "Calidad", "NO-STORE-DATOS": "Calidad", "COMPRESION": "Calidad",
    "REF-INEXISTENTE": "Calidad", "CODIGO-MUERTO": "Calidad", "MONOLITO": "Calidad",
    "PROYECTO": "Calidad", "GIT-MENSAJE": "Calidad", "GIT-HISTORIAL-DATOS": "Alta",
    "GIT-MENCION-SECRETO": "Media", "GITIGNORE-DATA": "Media", "DATA-SIN-CONTRATO": "Media",
    "ARCHIVO-GRANDE": "Media", "LIMITE": "Info",
}
ORDEN = ["Alta", "Media", "Baja", "Calidad", "Info"]

hallazgos = []
CATALOGOS = defaultdict(list)

def h(familia, archivo, linea, detalle, tablero=""):
    hallazgos.append({"familia": familia, "severidad": SEVERIDAD.get(familia, "Info"),
                      "archivo": archivo, "linea": linea, "tablero": tablero,
                      "detalle": detalle})

def corto(s, n=140):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"

def num_linea(texto, pos):
    return texto.count("\n", 0, pos) + 1

# --------------------------------------------------------------------------
# Escaner minimo de JS: cadenas, plantillas y parentesis
# --------------------------------------------------------------------------

def saltar_cadena(s, j, q):
    k = j + 1
    n = len(s)
    while k < <unidad-compartida>
        c = s[k]
        if c == "\\":
            k += 2
            continue
        if c == q or c == "\n":
            return k + 1
        k += 1
    return n

def es_regex(s, j):
    """¿El '/' en s[j] abre una expresion regular (y no es una division ni un comentario)?"""
    if s.startswith("//", j) or s.startswith("/*", j):
        return False
    k = j - 1
    while k >= 0 and s[k] in " \t":
        k -= 1
    if k < 0:
        return True
    previo = s[k]
    if previo in "(,=:[!&|?{};+-*%~^<>\n":
        return True
    palabra = re.search(r"(return|typeof|case|in|of|delete|void|throw|new)$", s[max(0, k - 8):k + 1])
    return bool(palabra)

def saltar_regex(s, j):
    k = j + 1
    n = len(s)
    en_clase = False
    while k < <unidad-compartida>
        c = s[k]
        if c == "\\":
            k += 2
            continue
        if c == "\n":
            return j + 1  # no era regex
        if c == "[":
            en_clase = True
        elif c == "]":
            en_clase = False
        elif c == "/" and not en_clase:
            k += 1
            while k < n and s[k].isalpha():
                k += 1
            return k
        k += 1
    return j + 1

def saltar_llaves(s, k):
    """k apunta despues de '${' o '{'. Devuelve el indice despues de la '}' que cierra."""
    prof = 1
    n = len(s)
    while k < <unidad-compartida>
        c = s[k]
        if c in "\"'":
            k = saltar_cadena(s, k, c)
            continue
        if c == "/" and es_regex(s, k):
            k = saltar_regex(s, k)
            continue
        if c == "`":
            k = saltar_plantilla(s, k)
            continue
        if c == "{":
            prof += 1
        elif c == "}":
            prof -= 1
            if prof == 0:
                return k + 1
        k += 1
    return n

def saltar_plantilla(s, j):
    k = j + 1
    n = len(s)
    while k < <unidad-compartida>
        c = s[k]
        if c == "\\":
            k += 2
            continue
        if c == "`":
            return k + 1
        if s.startswith("${", k):
            k = saltar_llaves(s, k + 2)
            continue
        k += 1
    return n

def partes_plantilla(s, j):
    """Plantilla que empieza en s[j]=='`'. Devuelve (texto_estatico, [(pos, expr)], fin)."""
    k = j + 1
    n = len(s)
    estatico = []
    exprs = []
    while k < <unidad-compartida>
        c = s[k]
        if c == "\\":
            estatico.append(s[k:k + 2])
            k += 2
            continue
        if c == "`":
            return "".join(estatico), exprs, k + 1
        if s.startswith("${", k):
            fin = saltar_llaves(s, k + 2)
            exprs.append((k + 2, s[k + 2:fin - 1]))
            estatico.append("\x00")
            k = fin
            continue
        estatico.append(c)
        k += 1
    return "".join(estatico), exprs, n

def extraer_expr(s, i, llamada):
    """Expresion que empieza en i: el lado derecho de una asignacion o los argumentos de una llamada."""
    prof = 0
    j = i
    n = min(len(s), i + 6000)
    while j < <unidad-compartida>
        c = s[j]
        if c in "\"'":
            j = saltar_cadena(s, j, c)
            continue
        if c == "`":
            j = saltar_plantilla(s, j)
            continue
        if s.startswith("//", j):
            k = s.find("\n", j)
            j = k if k != -1 else n
            continue
        if s.startswith("/*", j):
            k = s.find("*/", j + 2)
            j = k + 2 if k != -1 else n
            continue
        if c == "/" and es_regex(s, j):
            j = saltar_regex(s, j)
            continue
        if c in "([{":
            prof += 1
        elif c in ")]}":
            if prof == 0:
                break
            prof -= 1
        elif c == ";" and prof == 0:
            break
        elif c == "\n" and prof == 0 and not llamada:
            antes = s[i:j].rstrip()[-1:]
            despues = s[j + 1:j + 200].lstrip()[:1]
            if antes not in "+(,?:=&|" and despues not in "+.?:&|":
                break
        j += 1
    return s[i:j]

def codigo_fuera_de_literales(expr):
    """Separa una expresion en (codigo_suelto, [expresiones ${} de plantillas])."""
    fuera = []
    internas = []
    k = 0
    n = len(expr)
    while k < <unidad-compartida>
        c = expr[k]
        if c in "\"'":
            k = saltar_cadena(expr, k, c)
            fuera.append(" ")
            continue
        if c == "/" and es_regex(expr, k):
            k = saltar_regex(expr, k)
            fuera.append(" ")
            continue
        if c == "`":
            _, exprs, fin = partes_plantilla(expr, k)
            internas.extend(e for _, e in exprs)
            fuera.append(" ")
            k = fin
            continue
        fuera.append(c)
        k += 1
    return "".join(fuera), internas

def ramas_de(t, prof=0):
    """Lo que de verdad llega al HTML: las ramas de un ternario y las alternativas de || y ??,
    no las condiciones."""
    t = t.strip()
    while t.startswith("(") and t.endswith(")") and saltar_parentesis(t) == len(t):
        t = t[1:-1].strip()
    if prof > 6 or not t:
        return [t] if t else []
    protegido = t.replace("?.", "\x01.").replace("??", "\x02")
    partes = dividir_nivel0(protegido, "?")
    if len(partes) > 1:
        resto = "?".join(partes[1:])
        salida = []
        for x in dividir_nivel0(resto, ":"):
            salida.extend(ramas_de(x.replace("\x01", "?").replace("\x02", "??"), prof + 1))
        return salida
    alternativas = [p for p in re.split(r"\|\||\x02", protegido)]
    if len(alternativas) > 1 and all(saltar_parentesis("(" + a + ")") == len(a) + 2 for a in alternativas):
        salida = []
        for a in alternativas:
            salida.extend(ramas_de(a.replace("\x01", "?"), prof + 1))
        return salida
    return [t]

def saltar_parentesis(t):
    prof = 0
    for i, c in enumerate(t):
        if c == "(":
            prof += 1
        elif c == ")":
            prof -= 1
            if prof == 0:
                return i + 1
    return -1

def dividir_nivel0(s, seps):
    partes = []
    prof = 0
    actual = []
    for c in s:
        if c in "([{":
            prof += 1
        elif c in ")]}":
            prof -= 1
        if c in seps and prof == 0:
            partes.append("".join(actual))
            actual = []
        else:
            actual.append(c)
    partes.append("".join(actual))
    return partes

def trozos_dinamicos(expr, internas_tambien=True):
    """Trozos de codigo que terminan dentro del HTML armado por la expresion."""
    suelto, internas = codigo_fuera_de_literales(expr)
    trozos = list(internas) if internas_tambien else []
    # quitar la asignacion acumuladora: html += ... / out = ...
    suelto = re.sub(r"^\s*[\w$.\[\]]+\s*\+?=(?!=)", " ", suelto)
    for parte in dividir_nivel0(suelto, "+"):
        parte = parte.strip()
        if not parte:
            continue
        trozos.append(parte)
    limpios = []
    for t in trozos:
        limpios.extend(ramas_de(t))
    salida = []
    for t in limpios:
        t = re.sub(r"^[:,\s]+|[,\s]+$", "", t)
        # prefijo de asignacion que quedo en la linea: document.getElementById( ).innerHTML =
        t = re.sub(r"^[\w$.\[\]() ]+?\s*\+?=(?![=>])\s*", "", t)
        # parentesis de la expresion que la rodea: quitar solo los que no cierran nada
        while t.count(")") > t.count("(") and t.endswith(")"):
            t = t[:-1].rstrip()
        while t.count("(") > t.count(")") and t.startswith("("):
            t = t[1:].lstrip()
        t = t.strip()
        if not t or re.fullmatch(r"[\s\W]*", t):
            continue
        if t.endswith("(") or re.fullmatch(r"[\w$.]+\.(push|join|concat)", t):
            continue
        if re.search(r"\bfunction\b|=>|\{", t) or t.count("(") != t.count(")"):
            continue  # codigo, no un valor: las plantillas de adentro se revisan por su cuenta
        salida.append(t)
    return salida

NUMERICO = re.compile(
    r"(^|\W)(fmt\w*|format\w*|num\w*|money\w*|pct\w*|round\w*|parseInt|parseFloat|Number|fecha\w*|date\w*|"
    r"hora\w*|abbr\w*|compact\w*|"
    r"Math\.\w+|Intl\.\w+|toFixed|toLocaleString|toLocaleDateString|toLocaleTimeString|"
    r"toPrecision|abs|sum|count|avg|mean|kpi\w*)\s*\(|\.length\b|\.toFixed\(|\.toLocale\w*\(|"
    r"^[\d.\s*/+\-%]+$|^(i|j|k|n|idx|index|len|total|count|pct|percent|ancho|width|height|alto)$",
    re.I)
CONSTANTE = re.compile(r"^[A-Z][A-Z0-9_]*(\.[\w$]+)*$|^(t|tr|i18n|txt|lbl|L|T)\s*\(|"
                       r"^(i18n|TXT|LBL|LANG|TEXTOS|T|L)\b")

def clasificar_trozo(t, escapadores, generadores, contaminadas):
    """escapado | numerico | constante | indirecto | url | datos"""
    t0 = t.strip()
    llamada = re.match(r"^([\w$.]+)\s*\(", t0)
    if llamada:
        nombre = llamada.group(1).split(".")[-1]
        if nombre in escapadores or llamada.group(1) in escapadores or re.match(r"(esc|escape|sanitiz)", nombre, re.I):
            return "escapado"
        if nombre in generadores:
            return "indirecto"
        if re.search(r"(class|clase|cls|color|colour|style|estilo|icon|icono|badge|tone|tono)\w*$", nombre, re.I):
            return "constante"
    if "`" in t0 and re.search(r"<[a-zA-Z/]", t0):
        return "indirecto"  # plantilla anidada: se revisa por su cuenta
    if re.search(r"\.map\s*\(", t0) and re.search(r"\.join\b", t0):
        return "indirecto"  # las plantillas del map se revisan por su cuenta
    if re.fullmatch(r"[\w$.\[\]\s*/+\-%()]+", t0) and re.search(r"[*/%]|\s-\s|\w-\w|^\d", t0):
        return "numerico"
    if re.search(r"(^|\.)_?(n|count|total|pct|qty|cantidad|monto|valor|value|sum|avg|min|max|len|percent|porc\w*|"
                 r"share|days|dias|horas|hours|score|rank|x|y|w|h|width|height|dx|dy|cx|cy|r)$", t0, re.I) \
            or re.fullmatch(r"(count|counts|conteo|totales|totals)\w*\[[^\]]+\]", t0, re.I):
        return "numerico"
    if re.search(r"(^|\.)(color|colour|cls|clase|className|class\w*|icon\w*|flecha|arrow|dir|estilo|style|bg|fg|bd|border|"
                 r"tone|tono|lang|sufijo|suffix|unit|unidad|hidden|plegable|activo|active|selected|checked|"
                 r"disabled)$", t0, re.I) or re.fullmatch(r"[A-Z][A-Z0-9_]*(\.[\w$]+|\[[^\]]+\])*", t0):
        return "constante"
    if NUMERICO.search(t0):
        return "numerico"
    if CONSTANTE.search(t0):
        return "constante"
    if re.fullmatch(r"(true|false|null|undefined|''|\"\")|'[^']*'|\"[^\"]*\"", t0):
        return "constante"
    nombres = set(re.findall(r"[A-Za-z_$][\w$]*", t0))
    if nombres & contaminadas:
        return "url"
    if re.fullmatch(r"[A-Za-z_$][\w$]*", t0):
        return "variable"  # variable local: puede venir del codigo o de los datos
    return "datos"

# --------------------------------------------------------------------------
# Frontend
# --------------------------------------------------------------------------

SINKS = [
    (re.compile(r"\.(innerHTML|outerHTML)\s*(\+?=)(?!=)"), False),
    (re.compile(r"\.insertAdjacentHTML\s*\("), True),
    (re.compile(r"\bdocument\.write(ln)?\s*\("), True),
    (re.compile(r"\.(bindTooltip|bindPopup|setPopupContent|setTooltipContent)\s*\("), True),
    (re.compile(r"(\$|jQuery)\([^)]{0,80}\)\s*\.(html|append|prepend|before|after|replaceWith)\s*\("), True),
    (re.compile(r"\.parseFromString\s*\("), True),
    (re.compile(r"\.createContextualFragment\s*\("), True),
    (re.compile(r"\.srcdoc\s*=(?!=)"), False),
]
FUENTE_URL = re.compile(r"URLSearchParams|location\.(search|hash|href)|searchParams|"
                        r"\breadURL\b|\bgetParam\w*\s*\(|\bparams\.get\s*\(|decodeURIComponent\s*\(\s*location")
ASIGNA_URL = re.compile(
    r"(?:const|let|var)?\s*([A-Za-z_$][\w$]*)\s*=\s*[^;\n]*?(URLSearchParams|location\.(search|hash)|"
    r"searchParams|\bparams\.get\s*\(|\bgetParam\w*\s*\(|\breadURL\b|\burl\.get\s*\(|\bqs\.get\s*\()")
FOR_URL = re.compile(r"for\s*\(\s*(?:const|let|var)\s*\[\s*([\w$]+)\s*,\s*([\w$]+)\s*\]\s*of\s*([\w$.]+)")
FUNC_DEF = re.compile(
    r"(?:function\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)\s*\{|"
    r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:function\s*\(([^)]*)\)|\(([^)]*)\)\s*=>|([A-Za-z_$][\w$]*)\s*=>)\s*\{?)")

def funciones_js(texto):
    """[(nombre, params, inicio_cuerpo, fin_cuerpo, pos_def)]"""
    salida = []
    for m in FUNC_DEF.finditer(texto):
        nombre = m.group(1) or m.group(3)
        params = m.group(2) or m.group(4) or m.group(5) or m.group(6) or ""
        ini = m.end()
        if texto[ini - 1:ini] == "{":
            fin = saltar_llaves(texto, ini)
        else:
            fin = ini + len(extraer_expr(texto, ini, False))
        salida.append((nombre, [p.strip().split("=")[0].strip() for p in params.split(",") if p.strip()],
                       ini, fin, m.start()))
    return salida

def funcion_que_contiene(funcs, pos):
    mejor = None
    for f in funcs:
        if f[2] <= pos < f[3]:
            if mejor is None or f[2] > mejor[2]:
                mejor = f
    return mejor

def es_vendor(rel):
    r = "/" + rel.replace("\\", "/")
    return any(v in r for v in VENDOR) or rel.endswith(".min.js")

def tablero_de(rel):
    partes = rel.replace("\\", "/").split("/")
    return partes[0] if len(partes) > 1 else "(raiz)"

def neutraliza_csv(texto):
    return bool(re.search(r"\^\s*\[[^\]]*=[^\]]*\]|startsWith\(\s*['\"][=+@-]|"
                          r"\[\s*['\"]=['\"]\s*,\s*['\"]\+['\"]|csvSafe|safeCsv|neutraliz|"
                          r"formula\w*inj|sanitizeCsv", texto, re.I))

def revisar_frontend(root, archivos, escapadores, generadores, nombres_equipo):
    funciones_por_nombre = defaultdict(list)
    csv_compartido = any(neutraliza_csv(t) for r, t in archivos if tablero_de(r) == "shared")
    for rel, texto in archivos:
        tab = tablero_de(rel)
        lineas = texto.split("\n")
        largas = {i for i, ln in enumerate(lineas, 1) if len(ln) > LINEA_LARGA}

        def ignorar(pos):
            return num_linea(texto, pos) in largas

        # --- datos pegados -------------------------------------------------
        for m in re.finditer(r"(?:const|let|var)\s+([\w$]+)\s*=\s*\[\s*\{", texto):
            ini = texto.index("[", m.start())
            k = ini
            prof = 0
            n = len(texto)
            while k < <unidad-compartida>
                c = texto[k]
                if c in "\"'":
                    k = saltar_cadena(texto, k, c)
                    continue
                if c in "[{":
                    prof += 1
                elif c in "]}":
                    prof -= 1
                    if prof == 0:
                        break
                k += 1
            tam = k - ini
            if tam > 10_000:
                filas = texto.count("},", ini, k) + 1
                h("DATOS-PEGADOS", rel, num_linea(texto, m.start()),
                  f"arreglo `{m.group(1)}` pegado en el codigo: ~{filas:,} filas, {tam/1024:,.0f} KB "
                  "(no se leyo el contenido)", tab)
        for i in sorted(largas):
            ya = any(x["archivo"] == rel and x["linea"] == i and x["familia"] == "DATOS-PEGADOS"
                     for x in hallazgos)
            if not ya:
                h("DATOS-PEGADOS", rel, i, f"linea de {len(lineas[i-1])/1024:,.0f} KB: probable dato "
                  "pegado; no se analizo ni se imprime", tab)

        funcs = funciones_js(texto)
        for f in funcs:
            if f[0]:
                cuerpo = texto[f[2]:f[3]]
                if len(cuerpo) < 20_000:
                    funciones_por_nombre[f[0]].append((rel, num_linea(texto, f[4]),
                                                       re.sub(r"\s+", "", cuerpo)))
        # --- variables que vienen de la URL --------------------------------
        contaminadas = set()
        for m in ASIGNA_URL.finditer(texto):
            if not ignorar(m.start()):
                contaminadas.add(m.group(1))
        for m in FOR_URL.finditer(texto):
            if m.group(3) in contaminadas or re.search(r"param|query|search|url", m.group(3), re.I):
                contaminadas.update({m.group(1), m.group(2)})
        contaminadas -= {"window", "document", "location", "URLSearchParams", "decodeURIComponent",
                         "get", "has", "new", "const", "let", "var", "url", "href"}
        contaminadas = {c for c in contaminadas if len(c) >= 3}
        destinos = set()
        # URLSearchParams(...).forEach((v, k) => {...}): v y k solo valen dentro de ese cuerpo
        for m in re.finditer(r"(URLSearchParams\([^)]*\)|searchParams|\bparams|\bqs)\s*\.forEach\(\s*\(?\s*"
                             r"([\w$]+)\s*(?:,\s*([\w$]+))?\s*\)?\s*=>\s*\{", texto):
            locales = {x for x in (m.group(2), m.group(3)) if x}
            cuerpo = texto[m.end():saltar_llaves(texto, m.end())]
            rx_l = r"\b(" + "|".join(map(re.escape, locales)) + r")\b"
            for a in re.finditer(r"([\w$]+(?:\.[\w$]+|\[[^\]\n]+\])*)\s*=(?!=)\s*([^;\n]+)", cuerpo):
                if re.search(rx_l, a.group(2)):
                    destinos.add(re.sub(r"\[[^\]]+\]", "[]", a.group(1)))
                    if re.fullmatch(r"[\w$]{3,}", a.group(1)):
                        contaminadas.add(a.group(1))
            for p in re.finditer(r"([\w$]{3,})\.(push|unshift|add)\(\s*([^)\n]+)\)", cuerpo):
                if re.search(rx_l, p.group(3)):
                    contaminadas.add(p.group(1))
                    destinos.add(p.group(1) + "[]")
        for _ in range(2):
            for m in re.finditer(r"(?:const|let|var)\s+([\w$]{3,})\s*=\s*([^;\n]+)", texto):
                if contaminadas and set(re.findall(r"[A-Za-z_$][\w$]*", m.group(2))) & contaminadas:
                    contaminadas.add(m.group(1))
        if contaminadas:
            rx_c = r"\b(" + "|".join(map(re.escape, contaminadas)) + r")\b"
            for m in re.finditer(r"([\w$]+(?:\.[\w$]+|\[[^\]\n]+\])+)\s*=(?!=)\s*([^;\n]+)", texto):
                if re.search(rx_c, m.group(2)) and not ignorar(m.start()):
                    destinos.add(re.sub(r"\[[^\]]+\]", "[]", m.group(1)))
            # valores de la URL que terminan en algo llamado html
            for m in re.finditer(r"\b\w*html\w*\s*(?::|\+?=(?!=))\s*([^;\n]+(?:\n\s*[^;\n]+){0,2})", texto, re.I):
                linea_txt = lineas[num_linea(texto, m.start()) - 1].lstrip()
                if linea_txt.startswith(("//", "*", "/*")):
                    continue
                if re.search(rx_c, m.group(1)) and not ignorar(m.start()) and not re.search(
                        r"\b(" + "|".join(map(re.escape, escapadores)) + r")\s*[(),]|\besc\w*\s*[(),]", m.group(1)):
                    h("XSS-SINK", rel, num_linea(texto, m.start()),
                      f"[URL] `{corto(m.group(0), 80)}`: un valor de la URL entra a HTML sin escape", tab)
        lineas_url = [num_linea(texto, m.start()) for m in FUENTE_URL.finditer(texto)
                      if not ignorar(m.start())]
        if lineas_url:
            h("URL-FUENTE", rel, lineas_url[0],
              f"lee la URL en {len(lineas_url)} punto(s): lineas {', '.join(map(str, lineas_url[:12]))}"
              + (f"; variables que cargan valores de la URL: {', '.join(sorted(contaminadas)[:15])}"
                 if contaminadas else "")
              + (f"; los guarda en: {', '.join(sorted(destinos)[:10])}. Seguir esos destinos hasta donde se "
                 "pintan (chips, avisos, titulos): ahi tiene que haber esc() o textContent" if destinos else ""),
              tab)

        vistos = set()

        def reportar_trozos(fam, pos, trozos, contexto):
            malos = []
            variables = []
            for t in trozos:
                cls = clasificar_trozo(t, escapadores, generadores, contaminadas)
                if cls in ("url", "datos"):
                    malos.append((cls, t))
                elif cls == "variable":
                    variables.append(t)
            ln = num_linea(texto, pos)
            if not malos:
                if variables and not any(v[0] == ln for v in vistos):
                    vistos.add((ln, tuple(variables)))
                    h("XSS-VARIABLE", rel, ln, f"{contexto}: variable(s) sin escape -> "
                      + ", ".join(f"`{v}`" for v in variables[:5]) + ": revisar si traen datos", tab)
                return
            clave = (ln, tuple(t for _, t in malos))
            if clave in vistos or any(v[0] == ln for v in vistos):
                return
            vistos.add(clave)
            origen = "URL" if any(c == "url" for c, _ in malos) else "datos"
            h(fam, rel, ln, f"[{origen}] {contexto}: sin escape -> "
              + "; ".join(f"`{corto(t, 60)}`" for _, t in malos[:5]), tab)

        # --- sinks (primero, para que la linea quede con su contexto) -------
        for rx, llamada in SINKS:
            for m in rx.finditer(texto):
                if ignorar(m.start()):
                    continue
                expr = extraer_expr(texto, m.end(), llamada)
                trozos = trozos_dinamicos(expr, internas_tambien=False)
                if not trozos:
                    continue
                if len(trozos) == 1 and re.fullmatch(r"[A-Za-z_$][\w$]*", trozos[0].strip()):
                    var = trozos[0].strip()
                    f = funcion_que_contiene(funcs, m.start())
                    if f and var in f[1]:
                        h("XSS-HELPER", rel, num_linea(texto, m.start()),
                          f"`{f[0] or 'funcion anonima'}({', '.join(f[1])})` pinta como HTML su "
                          f"parametro `{var}`: revisar cada llamada a `{f[0]}`", tab)
                    elif var in contaminadas:
                        h("XSS-SINK", rel, num_linea(texto, m.start()),
                          f"[URL] `{corto(m.group(0), 40)}` recibe `{var}`, que carga un valor de la URL", tab)
                    continue
                reportar_trozos("XSS-SINK", m.start(), trozos, f"`{corto(m.group(0), 40)}`")
        # --- plantillas `...` que arman HTML --------------------------------
        def revisar_plantilla(inicio, prof=0):
            """Revisa la plantilla que empieza en `inicio` y, adentro de cada ${...}, las plantillas
            anidadas (filas.map(f => `<tr>${...}</tr>`)). Devuelve el indice donde termina."""
            est, exprs, fin = partes_plantilla(texto, inicio)
            if exprs and re.search(r"<\s*[a-zA-Z/!]", est):
                for pos, e in exprs:
                    reportar_trozos("XSS-PLANTILLA", pos, trozos_dinamicos(e), "plantilla que arma HTML")
            if prof < 8:
                for pos, e in exprs:
                    j = 0
                    while j < len(e):
                        c2 = e[j]
                        if c2 in "\"'":
                            j = saltar_cadena(e, j, c2)
                            continue
                        if c2 == "/" and es_regex(e, j):
                            j = saltar_regex(e, j)
                            continue
                        if c2 == "`":
                            j = revisar_plantilla(pos + j, prof + 1) - pos
                            continue
                        j += 1
            return fin

        k = 0
        n = len(texto)
        while k < <unidad-compartida>
            c = texto[k]
            if c in "\"'":
                k = saltar_cadena(texto, k, c)
                continue
            if c == "/" and texto.startswith("//", k):
                e = texto.find("\n", k)
                k = e if e != -1 else n
                continue
            if c == "/" and texto.startswith("/*", k):
                e = texto.find("*/", k + 2)
                k = e + 2 if e != -1 else n
                continue
            if c == "/" and es_regex(texto, k):
                k = saltar_regex(texto, k)
                continue
            if c == "`":
                if ignorar(k):
                    k = saltar_plantilla(texto, k)
                    continue
                fin = revisar_plantilla(k)
                k = fin
                continue
            k += 1
        # --- concatenaciones '<td>' + x ------------------------------------
        acumulado = 0
        for i, ln in enumerate(lineas, 1):
            pos = acumulado
            acumulado += len(ln) + 1
            if i in largas or "+" not in ln:
                continue
            if not re.search(r"(['\"])[^'\"\n]*<\s*/?[a-zA-Z][^'\"\n]*\1", ln):
                continue
            s = ln.strip()
            if s.startswith(("//", "*")):
                continue
            reportar_trozos("XSS-CONCAT", pos, trozos_dinamicos(s), "concatenacion que arma HTML")
        # --- CSV -------------------------------------------------------------
        csv = [mm.start() for mm in re.finditer(r"text/csv|\.csv['\"`]", texto, re.I)
               if not ignorar(mm.start())]
        if csv and not neutraliza_csv(texto) and not (csv_compartido and re.search(
                r"csvSafe|safeCsv|neutraliz|sanitizeCsv", texto, re.I)):
            h("CSV-SIN-NEUTRALIZAR", rel, num_linea(texto, csv[0]),
              "exporta a CSV y nada antepone ' a los valores que empiezan con = + - @", tab)
        # --- recursos externos ----------------------------------------------
        for m in re.finditer(r"(?:src|href|action)\s*=\s*[\"'](?:https?:)?//(?!localhost|127\.0\.0\.1)([^\"'/]+)"
                             r"|url\(\s*[\"']?https?://([^)\"'/]+)|fetch\(\s*[`\"']https?://([^`\"'/]+)"
                             r"|\.src\s*=\s*[`\"']https?://([^`\"'/]+)|L\.tileLayer\s*\(", texto):
            if ignorar(m.start()):
                continue
            dominio = m.group(1) or m.group(2) or m.group(3) or m.group(4) or "tileLayer"
            if m.group(0).startswith("href") and re.search(r"<a\s[^>]*$", texto[max(0, m.start() - 300):m.start()]):
                continue  # un enlace <a href> no carga nada
            h("EXTERNO", rel, num_linea(texto, m.start()),
              f"carga un recurso de `{dominio}`: el navegador de cada usuario le manda su IP", tab)
        # --- JS inline y manejadores ------------------------------------------
        if rel.endswith((".html", ".htm")):
            inline = len(re.findall(r"<script(?![^>]*\bsrc=)[^>]*>\s*\S", texto, re.I))
            onattr = len(re.findall(r"\son[a-z]+\s*=\s*[\"'\\]", texto, re.I))
            if inline or onattr:
                h("JS-INLINE", rel, 1, f"{inline} bloque(s) <script> inline y {onattr} atributo(s) on*=: "
                  "exigen 'unsafe-inline' en la CSP", tab)
        # --- fetch -----------------------------------------------------------
        for m in re.finditer(r"\bfetch\s*\(", texto):
            if ignorar(m.start()):
                continue
            ln = num_linea(texto, m.start())
            ventana = "\n".join(lineas[ln - 1:ln + 14])
            if re.search(r"\.ok\b|\.status\b|throwIfNot|checkStatus|assertOk", ventana):
                continue
            f = funcion_que_contiene(funcs, m.start())
            if f and re.search(r"\.ok\b|\.status\b", texto[f[2]:f[3]]):
                continue
            h("FETCH-SIN-OK", rel, ln, "fetch sin revisar r.ok/status: un 404 o 500 se trata como dato", tab)
        fetches = [m.start() for m in re.finditer(r"\bfetch\s*\(", texto) if not ignorar(m.start())]
        if fetches and not re.search(r"AbortController|AbortSignal\.timeout|signal\s*:", texto):
            h("FETCH-SIN-TIMEOUT", rel, num_linea(texto, fetches[0]),
              f"{len(fetches)} fetch sin AbortController ni timeout: si el servidor no contesta, el tablero "
              "se queda cargando para siempre", tab)
        # catalogos (objetos o arreglos en MAYUSCULAS) para comparar entre archivos
        for m in re.finditer(r"(?:const|let|var)\s+([A-Z][A-Z0-9_]{3,})\s*=\s*([\[{])", texto):
            if ignorar(m.start()) or m.group(1) in ("CONFIG", "TEXTOS", "I18N", "TXT", "LANG"):
                continue
            ini = m.end()
            fin = saltar_llaves(texto, ini) if m.group(2) == "{" else texto.find("];", ini)
            cuerpo = texto[ini:fin]
            if 200 < len(cuerpo) < 200_000:
                CATALOGOS[m.group(1)].append((rel, num_linea(texto, m.start()), re.sub(r"\s+", "", cuerpo)))
        # --- catch silencioso -------------------------------------------------
        for m in re.finditer(r"catch\s*(\([^)]*\))?\s*\{\s*(//[^\n]*\s*|/\*.*?\*/\s*)?"
                             r"(console\.\w+\([^;{}]*\);?\s*)?(return[^;{}]*;?\s*)?\}"
                             r"|\.catch\(\s*(\(\s*[\w$]*\s*\)|[\w$]+)\s*=>\s*(\{\s*\}|null|undefined|\[\]|\{\}|0|''|\"\"|"
                             r"console\.\w+\([^)]*\))\s*\)", texto, re.S):
            if ignorar(m.start()):
                continue
            h("CATCH-SILENCIOSO", rel, num_linea(texto, m.start()),
              f"el error se traga sin aviso en pantalla: `{corto(m.group(0), 70)}`", tab)
        # --- storage sin try -------------------------------------------------
        for m in re.finditer(r"\b(localStorage|sessionStorage)\s*(\.\s*(getItem|setItem|removeItem)|\[)", texto):
            if ignorar(m.start()):
                continue
            ln = num_linea(texto, m.start())
            atras = "\n".join(lineas[max(0, ln - 8):ln])
            f = funcion_que_contiene(funcs, m.start())
            dentro = texto[f[2]:m.start()] if f else ""
            if not re.search(r"\btry\s*\{", atras) and not re.search(r"\btry\s*\{", dentro):
                h("STORAGE-SIN-TRY", rel, ln, "localStorage/sessionStorage fuera de try/catch: en modo privado "
                  "o con almacenamiento bloqueado truena el tablero", tab)
        # --- fechas ----------------------------------------------------------
        for m in re.finditer(r"new\s+Date\s*\(\s*(['\"`]\d{4}-\d{2}-\d{2}['\"`]|"
                             r"[A-Za-z_$][\w$.]*(?:\[[^\]]{1,30}\])?(?:\.[\w$]+)*)\s*\)|Date\.parse\s*\(\s*([^)]*)\)",
                             texto):
            if ignorar(m.start()):
                continue
            arg = m.group(1) or m.group(2) or ""
            if not re.search(r"^['\"`]\d{4}|fecha|date|dia|day|_dt|dt\b|periodo|period|mes|month|"
                             r"semana|week|corte|cutoff|eta|etd|updated|generat|str|iso|ymd", arg, re.I):
                continue
            if re.search(r"T00|T12|\+ *['\"`]T|'T'|\"T\"", texto[max(0, m.start() - 80):m.start() + 80]):
                continue
            h("FECHA-UTC", rel, num_linea(texto, m.start()),
              f"`{corto(m.group(0), 60)}`: una fecha AAAA-MM-DD se lee como UTC y en Mexico cae un dia antes", tab)
        for m in re.finditer(r"toISOString\(\)\s*\.(slice|substring|substr)\(\s*0\s*,\s*10\s*\)|"
                             r"toISOString\(\)\s*\.split\(\s*['\"]T['\"]\s*\)", texto):
            if not ignorar(m.start()):
                h("FECHA-UTC", rel, num_linea(texto, m.start()),
                  "toISOString() recorta la fecha en UTC: despues de las 18:00 en Mexico da el dia siguiente", tab)
        # --- "actualizado" con la hora del navegador --------------------------
        for m in re.finditer(r"new\s+Date\s*\(\s*\)|Date\.now\s*\(\s*\)", texto):
            if ignorar(m.start()):
                continue
            ln = num_linea(texto, m.start())
            ventana = "\n".join(lineas[max(0, ln - 4):ln + 3])
            if re.search(r"updat|actualiz|[uú]ltima|last\s*refresh|as\s+of|corte|refreshed|fecha\s+de\s+datos",
                         ventana, re.I) and re.search(r"textContent|innerText|innerHTML|\.text\(", ventana):
                h("ACTUALIZADO-NAVEGADOR", rel, ln, "muestra 'actualizado' con la hora del navegador, no con la "
                  "fecha del dato (meta.json)", tab)
        # --- objetos de configuracion ---------------------------------------
        for m in re.finditer(r"(?:const|let|var|window\.)\s*([A-Z][A-Z0-9_]{2,})\s*=\s*\{", texto):
            nombre = m.group(1)
            ini = m.end()
            fin = saltar_llaves(texto, ini)
            claves = set(re.findall(r"([A-Za-z_$][\w$]*)\s*:", texto[ini:fin]))
            claves |= set(re.findall(r"['\"]([^'\"]+)['\"]\s*:", texto[ini:fin]))
            claves |= set(re.findall(r"\b" + re.escape(nombre) + r"\.([A-Za-z_$][\w$]*)\s*=[^=]", texto))
            reportadas = set()
            for u in re.finditer(r"\b" + re.escape(nombre) + r"((?:\??\.[A-Za-z_$][\w$]*)+)", texto):
                if ignorar(u.start()) or u.start() < fin and u.start() > m.start():
                    continue
                camino = [c for c in re.split(r"\??\.", u.group(1)) if c]
                faltan = [c for c in camino if c not in claves and c not in
                          ("length", "map", "forEach", "filter", "find", "includes", "keys", "values",
                           "entries", "toString", "join", "slice", "indexOf", "push", "some", "every")]
                if faltan and faltan[0] not in reportadas and not re.match(r"\s*=[^=]", texto[u.end():u.end() + 3]):
                    reportadas.add(faltan[0])
                    h("CONFIG-CLAVE-FALTA", rel, num_linea(texto, u.start()),
                      f"`{nombre}{u.group(1)}` usa `{faltan[0]}`, que no esta definida en `{nombre}`: "
                      "vale undefined en silencio", tab)
        # --- respaldo silencioso a datos pegados -----------------------------
        pegados = [x for x in hallazgos if x["archivo"] == rel and x["familia"] == "DATOS-PEGADOS"]
        nombres_peg = set(re.findall(r"`([\w$]+)`", " ".join(x["detalle"] for x in pegados)))
        for nm in nombres_peg:
            for m in re.finditer(r"catch|\.ok\b|!\s*[\w$.]+\.length|length\s*===?\s*0|\|\|", texto):
                if ignorar(m.start()):
                    continue
                ventana = texto[m.start():m.start() + 400]
                if re.search(r"\b" + re.escape(nm) + r"\b", ventana):
                    h("RESPALDO-SILENCIOSO", rel, num_linea(texto, m.start()),
                      f"si la API falla o viene vacia, cae a `{nm}` (datos pegados y viejos): revisar que avise", tab)
                    break
        # --- comentarios con informacion interna -----------------------------
        rx_nombres = (r"\b(" + "|".join(map(re.escape, nombres_equipo)) + r")\b") if nombres_equipo else None
        for m in re.finditer(r"(?<![:\"'\w])//[^\n]*|/\*.*?\*/|<!--.*?-->", texto, re.S):
            if ignorar(m.start()):
                continue
            c = m.group(0)
            if len(c) > 3000:
                continue
            motivo = []
            if rx_nombres and re.search(rx_nombres, c):
                motivo.append("nombre de persona")
            if re.search(r"pipeline|notebook|lakehouse|workspace|sharepoint|onelake|gateway|\\\\\\\\|"
                         r"\bN:\\|@[\w.-]+\.(com|mx)\b|\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b|password|contrase",
                         c, re.I):
                motivo.append("nombre interno de sistema, ruta o credencial")
            if re.search(r"\b(TODO|FIXME|XXX|HACK)\b", c):
                motivo.append("pendiente")
            if motivo:
                h("COMENTARIO-INTERNO", rel, num_linea(texto, m.start()),
                  f"{', '.join(motivo)} en un comentario que llega al navegador: `{corto(c, 70)}`", tab)
        # --- datos personales -------------------------------------------------
        pers = re.compile(r"\b(dateOfBirth|birth\w*|dob|fechaNac\w*|nacimiento|curp|nss|ssn|genero|gender|"
                          r"sexo|salar\w*|sueldo|domicilio|homeAddress|telefono\w*|phone\w*|personalEmail|"
                          r"rfc\w*|imss\w*|cuenta\w*Banc\w*|clabe)\b", re.I)
        usados = defaultdict(list)
        for m in pers.finditer(texto):
            if not ignorar(m.start()):
                usados[m.group(1)].append(num_linea(texto, m.start()))
        if usados:
            h("DATOS-PERSONALES", rel, min(v[0] for v in usados.values()),
              "campos personales en el codigo: " + ", ".join(f"{k} (l. {', '.join(map(str, v[:4]))})"
                                                             for k, v in usados.items())
              + ". Revisar: ¿el JSON los manda aunque la pagina no los muestre? ¿el tablero tiene grupo de AD propio?",
              tab)
    for nombre, defs in CATALOGOS.items():
        if len({r for r, _, _ in defs}) >= 2 and len({c for _, _, c in defs}) > 1:
            h("COPIA-DIVERGENTE", defs[0][0], defs[0][1],
              f"el catalogo `{nombre}` esta en {len(defs)} archivos y no coincide entre ellos: "
              + ", ".join(f"{r}:{l}" for r, l, _ in defs[:8]) + ". Unificarlo en un archivo compartido",
              tablero_de(defs[0][0]))
    # --- copias de funciones entre archivos -----------------------------------
    for nombre, defs in funciones_por_nombre.items():
        if len({r for r, _, _ in defs}) < 2 or len(nombre) < 3:
            continue
        if nombre in {"init", "main", "render", "load", "update", "draw", "setup", "run", "start", "onLoad",
                      "handler", "fn", "tick", "resize", "toggle", "reset", "apply", "build", "refresh"}:
            continue
        cuerpos = {c for _, _, c in defs}
        lugares = ", ".join(f"{r}:{l}" for r, l, _ in defs[:8])
        if len(cuerpos) > 1:
            h("COPIA-DIVERGENTE", defs[0][0], defs[0][1],
              f"`{nombre}` esta copiada en {len(defs)} archivos y las copias ya no son iguales "
              f"({len(cuerpos)} versiones): {lugares}", tablero_de(defs[0][0]))
        elif len(defs) >= 3:
            h("COPIA-IDENTICA", defs[0][0], defs[0][1],
              f"`{nombre}` esta copiada igual en {len(defs)} archivos: {lugares}", tablero_de(defs[0][0]))

# --------------------------------------------------------------------------
# Backend (Python)
# --------------------------------------------------------------------------

def funciones_py(texto):
    lineas = texto.split("\n")
    funcs = []
    for i, ln in enumerate(lineas):
        m = re.match(r"(\s*)def\s+(\w+)\s*\(", ln)
        if not m:
            continue
        ind = len(m.group(1))
        fin = len(lineas)
        for j in range(i + 1, len(lineas)):
            s = lineas[j]
            if s.strip() and (len(s) - len(s.lstrip())) <= ind and not s.lstrip().startswith(("#", ")")):
                fin = j
                break
        deco = []
        k = i - 1
        while k >= 0 and lineas[k].strip().startswith("@"):
            deco.append(lineas[k].strip())
            k -= 1
        funcs.append({"nombre": m.group(2), "ini": i + 1, "fin": fin, "cuerpo": "\n".join(lineas[i:fin]),
                      "deco": deco})
    return funcs

def revisar_backend(root, archivos):
    todos_py = "\n".join(t for _, t in archivos)
    filtros = set()
    for rel, texto in archivos:
        for f in funciones_py(texto):
            if re.search(r"permit|allow|safe|estatic|filtro|valid|_send_cached|servir_seguro|blocked|bloque",
                         f["nombre"], re.I) and not re.search(r"encabezad|header|after_request", f["nombre"], re.I):
                filtros.add(f["nombre"])
    for rel, texto in archivos:
        lineas = texto.split("\n")
        funcs = funciones_py(texto)
        # --- rutas que sirven archivos sin filtro ---------------------------
        for f in funcs:
            if f["nombre"] in filtros:
                continue
            for m in re.finditer(r"\b(send_from_directory|send_file)\s*\(", f["cuerpo"]):
                c = f["cuerpo"]
                fin = m.end()
                prof = 1
                while fin < len(c) and prof:
                    prof += {"(": 1, ")": -1}.get(c[fin], 0)
                    fin += 1
                args = [a.strip() for a in dividir_nivel0(c[m.end():fin - 1], ",") if a.strip()]
                archivo = args[1] if m.group(1) == "send_from_directory" and len(args) > 1 else (args[0] if args else "")
                if re.fullmatch(r"[rfbu]?['\"][^'\"{}]+['\"]", archivo):
                    continue  # archivo fijo, p. ej. "index.html"
                llama_filtro = any(re.search(r"\b" + re.escape(x) + r"\s*\(", f["cuerpo"])
                                   for x in filtros)
                if not llama_filtro:
                    ruta = next((d for d in f["deco"] if "route" in d), "")
                    ln = f["ini"] + f["cuerpo"][:m.start()].count("\n")
                    h("RUTA-SIN-FILTRO", rel, ln,
                      f"`{f['nombre']}` {corto(ruta, 60)} sirve un archivo variable "
                      f"sin pasar por {', '.join(sorted(filtros)) or 'ningun filtro'}", "(servidor)")
        # --- el filtro resiste Windows --------------------------------------
        # Se evalua el filtro COMPLETO del archivo: todas las funciones de filtro juntas (una puede
        # llamar a otra) y las constantes de modulo que usan (p. ej. una regex compilada afuera).
        del_filtro = [f for f in funcs if f["nombre"] in filtros and not f["nombre"].startswith("_send")
                      and re.search(r"endswith|startswith|\bin\b|split\(|search\(|match\(", f["cuerpo"])]
        if del_filtro:
            c = "\n".join(f["cuerpo"] for f in del_filtro)
            for nombre in set(re.findall(r"\b([A-Z_][A-Z0-9_]{2,})\b", c)):
                d = re.search(r"^" + re.escape(nombre) + r"\s*=.*$", texto, re.M)
                if d:
                    c += "\n" + d.group(0)
            falta = []
            if not re.search(r"['\"]:['\"]|['\"]:\$|:\\\$|ntfs|\$INDEX|\$DATA|\[[^\]\n]*:[^\]\n]*\]", c, re.I):
                falta.append("no rechaza ':' (flujos NTFS: `data::$INDEX_ALLOCATION`)")
            if not re.search(r"endswith\(\s*\(?\s*['\"][. ]|rstrip\(|\[-1\]\s*in\s*['\"][. ]|['\"]\.\s*['\"]\s*\)|"
                             r"\\s\]\$|\[\. \]\$|\[ \.\]\$|\[\\s\.\]\$|\[\.\\s\]\$", c):
                falta.append("no rechaza tramos que terminan en punto o espacio (`data./`)")
            if not re.search(r"realpath|\.resolve\(|abspath|safe_join|commonpath|samefile", c):
                falta.append("decide sobre el texto de la URL, no sobre la ruta real (realpath)")
            if falta:
                h("FILTRO-WINDOWS", rel, del_filtro[0]["ini"],
                  f"filtro de estaticos ({', '.join(f['nombre'] for f in del_filtro)}): " + "; ".join(falta),
                  "(servidor)")
        # --- host por defecto, debug ------------------------------------------
        for i, ln in enumerate(lineas, 1):
            s = ln.strip()
            if s.startswith("#"):
                continue
            if re.search(r"['\"]0\.0\.0\.0['\"]|['\"]::['\"]|host\s*=\s*['\"]['\"]", ln):
                h("HOST-TODAS", rel, i, f"escucha en todas las interfaces por defecto: `{corto(ln, 90)}`",
                  "(servidor)")
            if re.search(r"debug\s*=\s*True|DEBUG\s*=\s*True", ln):
                h("DEBUG", rel, i, f"debug encendido: `{corto(ln, 80)}`", "(servidor)")
        # --- CSP -------------------------------------------------------------
        for m in re.finditer(r"script-src[^;\"\n]*", texto):
            s = m.group(0)
            if "unsafe-inline" in s or "unsafe-eval" in s or re.search(r"\s\*|https?:\s|data:", s):
                h("CSP-UNSAFE", rel, num_linea(texto, m.start()),
                  f"`{corto(s, 80)}`: con esto la CSP no frena los XSS", "(servidor)")
        for m in re.finditer(r"(default|img|script|style|font|connect|frame|media)-src[^;\"\n]*"
                             r"(https?://[^\s;\"']+|\s\*(?=[\s;\"'])|https?:(?=[\s;\"']))", texto):
            h("CSP-EXTERNO", rel, num_linea(texto, m.start()),
              f"la CSP permite origen externo: `{corto(m.group(0), 90)}`", "(servidor)")
        if re.search(r"Content-Security-Policy", texto):
            for directiva in ("default-src", "object-src", "frame-ancestors"):
                if directiva not in texto:
                    h("CSP-UNSAFE", rel, num_linea(texto, texto.find("Content-Security-Policy")),
                      f"la CSP no define `{directiva}`", "(servidor)")
        # --- regex de nombres permisivas --------------------------------------
        for m in re.finditer(r"re\.compile\(\s*r?(['\"])(.*?)\1", texto):
            patron = m.group(2)
            if patron.endswith("$") and not patron.endswith("\\$"):
                var = re.search(r"(\w+)\s*=\s*re\.compile", texto[max(0, m.start() - 60):m.start() + 12])
                usa_match = var and re.search(re.escape(var.group(1)) + r"\.(match|search)\(", texto)
                if usa_match or not var:
                    h("REGEX-PERMISIVA", rel, num_linea(texto, m.start()),
                      f"`{corto(patron, 60)}` termina en `$`, que acepta un salto de linea final"
                      + ("; `\\d` acepta digitos Unicode (usar [0-9] o re.ASCII)" if "\\d" in patron else "")
                      + ": usar fullmatch", "(servidor)")
            elif "\\d" in patron and "fullmatch" in texto and "re.ASCII" not in texto and "re.A" not in texto:
                h("REGEX-PERMISIVA", rel, num_linea(texto, m.start()),
                  f"`{corto(patron, 60)}`: `\\d` acepta digitos Unicode (usar [0-9] o re.ASCII)", "(servidor)")
        # --- estado global sin lock ------------------------------------------
        globales = set(re.findall(r"^([A-Za-z_]\w*)\s*(?::[^=\n]+)?=\s*(?:\{|\[\]|dict\(\)|set\(\)|"
                                  r"OrderedDict\(\)|defaultdict\(|Counter\(|0\b|None\b)", texto, re.M))
        hay_lock = bool(re.search(r"threading\.(R?Lock|Semaphore)|\bR?Lock\(\)", texto))
        for g in sorted(globales):
            for f in funcs:
                patron = (r"\b" + re.escape(g) + r"(\[[^\]]*\]\s*(\+|-)?=(?!=)|\.(append|update|pop|popitem|"
                          r"setdefault|clear|add|discard|remove|extend|move_to_end)\(|\s*(\+|-)=)")
                if not re.search(r"global\s+[\w, ]*\b" + re.escape(g) + r"\b", f["cuerpo"]):
                    patron = patron.replace(r"|\s*(\+|-)=)", ")")
                m = re.search(patron, f["cuerpo"])
                if not m:
                    continue
                previo = f["cuerpo"][:m.start()]
                if hay_lock and re.search(r"with\s+[\w.]*(lock|mutex|_lk)\w*", previo, re.I):
                    continue
                ln = f["ini"] + previo.count("\n")
                h("GLOBAL-SIN-LOCK", rel, ln,
                  f"`{g}` es estado global y `{f['nombre']}` lo modifica sin lock (waitress atiende en varios hilos)",
                  "(servidor)")
                break
        # --- ETag ------------------------------------------------------------
        con_etag = [f for f in funcs if re.search(r"If-None-Match|if_none_match", f["cuerpo"])]
        if len(con_etag) >= 3:
            h("ETAG-DUPLICADO", rel, con_etag[0]["ini"],
              f"la logica de ETag esta copiada en {len(con_etag)} funciones: "
              + ", ".join(f"{f['nombre']}:{f['ini']}" for f in con_etag[:10]), "(servidor)")
        for f in con_etag:
            c = f["cuerpo"]
            p_etag = min([m.start() for m in re.finditer(r"If-None-Match|if_none_match", c)] or [len(c)])
            lectura = re.search(r"\bopen\(|\.read\w*\(|json\.loads?\(|_leer\w*\(|_descargar\w*\(|read_bytes|read_text|"
                                r"send_from_directory|send_file|_cargar\w*\(|_load\w*\(", c)
            if lectura and lectura.start() < p_etag:
                h("ETAG-LEE-ANTES", rel, f["ini"] + c[:lectura.start()].count("\n"),
                  f"`{f['nombre']}` lee el archivo antes de decidir el 304", "(servidor)")
        # --- cache de datos --------------------------------------------------
        cache_vals = [(num_linea(texto, m.start()), m.group(1)) for m in
                      re.finditer(r"Cache-Control['\"]\s*[\],]\s*=?\s*f?['\"]([^'\"]+)", texto)]
        if ("@app.route" in texto or "add_url_rule" in texto) and "/api" in texto:
            if not any("private" in v and "no-store" in v for _, v in cache_vals):
                h("CACHE-API", rel, cache_vals[0][0] if cache_vals else 1,
                  "ninguna respuesta de datos pone `Cache-Control: private, no-store`; valores que usa: "
                  + (", ".join(sorted({v for _, v in cache_vals})[:6]) or "ninguno"), "(servidor)")
            for ln, v in cache_vals:
                if re.search(r"public|max-age=[1-9]", v):
                    h("CACHE-API", rel, ln, f"`{v}`: si esta respuesta lleva datos, quedan en caches compartidos",
                      "(servidor)")
                if "no-store" in v and "private" not in v:
                    h("NO-STORE-DATOS", rel, ln, f"`{v}` obliga a bajar el JSON completo en cada carga; "
                      "para datos grandes usar no-cache + ETag", "(servidor)")
        # --- compresion ------------------------------------------------------
        if re.search(r"flask_compress|Compress\(", texto) and "send_from_directory" in texto:
            h("COMPRESION", rel, num_linea(texto, texto.find("Compress")),
              "Flask-Compress no comprime lo que sale de send_from_directory (HTML y estaticos) y vuelve a "
              "comprimir cada respuesta grande en cada peticion si no se cachea", "(servidor)")
        # --- bitacora --------------------------------------------------------
        if "@app.route" in texto or "Flask(" in texto:
            if not re.search(r"^\s*import logging|^\s*from logging|getLogger", texto, re.M):
                prints = len(re.findall(r"^\s*print\(", texto, re.M))
                h("SIN-BITACORA", rel, 1, f"sin `logging` ({prints} print): no queda registro de quien consulto "
                  "que datos", "(servidor)")
        # --- codigo muerto ---------------------------------------------------
        for m in re.finditer(r"^([A-Z][A-Z0-9_]+)\s*=\s*(set\(\)|\[\]|\{\}|frozenset\(\))\s*$", texto, re.M):
            g = m.group(1)
            if not re.search(r"\b" + g + r"(\.(add|append|update|extend|setdefault)\(|\[[^\]]+\]\s*=(?!=)|\s*[|+]=)",
                             todos_py):
                h("CODIGO-MUERTO", rel, num_linea(texto, m.start()),
                  f"`{g}` siempre esta vacio: nadie le agrega nada", "(servidor)")
        # --- archivos que el servidor busca y no existen ---------------------
        # (los .json los publica el pipeline en la carpeta de datos: no se buscan aqui)
        for m in re.finditer(r"(?:exists|isfile|open)\s*\([^)\n]*?['\"]([\w\-]+\.(?:txt|flag|lock|py|done|ok))['\"]",
                             texto):
            nombre = m.group(1)
            if not any(Path(r).name == nombre for r in _TODOS):
                h("REF-INEXISTENTE", rel, num_linea(texto, m.start()),
                  f"el servidor busca `{nombre}`: no esta en esta carpeta (¿lo publica un pipeline, o ya no existe?)",
                  "(servidor)")

_TODOS = []

# --------------------------------------------------------------------------
# Proyecto, dependencias, referencias, git
# --------------------------------------------------------------------------

def revisar_proyecto(root, todos, textos):
    nombres = {Path(r).name.lower() for r in todos}
    dirs = set()
    for r in todos:
        for par in Path(r).parents:
            if str(par) not in (".", ""):
                dirs.add(par.name.lower())
    for rel in todos:
        if Path(rel).name.lower().startswith("requirements") and rel.endswith(".txt"):
            texto = textos.get(rel) or (root / rel).read_text(encoding="utf-8", errors="replace")
            fijas = []
            for i, ln in enumerate(texto.split("\n"), 1):
                s = ln.split("#")[0].strip()
                if not s or s.startswith("-"):
                    continue
                if "==" not in s:
                    h("DEP-SIN-FIJAR", rel, i, f"`{s}` sin version exacta", "(servidor)")
                else:
                    fijas.append(s)
            if fijas:
                h("DEPENDENCIAS", rel, 1, "revisar cada una contra vulnerabilidades (osv/pip-audit o a mano): "
                  + ", ".join(fijas), "(servidor)")
    rx = re.compile(r"(?<![\w/.-])([\w-]+\.(?:py|md|bat|sh|ps1|txt|yml|yaml|toml|cfg|ini))\b")
    for rel, texto in textos.items():
        if not rel.endswith((".py", ".md", ".bat", ".sh", ".ps1", ".txt", ".html", ".js")):
            continue
        faltan = {}
        for m in rx.finditer(texto):
            nombre = m.group(1)
            if nombre.lower() in nombres or nombre.lower() in {"requirements.txt", "setup.py", "readme.md",
                                                               "package.json", "robots.txt"}:
                continue
            if re.match(r"(test_|conftest)", nombre) or rel.endswith((".html", ".js")) and not nombre.endswith(".py"):
                continue
            faltan.setdefault(nombre, num_linea(texto, m.start()))
        if rel.endswith(".md"):
            for m in re.finditer(r"`([a-z][\w-]{2,})/`", texto):
                if m.group(1).lower() not in dirs and m.group(1) not in {"data", "notebooks", "fuentes", "build",
                                                                         "scripts", "api", "shared", "vendor", "pages"}:
                    faltan.setdefault(m.group(1) + "/", num_linea(texto, m.start()))
        for m in re.finditer(r"commit\s+`?([0-9a-f]{7,40})\b", texto, re.I):
            faltan.setdefault("commit " + m.group(1), num_linea(texto, m.start()))
        for nombre, ln in list(faltan.items())[:15]:
            h("REF-INEXISTENTE", rel, ln, f"menciona `{nombre}`, que no esta en esta carpeta "
              "(si es un commit: verificar que exista en el repo)", tablero_de(rel))
    for rel, texto in textos.items():
        n = texto.count("\n") + 1
        if n > 2000 and rel.endswith((".py", ".html", ".js")):
            h("MONOLITO", rel, 1, f"{<unidad-compartida>,} lineas en un solo archivo", tablero_de(rel))
    temas = defaultdict(list)
    for rel, texto in textos.items():
        m = re.search(r":root\s*\{([^}]{200,})\}", texto)
        if m and rel.endswith((".html", ".css")):
            temas[frozenset(re.findall(r"(--[\w-]+)\s*:", m.group(1)))].append(rel)
    for vars_, rels in temas.items():
        if len(rels) >= 3 and len(vars_) >= 5:
            h("COPIA-IDENTICA", rels[0], 1, f"el tema CSS (:root) esta copiado en {len(rels)} archivos: "
              + ", ".join(rels[:6]), tablero_de(rels[0]))
    readme = [r for r in todos if Path(r).name.lower() == "readme.md" and "/" not in r]
    if not readme or (root / readme[0]).stat().st_size < 200:
        h("PROYECTO", ".", 1, "README vacio o ausente", "(raiz)")
    if not any(re.search(r"(^|/)(tests?/|test_\w+\.py$|\w+_test\.py$)", r) for r in todos):
        h("PROYECTO", ".", 1, "sin pruebas automaticas (tests/ o test_*.py)", "(raiz)")
    if not (root / ".github" / "workflows").is_dir():
        h("PROYECTO", ".", 1, "sin CI en .github/workflows (ni revisar-datos.yml)", "(raiz)")
    if not any(Path(r).name in {".flake8", "ruff.toml", "pyproject.toml", ".eslintrc", ".eslintrc.json",
                                "eslint.config.js", "setup.cfg"} for r in todos):
        h("PROYECTO", ".", 1, "sin configuracion de linter (ruff/flake8/eslint)", "(raiz)")
    for rel in todos:
        p = root / rel
        ext = p.suffix.lower()
        try:
            tam = p.stat().st_size
        except OSError:
            continue
        if tam > 10 * 1024 * 1024:
            h("ARCHIVO-GRANDE", rel, 1, f"{tam/1024/1024:,.1f} MB", tablero_de(rel))
        partes = rel.split("/")
        if ext in EXT_DATOS and "data" in [x.lower() for x in partes[:-1]]:
            base = root
            con = (root / "CONTRATO.md").exists()
            for parte in partes[:-1]:
                base = base / parte
                if (base / "CONTRATO.md").exists():
                    con = True
            if not con:
                h("DATA-SIN-CONTRATO", rel, 1, f"archivo de datos ({tam/1024:,.0f} KB) en data/ sin CONTRATO.md; "
                  "no se leyo", tablero_de(rel))

def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        return r.stdout if r.returncode == 0 else None
    except Exception:
        return None

def revisar_git(root, todos):
    if git(root, "rev-parse", "--show-toplevel") is None:
        h("LIMITE", ".", 1, "no es repo de git: historial, mensajes y .gitignore no se revisaron", "(raiz)")
        return
    log = git(root, "log", "--all", "--format=%h%x09%s") or ""
    for ln in log.splitlines():
        if "\t" not in ln:
            continue
        sha, msg = ln.split("\t", 1)
        if re.fullmatch(r"\s*(v(ersion|ersi[oó]n)?\s*\d*[\w .-]{0,12}|update\w*|fix|wip|cambios?|changes?|test|"
                        r"prueba|\.|-|x|asdf|commit|subida|upload\w*)\s*", msg, re.I):
            h("GIT-MENSAJE", ".", 1, f"{sha}: mensaje sin informacion (`{corto(msg, 40)}`)", "(git)")
        if re.search(r"token|secret|password|contrase|api[_ -]?key|credencial|\.env\b", msg, re.I):
            h("GIT-MENCION-SECRETO", ".", 1, f"{sha}: `{corto(msg, 80)}`: confirmar que ese secreto se revoco",
              "(git)")
    directos = git(root, "rev-list", "--count", "--no-merges", "--first-parent", "HEAD")
    merges = git(root, "rev-list", "--count", "--merges", "HEAD")
    if directos and merges is not None and int(directos) > 5 and int(merges or 0) == 0:
        h("GIT-MENSAJE", ".", 1, f"{directos.strip()} commits directos a la rama y ningun merge: sin PR ni revision",
          "(git)")
    hist = git(root, "log", "--all", "--diff-filter=A", "--name-only", "--format=") or ""
    presentes = set(todos)
    vistos = set()
    for nombre in hist.splitlines():
        nombre = nombre.strip()
        if not nombre or nombre in vistos:
            continue
        vistos.add(nombre)
        ext = Path(nombre).suffix.lower()
        if ext in EXT_DATOS or Path(nombre).name.lower() == ".env" or ext in {".pem", ".key", ".pfx", ".p12"}:
            if "/vendor/" in "/" + nombre or Path(nombre).name in {"package.json", "package-lock.json",
                                                                   "manifest.json", "tsconfig.json"}:
                continue
            estado = "sigue en HEAD" if nombre in presentes else "borrado, pero sigue en el historial"
            h("GIT-HISTORIAL-DATOS", nombre, 1, f"{estado}; no se leyo el contenido", "(git)")
    for tab in sorted({tablero_de(r) for r in todos if tablero_de(r) != "(raiz)"}):
        prueba = f"{tab}/data/dashboard/prueba.json"
        if git(root, "check-ignore", "-q", prueba) is None:
            h("GITIGNORE-DATA", ".gitignore", 1, f"`{prueba}` no queda ignorado: falta `**/data/`", tab)
            break

# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ruta")
    ap.add_argument("--json", help="guardar los hallazgos en este archivo")
    ap.add_argument("--nombres", default="Haz,otra persona,otra persona,otra persona",
                    help="nombres de personas que no deben ir en comentarios")
    a = ap.parse_args()
    root = Path(a.ruta).resolve()
    if not root.is_dir():
        print(f"No existe la carpeta: {root}")
        return 2

    todos = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SALTAR_DIRS]
        for fn in fns:
            todos.append(os.path.relpath(os.path.join(dp, fn), root).replace("\\", "/"))
    if len(todos) > 20000:
        print(f"{len(todos)} archivos: demasiados. Revisa una subcarpeta.")
        return 2
    _TODOS.extend(todos)

    textos = {}
    front, back = [], []
    saltados = 0
    for rel in todos:
        ext = Path(rel).suffix.lower()
        if ext not in EXT_FRONT | EXT_BACK | EXT_DOCS and Path(rel).name.lower() not in {"web.config"}:
            continue
        if ext in EXT_FRONT and es_vendor(rel):
            saltados += 1
            continue
        try:
            texto = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            h("LIMITE", rel, 1, f"no se pudo leer: {e}")
            continue
        textos[rel] = texto
        if ext in EXT_FRONT:
            front.append((rel, texto))
        elif ext in EXT_BACK:
            back.append((rel, texto))

    escapadores = {"esc", "escape", "escapeHtml", "escapeHTML", "escHtml", "htmlEscape", "encodeHTML",
                   "sanitize", "sanitizeHtml", "DOMPurify.sanitize", "sanitizeHTML"}
    generadores = set()
    for rel, texto in front:
        for f in funciones_js(texto):
            if not f[0]:
                continue
            cuerpo = texto[f[2]:f[3]]
            if re.search(r"&lt;|&amp;|&#0?60;|&#x3c;", cuerpo, re.I) and len(cuerpo) < 800 \
                    and "replace" in cuerpo:
                escapadores.add(f[0])
            elif "`" in cuerpo and re.search(r"<\s*[a-zA-Z]", cuerpo):
                generadores.add(f[0])
    generadores -= escapadores

    revisar_frontend(root, front, escapadores, generadores,
                     [x.strip() for x in a.nombres.split(",") if x.strip()])
    revisar_backend(root, back)
    revisar_proyecto(root, todos, textos)
    revisar_git(root, todos)
    if saltados:
        h("LIMITE", ".", 1, f"{saltados} archivo(s) de librerias de terceros (vendor, .min.js) no se analizaron")

    tableros = sorted({tablero_de(r) for r, _ in front if tablero_de(r) != "(raiz)"})
    print(f"# Barrido del portal: {root.name}\n")
    print(f"{len(todos)} archivos; {len(front)} de frontend en {len(tableros)} carpetas; {len(back)} .py. "
          f"Funciones de escape detectadas: {', '.join(sorted(escapadores))}.\n")
    cuenta = defaultdict(lambda: defaultdict(int))
    for x in hallazgos:
        cuenta[x["tablero"] or "-"][x["familia"]] += 1
    print("## XSS por carpeta (todas, tambien las que dan cero)\n")
    print("| Carpeta | plantillas | concatenaciones | sinks | helpers | lee la URL |")
    print("|---|---|---|---|---|---|")
    for t in tableros + ["(raiz)"]:
        c = cuenta.get(t, {})
        print(f"| {t} | {c.get('XSS-PLANTILLA', 0)} | {c.get('XSS-CONCAT', 0)} | {c.get('XSS-SINK', 0)} | "
              f"{c.get('XSS-HELPER', 0)} | {'si' if c.get('URL-FUENTE') else 'no'} |")
    print()
    for sev in ORDEN:
        grupo = [x for x in hallazgos if x["severidad"] == sev]
        if not grupo:
            continue
        print(f"## {sev} ({len(grupo)})\n")
        por_fam = defaultdict(list)
        for x in grupo:
            por_fam[x["familia"]].append(x)
        tope = {"Alta": 80, "Media": 40}.get(sev, 12)
        for fam, xs in sorted(por_fam.items()):
            print(f"### {fam} ({len(xs)})\n")
            for x in sorted(xs, key=lambda y: (y["archivo"], y["linea"]))[:tope]:
                print(f"- `{x['archivo']}:{x['linea']}` — {corto(x['detalle'], 220)}")
            if len(xs) > tope:
                print(f"- ... y {len(xs) - tope} mas (ver --json)")
            print()
    if a.json:
        Path(a.json).write_text(json.dumps(hallazgos, ensure_ascii=False, indent=1), encoding="utf-8")
    return 1 if any(x["severidad"] == "Alta" for x in hallazgos) else 0

if __name__ == "__main__":
    sys.exit(main())
