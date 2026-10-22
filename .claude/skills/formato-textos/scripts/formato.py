# formato.py — reglas de mayusculas y puntuacion para el texto de los tableros (ES y EN).
#
#   proper(texto, lang)  -> titulos, etiquetas, botones, filtros, encabezados, ejes, chips, KPIs
#   frase(texto)         -> subtitulos, notas, avisos, textos de ayuda: oracion con punto
#   cola(texto)          -> final de frase que el codigo pega despues de un numero: minuscula y punto
#
# Uso rapido:  python formato.py "materiales por estatus de cobertura" es
import re
import sys

CONECTORES = {
    'es': {'de', 'del', 'la', 'las', 'el', 'los', 'lo', 'y', 'e', 'o', 'u', 'a', 'al', 'en', 'por', 'para',
           'con', 'sin', 'sobre', 'entre', 'que', 'un', 'una', 'unos', 'unas', 'vs', 'desde', 'hasta', 'según',
           'contra', 'hacia', 'ante', 'tras', 'su', 'sus'},
    'en': {'of', 'the', 'a', 'an', 'and', 'or', 'nor', 'by', 'in', 'on', 'at', 'to', 'for', 'per', 'from',
           'with', 'without', 'vs', 'as', 'into', 'than', 'via'},
}
# Despues de estos simbolos la palabra va con mayuscula, sea o no conector
SIMBOLOS = set('([{/\\-+=<>?_"`:;.,·|&*#@!¿¡')
# Terminos de los sistemas que se escriben siempre igual (estatus de Oracle/SAP, nombres de reporte)
TERMINOS = ['Not On Hold', 'On Hold', 'Schedule Ship Date', 'Request Date', 'Promise Date', 'Customer Related',
            'Open Orders', 'Executive Summary', 'Y Meadows', 'Past Due Details']
EXT = r'\.(?:csv|json|xlsx|xlsm|py|md|txt|html)\b'
# Nombres de archivo y rutas: divisiones.csv, manual/bridge_manual.csv, manual/
ARCHIVO = re.compile(r'\{\w+\}|\$\{[^}]*\}|\S*' + EXT + r'|\S+/(?=\s|$)')   # + plantillas {n}, ${x}
_TOKEN = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?|\w+|\s+|.", re.UNICODE)
_MARCA = '⁣'   # separador invisible: guarda lo que no se toca mientras se formatea lo demas

def es_sigla(w):
    """SAP, MB52, ZE_SD48, QI, 3M, 1er, PO#: se quedan como vienen."""
    letras = [c for c in w if c.isalpha()]
    if any(c.isdigit() for c in w):
        return True
    return len(letras) >= 2 and all(c.isupper() for c in letras)

def _proper(texto, conectores):
    out, previo = [], ''          # previo = ultimo caracter que no es espacio
    primera = True
    for tok in _TOKEN.findall(texto):
        if tok.isspace() or not tok[0].isalpha():
            out.append(tok)
            if not tok.isspace():
                previo = tok[-1]
                if tok[0].isdigit() or tok == '%' or tok == _MARCA:   # '28.0%', '% de ...': no abren etiqueta
                    primera = False
            continue
        if es_sigla(tok):
            w = tok
        elif len(tok) == 1 and tok.isupper() and not primera:   # 'Y Meadows': una letra mayuscula es nombre
            w = tok
        elif tok.lower() == 'vs':                # vs siempre en minuscula, aunque abra la etiqueta
            w = 'vs'
        elif primera or previo in SIMBOLOS:
            w = tok[0].upper() + tok[1:]
        elif tok.lower() in conectores:
            w = tok.lower()
        else:
            w = tok[0].upper() + tok[1:]
        out.append(w)
        previo, primera = tok[-1], False
    return ''.join(out)

def proper(texto, lang='es'):
    guardados = []

    def guardar(valor):
        guardados.append(valor)
        return f'{_MARCA}{len(guardados) - 1}{_MARCA}'

    for t in TERMINOS:
        texto = re.sub(re.escape(t), lambda m, t=t: guardar(t), texto, flags=re.I)
    texto = ARCHIVO.sub(lambda m: guardar(m.group(0)), texto)
    # Los dos idiomas: las etiquetas mezclan (el nombre de la hoja de Excel en ingles dentro del tablero en
    # espanol, 'Past Due Reason by Site'). Ningun conector de un idioma es palabra suelta del otro.
    out = _proper(texto, CONECTORES['es'] | CONECTORES['en'])
    return re.sub(_MARCA + r'(\d+)' + _MARCA, lambda m: guardados[int(m.group(1))], out)

def cola(texto):
    """Final de frase que el codigo pega despues de un numero ('28.0% ' + 'de los materiales'):
    se queda en minuscula y lleva el punto."""
    t = texto.rstrip()
    return t if not t or t[-1] in '.…:?!' else t + '.'

def frase(texto):
    """Mayuscula inicial (si empieza con letra) y punto final si no trae cierre."""
    t = texto.strip()
    if not t:
        return t
    if t[0].isalpha() and not es_sigla(t.split()[0]):
        t = t[0].upper() + t[1:]
    if t[-1] not in '.…:?!':
        t += '.'
    return t

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    txt = sys.argv[1] if len(sys.argv) > 1 else ''
    lang = sys.argv[2] if len(sys.argv) > 2 else 'es'
    print('proper:', proper(txt, lang))
    print('frase: ', frase(txt))
