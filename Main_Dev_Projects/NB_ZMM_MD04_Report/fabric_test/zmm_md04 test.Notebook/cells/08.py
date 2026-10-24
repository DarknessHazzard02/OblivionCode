
import notebookutils
p = "/lakehouse/default/Files/SAP/ZMM_MD04/ZMM_MD04 RAW/MMD142_USALL_ZMMMD04_2026-08-06_06-04-00.txt"
lineas = open(p, encoding="utf-8").read().splitlines()

# El encabezado real (la primera línea con muchos pipes, saltando separadores)
enc = next(l for l in lineas[1:] if l.startswith("|") and "-------" not in l)
pos_enc = [i for i, ch in enumerate(enc) if ch == "|"]
print(f"encabezado: {len(pos_enc)} pipes")
print(f"posiciones: {pos_enc[:12]} ...\n")

# Comparar contra unas cuantas filas normales y una desalineada
normales = [l for l in lineas if l.startswith("|") and "-------" not in l and l != enc][:3]
mala = next(l for l in lineas if "77412093610.Q" in l)

for etiqueta, l in [("normal 1", normales[0]), ("normal 2", normales[1]),
                    ("DESALINEADA", mala)]:
    pos = [i for i, ch in enumerate(l) if ch == "|"]
    print(f"{etiqueta:<12} {len(pos):>3} pipes · ¿mismas posiciones que el encabezado? "
          f"{pos == pos_enc}")
    if pos != pos_enc:
        extra = sorted(set(pos) - set(pos_enc))
        print(f"             pipes en posiciones que el encabezado no tiene: {extra[:10]}")

