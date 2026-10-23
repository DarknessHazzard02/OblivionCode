"""
generar_items_fabric.py — emite los items de Fabric para la ingesta SAP.

Genera bajo `fabric/` los 4 Copy Jobs y los 4 pipelines, en el formato que la
integración Git de Fabric sincroniza. Se generan con código y no a mano porque
son 8 items con GUIDs cruzados: un id mal copiado deja un pipeline apuntando a
la nada y Fabric no avisa hasta que corre.

Clonados de `ZMM_MD04_ON_PREM_DATA_TO_LAKEHOUSE.CopyJob` y
`ZMM_MD04_PIPELINE_CI.DataPipeline`, que ya funcionan en producción.

Dato clave descubierto al comparar los dos: **el `logicalId` del `.platform` es
exactamente el id con el que el pipeline referencia al item** (`copyJobId`,
`notebookId`). Por eso se pueden crear ambos en el mismo push, sin esperar a
que Fabric asigne ids.

Uso:  python generar_items_fabric.py
"""

import json
from pathlib import Path

BASE = Path(__file__).parent
DESTINO = BASE / "fabric" / "SAP_TRANSACIONES"

# Prefijo de esta entrega. Nada más en el workspace lo usa, así que la regla
# para quien mire la lista de items es simple: si empieza con SAPCARGA_, es
# nuevo; si no, ya estaba.
#
# Nació de un problema real: los nombres originales eran
# `MB52_ON_PREM_DATA_TO_LAKEHOUSE` y `MB52_PIPELINE_CI`, y en el workspace ya
# vivían `SAP_MB52_ON_PREM_DATA_TO_LAKEHOUSE`, `MB52_PIPELINE` y
# `SAP_MB52_CI_PL`. Cuatro nombres casi iguales: imposible saber cuál era cuál,
# y por eso se borraron items buenos por error.
PREFIJO = "SAPCARGA_"

# Los pipelines se despliegan DESPUÉS de los copy jobs, no junto con ellos.
# Fabric resuelve las dependencias de un pipeline antes de materializar los
# items del mismo push, así que un pipeline que apunta a un copy job recién
# creado falla con "Failed to discover dependencies". Se generan en una carpeta
# aparte y se suben en un segundo commit, cuando los copy jobs ya existen.
DESTINO_FASE2 = BASE / "fabric_fase2" / "SAP_TRANSACIONES"

SCHEMA_PLATFORM = ("https://developer.microsoft.com/json-schemas/fabric/"
                   "gitIntegration/platformProperties/2.0.0/schema.json")
SCHEMA_SCHEDULES = ("https://developer.microsoft.com/json-schemas/fabric/"
                    "gitIntegration/schedules/1.0.0/schema.json")

# Conexión al gateway que ya tiene acceso a <carpeta-compartida>
# Este GUID no se puede inventar: identifica la conexión ya autorizada.
CONEXION_FILESERVER = "<GUID>"

# <lakehouse>, en la representación que usa el Copy Job de MD04.
LAKEHOUSE_ARTIFACT = "<GUID>"

# El notebook cargador común.
NOTEBOOK_CARGADOR = "<GUID>"

# Conexión que usa la actividad InvokeCopyJob. Se toma de MD04.
#
# ESTE CAMPO ERA LA CAUSA del "Failed to discover dependencies". Sin
# `externalReferences`, Fabric intenta leer la conexión al descubrir las
# dependencias del pipeline, la encuentra nula, y revienta con
# "Object reference not set to an instance of an object" — un NullReference
# que no dice nada de lo que falta.
#
# Es distinta de la conexión del gateway (<GUID>...): aquella es del Copy Job
# al share on-prem; esta es del pipeline al Copy Job.
CONEXION_INVOKE_COPYJOB = "<GUID>"

# Timeout y reintentos, calcados de MD04. Van en TODAS las actividades.
POLICY_ACTIVIDAD = {
    "timeout": "0.12:00:00",
    "retry": 0,
    "retryIntervalInSeconds": 30,
    "secureInput": False,
    "secureOutput": False,
}
POLICY_SETVARIABLE = {"secureInput": False, "secureOutput": False}

# Las rutas de origen son RELATIVAS a la raíz de la conexión: MD04 usa
# "ZMM_MD04" para <carpeta-compartida>
FUENTES = [
    {
        "nombre": "MB52",
        "carpeta_item": "SAP_MB52",
        "origen": "SDDnnn",
        "destino": "SAP/MB52/MB52_CopyJob",
        "copyjob_id": "<GUID>",
        "pipeline_id": "<GUID>",
        "hora": "06:20",
    },
    {
        "nombre": "ZSD49N",
        "carpeta_item": "SAP_ZSD49N",
        "origen": "ZSD49N - PD Report",
        "destino": "SAP/ZSD49N/ZSD49N_CopyJob",
        "copyjob_id": "<GUID>",
        "pipeline_id": "<GUID>",
        "hora": "06:25",
    },
    {
        "nombre": "COOIS_HEADERS",
        "carpeta_item": "SAP_COOIS",
        "origen": "COOIS/COOIS Header",
        "destino": "SAP/COOIS/COOIS Header",
        "copyjob_id": "<GUID>",
        "pipeline_id": "<GUID>",
        "hora": "06:30",
    },
    {
        "nombre": "COOIS_COMPONENTS",
        "carpeta_item": "SAP_COOIS",
        "origen": "COOIS/COOIS Components",
        "destino": "SAP/COOIS/COOIS Components",
        "copyjob_id": "<GUID>",
        "pipeline_id": "<GUID>",
        "hora": "06:35",
    },
]

def platform(tipo, nombre, logical_id, descripcion):
    return {
        "$schema": SCHEMA_PLATFORM,
        "metadata": {"type": tipo, "displayName": nombre, "description": descripcion},
        "config": {"version": "2.0", "logicalId": logical_id},
    }

def copy_job(f):
    """Copia binaria del share a OneLake, incremental.

    DIFERENCIA DELIBERADA con el molde de MD04: aquel está tipado como
    `DelimitedText` con `columnDelimiter: "|"`, o sea que parsea el archivo y lo
    reescribe. Nuestro parser depende de la POSICIÓN EXACTA de los pipes para
    realinear las filas corridas, y un round-trip de texto delimitado puede
    moverlas. Además, un XLSX pasado por DelimitedText se corrompe.

    `Binary` copia el archivo byte por byte y conserva su nombre — que es de
    donde sale FILE_DATE.
    """
    return {
        "properties": {
            "jobMode": "CDC",
            "source": {
                "type": "Binary",
                "connectionSettings": {
                    "type": "FileServer",
                    "externalReferences": {"connection": CONEXION_FILESERVER},
                },
            },
            "destination": {
                "type": "Binary",
                "connectionSettings": {
                    "type": "Lakehouse",
                    "typeProperties": {
                        "workspaceId": "<GUID>",
                        "artifactId": LAKEHOUSE_ARTIFACT,
                        "rootFolder": "Files",
                    },
                },
            },
            "policy": {"timeout": "0.12:00:00", "retry": 0},
        },
        "activities": [{
            "id": f["copyjob_id"],
            "properties": {
                "source": {
                    "datasetSettings": {
                        "location": {
                            "type": "FileServerLocation",
                            "folderPath": f["origen"],
                        },
                    },
                    # Lo mismo que usa MD04: trae solo lo nuevo desde la última
                    # corrida, con una foto completa la primera vez.
                    "changeDataSettings": {"readMethod": "SnapshotPlusIncremental"},
                    "storeSettings": {"recursive": True,
                                      "enablePartitionDiscovery": False},
                    "formatSettings": {},
                },
                "destination": {
                    "writeBehavior": "Append",
                    "datasetSettings": {
                        "location": {
                            "type": "LakehouseLocation",
                            "folderPath": f["destino"],
                        },
                    },
                    "storeSettings": {"copyBehavior": "PreserveHierarchy"},
                    "formatSettings": {},
                    "applyVOrder": False,
                },
                "enableStaging": False,
            },
        }],
    }

def pipeline(f):
    """copy job -> notebook cargador, con marcas de tiempo y estatus.

    Más corto que el de MD04: se dejan fuera la actividad de correo y el
    notebook de bitácora, que referencian items y conexiones que no se han
    revisado. El estado igual queda visible porque el cargador termina con
    notebookutils.notebook.exit(json).
    """
    return {
        "properties": {
            "activities": [
                {
                    "name": "START_TIME",
                    "type": "SetVariable",
                    "dependsOn": [],
                    "policy": POLICY_SETVARIABLE,
                    "typeProperties": {
                        "variableName": "START_TIME",
                        "value": {"value": "@utcNow()", "type": "Expression"},
                    },
                },
                {
                    "name": "Copy job",
                    "type": "InvokeCopyJob",
                    "dependsOn": [{"activity": "START_TIME",
                                   "dependencyConditions": ["Succeeded"]}],
                    "policy": POLICY_ACTIVIDAD,
                    "typeProperties": {
                        "copyJobId": f["copyjob_id"],
                        "workspaceId": "<GUID>",
                    },
                    # Sin esto, el Update all revienta con un NullReference.
                    "externalReferences": {"connection": CONEXION_INVOKE_COPYJOB},
                },
                {
                    "name": "Cargar tabla",
                    "type": "TridentNotebook",
                    "dependsOn": [{"activity": "Copy job",
                                   "dependencyConditions": ["Succeeded"]}],
                    "policy": POLICY_ACTIVIDAD,
                    "typeProperties": {
                        "notebookId": NOTEBOOK_CARGADOR,
                        "workspaceId": "<GUID>",
                        # SOLO `fuente`, y como string.
                        #
                        # `force_reload` y `recrear_tabla` se quedan con el default
                        # del notebook (False y True), que es justo lo que quiere la
                        # corrida diaria. Pasarlos desde aquí era un error: Fabric
                        # inyectaba el string "False", y en Python `not "False"` es
                        # False — la bandera se habría ignorado en silencio, que es
                        # exactamente el tipo de falla que no da error.
                        "parameters": {
                            "fuente": {"value": f["nombre"], "type": "string"},
                        },
                    },
                },
                {
                    "name": "END_TIME",
                    "type": "SetVariable",
                    "dependsOn": [{"activity": "Cargar tabla",
                                   "dependencyConditions": ["Completed"]}],
                    "policy": POLICY_SETVARIABLE,
                    "typeProperties": {
                        "variableName": "END_TIME",
                        "value": {"value": "@utcNow()", "type": "Expression"},
                    },
                },
                {
                    "name": "STATUS",
                    "type": "SetVariable",
                    "dependsOn": [{"activity": "END_TIME",
                                   "dependencyConditions": ["Completed"]}],
                    "policy": POLICY_SETVARIABLE,
                    "typeProperties": {
                        "variableName": "STATUS",
                        "value": {"value": "@activity('Cargar tabla').status",
                                  "type": "Expression"},
                    },
                },
            ],
            "variables": {
                "START_TIME": {"type": "String"},
                "END_TIME": {"type": "String"},
                "STATUS": {"type": "String"},
            },
        }
    }

def schedule(hora):
    """Lunes a viernes, mismo huso que MD04. Las horas se escalonan para que
    los cuatro copy jobs no peguen al gateway al mismo tiempo."""
    return {
        "$schema": SCHEMA_SCHEDULES,
        "schedules": [{
            "enabled": False,   # se prende a mano tras validar la primera corrida
            "jobType": "Execute",
            "configuration": {
                "type": "Weekly",
                "startDateTime": "2026-08-14T00:00:00",
                "endDateTime": "2027-08-14T00:00:00",
                "localTimeZoneId": "Central Standard Time (Mexico)",
                "times": [hora],
                "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            },
        }],
    }

def escribir(ruta, contenido):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(contenido, indent=2, ensure_ascii=False)
    ruta.write_text(texto + "\n", encoding="utf-8")
    print(f"  {ruta.relative_to(BASE)}")

def main():
    ids = set()
    for f in FUENTES:
        for k in ("copyjob_id", "pipeline_id"):
            if f[k] in ids:
                raise SystemExit(f"GUID repetido: {f[k]} en {f['nombre']}.{k}")
            ids.add(f[k])

    for f in FUENTES:
        print(f"\n{f['nombre']}")

        # FASE 1 — copy jobs. No dependen de nada, entran solos.
        nombre_cj = f"{PREFIJO}{f['nombre']}_COPYJOB"
        cj = DESTINO / f["carpeta_item"] / f"{nombre_cj}.CopyJob"
        escribir(cj / ".platform", platform(
            "CopyJob", nombre_cj, f["copyjob_id"],
            f"Copia incremental de {f['origen']} (share on-prem) a Files/{f['destino']}"))
        escribir(cj / "copyjob-content.json", copy_job(f))

        # FASE 2 — pipelines. Dependen del copy job, van en el segundo commit.
        nombre_pl = f"{PREFIJO}{f['nombre']}_PIPELINE"
        pl = DESTINO_FASE2 / f["carpeta_item"] / f"{nombre_pl}.DataPipeline"
        escribir(pl / ".platform", platform(
            "DataPipeline", nombre_pl, f["pipeline_id"],
            f"Ingesta {f['nombre']}: {nombre_cj} + carga a tabla Delta"))
        escribir(pl / "pipeline-content.json", pipeline(f))
        escribir(pl / ".schedules", schedule(f["hora"]))

    print(f"\nFASE 1 (se sube ahora):     {DESTINO.relative_to(BASE)}")
    print(f"FASE 2 (tras el Update all): {DESTINO_FASE2.relative_to(BASE)}")
    print("Calendarios generados APAGADOS: se prenden tras validar la primera corrida.")

if __name__ == "__main__":
    main()
