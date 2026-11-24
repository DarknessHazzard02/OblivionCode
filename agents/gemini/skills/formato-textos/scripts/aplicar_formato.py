# aplicar_formato.py — propone (y con --aplicar, escribe) el formato de los textos del I18N de un app.js.
#
#   python aplicar_formato.py <app.js> [--reglas reglas.json] [--aplicar]
#
# reglas.json (opcional): {"frase": ["llave", ...], "etiqueta": [...], "igual": [...]}
# Sin reglas, la clase sale del nombre de la llave (ver CLASE_FRASE / CLASE_IGUAL) y todo lo demas es
# etiqueta. Imprime cada cambio para revisarlo antes de aplicarlo.
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from formato import cola, frase, proper  # noqa: E402

CLASE_FRASE = re.compile(r'(_sub|Sub|Detail|Det|degradedStructure|noData|loading|m_sin\w*|m_intentos|'
                         r'(cortes|degraded|demo|error|semi|sdd|cons)Title|faltaFuente)$')   # titulos de la banda: oraciones
# Lo que el codigo pega despues de un numero: minuscula y punto
CLASE_COLA = re.compile(r'^(k_of\w*|fueraRango|seleccionadaOculta|seleccionadasOcultas)$')
# Palabras que el codigo pega a media frase ("61 materiales", "1 of 3"): se quedan como estan
CLASE_IGUAL = re.compile(r'^(of|rows|showing|materiales|unidades|ordenes|so|archivos|renglones|envios|'
                         r'seleccionados|si|no|inmediato)$')
PAR = re.compile(r'((?:"[^"]+"|[A-Za-z_][\w]*))\s*:\s*"((?:[^"\\]|\\.)*)"')

def bloques_i18n(src):
    """Rango (inicio, fin) del objeto de cada idioma dentro de `const I18N = { es: {...}, en: {...} }`."""
    i = src.index('const I18N')
    out = {}
    for lang in ('es', 'en'):
        m = re.compile(r'\b' + lang + r'\s*:\s*\{').search(src, i)
        prof, j = 0, m.end() - 1
        while True:
            if src[j] == '{':
                prof += 1
            elif src[j] == '}':
                prof -= 1
                if prof == 0:
                    break
            elif src[j] == '"':
                j += 1
                while src[j] != '"':
                    j += 2 if src[j] == '\\' else 1
            j += 1
        out[lang] = (m.end(), j)
        i = j
    return out

def clase(llave, reglas):
    for c in ('igual', 'cola', 'frase', 'etiqueta'):
        if llave in reglas.get(c, []):
            return c
    if CLASE_COLA.match(llave):
        return 'cola'
    if CLASE_IGUAL.match(llave):
        return 'igual'
    if CLASE_FRASE.search(llave):
        return 'frase'
    return 'etiqueta'

CAMPOS_FRASE = re.compile(r'\b(medida|calculo|filtros|granularidad|purpose)\s*:\s*"((?:[^"\\]|\\.)*)"')
LISTAS_FRASE = re.compile(r'\b(transformations|measures|rules|limitations)\s*:\s*\[(.*?)\]', re.S)
CADENA = re.compile(r'"((?:[^"\\]|\\.)*)"')

def config_frases(src, cambios):
    """CONFIG.visuals[..].info y CONFIG.documentation: todo es frase (mayuscula inicial y punto)."""
    a, b = src.index('const CONFIG'), src.index('const I18N')
    bloque = src[a:b]

    def campo(m):
        nuevo = frase(m.group(2))
        if nuevo != m.group(2):
            cambios.append(('cfg', m.group(1), 'frase', m.group(2), nuevo))
        return m.group(0).replace('"' + m.group(2) + '"', '"' + nuevo + '"', 1)

    def lista(m):
        def elem(e):
            nuevo = frase(e.group(1))
            if nuevo != e.group(1):
                cambios.append(('cfg', m.group(1), 'frase', e.group(1), nuevo))
            return '"' + nuevo + '"'
        return m.group(1) + ': [' + CADENA.sub(elem, m.group(2)) + ']'
    bloque = CAMPOS_FRASE.sub(campo, bloque)
    bloque = LISTAS_FRASE.sub(lista, bloque)
    return src[:a] + bloque + src[b:]

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    path = Path(sys.argv[1])
    reglas = {}
    if '--reglas' in sys.argv:
        reglas = json.loads(Path(sys.argv[sys.argv.index('--reglas') + 1]).read_text(encoding='utf-8'))
    src = path.read_text(encoding='utf-8')
    cambios = []
    for lang, (a, b) in sorted(bloques_i18n(src).items(), key=lambda x: -x[1][0]):
        bloque = src[a:b]

        def sub(m):
            llave, valor = m.group(1).strip('"'), m.group(2)
            fijo = reglas.get('valores', {}).get(llave, {}).get(lang)
            if fijo is not None:                      # texto corregido a mano (gramatica, terminos)
                if fijo != valor:
                    cambios.append((lang, llave, 'fijo', valor, fijo))
                return m.group(0).replace('"' + valor + '"', '"' + fijo + '"', 1)
            c = clase(llave, reglas)
            nuevo = {'igual': lambda v: v, 'frase': frase, 'cola': cola}.get(c, lambda v: proper(v, lang))(valor)
            if nuevo != valor:
                cambios.append((lang, llave, c, valor, nuevo))
            return m.group(0).replace('"' + valor + '"', '"' + nuevo + '"', 1)
        src = src[:a] + PAR.sub(sub, bloque) + src[b:]
    if '--config' in sys.argv:
        src = config_frases(src, cambios)
    for lang, llave, c, v, n in sorted(cambios):
        print(f'{lang}\t{c}\t{llave}\t{v}\t=>\t{n}')
    print(f'# {len(cambios)} cambios', file=sys.stderr)
    if '--aplicar' in sys.argv:
        path.write_text(src, encoding='utf-8')
        print(f'# escrito {path}', file=sys.stderr)

if __name__ == '__main__':
    main()
