---
name: fabric-sap-ingesta
description: Cómo llevar archivos y reportes de SAP a tablas Delta en Microsoft Fabric, y cómo desplegar items de Fabric por integración Git. Cubre el formato de las listas ALV (que llegan como .csv pero no lo son), números europeos, negativos con signo al final, encabezados truncados y repetidos, el formato de los items (.platform, notebook-content.py, pipeline-content.json, copyjob-content.json) y la lista de errores que ya nos costaron horas. Úsala SIEMPRE que se mencione SAP, importar SAP, importar de SAP, cargar SAP, ingesta de SAP, extracto de SAP, reporte de SAP, archivo de SAP, transacción, transacción de SAP, código de transacción, o cualquiera de ellas por nombre - MB52, MB51, ZSD49N, COOIS, MD04, ZMM_MD04, ZPP41N, ZDP04N, ZTRACE16, ZMM, ZSD, SDDnnn, SDDnnn, SQ00, ME2L, KE24, COGI, MC05, VL06O, LUIA, BW, master data, catálogos SAP. También cuando se hable de ALV, ancho fijo, lista paginada, Copy Job, gateway, on-prem, lakehouse, OneLake, <lakehouse>, tabla Delta, pipeline de Fabric, notebook de Fabric, Dataflow Gen2, integración Git de Fabric, Source control, Update all, commit desde el workspace, o cuando haya que ingerir un archivo nuevo a Fabric o crear un item de Fabric desde git.
---

# Ingesta de SAP a Fabric — equipo de BI

Todo lo de SAP se importa igual, así que esto es el molde. Cada regla salió de
algo que ya falló.

**De dónde sale cada dato —qué transacción, qué user group, qué query, cómo se
llama el archivo y en qué tabla cae— está en la skill `sap-catalogo-fuentes`.**
Esta de aquí es el *cómo se construye*; esa es el *de dónde viene*.

**El molde de referencia en el workspace BI es `ZMM_MD04_PIPELINE_CI`.**
Antes de escribir un item nuevo, léelo y **compara campo por campo**. La mitad
de los errores de esta lista se habrían evitado con ese diff.

---

## ⛔ CIERRA SIEMPRE CON LO QUE TIENE QUE HACER UNA PERSONA

**Toda respuesta que entregue algo termina con una seccion `Lo que tienes que
hacer`.** No es cortesia: la mitad de este trabajo son pasos que Claude **no
puede** dar —correr un item en Fabric, aprobar un PR, renombrar una conexion,
cambiar una variante en SAP, mirar si un archivo aterrizo— y si no quedan
escritos, la entrega se queda a medias sin que nadie se entere.

La lista va **numerada y en orden**, con solo lo que le toca a la persona. Lo
que Claude ya hizo va arriba, en el resumen, no aqui.

Cada punto dice tres cosas:

| | |
|---|---|
| **donde** | la ruta de clicks o el comando exacto, no "en el portal" |
| **que vas a ver si salio bien** | el numero, el archivo o el mensaje concreto |
| **como se ve si fallo en silencio** | lo que hay que mirar para no dar por bueno un verde |

Ese tercer renglon es el que importa en este equipo: **casi todas nuestras
fallas salen en verde**. Un Copy Job apuntando a una carpeta que no existe, un
notebook que se salta el archivo por la bitacora, un pipeline cuyo Copy no
corrio y dejo el JSON de ayer. "Corrio bien" no es una comprobacion; "hay un
archivo en esta carpeta con la fecha de hoy" si lo es.

Y dos reglas mas:

- **Si no hay nada que hacer, decirlo:** *"Nada de tu lado por ahora"*. Una
  respuesta sin cierre deja a la persona adivinando si le toca algo.
- **Nunca cerrar con un "avisame" a secas.** Avisar de que, y como se sabe.

```
## Lo que tienes que hacer

1. **Corre el Copy Job `SAP_MB51_ALLUS_COPYJOB`** (abrelo y dale Run).
   Bien: al terminar, en `Files/SAP/MB51_ALLUS/MB51_ALLUS_CopyJob` hay
   archivos `MMS103_...`. Mal en silencio: el job sale verde y la carpeta
   esta vacia, que es como se ve una ruta de origen equivocada.
2. ...
```

---

## ⛔ NADA DE LO QUE ENTREGAMOS LLEVA FIRMA DE IA

**Aplica a quien trabaje con estas reglas por igual.**

Ni el codigo, ni los commits, ni los pull requests, ni los notebooks, ni los
tableros, ni los documentos llevan el nombre de Claude en ninguna parte:

- **Sin trailer `Co-Authored-By`** en los mensajes de commit.
- **Sin pie "Generated with ..."** en el cuerpo de los PR.
- **Sin creditos** en comentarios de codigo, encabezados de notebook, el pie de
  un tablero, ni el panel de documentacion.

El trabajo sale a nombre de **quien lo empuja**, y de nadie mas.

Los dos scripts de push del equipo lo traian fijo y ya se les quito
(`assets/push_git.py` y `assets/push_items.py`).

### Como se apaga de raiz, sin depender de que nadie se acuerde

Claude Code agrega esas firmas por default. La memoria y esta skill son
recordatorios; **lo que de verdad lo apaga es un ajuste**, en el
`~/.claude/settings.json` de cada quien:

```json
{
  "attribution": {
    "commit": "",
    "pr": ""
  }
}
```

Cadena vacia = sin firma. Surte efecto de inmediato, sin reiniciar.

⛔ **Es por maquina.** **Hay que ponerlo en cada máquina**, o sus commits van a seguir saliendo firmados aunque estas
skills digan lo contrario.

---

## ⛔ CONTRASEÑAS Y CIBERSEGURIDAD: NO SE NEGOCIAN

**Aplica a quien trabaje con estas reglas por igual.**

No se flexibiliza "solo por esta vez" y no cambia porque haya prisa. Si una
instrucción choca con esta sección, gana esta sección.

- **Ninguna contraseña, token, llave ni cadena de conexión con secreto** en
  código, notebooks, `pipeline-content.json`, Base parameters, commits, PR,
  documentos ni en el chat. Ni "temporalmente", ni "para probar".
- **Las credenciales no se prestan.** Cada quien la suya; un usuario prestado
  deja el rastro a nombre de quien lo prestó.
- **Claude no captura credenciales.** Dice el paso; la persona las captura.
- **Si una credencial se filtró: rotarla primero**, limpiar después. Borrar el
  commit no la invalida, y hay que avisar a IT.

### Y avisar ANTES de lo que IT puede marcar como sospechoso

Casi todo lo que hace este equipo es legítimo. El punto es que nadie se entere
**después**, cuando ya llegó el correo de seguridad.

**Cuando algo caiga en esta lista, Claude se detiene y no continúa hasta
confirmación explícita:** exportar volúmenes inusuales de datos; mover datos
corporativos a destinos personales (correo, Drive, USB, equipo propio);
publicarlos en servicios externos; credenciales en texto plano o cuentas
prestadas; scraping o automatización contra sistemas corporativos; consultas
pesadas fuera de la ventana del DBA; borrado o barrido masivo en `<carpeta-compartida>` o en un
repo; software no aprobado o permisos de administrador innecesarios; desactivar
antivirus o firewall.

El aviso dice cuatro cosas: **qué** exactamente lo dispara, **por qué** se ve
sospechoso desde IT, **la alternativa** que no lo dispara, y **a quién avisar**
antes si de todos modos hay que hacerlo.

> Avisar antes convierte una alerta en un trámite. Avisar después la convierte en
> una investigación.

**La versión completa está en `las reglas de seguridad`**, en la raíz del repo de
skills, que se lee en **toda** sesión — no solo cuando esta skill se activa. Si
no lo tienes enlazado, ve el `README.md`.

---

## PASO 0 — Antes de escribir una línea

1. **Consigue un archivo real** y perfílalo. No confíes en la extensión ni en el
   nombre de las columnas (sección 1).
2. **Lee el item equivalente que ya funciona** en el repo de Fabric y compáralo
   contra lo que vas a generar (sección 4).
3. **Pregunta si la tabla destino ya existe.** Si existe, quién la escribe hoy y
   quién la consume.
4. **Prueba el parser en local**, contra el archivo real, antes de subir nada.

---

## 1. Los archivos de SAP no son lo que aparentan

### La extensión miente

`SDDnnn_MATERIAL_LIST_MB52_….csv` y `SDDnnn_PD_REPORT_….csv` tienen extensión
`.csv` y **no tienen ni una coma**. Son listas ALV: ancho fijo, marco de pipes,
paginadas.

```
13.08.2026 Display Warehouse Stocks of Material          1     <- titulo de pagina
------------------------------------------------------------  <- separador
|Material  |Material Description  |BUn|Plnt|  Unrestricted|    <- encabezado
|----------------------------------------------------------
|136017    |Combo 5SP14N445KFD    |UN |US70|          946 |    <- dato
```

**Lo primero es contar cuántas veces se repite el encabezado.** SAP lo reimprime
en cada página: 227 veces en un MB52 de 13 mil filas, 314 en un ZSD49N de 17 mil.
Si no las descartas, entran como datos.

### ⛔ Lee el archivo COMPLETO — y compruébalo

Para un ALV hay que leer todo el archivo de un jalón: las líneas dependen unas de
otras (encabezado, separadores, paginación). **Léelo con `open()` desde el mount
local**, no con `spark.read.text()`.

```python
with open("/lakehouse/default/Files/SAP/.../archivo.csv",
          "r", encoding="utf-8-sig", errors="replace") as fh:
    texto = fh.read()
```

El intento con Spark falló así:

```python
spark.read.option("wholetext", True)     # bool de Python -> se IGNORA
```

`option()` espera un **string**. Con un bool la opción se descarta, Spark cae a
su modo normal —una fila por línea— y `.collect()[0][0]` devuelve **solo la
primera**. El parser recibe una línea y falla con *"No encontré el encabezado"*,
que apunta al lugar equivocado. Costó dos corridas y un diagnóstico falso.

**Cómo se reconoce:** el mensaje muestra `Primeras lineas: [...]` con **un solo
elemento**, y ese elemento es literalmente la primera línea del archivo
(`['Embraco S/A']`). Si ves eso, el problema es la lectura, no el formato.

Y pon una validación que lo convierta en un error honesto:

```python
if texto.count("\n") + 1 < 10:
    raise ValueError("Solo se leyeron N lineas. Revisa la LECTURA, no el reporte.")
```

`open()` en modo universal newlines además resuelve solo el CRLF/CR/LF.

### Normaliza los saltos de línea ANTES de partir

**Los exports de SAP no son consistentes entre sí.** En la misma carpeta de MB52
había archivos de agosto con `CRLF` y de julio con **`CR` solo**.

```python
texto = texto.replace("\r\n", "\n").replace("\r", "\n")
```

Sin eso, un `split("\n")` sobre un archivo CR deja **una sola línea gigante**, no
encuentra el encabezado, y el error apunta al lugar equivocado:

```
No encontre el encabezado que empieza con '|Material'.
Primeras lineas: ['30.07.2026 Display Warehouse Stocks of Material   1']
```

> La pista está en que la lista trae **un solo elemento**. Si el archivo tuviera
> saltos, mostraría tres.

Y prueba el parser con los tres estilos, no solo con el archivo que te tocó:
CRLF, CR y LF deben dar el mismo conteo.

### Cortar por posición, no por `split("|")`

El reporte es de **ancho fijo**. Las líneas que se "desalinean" no traen un pipe
dentro del texto: traen la línea **corrida** unos caracteres, porque el contenido
tiene un tabulador que SAP contó con un ancho y escribió con otro.

Empareja cada corte del encabezado con el pipe más cercano de la línea, con
tolerancia de ~3 caracteres. Si un corte no encuentra pareja, o dos caen en el
mismo pipe, **la fila va a cuarentena y se cuenta** — es preferible perderla y
saberlo, a meterla con las columnas recorridas.

> Exigir que las posiciones coincidieran *exactamente* mandó 39 filas sanas a
> cuarentena. El criterio bueno es el **número** de pipes; la posición solo sirve
> para rescatar a las que fallan.

Implementación probada: `assets/sap_parser.py`.

### Números europeos y negativos al final

```
2.450,14   ->  2450.14      punto de miles, coma decimal
3.500,000  ->  3500.0
676.000-   ->  -676.0       el signo va AL FINAL (formato SAP)
```

Un `cast` directo los destruye. **Un valor que no parsea sale `NULL` y se cuenta
aparte, nunca 0**: un ilegible convertido en cero se suma a los totales y nadie
se entera.

### Los XLSX son más limpios, pero NO les creas los tipos

COOIS llega en XLSX con encabezados completos. Tentador dejar que pandas y Spark
infieran. **No lo hagas.** Lo que pasó al confiar en la inferencia:

```
Bill_of_material     "00132844"  ->  132844.0     llaves de SAP con los
Item_component_list  "0010"      ->  10           ceros comidos
```

Y las columnas **100% vacías** se infirieron `double`, porque pandas ve todo NaN
y le pone float64. El día que SAP mande una `X` en `Deletion_flag`, la carga
truena o coerce.

La regla es la misma que en el ALV, no una distinta:

```python
pdf = pd.read_excel(ruta, dtype=object)          # sin inferencia
# declarar COLUMNAS_NUMERICAS y COLUMNAS_FECHA por fuente;
# TODO LO DEMAS se pasa a str() y el vacio a None
```

Y construye el `StructType` explícito para `createDataFrame`. Dejar que Spark
infiera desde un `object` con NaN mezclado es la otra mitad del problema.

---

## 2. Las columnas

### Encabezados truncados al ancho de la columna

SAP corta el nombre al ancho visible. En ZSD49N, 20 de 56 llegan mutilados:
`Sales Orde`, `Ordered qt`, `Cust. Requ`, `Deliv.crea`, `Planned Pr`…

**Mide el contenido antes de bautizarlas.** `Sales Orde` parece un folio y trae
fechas (`01.08.2025`). `Planned Pr` parece "Price" y trae fechas. Si el contenido
contradice al nombre, **deja el nombre truncado** y anótalo como pendiente de
confirmar en SAP: un nombre equivocado es peor que uno feo.

### Encabezados repetidos

ZSD49N trae **dos columnas llamadas `Confirmed`**. Medido: la 17 trae cantidades
(`3.500,000`), la 18 una bandera (`X`).

Desambigua **por posición**, no por nombre — un mapeo por nombre renombraría las
dos. Y valida que después del mapeo no queden nombres duplicados, o la escritura
en Delta truena.

> Este es el patrón que costó más caro del que hay registro: el ZMM_MD04 traía
> dos `Tiempo Tratamiento EM`, la segunda era la unidad del precio, el dataflow
> la descartó como "Column34" y **el tablero estuvo 458× inflado dos años**.

### Qué columnas se convierten a número: DECLÁRALAS A MANO

La detección automática propuso convertir `Cust Nr`, `Order`, `Item`, `Delivery`
y `Price List`. Son identificadores: `0000305439` convertido a número queda en
`305439` y **deja de casar con SAP**.

> **La regla: se convierte lo que se SUMA. Lo que identifica algo se queda texto,
> aunque parezca número.**

### No tires columnas en el `select`

`SAP_MB52_CI_NB` mapea `Unrestricted -> Stock` y termina con un `select` contra
un esquema fijo de 19 columnas. El archivo crudo trae además `Blocked`,
`Value BlockedStock`, `Qual.Insp.`, `Stock in tfr` y `Returns`. **Todas se
descartan en silencio**, incluido el stock bloqueado.

Antes de fijar un esquema, cuenta las columnas del archivo y compáralas con las
de la tabla. Si no cuadran, **aborta diciendo cuáles faltan**.

### Nombres para Delta

Delta rechaza espacios y puntos al **crear** una tabla. Renombra
(`Qual.Insp.` → `Quality_Inspection`) en vez de activar column mapping: es la
convención del lakehouse y no deja la tabla atada a una propiedad especial.

---

## 3. Las dos columnas de control, siempre

| Columna | De dónde sale |
|---|---|
| `FILE_DATE` | Del **nombre** del archivo |
| `LOAD_DATE` | Cuándo se escribió la tabla |

**Que se separen es la alarma:** si `LOAD_DATE` es de hoy y `FILE_DATE` de hace
tres días, el job local dejó de bajar archivos y **nada falla** — el tablero solo
se queda viejo, jurando que está fresco.

Cada fuente tiene **su propio patrón de fecha**, no lo generalices:

```
SDDnnn_..._2026-08-13_02-25-59.csv     YYYY-MM-DD
SDDnnn_..._2026-08-13_12-56-13AM.csv   YYYY-MM-DD + AM/PM
COOIS_Headers_08.13.2026.xlsx          MM.DD.YYYY
```

Si el patrón no casa, **falla con nombre propio**. Nunca sustituyas por la fecha
de hoy.

### ⛔ Elige el archivo por la fecha del NOMBRE, no por `modifyTime`

El Copy Job en `SnapshotPlusIncremental` trae la **carpeta completa** en su
primera corrida, así que todos los archivos quedan escritos casi al mismo tiempo
y su `modifyTime` en el lakehouse no dice nada del día al que se refieren.

Con `max(archivos, key=modifyTime)` se cargó un MB52 **del 30 de julio** habiendo
uno del 13 de agosto en la misma carpeta. Y no dio error: cargó, contó filas, y
reportó OK.

```python
fechados = [(fecha_de_archivo(f.name), f) for f in candidatos]
FILE_DATE, archivo = max([(fh, f) for fh, f in fechados if fh],
                         key=lambda par: (par[0], par[1].modifyTime))
```

Y avisa si el más reciente tiene más de un día: es la señal de que el job local
dejó de bajar archivos.

> El nombre de SDDnnn dice `12-56-13AM` y el encabezado dentro del archivo dice
> `13/08/2026 03:45`. No coinciden. Vale la pena guardar el sello interno aparte.

---

## 3 bis. ⛔ Dos capas siempre: la cruda y la limpia

**Regla del negocio, no negociable.** Todo archivo aterriza primero en una tabla
**cruda**, fiel al archivo, y las transformaciones van en una **segunda tabla**:

```
archivo  →  SAP_<FUENTE>         el archivo tal cual, columna por columna
                 ↓
            SAP_<FUENTE>_CLEAN   renombres, filtros de estatus, columnas derivadas
```

La cruda **se conserva completa**: nada de filtrar filas ni tirar columnas ahí.
Lo único que se le agrega son `FILE_DATE` y `LOAD_DATE`. La limpia se puede
rehacer desde cero en cualquier momento; la cruda no, porque el archivo del día
ya no está.

### Por qué
`SAP_ZSD49N_CLEAN` elimina las líneas facturadas — es una de sus reglas. Meses
después hizo falta la **última factura registrada** como fecha de negocio del
tablero… y esa columna solo existe en las filas que la limpieza borra. Con una
sola capa, ese dato se habría perdido para siempre y ni sabríamos que existió.

Los otros dos motivos:

- **Una regla de negocio cambia.** Si la limpieza vive encima de la cruda, se
  reescribe el notebook limpio y se vuelve a correr. Si vive dentro de la carga,
  hay que volver a pedir los archivos.
- **Otro reporte necesita lo que este tira.** El PD report, open orders y el MRP
  salen del mismo ZSD49N con filtros distintos. Cada uno se cuelga de la cruda.

### Cómo se ve en la práctica

| capa | nombre | qué lleva | modo |
|---|---|---|---|
| cruda | `SAP_MB52` | las 17 columnas del archivo, en ancho | se reescribe cada día |
| limpia | `SAP_MB52_CLEAN` | formato largo, un renglón por estatus | se reescribe cada día |

El notebook cargador **no sabe reglas de negocio**: parsea, tipa y escribe. Todo
lo que sea criterio —qué se excluye, cómo se renombra, qué se deriva— va en el
notebook de limpieza, encadenado después en el mismo pipeline.

Y la limpia **reporta lo que descartó**: cuántas filas, por qué regla, y aborta
si las cubetas no suman la entrada (ver la sección de `NULL` en 7 bis).

## 4. Desplegar items por integración Git

### Fabric JALA, no le empujan

Un push a GitHub **no hace nada** hasta que alguien aplica los cambios:
workspace → **Source control** → pestaña **Updates** → **Update all**.

De ahí la regla que se vuelve obligatoria: **nunca edites un item dentro de
Fabric.** La fuente es el archivo del repo; un cambio hecho en la UI se pierde en
el siguiente update.

### El formato de cada item

```
<Nombre>.Notebook/       .platform + notebook-content.py
<Nombre>.DataPipeline/   .platform + pipeline-content.json + .schedules
<Nombre>.CopyJob/        .platform + copyjob-content.json + .schedules
```

```json
// .platform
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
  "metadata": { "type": "Notebook", "displayName": "..." },
  "config": { "version": "2.0", "logicalId": "<GUID nuevo>" }
}
```

**El `logicalId` es el id con el que otros items lo referencian** (`copyJobId`,
`notebookId`). Verificado: sobrevive intacto al *Update all*, así que se pueden
crear varios items que se referencian entre sí en el mismo push.

### ⛔ El código va DESPUÉS del `# CELL`, nunca entre `# META` y `# CELL`

Si insertas código en la región `# METADATA` —entre el `# META {...}` de una
celda y el `# CELL` de la siguiente— Fabric **rechaza el item al importarlo**:

```
PyToIPynbFailure
"Additional text encountered after finished reading JSON content: #.
 Path '', line 7, position 0.", InternalServerError
```

Fabric lee ese `# META` como JSON al convertir el `.py` en `.ipynb`, encuentra
texto después y truena. **El mensaje engaña dos veces:** habla de JSON, que
suena a `.platform` o a `pipeline-content.json`, y dice "line 7", que es el
encabezado del notebook. El código intruso estaba en la línea 640.

Pasa fácil al parchar con scripts: si el ancla es un `# CELL` y se inserta
*antes*, el código cae en la región de metadatos de la celda anterior.

**La comprobación, antes de subir:**

```python
import re, pathlib
t = pathlib.Path(nb).read_text(encoding="utf-8")
for b in re.split(r"^# METADATA \*+\s*$", t, flags=re.M)[1:]:
    cuerpo = re.split(r"^# (CELL|MARKDOWN|PARAMETERS CELL) \*+\s*$", b, flags=re.M)[0]
    intrusas = [l for l in cuerpo.splitlines() if l.strip() and not l.startswith("# META")]
    assert not intrusas, f"código dentro de METADATA: {intrusas[:3]}"
```

Si pasa, ninguna región de metadatos tiene nada que no sea `# META`.

### ⛔ Nada de celdas mágicas: Fabric las duplica al serializarlas

```
%run <tablero>_00_reglas%run <tablero>_00_reglas
```

Duplicada, concatenada y sin el prefijo `# MAGIC`. Los dos notebooks habrían
tronado en esa celda en su primera corrida, y todas las funciones compartidas
habrían quedado indefinidas.

**No hay forma de comprobar cómo serializa Fabric una celda mágica sin subirla
y correrla**, así que escribirla es apostar a ciegas dentro de un item que ya
está en producción.

> **Si dos notebooks necesitan compartir código, INYÉCTALO al construir el
> item** desde un archivo único del repo, como una celda de código normal. No
> lo invoques en tiempo de ejecución.

La fuente sigue siendo un solo archivo —que es lo que evita que las reglas se
desincronicen—; lo que cambia es que la copia la hace el build y no Fabric.
Y el generador debe **fallar si sobrevive cualquier `# MAGIC`**:

```python
assert "# MAGIC" not in texto, f"{nombre}: quedó una celda mágica"
```

Vale la pena además comprobar que el item es autocontenido: que cada función
que el notebook *usa* esté *definida* en el mismo archivo.

**Cómo se detectó**, y es el procedimiento que conviene repetir después de cada
*Update all*: comparar el repo contra lo que Fabric devolvió, con el filtro que
quita comentarios y líneas vacías (más arriba en esta sección). Casi todo el
diff era el reformateo cosmético del markdown; esa línea era **lo único que no
lo era**.

> Un item compartido que deja de usarse hay que **borrarlo**, no dejarlo ahí.
> Uno inerte que parece la fuente es peor que no tenerlo: alguien lo va a
> editar creyendo que surte efecto. Antes de quitarlo, comprueba que ningún
> otro item use su `logicalId`.

### El notebook lleva el lakehouse adentro

```python
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "<GUID>",
# META       "default_lakehouse_name": "<lakehouse>",
# META       "default_lakehouse_workspace_id": "<GUID>",
```

> ⚠ **Nota de migración.** Esos GUID
> son del workspace anterior (`<org>/<repo-fabric-anterior>`). Los items vigentes
> están en `<org>/<repo-fabric>`, rama `fabric`: workspace
> `<GUID>`, lakehouse `<GUID>`,
> **sin esquemas** (`Tables/<tabla>`). Toma los valores de un item que ya
> funcione ahí, no de este ejemplo.

Esto mata dos trampas viejas: ya no hay que reasociar el lakehouse ni recapturar
los Base parameters en cada reimport. Y la celda de parámetros va marcada como
`# PARAMETERS CELL ********************` — sin esa marca **Fabric descarta los
parámetros en silencio** y el notebook corre con sus defaults.

### ⛔ `InvokeCopyJob` necesita `externalReferences`

```json
{
  "type": "InvokeCopyJob",
  "policy": { "timeout": "0.12:00:00", "retry": 0, "retryIntervalInSeconds": 30,
              "secureInput": false, "secureOutput": false },
  "typeProperties": { "copyJobId": "<logicalId>", "workspaceId": "<GUID>" },
  "externalReferences": { "connection": "<GUID>" }
}
```

**Sin `externalReferences`, el *Update all* falla con:**

```
Failed to discover dependencies
"ErrorMessage": "Object reference not set to an instance of an object."
```

Ese NullReference **no dice qué campo falta**. Costó dos despliegues y una
teoría equivocada (creímos que era el orden de creación de los items).

Ojo: son **dos conexiones distintas**. La del Copy Job va al share on-prem; la
del `InvokeCopyJob` va del pipeline al Copy Job.

### `policy` en todas las actividades

`SetVariable` lleva `{"secureInput": false, "secureOutput": false}`; las demás
llevan además `timeout`, `retry` y `retryIntervalInSeconds`.

### Parámetros de notebook: strings

```json
"parameters": { "fuente": { "value": "MB52", "type": "string" } }
```

**No pases booleanos.** `{"value": "False", "type": "bool"}` llega al notebook
como el string `"False"`, y en Python `not "False"` es `False`: la bandera se
ignora en silencio. Deja los booleanos como default en el notebook.

### Copy Job: `Binary`, no `DelimitedText`

El molde de MD04 está tipado como `DelimitedText` con `columnDelimiter: "|"`, o
sea que **parsea el archivo y lo reescribe**. Dos problemas: el parser ALV
depende de la posición exacta de los pipes, y un XLSX pasado por DelimitedText se
corrompe.

`Binary` copia byte por byte y conserva el nombre — de donde sale `FILE_DATE`.
Verificado: Fabric lo acepta y lo conserva tras la normalización.

### Las rutas de origen son RELATIVAS a la conexión

MD04 usa `folderPath: "ZMM_MD04"`, no la ruta completa: la conexión del gateway
ya apunta a `<carpeta-compartida>`. **Reusa el GUID
de conexión del Copy Job que ya funciona** — ese id identifica la conexión
autorizada y no se puede inventar.

### Después del Update all, los items salen como *Modified*

Es normal: Fabric completa la definición al materializarlos. **Commitea** para
que git guarde la versión normalizada — y de paso te deja verificar qué respetó
y qué reescribió.

**Lo que reescribe en los notebooks es cosmético, y ensucia los diffs.** Fabric
quita las líneas en blanco de los bloques markdown y las pega al renglón anterior
(`# # Título` en vez de `#` + `# Título`), y le quita el salto de línea final al
`.platform`. Así que **todo PR posterior al primer commit desde el workspace
arrastra ese ruido**, y a simple vista parece que Fabric cambió algo de fondo.

Antes de leer un diff de estos, sepáralo:

```bash
gh pr diff <n> --repo <owner>/<repo> \
  | grep -E "^[+-]" | grep -vE "^(\+\+\+|---)" \
  | grep -vE "^[+-]\s*#" | grep -vE "^[+-]\s*$"
```

Lo que quede es el cambio de verdad. Si sale vacío, el PR es puro reformateo.

Es un ping-pong sin consecuencias: se mergea tu versión, Fabric la vuelve a
normalizar en el siguiente commit. No pelees con él ni adoptes su formato.

---

## 5. Nomenclatura: `ERP_TRANSACCION_ESPECIFICACION`

**Regla del equipo, obligatoria y sin excepciones.** Toda tabla, Copy Job,
pipeline y notebook lleva tres segmentos:

```
ERP  _  TRANSACCION  _  ESPECIFICACION
SAP  _  ZSD49N       _  ALLUS
SAP  _  MB51         _  ALLUS
```

- **ERP** — el sistema de origen: `SAP`, `ORACLE`, `JDE`, `D365`.
- **TRANSACCION** — el código con el que se teclea en el ERP: `ZSD49N`, `MB51`,
  `MB52`, `COOIS`, `ZE_SD48`. **No es el nombre del job ni el del archivo.**
  `SDDnnn`, `SDDnnn` y `MMS103` son nombres de descarga, no transacciones, y no
  van en este segmento. De qué carpeta sale cada uno se contesta en
  `sap-catalogo-fuentes`, que es donde vive esa correspondencia.
- **ESPECIFICACION** — qué recorte de esa transacción es: `ALLUS`, `VMI`, `PD`,
  `HEADERS`, `COMPONENTS`. **Nunca se omite**, aunque hoy exista un solo
  extracto. El día que aparezca el segundo, el primero se queda sin cómo
  llamarse y hay que renombrarlo — que es justo lo que rompe las referencias por
  `logicalId`.

El tipo de item y la capa van como sufijo:

```
SAP_ZSD49N_ALLUS            tabla cruda
SAP_ZSD49N_ALLUS_CLEAN      tabla limpia
SAP_ZSD49N_ALLUS_COPYJOB    Copy Job
SAP_ZSD49N_ALLUS_PIPELINE   pipeline
```

⛔ **`SAPCARGA_` quedó deprecado.** Los items que ya lo llevan **se quedan como
están** —renombrarlos rompe las referencias por `logicalId`— pero nada nuevo lo
usa.

### Las carpetas del workspace: una de SAP, y adentro una por transacción

```
SAP_TRANSACIONES/            la carpeta del ERP
├── SAP_ZSD49N/              una por TRANSACCION, no por extracto
│   ├── SAP_ZSD49N_ALLUS_COPYJOB.CopyJob
│   └── SAP_ZSD49N_ALLUS_PIPELINE.DataPipeline
├── SAP_MB51/
├── SAP_MB52/
└── SAP_COOIS/
```

Los extractos distintos de una misma transacción **conviven en la carpeta de su
transacción**; los distingue el segmento ESPECIFICACION del nombre, que para eso
está. No se abre una carpeta por extracto.

> `SAP_TRANSACIONES/SAP_ZSD49N_VMI/` es anterior a esta regla y se queda donde
> está. No es el patrón a copiar.

### La convención acerca los nombres; el cuidado al borrar sigue siendo tuyo

Se desplegaron items llamados `MB52_ON_PREM_DATA_TO_LAKEHOUSE` y
`MB52_PIPELINE_CI` en un workspace donde ya vivían
`SAP_MB52_ON_PREM_DATA_TO_LAKEHOUSE`, `MB52_PIPELINE` y `SAP_MB52_CI_PL`.

Cuatro nombres a un prefijo de distancia. Resultado: **se borraron items buenos
por error** tratando de distinguir lo nuevo de lo viejo.

La convención ayuda porque el nombre dice *qué extracto es*, en vez de dejar la
diferencia en un prefijo que hay que adivinar. Pero **no resuelve el incidente
de arriba: lo agudiza.** `SAP_ZSD49N_ALLUS` y `SAP_ZSD49N_VMI` se parecen a
propósito, y en una lista larga son casi el mismo renglón. Así que lo que salvó
aquella vez sigue siendo obligatorio:

- **Antes de nombrar, lista los nombres que ya existen** y busca parecidos, no
  solo colisiones exactas.
- **Antes de borrar cualquier item, comprueba que ningún otro use su
  `logicalId`.** Con nombres que se parecen por diseño, la lista de nombres ya
  no alcanza para decidir qué sobra.
- **No inventes carpetas nuevas.** La estructura está definida arriba: si el
  item no cabe en la carpeta de su transacción, el problema es el nombre, no la
  carpeta.

---

## 5 bis. ⛔ "This Git branch was deleted" casi nunca significa eso

El panel *Source control* de Fabric puede mostrar **"This Git branch was
deleted"** con un botón para ir a desconectar la rama. Visto
durante un incidente de GitHub: la rama existía perfectamente.

Fabric le pregunta a GitHub si la rama existe. Con la API degradada la pregunta
devuelve **404**, y Fabric traduce ese 404 a "la borraron". El mensaje es una
conclusión, no un dato.

**Antes de tocar ese botón, comprueba el hecho:**

```bash
git ls-remote --heads https://github.com/<owner>/<repo>.git <rama>
```

Si sale el SHA, la rama está viva y **no hay nada que arreglar**: se espera y se
recarga el panel con ↻. Desconectar rompería una conexión sana por información
falsa, y luego hay que rearmar el mapeo del workspace.

Es el mismo patrón de la sección 6: un mensaje alarmante de Fabric empujando a
una acción destructiva. **Verifica primero, actúa después.**

## 6. Cuando algo se borra por error

**Mientras no le des Commit, git conserva el estado bueno.** Los borrados del
workspace aparecen en *Changes* como `Deleted`; se deshacen con **Undo** (el
botón está al fondo del panel, junto a Commit — se corta si la lista es larga).

**Nunca commitees con borrados pendientes que no entiendas.**

---

## 7. Clonar el repo en Windows falla

`git clone` del repo de Fabric deja el working tree incompleto: hay items con
espacios al final y `&#32;` en el nombre, que Windows no puede crear. Un
`git add -A` en ese estado **borra cientos de archivos**.

La salida es **git sin working tree**: el índice se arma a mano y esos nombres
nunca tocan el disco. Hay dos caminos y conviene conocer los dos, porque el
primero se cayó.

### ⛔ Cuando la Git Data API contesta 404 (visto)

`gh api` puede empezar a contestar **404 en todo lo que sean datos de git**
—`git/ref`, `git/refs/heads`, `git/blobs`, `commits`, `branches`, `tarball`—
con el mismo token que **sí** lee la metadata del repo y los pull requests. Pasó
en dos repos de la misma organización a la vez, y no era intermitencia de un
reintento: falló igual tres veces seguidas durante un buen rato.

Lo que confunde es el **404**: se lee como "esa rama no existe" y manda a buscar
quién la borró. **No lo asumas.** Pregúntale al protocolo git, que va por otro
camino:

```bash
git ls-remote --heads https://github.com/<owner>/<repo>.git
```

Si ahí salen las ramas, el repo está entero. La primera vez perdí un rato
convencido de que alguien había borrado la rama `fabric` con todo el trabajo.

**Pista de que es degradación de GitHub y no permisos:** al poco rato
`gh pr create` empezó a tirar `HTTP 503 ... api.github.com/graphql`. Si ves 503
en GraphQL, el 404 de las otras rutas es del mismo lado, no tuyo.

**Lo que siguió funcionando:** el protocolo git, y la API REST de *pulls*. Así
que el PR se crea con `gh api -X POST repos/<owner>/<repo>/pulls` en vez de
`gh pr create`, que usa GraphQL.

### El camino que funciona: `--no-checkout` + plumbing

```bash
git clone --no-checkout --depth 1 --branch <rama-base> <url> repo
cd repo
git read-tree <rama-base>                    # el indice desde el ARBOL, no del disco
sha=$(git hash-object -w --stdin < archivo)   # el blob
git update-index --add --cacheinfo 100644,$sha,"ruta/dentro/del/repo"
tree=$(git write-tree)
commit=$(git commit-tree $tree -p <rama-base> -m "mensaje")
git push origin $commit:refs/heads/<rama-nueva>
gh pr create --base <rama-base> --head <rama-nueva> --title ... --body ...
```

`read-tree` es la clave: `git add` querría leer el working tree que a propósito
no existe. Y `gh pr create` sí funciona — la API de *pulls* nunca se cayó.

Ver `assets/push_git.py` (vigente) y `assets/push_items.py` (el de la API, por si
la vuelven a habilitar).

Y **verifica el diff antes de mergear**:

```bash
git -C repo diff --stat <rama-base> <rama-nueva>
```

Solo deben aparecer tus archivos. Si sale algo borrado que no es tuyo, párale.

---

## 7 pre. ⛔ Los notebooks de Fabric traen los saltos de línea MEZCLADOS

Fabric guarda `notebook-content.py` con dos terminadores a la vez:

| lo que es | terminador |
|---|---|
| el andamiaje `# META`, `# CELL`, `# METADATA` | **LF** |
| las líneas de código | **CRLF** |

Cualquier script que lo lea como texto y lo vuelva a escribir uniforma los dos
—da igual a cuál— y reescribe las ~70 líneas de andamiaje. El cambio de verdad
queda enterrado entre ellas.

Y hay una trampa encima: en Windows, `subprocess.run(..., text=True)` **traduce
los saltos al escribir en la tubería**, así que el archivo llega al repo con
terminadores distintos de los que tiene en disco. Se ve bien en el editor y mal
en el PR.

> **La herramienta que empuja no opina sobre el formato: manda los BYTES tal
> cual.** `p.read_bytes()` y `subprocess.run(..., input=datos)` sin `text=True`.
> El espejo local guarda la verdad, y se repone desde la rama cuando se desvía.

Intentar ser listo tampoco funciona: una versión intermedia convertía "al estilo
que usa la rama", contaba CRLF contra LF y ganaba CRLF — y volvía a reescribir
las 70 líneas de andamiaje, que son justo las LF. **Un archivo mezclado no tiene
"un estilo".**

Antes de empujar, mide:

```python
crlf = b.count(b"\r\n"); lf = b.count(b"\n") - crlf
```

Si el diff del PR tiene más líneas que tu cambio, **no lo mergees**: revisa los
saltos de línea antes. Un diff de archivo completo no se puede revisar, y un
cambio de verdad se esconde ahí sin ningún esfuerzo.

## 7 pre bis. ⛔ El Copy Job incremental y la fecha que Windows conserva

Todos los Copy Jobs usan `readMethod: "SnapshotPlusIncremental"`, que copia lo
modificado **desde la última corrida**, comparando la fecha de modificación.

Y ahí está la trampa: **al copiar un archivo, Windows conserva la fecha de
modificación del original.** El reporte llegó a `<unidad-compartida>` a la una de la tarde pero
presentándose como "modificado 11:15". La corrida de las 12:16 ya había movido la
marca de agua más allá, así que desde entonces lo saltaba. Iba a saltarlo
siempre, por más veces que se corriera.

> **Un archivo dejado A MANO en la carpeta de origen necesita que se le refresque
> el sello, o el Copy Job incremental no lo ve nunca.**

```powershell
(Get-Item "<carpeta-compartida>").LastWriteTime = Get-Date
```

**Renombrarlo NO basta**: en Windows renombrar no cambia la fecha de
modificación.

La alternativa es pasar el Copy Job a `jobMode: "Batch"` —copia completa cada
vez—, y ahí la llave `changeDataSettings` **se quita**, no se cambia de valor.
Pero eso crece con los meses: una carpeta con un extracto diario de 6 MB llega a
2 GB al año, y copiarla completa todos los días deja de ser gratis. Solo vale la
pena si la carpeta de origen se poda.

**Cómo se detecta:** el archivo está en la carpeta de origen y no en el
lakehouse. El aviso del cargador —*"el archivo más reciente tiene N días"*— es la
señal de que algo se quedó sin viajar.

## 7 pre ter. ⛔ El `~$` de Excel tumba el Copy Job entero

    Error occurred when trying to access the file in Folder
    '\...\<reporte SAP>\~$07.SEP.2026 - SK Shipment report.xlsx', File filter: ''
    The process cannot access the file ... because it is being used by
    another process.

`~$<nombre>` es el **archivo de propietario** que Excel crea mientras alguien
tiene el libro abierto y borra al cerrarlo. Windows lo mantiene bloqueado, el
gateway no lo puede leer, y **se cae la copia completa** — no ese archivo, la
corrida entera.

Las once fuentes anteriores nunca lo vieron porque todas son listas ALV en `.txt`
que SAP escribe y nadie abre. **En cuanto una fuente es un XLSX que vive en una
carpeta donde una persona trabaja, esto va a pasar.**

### Se tapa en las DOS capas, y protegen de cosas distintas

**1. Que el Copy Job no lo intente copiar** — es lo que desbloquea la corrida.

Los comodines de ADF son solo `*` y `?`: **no hay forma de decir "todo MENOS lo
que empiece con `~$`"**. Pero sí de exigir la forma del nombre bueno, y ahí es
donde se separan:

```
  07.SEP.2026 - SK Shipment report.xlsx   ->  '0' '7' '.'   casa
~$07.SEP.2026 - SK Shipment report.xlsx   ->  '~' '$' '0'   no casa
```

El prefijo ocupa **exactamente dos caracteres**, así que pedir un punto en el
tercero —el separador del día— lo deja fuera:

```json
"storeSettings": {
  "recursive": true,
  "enablePartitionDiscovery": false,
  "wildcardFileName": "??.*.xlsx"
}
```

> Compruébalo con `fnmatch.fnmatchcase`, que implementa los mismos dos
> comodines. Incluye en la prueba el bloqueo de un día de **un solo dígito**
> (`~$1.SEP...`), que es el caso que casi se cuela.

**2. Que el cargador no lo consideraría** — es la red por si algún día se cuela.

No es paranoia: el bloqueo **termina en `.xlsx`** y su nombre **conserva la
fecha**, así que pasa los tres filtros de selección y **empata** con el archivo
bueno; el desempate por hora tampoco los separa. La tabla se quedaría con 165
bytes de basura binaria. El descarte va por el prefijo, antes de todo lo demás, y
aplica a **todas** las fuentes: es basura de Windows, no de una transacción.

```python
candidatos = [f for f in archivos
              if not f.isDir and not f.name.startswith("~$")
              and f.name.lower().endswith(CFG["extensiones"])]
```

### El precio, y por qué es aceptable

Cambiar el filtro hace que el Copy Job vuelva a hacer **snapshot completo**. Es
inofensivo: el destino es `Append` y el cargador elige por fecha del nombre y
descarta por nombre + contenido (§ 7 quater).

### El riesgo que queda, dicho en voz alta

El comodín **es posicional**: si mañana los archivos llegan como
`7.SEP.2026 - ...` (día sin cero) o `2026-09-07 ...`, dejan de casar y el Copy
Job **no copia nada sin fallar**. El cargador seguiría sirviendo el último
archivo que sí llegó, y el pipeline saldría verde. La señal es el aviso de
§ 7 pre bis: *"el archivo más reciente tiene N días"*. **Si cambia la convención
del nombre, hay que cambiar el comodín.**

## 7 pre quater. ⛔ `to_date` no devuelve nulo cuando no casa: TRUENA

    SparkUpgradeException
    [INCONSISTENT_BEHAVIOR_CROSS_VERSION.PARSE_DATETIME_BY_NEW_PARSER]
    Fail to parse '26.5.2026' in the new parser.

El normalizador probaba varios formatos con un `coalesce`:

```python
F.coalesce(
    F.date_format(F.to_date(c, "dd.MM.yyyy"), "yyyy-MM-dd"),
    F.date_format(F.to_date(c, "d.M.yyyy"),   "yyyy-MM-dd"),   # nunca llegaba
    ...)
```

**Eso solo funciona si el formato que no casa devuelve NULO.** Con la política
por default de Spark 3 —`EXCEPTION`— lo que hace es **lanzar**, y `coalesce`
evalúa sus ramas en orden: la primera que no case tumba el notebook antes de que
las siguientes tengan turno.

> **Una cascada de `to_date` es una ilusión mientras la política sea EXCEPTION.**

Pasó desapercibido en ocho fuentes porque en todas el **primer** formato casaba
con todos los valores y `coalesce` corta ahí. Bastó un `26.5.2026` —sin ceros de
relleno, contra un `dd.MM.yyyy` que exige dos dígitos— para que muriera en la
primera fila. La cascada nunca funcionó; simplemente nadie la había usado.

```python
# CORRECTED, NO LEGACY: se queda el parser nuevo y solo deja de tronar.
# LEGACY además cambia las reglas de parseo de las fuentes que hoy funcionan.
spark.conf.set("spark.sql.legacy.timeParserPolicy", "CORRECTED")
```

### ⛔ Y al dejar de tronar, hace falta una guardia

Lo que antes reventaba ahora sale en **nulos callados**: si el formato del
reporte cambia, la columna llega VACÍA al tablero y el pipeline sale en verde.

La regla que distingue los dos casos: **que fallen algunos valores es dato
sucio, un aviso; que fallen TODOS es un cambio de formato, y se aborta.**

```python
_r = df.select(
    F.count(F.when(_tenia, F.lit(1))).alias("tenian"),
    F.count(F.when(_tenia & F.col(_c).isNull(), F.lit(1))).alias("malos"),
).first()   # las dos cuentas en UNA pasada: un count() por columna no es gratis
```

### Por qué la prueba local no lo agarra

`probar_*_local.py` valida el mapeo con **pandas**, que parsea con otras reglas y
acepta `26.5.2026` sin chistar. **Cualquier cosa que dependa del parser de Spark
—fechas, casts, `coalesce`— solo aparece corriendo el notebook.** La prueba local
sirve para el esquema y los nombres, no para los tipos.

## 7 bis. Trampas de PySpark que ya nos costaron

**`Row` no tiene `.get()`.** Soporta `r["col"]` y `r.col`, pero no el `.get()`
de diccionario. Esto truena con un `AttributeError: get` que no dice dónde:

```python
por_estatus = {r["clave"]: r for r in df.groupBy(...).agg(...).collect()}
fila.get("filas", 0)            # AttributeError
```

Al construir diccionarios desde `collect()` o `first()`, **siempre `.asDict()`**.

**`spark.read.option("wholetext", True)` ignora el bool.** `option()` espera un
string; con un bool la opción se descarta en silencio. Ver la sección 1.

**⛔ `mssparkutils.fs.head` corta a 100 KB, le pidas lo que le pidas.** El
segundo argumento no sube ese techo: devuelve los primeros 102,400 bytes **como
si fueran el archivo completo**, sin error ni aviso. El reventón llega después,
en el parser, y no menciona el truncamiento:

```
JSONDecodeError: Expecting ',' delimiter: line 1 column 102401 (char 102400)
```

Ese `102401` es la única pista. Para leer un archivo entero de OneLake, usa el
punto de montaje:

```python
with open(f"/lakehouse/default/{carpeta}/{nombre}", encoding="utf-8") as fh:
    crudo = fh.read()
```

Y **compara los bytes leídos contra `fs.ls(...)[0].size`**. Una lectura corta que
casualmente parsee —un JSON de arreglos anidados puede cerrar antes de tiempo—
pasa desapercibida y contamina todo lo que venga después.

`fs.head` sirve para espiar las primeras líneas de un archivo, no para leerlo.

**Las rutas de OneLake distinguen mayúsculas.** `Files/SAP/Proveedor-A` y
`Files/SAP/Proveedor-A` son rutas distintas, y la segunda es la que existe. Antes de
escribir una ruta en la config, **lístala**:

```python
for f in notebookutils.fs.ls("Files/SAP"):
    print(f.name)
```

**Y cuando un `ls` falle, distingue `PathNotFound` de "no hay lakehouse".** Un
mensaje que diga "revisa que el notebook siga asociado al lakehouse" cuando lo
que falta es la carpeta manda a buscar por el lado equivocado. Al fallar,
**lista las carpetas hermanas** en el propio mensaje: el nombre correcto salta a
la vista sin ir a buscarlo.

### ⛔ `spark.table("nombre")` necesita un lakehouse ADJUNTO — y su hermano falla callado

```
UnsupportedOperationException
No default context found, please attach a lakehouse before running spark sql
queries with partial namespaces
```

`spark.table("sap_zmm_md04_vigente")` usa un **namespace parcial**: depende de
que el notebook tenga un lakehouse adjunto. Corriendo a mano suele funcionar
—la sesión hereda el lakehouse del notebook abierto— así que el problema
aparece hasta que lo lanza el pipeline. **Declarar `dependencies.lakehouse` en
el METADATA no basta.**

**Lo peligroso no es ese error, es su hermano silencioso.** `spark.table(...)`
truena y se ve. Pero `spark.catalog.tableExists(nombre)` en la misma situación
**no truena: devuelve `False`**. Y ese patrón está en todos lados:

```python
uom = spark.table(TABLA_UOM) if spark.catalog.tableExists(TABLA_UOM) else None
```

Sin lakehouse adjunto se va por la rama del "no existe" y el proceso sigue
**como si la tabla no estuviera** — dejando la medida que dependía de ella en
nulo, sin error, con el pipeline en verde. Es el default silencioso de la § 14
de `dashboard-standards`, entrando por una puerta nueva.

> **Lee las tablas por su RUTA, no por su nombre.** No hay contexto que
> heredar ni que adjuntar, y funciona igual a mano que desde el pipeline.

```python
def tabla(nombre):
    return spark.read.format("delta").load(f"{base_path}/Tables/{nombre}")

def tabla_existe(nombre):
    """Le pregunta al ALMACENAMIENTO, no al catálogo."""
    try:
        return notebookutils.fs.exists(f"{base_path}/Tables/{nombre}")
    except Exception:
        return False
```

Y que el notebook no arranque a ciegas: si la tabla fuente no está en la ruta
que arman `workspace_id` y `lakehouse_id`, decirlo **con la ruta completa** en
vez de fallar tres celdas más adelante.

**Un `grep` que lo caza antes de desplegar:**

```bash
grep -n "spark\.table(\|spark\.catalog" notebook-content.py
```

Cualquier resultado fuera de un comentario es un item que va a fallar —o peor,
a mentir— cuando lo corra un pipeline.

### ⛔ Un alias de join no sobrevive a una cadena de `withColumn`

```
A column or function parameter with name `m`.`qty_107` cannot be resolved.
Did you mean one of the following? [`qty_107`, `qty_108`, ..., `z`.`ETD`]
```

El join estaba bien. Lo que lo rompe es lo que viene despues:

```python
j = a.alias("z").join(b.alias("m"), ["po"], "left")
j = j.withColumn("qty_107", medida(F.col("m.qty_107")))   # crea una de PRIMER NIVEL
...
j = j.withColumn("estatus", F.when(F.col("m.qty_107") <= 0, ...))   # ⛔ ya no resuelve
```

Al crear una columna de primer nivel **con el mismo nombre**, esta tapa a la del
alias; y despues de varios `withColumn` el DataFrame ya es una proyeccion donde
el calificador dejo de existir.

**La pista está en el propio mensaje:** sugiere `qty_107` a secas y sigue
reconociendo `z`.`ETD`. O sea que el alias que *todavia no se ha tapado* si
resuelve — es un fallo por SOMBRA, no por alias invalido. Por eso aparece a
media cadena y no al construir el join, que es lo que despista.

> **No dependas del alias: prefija antes de unir.** Asi ningun nombre choca y no
> hay nada que calificar.

```python
LLAVES = ("po", "material_norm")
b_pref = b.select(*[F.col(c).alias(c if c in LLAVES else f"b_{c}") for c in b.columns])
j = a.join(b_pref, list(LLAVES), "left")
```

**Y esto los greps NO lo atrapan.** Es el limite de la prueba local: sin Spark no
hay plan que resolver, asi que los patrones conocidos —`.get()` sobre Row, el
`NULL` en filtros, `spark.table`— se cazan leyendo, pero la resolucion de
nombres solo falla corriendo. Un grep util antes de subir:

```bash
grep -n 'F\.col("[a-z]\.' notebook-content.py    # cualquier referencia calificada
```

Si sale algo y el notebook encadena `withColumn`, prefija en vez de calificar.

### ⛔ Después del `.collect()`, el nulo es de Python — y `sorted()` truena

```
TypeError: '<' not supported between instances of 'NoneType' and 'str'
```

Al hacer `.collect()`, una columna anulable de Spark llega a Python como
`None`. Ordenar una colección que mezcla `None` con `str` truena — y **el
mensaje no dice qué campo fue**, así que hay que ir a buscarlo a mano entre
todos los `sorted()` del notebook.

**La salida fácil es peor que el error.** Lo que sale natural es filtrarlos:

```python
sorted({f["centro"] for f in filas if f["centro"]})     # ⛔
```

Eso no truena, y por eso es peor: **tira el nulo del catálogo en silencio**.
Esas filas quedan inalcanzables por cualquier filtro del tablero — el mismo
bug del § 13 bis de `dashboard-standards`, entrando por otra puerta.

> **El nulo se aparta antes de ordenar y se devuelve al final, no se filtra.**

```python
def valores(campo, filas):
    vistos = {f[campo] for f in filas}
    hay_nulo = any(v is None or v == "" for v in vistos)
    return (sorted(v for v in vistos if v is not None and v != "")
            + ([None] if hay_nulo else []))
```

**Y ojo con el arreglo a medias, que fue el segundo intento y falló igual.**
Para una colección de tuplas se separó en dos `sorted` —las que tienen clave y
las que no— y parecía suficiente. No lo es: si en el dato conviven `None` y
`""` —que pasa—, el grupo de los "vacíos" acaba comparando `None` con `""` y
truena un nivel más abajo. Se resuelve con una **llave de ordenamiento que
nunca compara `None`**, y colapsando `""` a `None` para que el catálogo no
traiga dos entradas que significan lo mismo:

```python
sorted(pares, key=lambda x: (x[0] is None, x[0] or "", x[1]))
```

**Cómo se prueba sin subir nada:** con un caso a mano que traiga nulos en
**todos** los campos, incluida la mezcla `None`/`""`, y comprobando que el JSON
resultante serializa. Es la clase de error que el dato de prueba bonito nunca
encuentra.

### ⛔ `NULL == "x"` no es `False`, es `NULL` — y el filtro te vacía la tabla

La que más caro salió. Spark usa lógica de **tres valores**, Python de dos:

```python
es_rechazada = F.col("_accion") == "x"      # _accion es NULL si no hay motivo
limpio = df.filter(~es_rechazada & ~ya_facturada)
```

`NULL == "x"` → `NULL`. `~NULL` → `NULL`. `NULL & lo que sea` → `NULL`, y el
filtro descarta la fila. **`SAP_ZSD49N_CLEAN` salió con 36 filas de 17,323**: se
cayeron justo las líneas *sin* motivo de rechazo, o sea las normales. Las 36
sobrevivientes eran las únicas con un código en el catálogo — por eso el tablero
reportó que el 100% de la demanda estaba bloqueada, y era creíble.

En Python `None == "x"` **sí** da `False`, así que el prototipo local pasó limpio.

```python
es_rechazada = F.col("_accion").eqNullSafe("x")               # NULL <=> "x" = False
sin_valor    = F.coalesce(F.col("cantidad"), F.lit(0.0)) != 0  # o coalesce antes
```

Aplica a cualquier columna anulable dentro de un `filter`, un `~`, un `&` o un
`|`. En un `F.when` no muerde: la condición `NULL` simplemente no coincide y cae
al siguiente `when`.

**La red que lo caza sola:** cuando un proceso reparte filas en cubetas, verifica
que sumen la entrada, y **aborta** si no.

```python
if n_rechazadas + n_facturadas + SALIDA != ENTRADA:
    raise ValueError(f"Se perdieron filas: entrada {ENTRADA:,} pero "
                     f"{n_rechazadas:,} + {n_facturadas:,} + {SALIDA:,} = "
                     f"{n_rechazadas + n_facturadas + SALIDA:,}")
```

`297 + 13,541 + 36 != 17,323` lo hubiera detenido en la corrida misma, en vez de
descubrirlo tres notebooks después porque un KPI se veía raro. Un conteo que
sobrevive solo no basta: **cuadra las cubetas contra el total**.

**El límite de la prueba local.** Ejecutar las celdas del notebook fuera de
Fabric sirve para el parser y las reglas de negocio, pero **salta las celdas que
usan Spark**, así que esta clase de error no puede aparecer ahí. Compénsalo:

- Validaciones que corran **antes** de escribir, para que un fallo no deje la
  tabla a medias.
- Un `grep` de `.get(` sobre variables que vengan de `collect()` / `first()`
  antes de desplegar.
- Un `grep` de `~F.col`, `filter(` con `&`/`|`, y `== "` sobre columnas
  anulables: es donde se esconde el `NULL` de arriba.
- **Compara el conteo de la corrida real contra el del prototipo local.** Si el
  local decía 3,412 y Fabric dice 36, no es que los datos cambiaron.

## 7 ter. ⛔ Un cuadre por totales no prueba que el día a día esté bien

La razón: un **traspaso entre plantas viene como dos renglones** con el mismo
`Object_Number`, la salida negativa y la entrada positiva. Consolidado por
material **se cancelan en el total**, así que cualquier suma pasa en verde. Pero
las dos patas **traen fechas distintas**, y en el día a día el material
desaparece del balance durante el tránsito aunque nunca salió de la empresa.

Como el faltante es el **punto más bajo** del balance, se tragaba el hueco: un
material reportaba 772 cuando su faltante real eran 386.

### La regla

- **Si la medida es un extremo (mínimo, máximo, pico, primer día en rojo), un
  cuadre por sumas no la valida.** Suma y extremo son preguntas distintas: dos
  renglones que se cancelan dejan la suma intacta y mueven el extremo.
- **Valida el extremo contra su propia definición.** El chequeo que encontró
  esto fue `Faltante == -min(Inventario_Final)`, no una suma.
- **Un renglón negativo donde esperas positivos es una pata, no un dato.**
  Busca su gemelo por **número de documento**, nunca por cantidad: cruzar por
  cantidad da producto cartesiano y "tránsitos" negativos que no existen.
- **Quita las dos patas, no solo la negativa.** Dejar la entrada inventa
  material en la planta que recibe y tapa faltantes reales.
- **Un par al que le falta una pata suele ser el horizonte del extracto**, no un
  movimiento real: su gemelo cae después del último día del archivo.

### Cómo se detecta antes de que llegue al tablero

Un número aritméticamente imposible en la lista que el usuario ve. En este caso:
inventario 166, demanda 552, suministro 0, faltante 772 — sin suministro el
balance solo baja, así que 772 no cabía. **Revisa a mano las 10 filas más
expuestas de cada tablero antes de darlo por bueno**; la fila que no cierra
sola es la que destapa el error de diseño.

## 7 quater. ⛔ Cambiar el parser no recarga nada: la bitácora lo salta

El cargador es idempotente. Si el archivo del día ya está en la bitácora,
`if ya_cargado and not force_reload:` sale temprano y **no reprocesa**. El
pipeline corre, sale en verde, y la tabla se queda exactamente igual.

Eso está bien casi siempre, y está mal justo cuando **cambiaste el código de
lectura**: arreglas la codificación, subes el PR, corres el pipeline, y el dato
sigue roto porque el archivo nunca se volvió a leer.

### ⛔ Y la identidad de un archivo NO es su nombre

La bitácora comparaba `(fuente, nombre, estado="OK")`. Para las fuentes cuyo
nombre lleva la fecha eso alcanza —cada día es un archivo distinto—, pero **un
catálogo estático se llama siempre igual**, así que quedaba marcado como cargado
para siempre: no era que costara recargarlo, es que **nunca iba a poder
recargarse**.

Y el `Skipped` es una salida limpia, así que el pipeline reporta éxito.

> **Un catálogo se recarga SIEMPRE.** Correr su pipeline ya es la instrucción
> "recárgalo": no hay nada que detectar, y son mil renglones. La fuente lo
> declara con `"siempre_recargar": True`, y eso es más simple y más robusto que
> cualquier detección de cambios.

Y para las fuentes que sí llevan bitácora:

> **La identidad es `(fuente, nombre, tamaño, sello de modificación)`.** Si el
> archivo se reemplaza, el tamaño o el sello cambian y se recarga solo. Sirve
> para el otro caso: un extracto del mismo día re-exportado y corregido llega
> con el mismo nombre.

Y cuando la bitácora **no pueda probar** que es el mismo archivo —filas viejas
sin esas columnas—, se recarga. Reprocesar cuesta minutos; servir el dato viejo
cuesta decisiones. El default va del lado seguro.

**La señal de que te pasó:** el output de la actividad dice `"status": "Skipped"`.
Si corriste el pipeline esperando datos nuevos y ves eso, no se cargó nada.

**Cada vez que toques el parser, el mapeo de columnas o la codificación, la
recarga va con `force_reload = True`.** Y la señal para confirmar que sí pasó no
es que el pipeline salga verde: es que **`actualizado` de esa fuente en el
`meta.json` sea posterior a tu cambio**. Si dice una hora anterior, no corrió —
y el tablero te va a enseñar el dato viejo sin quejarse de nada.

## 7 quinquies. ⛔ Mergear no es probar: corre el item ANTES del merge

La causa estaba lejos del cambio: `limpio()`, el saneador que corre sobre cada
valor antes de `json.dumps`, conocía `None`, bool, fechas, int y str, y todo lo
demás lo mandaba a `float()`. Nunca había visto una columna `array` porque
**ninguna de las pestañas anteriores publicaba una**. La pestaña nueva sí —la
lista de plantas de cada factura— y la reventó.

### La regla

- **Ningún cambio a un item que ya corre en producción se mergea sin haberlo
  corrido una vez completo.** No "lo leí con calma", no "es aditivo":
  **corrido**, en Fabric, de principio a fin. Cuesta cinco minutos, y ese día
  costó un día de datos viejos.
- **Correr incluye mirar lo que produjo**, no solo que salga en verde: el
  `generated_at` del `meta.json`, el conteo de filas, el tamaño de cada archivo.
  Ver § 15 de `dashboard-standards`.
- **Un cambio que solo AGREGA también rompe.** Aquí no falló la pestaña nueva:
  falló una función compartida que llevaba meses bien y que la pestaña nueva
  estrenó por un camino inédito. Lo que se prueba no es lo que tocaste, es
  **el item entero**.
- **Pregúntate qué estrena el cambio**: un tipo de dato que nunca había pasado
  por ahí (array, struct, fecha nula, texto con acentos), una tabla que antes no
  se leía, un archivo que antes no existía. Ahí es donde se rompen las
  funciones compartidas, no en las líneas que escribiste.
- **Si el item vive dentro de un pipeline, prueba el pipeline**, no el notebook
  suelto: el orden entre actividades es parte de lo que cambiaste.
- **Cuando falle, el error exacto está en el historial de ejecuciones de
  Fabric** (`errorValue`). Leerlo es más rápido que deducirlo del código.
- **Una actividad que falla se lleva a las que dependen de ella, y eso no se
  ve.** Aquí el Copy que publica dependía del notebook: al morir el notebook, la
  copia se saltó y el JSON viejo se quedó en su lugar. Un tablero con datos de
  ayer se ve **idéntico** a uno al día.

## 7 sexies. ⛔ Dos formatos de la misma fuente = un solo esquema

**1. El nulo de la fuente se escribe de más de una forma.** SAP dice "esta fila
no tiene fecha" con `00.00.0000` en un formato y `00/00/0000` en el otro. El
cargador solo conocía el de los puntos, así que el literal con diagonales se
escribió tal cual en la columna `Date`. Nadie se enteró en la carga; tronó dos
pasos después, al publicar:

```
ValueError: 2,808 valores de Date no parsean con
            formato=('dd.MM.yyyy', 'MM/dd/yyyy')
```

El chequeo tenía razón: eran un nulo que nunca se declaró. Pero el error salió
en el publicador, a dos notebooks de distancia del lugar donde se podía
arreglar.

> **El nulo declarado de la fuente se resuelve en la CARGA.** Ahí es donde se
> conoce el archivo. Cada capa que lo deja pasar como texto tiene que volver a
> adivinar qué significa, y basta con que una no adivine igual para que el
> pipeline muera lejos de la causa.

**2. Los dos parsers devolvían esquemas distintos** — 14 columnas el tabulado y
21 el de ancho fijo. Siete columnas desaparecían según cómo se hubiera bajado el
archivo ese día, y dos de ellas se consumían aguas abajo. La tabla se reescribe
con menos columnas, el pipeline sale en verde, y los campos que se cayeron
simplemente dejan de existir.

> **Si una fuente se puede leer de dos maneras, las dos entregan EXACTAMENTE el
> mismo esquema, y hay un guardia que truena si dejan de coincidir.** No basta
> con que los dos parsers "funcionen": tienen que producir lo mismo.

```python
if list(cols) != list(COLUMNAS_ESPERADAS):
    raise ValueError(
        f"El parser {cual} entregó {len(cols)} columnas y el esquema común "
        f"tiene {len(COLUMNAS_ESPERADAS)}. Sobran {...}, faltan {...}.")
```

Y lo que un formato de verdad no pueda dar va en **NULO declarado y contado**,
nunca ausente: una columna que falta cambia el esquema, una columna en nulo no.

**Cómo se comprueba, y es barato:** un script local que **extrae los parsers del
propio notebook** —no una copia, que se desincroniza— y corre los dos formatos
lado a lado, comparando esquema, conteos y el formato de cada fecha. Es lo que
convirtió "los dos funcionan" en "los dos entregan lo mismo, medido".

## 7 septies. ⛔ La columna que venía gratis de un join comodín

```
PySparkValueError · errorValue: "Familia"
```

Que es `r["Familia"]` sobre una fila que no la trae — el nombre pelón, sin decir
qué tabla ni qué paso.

Dos reglas:

> **Cuando un campo deja de salir de un comodín y pasa a tener fuente real, hay
> que revisar TODAS las tablas que lo publicaban.** Antes lo recibían gratis por
> el join; después hay que pedirlo tabla por tabla. Y no da error al escribir:
> la columna simplemente ya no está.

> **Antes de leer una tabla campo por campo, comprueba que traiga los campos.**
> `r["X"]` sobre una columna ausente sale como el nombre solo en un error de
> motor. Tres líneas lo convierten en un mensaje que dice dónde buscar:

```python
def exigir(df, nombre, campos):
    faltan = [c for c in campos if c not in set(df.columns)]
    if faltan:
        raise ValueError(f"{nombre} no trae {faltan}. Sí tiene: {sorted(df.columns)}.")
```

## 8. El notebook cargador

- **Uno solo, parametrizado por fuente.** Lo que cambia entre MB52, ZSD49N y
  COOIS son datos (carpeta, tabla, formato, mapeo), no lógica. Un bug se arregla
  en un lugar.
- **Valida los insumos y falla con nombre propio**: qué columnas esperaba y no
  encontró. Eso vale más que veinte minutos de `AnalysisException`.
- **Termina con `notebookutils.notebook.exit(json.dumps({...}))`** para que el
  estado salga en el output de la actividad y no enterrado en el snapshot:
  ```json
  {"status": "OK", "filas": 13377, "columnas": 19, "cuarentena": 0,
   "numericos_ilegibles": {}, "por_confirmar": [...]}
  ```
- **Bitácora de archivos procesados** en su propia tabla, para no reprocesar y
  para saber qué se cargó cuándo.
- **Aborta antes de escribir** si el conteo de filas o de columnas no cuadra. El
  paso que publica tiene que poder fallar en rojo.

---

## Checklist antes de subir items a Fabric

- [ ] **Dos capas**: la cruda es fiel al archivo —nada filtrado, ninguna columna
      tirada— y todas las reglas de negocio viven en `_CLEAN`
- [ ] Perfilaste un archivo real: filas, columnas, encabezados repetidos, tipos
- [ ] El ALV se lee con `open()`, y el notebook valida cuántas líneas leyó
- [ ] Probaste el parser con CRLF, CR y LF, no solo con el archivo que te tocó
- [ ] El archivo se elige por la fecha del **nombre**, no por `modifyTime`
- [ ] Con Copy Job incremental, un archivo puesto A MANO lleva el sello
      refrescado; si no, no viaja nunca (§ 7 pre bis)
- [ ] Miraste **varios** archivos de la carpeta, no solo el más nuevo: los
      viejos pueden traer otro formato
- [ ] En XLSX: `dtype=object` y `StructType` explícito, sin inferencia
- [ ] Verificaste en la tabla ya cargada que los IDs conservan sus ceros a la
      izquierda (`00132844`, no `132844.0`)
- [ ] Contaste las columnas del archivo vs las que va a tener la tabla
- [ ] Las columnas numéricas están declaradas a mano, sin identificadores
- [ ] Los valores ilegibles salen NULL y contados, nunca 0
- [ ] `FILE_DATE` y `LOAD_DATE` presentes, con el patrón de fecha de esa fuente
- [ ] Comparaste tu `pipeline-content.json` **campo por campo** contra uno que ya
      funciona, y no falta ninguna clave
- [ ] `InvokeCopyJob` trae `externalReferences.connection`
- [ ] Todas las actividades traen `policy`
- [ ] Los parámetros de notebook van como `string`
- [ ] El Copy Job es `Binary` y su ruta de origen es relativa a la conexión
- [ ] Todo item nuevo se llama `ERP_TRANSACCION_ESPECIFICACION` (+ sufijo de
      tipo), la ESPECIFICACION **no se omitió**, y el segmento TRANSACCION es el
      código del ERP y no el del archivo (`ZSD49N`, no `SDDnnn`) (§ 5)
- [ ] El item cayó en `SAP_TRANSACIONES/SAP_<TRANSACCION>/`, y no agregaste
      carpetas nuevas (§ 5)
- [ ] Listaste los nombres que ya existen y buscaste **parecidos**, no solo
      colisiones exactas — la convención los acerca a propósito (§ 5)
- [ ] El diff del PR es solo `added` / `renamed` de items tuyos
- [ ] El diff del PR tiene **el tamaño de tu cambio**. Si sale el archivo
      completo, son los saltos de línea mezclados (§ 7 pre), no lo mergees
- [ ] Las fuentes de nombre FIJO (catálogos) se recargan siempre; la bitácora
      es para lo que llega distinto cada día (§ 7 quater)
- [ ] La bitácora distingue un archivo REEMPLAZADO de uno repetido (nombre +
      tamaño + sello) (§ 7 quater)
- [ ] **Cero celdas mágicas**: ningún `# MAGIC` en un item que se despliega por
      Git — Fabric las duplica al serializarlas (§ 4). El código compartido se
      inyecta al construir, no se invoca con `%run`
- [ ] Ningún `sorted()` sobre datos venidos de `.collect()` puede toparse con
      un `None` — y los nulos se devuelven al final, no se filtran (§ 7 bis)
- [ ] **Ninguna tabla se lee con `spark.table` ni `spark.catalog`**: por ruta
      `abfss`, o falla desde el pipeline y `tableExists` miente devolviendo
      `False` (§ 7 bis)
- [ ] Los calendarios van apagados hasta validar la primera corrida
- [ ] Probaste el parser en local contra el archivo real antes de desplegar
- [ ] **Corriste el item completo en Fabric ANTES de mergear**, y miraste lo
      que produjo —no solo que saliera en verde— (§ 7 quinquies)
- [ ] Si la fuente se puede bajar de dos formas, los dos parsers entregan el
      **mismo esquema**, con un guardia que truena si no (§ 7 sexies)
- [ ] El marcador de "sin dato" de la fuente está resuelto **en la carga**, y
      conoces todas sus escrituras (`00.00.0000` y `00/00/0000`) (§ 7 sexies)
- [ ] Si un campo dejó de venir de un comodín, revisaste **todas** las tablas
      que lo publicaban, no solo la que estabas tocando (§ 7 septies)
- [ ] Las tablas que se leen fila por fila se comprueban antes, para que una
      columna ausente diga su nombre y su tabla (§ 7 septies)
