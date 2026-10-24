
p = "/lakehouse/default/Files/SAP/ZMM_MD04/rejects/2026-08-06_MMD142_USALL_ZMMMD04_2026-08-06_06-04-00.txt"
for l in open(p, encoding="utf-8").read().splitlines():
    if "635731" in l or "777676" in l:
        print(l[:200])

