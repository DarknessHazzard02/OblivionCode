---
name: sap-catalogo-fuentes
description: Catálogo de las fuentes de SAP del equipo de Logistics - de qué transacción sale cada reporte, cómo se saca (user group, query, variante, layout), cómo se llama el archivo, en qué carpeta de <carpeta-compartida>
---

# Catálogo de fuentes de SAP — equipo de BI

De dónde sale cada dato. Este documento contesta *"¿qué transacción da esto y cómo
se saca?"*; cómo construir la ingesta está en la skill **fabric-sap-ingesta**.

**La ruta base de todos los extractos** es
`<carpeta-compartida>`, y las rutas de los Copy Jobs
son **relativas** a ella.

---

## ⛔ CIERRA SIEMPRE CON LO QUE TIENE QUE HACER UNA PERSONA

**Toda respuesta que entregue algo termina con una sección `Lo que tienes que
hacer`.** En esta skill aplica igual que en las demás: localizar la fuente casi
nunca es el final del trabajo — alguien tiene que entrar a SAP, correr la
transacción con su variante y su layout, y dejar el archivo en su carpeta.

La lista va **numerada y en orden**, con solo lo que le toca a la persona, y cada
punto dice **dónde** (la transacción y la variante exactas, no "en SAP"), **qué
va a ver si salió bien** (el archivo, con su nombre y su fecha, en su carpeta) y
**cómo se ve si falló en silencio** — que aquí casi siempre es un archivo que sí
existe pero trae la variante equivocada, o el de ayer sin sobrescribir.

Si no hay nada que hacer, decirlo: *"Nada de tu lado por ahora"*. Y nunca cerrar
con un "avísame" a secas: avisar de qué, y cómo se sabe.

---

## ⛔ CONTRASEÑAS Y CIBERSEGURIDAD: NO SE NEGOCIAN

**Aplica a quien trabaje con estas reglas por igual.**

- **Ninguna contraseña, token ni cadena de conexión con secreto** en código,
  notebooks, commits, PR, documentos ni en el chat. Ni para probar.
- **Las credenciales no se prestan.** El usuario de SAP tampoco: lo que se baje
  con él queda a nombre de quien lo prestó.
- **Si una credencial se filtró: rotarla primero**, limpiar después, avisar a IT.

**Y avisar ANTES de lo que IT puede marcar como sospechoso.** En el trabajo de
esta skill, lo que más se acerca es **bajar de SAP volúmenes o frecuencias
inusuales**, y **sacar los extractos fuera de `<carpeta-compartida>`** — a un correo personal, a
un Drive, a una USB. Los sistemas de fuga miran volumen y destino, no intención.

**Cuando algo caiga ahí, Claude se detiene y no continúa hasta confirmación
explícita**, diciendo qué lo dispara, por qué, la alternativa que no lo dispara y
a quién avisar antes.

**La versión completa está en `las reglas de seguridad`**, en la raíz del repo de
skills, que se lee en **toda** sesión — no solo cuando esta skill se activa.

---

## Cómo leer una entrada

| campo | qué es |
|---|---|
| **Transacción** | el código que se teclea en SAP |
| **Cómo se saca** | los pasos que no son obvios: user group, nombre de la query, variante, layout |
| **Archivo** | el patrón del nombre, que es de donde sale `FILE_DATE` |
| **Carpeta** | subcarpeta de la ruta base |
| **Tablas** | cruda y limpia en `<lakehouse>` |

⛔ **Si una fuente no tiene variante ni layout guardados, anótalo.** Significa que
quien la saque tiene que reconstruir la selección a mano, y que dos personas
pueden bajar cosas distintas con el mismo nombre de archivo.

---

## SQ00 → Material Master

**La transacción es de queries y hay miles**, así que el nombre de la transacción
no identifica nada. Hay que llegar a la query correcta:

```
SQ00
  → User group:  ENA_SD
  → Query:       MRP1_MRP2
```

**Sin variante y sin layout.** Está pendiente crearlos — hoy la selección se
arma a mano cada vez, así que el contenido depende de quien la corra.

Por eso el archivo se guarda como **`Material Master`** y no con el nombre de la
transacción: `SQ00` no le diría nada a nadie.

| | |
|---|---|
| Archivo | `MaterialMaster US YYYY.MM.DD.xlsx` |
| Carpeta | `Material Master` |
| Formato | XLSX, hoja `Sheet1` |
| Tablas | `SAP_MATERIAL_MASTER` → `SAP_MATERIAL_MASTER_CLEAN` |

**Qué contiene:** datos maestros de MRP por material y planta. 138,530 filas y 18
plantas en el extracto.

Lo que se busca ahí son dos columnas:

- **`ProcType`** — `E` se produce en esa planta, `F` se trae de otro lado, `X` ambas
- **`SPT`** (special procurement type) — cuando es `F`, de dónde viene

El catálogo del SPT, con el código y el nombre juntos porque `Z4` y `Z9` son los
dos Brasil y nadie supo explicar la diferencia:

```
Z4 Brasil · Z5 Slovakia · Z6 Italy · Z7 BESCO China
Z8 EECON China · Z9 Brasil · ZZ Mexico (producción en US10)
```

**Sin clasificar, pendientes de preguntar:** `Z1`, `Z2`, `Z3`, `ZA`, `ZU` y unos
numéricos (`10`–`60`, `95`). Los `Z3` son los que más urgen: tocan materiales con
demanda real.

> **La regla de negocio que no es obvia:** para saber de dónde sale el suministro,
> lo que decide **no** es el SPT sino si el material tiene renglón en **US10 con
> `ProcType = E`**. Si lo tiene, se produce aquí y su suministro son órdenes de
> producción; si no, entra por PO. El SPT sirve para *etiquetar* el origen.
>
> Trampas: el `SPT` vacío es **válido** (72% de las filas), y `SafetyTime` y `BUn`
> vienen **dos veces** en el encabezado.

---

## MB52 → inventario por planta y almacén

| | |
|---|---|
| Archivo | `SDDnnn_MATERIAL_LIST_MB52_YYYY-MM-DD_HH-MM-SS.csv` |
| Carpeta | `SDDnnn` |
| Formato | **lista ALV** con marco de pipes, paginada — la extensión `.csv` miente |
| Tablas | `SAP_MB52` → `SAP_MB52_CLEAN` (formato largo, un renglón por estatus) |

**Qué contiene:** stock por material, planta, almacén y estatus. Las cinco cubetas
son `Unrestricted`, `Quality Inspection`, `Blocked`, `Stock in Transfer` y
`Returns`, cada una con su valor en dinero salvo `Returns`.

**Solo `Unrestricted` es usable.** El resto existe en el sistema y no se puede
ocupar — es el punto del tablero de Proveedor-A.

---

## ZSD49N → sales orders abiertas (PD Report)

| | |
|---|---|
| Archivo | `SDDnnn_PD_REPORT_YYYY-MM-DD_HH-MM-SSAM.csv` |
| Carpeta | `ZSD49N - PD Report` |
| Formato | lista ALV con pipes, 56 columnas, encabezado repetido ~314 veces |
| Tablas | `SAP_ZSD49N` → `SAP_ZSD49N_CLEAN` |

**Qué contiene:** una línea por SO y posición, con cliente, cantidades, reason for
rejection y una docena de fechas.

**Su limpieza tiene reglas propias y son del negocio, no técnicas.** Están en la
memoria del proyecto (`limpieza-zsd49n`): motivos de rechazo que excluyen, motivos
que se marcan para revisar, propagación por `Order`+`Item`, líneas facturadas
fuera, `Pending_Qty = ordered − confirmed`, y los 7 días de colchón para el cruce
de frontera.

**Ojo con dos nombres**: `Customer r` es *Customer Request Date* y `Cust. Requ` es
*Customer Request Date NAR*. Están al revés de lo que parece.

---

## COOIS → órdenes de producción

Dos extractos distintos de la misma transacción:

| | Headers | Components |
|---|---|---|
| Archivo | `COOIS_Headers_MM.DD.YYYY.xlsx` | `COOIS_Components_MM.DD.YYYY.xlsx` |
| Carpeta | `COOIS\COOIS Header` | `COOIS\COOIS Components` |
| Tabla | `SAP_COOIS_HEADERS` | `SAP_COOIS_COMPONENTS` |

**La fecha del nombre va `MM.DD.YYYY`**, al revés que los ALV. Cada fuente trae su
propio patrón; no lo generalices.

**Qué contiene Headers:** una orden por renglón, con cantidad, entregado, fechas
básicas y `Deletion_flag`. Lo pendiente por producir es
`Order_quantity − Quantity_Delivered`; una orden entregada al 100% ya está en el
inventario de MB52 y contarla otra vez la duplica.

**Todas las órdenes están en US10.** Ahí se produce y de ahí viaja al almacén.

---

## ZMM_MD04 → órdenes de compra abiertas

**No es la MD04 estándar de SAP.** Es un reporte Z de POs abiertas, y ya corre
diario alimentando los tableros de **PGI** y del **tablero A**, así que no se
puede apagar.

| | |
|---|---|
| Carpeta | `ZMM_MD04` |
| Tablas | `SAP_ZMM_MD04` + bitácora `SAP_ZMM_MD04_LOG` |

**Qué contiene:** `Centro`, `Material`, `Proveedor` y su nombre, `Pedido` y
`Posición`, `Cantidad`, y varias fechas y señales de problema (`Excepción`,
`Reschedule Days`, `Aging`, `Status`).

> ⛔ **El notebook renombra columnas al escribir la tabla.** La más importante:
> **`Fecha Planta TC` se guarda como `Fecha Embarque LA`.** Si alguien pide "la
> fecha de planta TC", en la tabla se llama distinto.

Su pipeline `ZMM_MD04_PIPELINE_CI` es **el molde** para cualquier ingesta nueva.

---

## ZE_SD48 → stock, demanda y suministro en un solo reporte

**Transacción: `ZEU_RSDR001N`**, *Net Inventory Report*. El nombre `ZE_SD48` es el
que usa el equipo.

| | |
|---|---|
| Archivo | `ZE_SD48 YYYY.MM.DD.txt` |
| Carpeta | `ZE_SD48` |
| Tabla | `SAP_ZE_SD48` |

**Quien lo saca define el alcance**, y eso cambia todo:

- **Las plantas.** El primer sample salió solo de US10 y no servía para nada;
  con todas las US da 15 plantas.
- **El horizonte.** El primer extracto salió cortado a fin de mes **por
  velocidad**, no por límite del reporte.

**Qué contiene:** por material y planta, en bloques — un renglón `Stock` abre el
material, los siguientes heredan su planta y material, y dos renglones de totales
lo cierran con el desglose por estatus. Las cantidades vienen **con signo**
(demanda negativa) y `Remain Qty` es el saldo corrido: SAP ya lo netea.

Tipos de renglón: `Stock` · suministro (`PchOrd`, `ShipNt`, `PurRqs`, `PRqRel`,
`PrdOrd`, `PlOrd.`, `ConRel`) · demanda (`Order` con cliente, `OrdRes`, `DepReq`,
`IndReq`, `Deliv.`, `UnplRq`) · `QM lot`.

**Dos formatos de descarga, y no son equivalentes:**

| | tabulado | unconverted |
|---|---|---|
| estructura | tabuladores, posiciones que **se recorren entre extractos** | ancho fijo, posiciones del encabezado |
| campo `Qty` | ~10 caracteres | **15 caracteres** |
| columnas `CN` y `Obj.Tp` | casi siempre vacías | poblado |

> ⛔ **El tabulado TRUNCA los números que no caben.** `*43847.741` avisa con el
> asterisco, pero `15053,081` trae las comas mal puestas, **convierte igual y está
> mal**. En los totales de stock daba 35.5M contra 1.1M reales. Medido: 60 de
> 46,161 valores (0.13%), todos en US10 y en materiales de volumen millonario.
>
> El unconverted tiene el campo más ancho y probablemente lo resuelve, pero
> **falta comprobarlo** con un extracto que incluya uno de esos materiales.

---

## Lista de impacto de Proveedor-A → el universo del tablero

No sale de SAP: la entrega el área.

| | |
|---|---|
| Archivo | `Proveedor-A_Impact.xlsx`, hoja `Products` |
| Carpeta | se sube **a mano** a `Files/SAP/Proveedor-A` del lakehouse |
| Tabla | `Proveedor-A_PRODUCTOS_AFECTADOS` |

**No pasa por Copy Job** y su nombre no trae fecha, así que `FILE_DATE` sale de la
fecha del archivo en el lakehouse — excepción declarada, no un fallback silencioso.

El universo son los `Status` que empiezan con `AFFECTED`. `NO BOM COVERAGE` **no**
significa limpio: significa que no se pudo verificar, y el tablero lo declara.

> Las rutas de OneLake distinguen mayúsculas: la carpeta es `Proveedor-A`, no `Proveedor-A`.

---

## Lo que falta documentar

- **Variantes y layouts.** Ninguna de estas fuentes tiene variante guardada. Hay
  que crearlas para que dos personas bajen lo mismo.
- **Qué son `Z1`, `Z2`, `Z3`, `ZA`, `ZU`** en el SPT.
- **Qué es exactamente `Preparat. Date`** de ZE_SD48. Medido: coincide 88% con
  `Planned_Preparation_Date` de ZSD49N y 78% con `Customer_Request_Date`.
- Cinco columnas truncadas de ZSD49N sin confirmar: `Deadline D`, `Deadline C`,
  `Customer P`, `Shipping b`, `Shipping d`.
