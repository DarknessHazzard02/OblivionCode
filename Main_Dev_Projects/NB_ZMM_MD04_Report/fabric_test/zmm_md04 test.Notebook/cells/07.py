
from pyspark.sql import functions as F
nb  = spark.table("sap_zmm_md04_vigente")
dfw = spark.table("SAP_ZMM_MD04").filter(F.col("EXECUTION_DATE") == "2026-08-06")

mats = ["77233554","77269668","77049219","77637835","77437336","77887719","77275405",
        "77814976","77228750","77331855","77823545","77701214","77108081","77738965",
        "77442621","77987351","77709422","77554563","77593134","77550324","77182229",
        "77997791","77251084","77457208","77502829","77005437","77607215","77514340",
        "77539056","77621857","77209450","77845590","77057585","77942143","77471087",
        "77228448","77497796","77226731","77348591","77428953","77005602",
        "77973895","77601715","77841771","77044574","77246059","77628520","77605306",
        "77606756","77624794","77770007","77012737","77099193","77769111","77068196",
        "77895272","77254157","77534957","77090243"]
provs = ["9900003","9900002","9900004","9900001","9900005"]

def cuenta(d, quien):
    m = d.filter(F.col("Material").isin(mats)).count()
    cond = F.lit(False)
    for p in provs:
        cond = cond | F.col("Proveedor").contains(p)
    pr = d.filter(cond).count()
    print(f"{quien:<10} materiales excluidos: {m:>4} · proveedores excluidos: {pr:>4}")

cuenta(nb,  "notebook")
cuenta(dfw, "dataflow")
print(f"\ntotal notebook: {nb.count()} · dataflow: {dfw.count()} · diferencia: {nb.count()-dfw.count()}")

