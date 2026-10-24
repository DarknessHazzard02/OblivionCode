
from pyspark.sql import functions as F
import notebookutils

workspace_id = "<workspace-id-03>"
lakehouse_id = "<lakehouse-id-04>"
base = "abfss://" + workspace_id + "@onelake.dfs.fabric.microsoft.com/" + lakehouse_id

t = spark.table("sap_zmm_md04_vigente")
col = [x for x in t.columns if "Tratamiento" in x][0]
print("columna:", col, "| tipo:", dict(t.dtypes)[col])
print("no nulos:", t.filter(F.col(col).isNotNull()).count(), "de", t.count())

carpeta = base + "/Files/SAP/ZMM_MD04/ZMM_MD04 RAW"
todos = [f for f in notebookutils.fs.ls(carpeta) if not f.isDir]
arch = sorted(todos, key=lambda f: f.modifyTime)[-1]
print("archivo:", arch.name)

lineas = spark.read.text(arch.path).collect()
enc = next(l.value for l in lineas if "Centro" in l.value and "|" in l.value)
campos_enc = [x.strip() for x in enc.split("|")]
print("ultimas columnas:", campos_enc[-5:])

interes = ["Material", "Unidad Med", "Cantidad", "Precio Neto", "Por", "Mon", "Tiempo Tratamiento EM"]
for l in lineas:
    if "12113220" not in l.value:
        continue
    if l.value.count("|") < 20:
        continue
    campos = [x.strip() for x in l.value.split("|")]
    print("--- material 12113220 ---")
    for nombre, val in zip(campos_enc, campos):
        if nombre in interes:
            print("   ", nombre, "=", repr(val))
    break

