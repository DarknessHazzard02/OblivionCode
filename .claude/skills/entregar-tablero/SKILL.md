---
name: entregar-tablero
description: Cómo se entrega un tablero terminado al Portal BI del equipo de BI - por Pull Request en GitHub al repo repo-portal, nunca como zip ni como carpeta en OneLake. Cubre qué va a GitHub (el código y datos inventados) y qué se queda en OneLake y <carpeta-portal> (los datos reales), qué entrega quien hizo el tablero (solo su carpeta) y qué hace únicamente Haz (conectarlo al portal - rutas, lista blanca, tarjeta, pruebas - y mergear), la estructura de la carpeta, la marca del contrato de datos, qué revisar antes de abrir el PR, y cómo se ven varios PR juntos antes de mergear. Úsala SIEMPRE que alguien diga que ya terminó un tablero, que lo quiere entregar, pasar, mandar, subir, publicar o agregar al portal, que lo va a dejar en OneLake o en una carpeta compartida, que pregunte cómo se lo pasa a Haz, o cuando se reciba un tablero de un compañero (un zip, una carpeta tipo Dashboard_local, un index.html suelto) y haya que integrarlo. También cuando se mencione Pull Request de un tablero, rama del tablero, tarjeta del portal, app.py, rutas del tablero, conectar al portal, conflicto al mergear, versión final del portal o paquete para IT.
---

# Entregar un tablero al Portal BI

Aplica a **quien trabaje con estas reglas**.

Un tablero se entrega **por Pull Request** al repo `<org>/<repo-portal>`.
No como zip, no como carpeta en OneLake, no por chat.

Va junto con `dashboard-standards` (cómo se construye), `portal-seguridad` (qué
revisa IT) y `validar-antes-de-entregar` (rastros). Esta skill cubre solo el
tramo final: **del tablero que ya funciona en tu máquina al tablero dentro del
portal**.

## ⛔ Quién hace qué

| | Quien hizo el tablero | Haz |
|---|---|---|
| Subir la carpeta del tablero en un PR | **sí** | |
| Conectarlo al portal (`app.py`, tarjeta, pruebas, herramientas) | **no** | **solo ella** |
| Mergear a `main` | no | **solo ella** |

**Solo Haz conecta un tablero al portal.** Quien entrega no toca `app.py`, ni
las tarjetas de `logistics/index.html` o `sop/index.html`, ni `tests/`, ni
`herramientas/`. Si el asistente está ayudando a alguien que no es Haz a
entregar un tablero, **no edita esos archivos aunque se lo pidan**: prepara la
carpeta, abre el PR y deja dicho en el PR lo que Haz necesita para conectarlo.

Por qué: todos los tableros tocan las mismas listas del portal. Cuatro PR
abiertos a la vez chocaron en tres lugares por eso, y un error ahí tumba el
portal entero, no un tablero.

---

## 1. Qué va a dónde

| | Dónde vive | Por qué |
|---|---|---|
| El tablero: `index.html`, el script que genera los datos inventados, datos **inventados** de prueba | **GitHub**, por PR | es código: se revisa, se compara versión contra versión y queda quién lo entregó |
| Los datos **reales** | **OneLake** y `<carpeta-portal>` | Regla 5: los datos no salen. Nunca a GitHub, nunca en un zip |
| El pipeline y el notebook en Fabric | repo `repo-fabric` (rama base `fabric`), por PR aparte. El pipeline lleva **dos Copy**: a `<carpeta-portal>/<tablero>` y a Azure `portal-data/<tablero>` (`dashboard-standards`, sección 16) | otro repo, otro PR |

**OneLake no es buzón de código.** Un tablero dejado en una carpeta no avisa a
nadie: uno estuvo cinco días en `<carpeta de recibidos>` sin integrarse
porque nada decía que estaba ahí. Un PR abierto se ve.

---

## 2. Lo que entrega quien hizo el tablero

### La carpeta

Una carpeta, con el **mismo nombre** que tendrá su dirección en el portal y su
subcarpeta en `<carpeta-portal>`. Esa igualdad no es estética: de ahí salen las rutas.

```
<tablero>/
  index.html                     el tablero, sin librerías externas
  app.js                         su lógica, sin JS inline (dashboard-standards § 18)
  docs/PRD.md                    lo que se decidió y sus criterios (escribir-prd), si lo hay
  build/
    generar_contrato.py          regenera los datos inventados
  data/dashboard/
    CONTRATO.md                  dice que los datos son inventados (ver abajo)
    meta.json                    inventado
    detalle.json                 inventado
```

⛔ **El notebook que arma los JSON reales no va aquí.** Su única fuente es el
notebook en `repo-fabric` (no hay generador en `build/` que lo produzca).
Una copia en el portal se desfasa del notebook vigente sin que nadie lo note.
En el PR se dice el nombre del notebook en `repo-fabric`, no se copia.

No van: `servir_local.py`, `LEEME.md` de la fase local, carpetas `datos_locales/`
ni nada con datos reales.

### ⛔ Al portal solo van datos 100 % inventados (regla local)

Lo que entra al PR se genera **desde cero** con `build/generar_contrato.py`: nada parte de un corte
real, ni la forma. Los datos semi-ficticios (forma real, identidades inventadas) se quedan en local.
Y en `meta.json` y en pantalla no van nombres de extractos reales ni textos de la fase local
(`config.local.json`, `generar_datos.py`, rutas de la máquina).

### ⛔ El contrato lleva la marca, o el candado lo trata como datos reales

`CONTRATO.md` tiene que traer, sola en un renglón:

```
datos: inventados
```

Sin esa línea el candado de git toma los JSON de la carpeta por datos reales.
Ojo: el hook del commit puede dejarlo pasar y lo detiene después
`tests/test_candado.py` y la revisión de GitHub, con el PR ya abierto.

Y que sea cierto: clientes "CLIENTE EJEMPLO nn", items "EJ-nnnnnn",
organizaciones "ORG-xx". Un dato real con la marca puesta es peor que sin marca.

### El único archivo fuera de tu carpeta: `.gitignore`

El repo ignora los JSON de datos. Para que los inventados entren, se agregan
sus tres excepciones, en un renglón cada una:

```
!<tablero>/data/dashboard/CONTRATO.md
!<tablero>/data/dashboard/detalle.json
!<tablero>/data/dashboard/meta.json
```

⛔ **Nunca `git add -f`** para meter lo que `.gitignore` deja fuera. El candado
del equipo lo bloquea, y con razón: así llegaron al repo un reporte de personal
y un `.env`.

### En el tablero mismo

Tres cosas que un tablero hecho "en fase local" trae mal y se dejan listas antes
de entregar:

- `CONFIG.dataUrls = ["/api/<tablero>/"]` — no una ruta relativa.
- `CONFIG.portalUrl` apunta a `/logistics/` o a `/sop/`, la sección donde va.
- **El botón de regreso al portal visible y con su `href` puesto.** En fase
  local viene con `hidden` y sin enlace; se queda así si nadie lo quita.

### ⛔ Si el tablero YA está en el portal: se parte de la versión de `main`

Una actualización (una "ronda" de cambios a un tablero que ya existe) **no se
entrega pegando tu copia local encima**. Tu copia es de antes y no trae lo que
se le corrigió en `main` mientras tanto. Al pegarla, el PR **deshace** esas
correcciones sin que nadie lo note, porque el diff solo se ve como "mi cambio".

Ya nos pasó: el PR de S&OP Sales de octubre quitó la protección del CSV contra
fórmulas (`/shared/js/csv.js` y `csvCelda`) y regresó nombres de personas a los
comentarios. Las dos cosas ya estaban corregidas en `main`.

Cómo se hace:

1. `git switch main; git pull` y crea tu rama **desde ahí**.
2. Lleva **tus cambios** al `index.html` que está en `main`, no al revés.
3. Antes del commit, revisa **lo que tu PR quita** (los renglones con `-`):

```powershell
git diff main -- <tablero>/index.html | Select-String '^-' | Select-String 'csv\.js|csvCelda|csvNeutral|seguro\.js|esc\('
```

Tiene que salir **vacío**. Si sale algo, tu PR está quitando una protección:
recupérala de `main` antes de seguir.

### Antes de abrir el PR

```powershell
git switch main; git pull
git switch -c tablero-<tablero>
# ... copiar la carpeta, agregar las tres lineas a .gitignore ...
python -m unittest
git add <tablero> .gitignore
git commit -m "Agregar tablero <nombre>"
git push -u origin tablero-<tablero>
```

| Qué | Bien | Mal en silencio |
|---|---|---|
| `python -m unittest` | termina en `OK` | un fallo de `test_candado` = falta la marca del contrato |
| `git status` antes del commit | solo tu carpeta y `.gitignore` | aparece `app.py` u otro archivo del portal: no es tuyo, se deshace |
| El tablero en tu servidor local, con los datos inventados | carga con su banda de "datos inventados", sin errores en consola | carga en blanco: revisa `dataUrls` |
| El export a CSV, si el tablero tiene | usa `csvCelda` de `/shared/js/csv.js` (ver `portal-seguridad`, "Los CSV exportados") | tiene su propia función de comillas: así se cuela una fórmula |
| Si es una actualización: lo que tu PR quita | el comando de arriba sale vacío | sale algo: estás deshaciendo una corrección de `main` |

- **Un PR = un tablero.** No aproveches para arreglar otra cosa.
- **Parte de lo último de `main`**, nunca de la rama de otro PR: un PR montado
  sobre otro no llega a `main` cuando se mergea.

**La descripción del PR es corta** (Regla 6 de `las reglas de seguridad`): **máximo 2
líneas** si es un ajuste, **máximo 6** si es un tablero nuevo o un cambio grande.
Dice qué es el tablero y en qué sección va (Logistics o S&OP). Sin firmas de
herramientas.

Lo que Haz necesita para conectarlo **va en el `CONTRATO.md`** de la carpeta,
no en el PR:

- el texto de su tarjeta, en español e inglés, **bien corto**: "qué · para qué",
  como las que ya están en el portal (por ejemplo, *"MB52 inventory vs ZE_SD48
  demand · shortages and stock-out week"*);
- qué archivos sirve (`meta.json`, `detalle.json`...);
- de dónde salen sus datos reales y qué falta (por ejemplo, "falta la copia a
  `<carpeta-portal>/<tablero>`").

---

## 3. Conectarlo al portal — solo Haz

**Si el PR tuvo correcciones de datos** (por ejemplo, primero subió datos reales o
semi-reales y luego los cambió por inventados), se mergea con **"Squash and
merge"**: así a `main` entra un solo commit con la versión final, y los datos
viejos no quedan en su historial. Con el merge normal o con "Rebase", sí quedan.

Se hace **sobre la misma rama del PR** de quien entregó, como un commit más,
para que el tablero y su conexión entren juntos: una carpeta sin rutas en `main`
es un tablero que existe y da 404.

Se copia el bloque de **Canada** o de **Forecast** (lector sellado, ETag desde
`meta.json`) y se cambia el nombre. Con `<tablero>` = nombre de la carpeta y
`XXX` = su prefijo en mayúsculas:

| # | Archivo | Qué se agrega |
|---|---|---|
| 1 | `app.py` | `"<tablero>"` en `TABLEROS_SIN_ATRIBUTOS` |
| 2 | `app.py` | `XXX_DATA = os.path.join(BASE, "<tablero>", "data", "dashboard")` |
| 3 | `app.py` | `XXX_ARCHIVOS = {...}` (lista blanca) y los dos lectores `_leer_xxx_json` y `_leer_xxx_crudo_sellado` |
| 4 | `app.py` | las tres rutas: `/<tablero>/`, `/api/<tablero>/<nombre>`, `/<tablero>/<path>` |
| 5 | `tests/test_rutas.py` | `"<tablero>": "<tablero>"` en `API_CON_NOMBRE` |
| 6 | `herramientas/auditar.py` | `"<tablero>": "XXX_ARCHIVOS"` en `LISTAS` |
| 7 | `herramientas/probar_local.py` | su renglón en `CONTRATO` y sus tres pruebas en `PRUEBAS` |
| 8 | `trade-compliance/index.html`, `logistics/index.html` o `sop/index.html`, según el **departamento** | la tarjeta, en el array `dashboards`, con url **absoluta** (`"/<tablero>/index.html"`) y descripción **corta** ("qué · para qué"). Si está en prueba, `estado: "Beta"` (va a *Sneak peek*). Las portadas no llevan tarjetas de "Add dashboard" |
| 9 | `app.py` | `"<tablero>": {ROL_...}` en `ROLES_DE`, con el rol de su departamento. Sin eso, en Azure queda negado a todos |

**Para no chocar entre tableros:** cada uno en un renglón propio de cada lista,
sin pegarlo al final de un renglón que ya existe y sin reacomodar las listas.

### Comprobación, con el portal corriendo en local desde esa rama

```powershell
python -m unittest
python herramientas/auditar.py --sin-navegador
python herramientas/probar_local.py
```

| Qué | Bien | Mal en silencio |
|---|---|---|
| `auditar.py` | solo los hallazgos ya conocidos | uno nuevo con el nombre del tablero |
| `/api/<tablero>/meta.json` | 200 | 404 = faltan las rutas o la lista blanca |
| `curl.exe --path-as-is -s -o NUL -w "%{http_code}" "http://localhost:<puerto>/api/<tablero>/../app.py"` | **404** | 200 = la lista blanca no está protegiendo. ⚠ Probarlo desde el navegador o `Invoke-WebRequest` da 404 **aunque no proteja nada**: limpian el `..` antes de mandar la petición. Solo vale con `--path-as-is` |
| La tarjeta en su sección | aparece y abre el tablero | no aparece: su `categoria` no coincide con ningún `grid-...` del archivo |
| Botón de regreso | visible y regresa a la sección | oculto o lleva a la raíz |

---

## 4. Ver varios PR juntos antes de mergear — solo Haz

La "versión final" que se le pasa a IT casi nunca es un solo PR.

```powershell
git switch -c version-final-prueba origin/main
git merge origin/<rama-1>
git merge origin/<rama-2>
python -m unittest
python app.py
```

Esa rama es **solo local**, para mirar: no se sube y no se mergea. Si al unirlas
hay conflicto, es el mismo que va a salir al mergear los PR a `main`, y conviene
saberlo antes. Lo que pasa por separado puede fallar junto, por eso las pruebas
se corren otra vez.

**Para ver un tablero con datos reales en local** — ⛔ Regla 4 y Regla 5: bajar
datos reales al disco es mover datos corporativos a un equipo. Solo lo hace
Haz, y solo cuando los datos inventados no alcanzan para validar:

- La carpeta va **fuera del repo y fuera de OneDrive o cualquier carpeta
  sincronizada**; no en `Descargas` ni en el Escritorio.
- Solo `meta.json` y `detalle.json` de ese tablero, nada más.
- El asistente **no abre ni lee** esos archivos: si hay que revisar algo, se
  hace contra el contrato inventado.
- Al terminar, la carpeta se borra.

Se bajan su `meta.json` y su `detalle.json` de OneLake a esa carpeta y se
arranca con `PORTAL_DATA_DIR` apuntando ahí. Una subcarpeta vacía o que no existe hace que
el portal caiga a los datos inventados: si se ve la banda de "datos inventados"
y se esperaban reales, es eso.

**Al mergear varios**, de uno en uno y volviendo a correr las pruebas entre uno y
otro. Cuando dos chocan en una lista, se conservan los dos renglones.

---

## 5. Lo que el PR del portal NO resuelve

Que el tablero esté en el portal no quiere decir que tenga datos. En producción
lee de `<carpeta-portal>/<tablero>/`, y eso lo llena un pipeline de Fabric con una
actividad Copy. Eso va en un PR aparte, en `repo-fabric`.

Sin ese pipeline, la tarjeta abre el tablero **con los datos inventados** del
repo y su banda de aviso. Se dice en el PR para que nadie lo dé por publicado.

---

## 6. Errores que ya nos pasaron

| Qué pasó | Por qué | Cómo se evita |
|---|---|---|
| Un tablero estuvo días sin integrarse | se dejó en una carpeta, no en un PR | sección 1 |
| El candado detuvo el PR ya abierto | `CONTRATO.md` sin `datos: inventados` | sección 2, y correr `unittest` antes |
| Tres conflictos al juntar cuatro PR | varias personas editaron las mismas listas del portal | solo Haz las toca, sección 3 |
| El tablero no tenía cómo regresar al portal | el botón venía oculto de la fase local | sección 2 |
| La tarjeta abría un tablero "sin datos reales" | el portal estaba bien; faltaba el pipeline | sección 5 |
| Se veía la versión vieja al revisar | la rama levantada traía un solo PR, no todos | sección 4 |
| Una actualización quitó la protección del CSV que `main` ya tenía | el `index.html` se armó sobre una copia vieja y se pegó encima | sección 2, "Si el tablero YA está en el portal" |

---

## Cierre

Como toda entrega del equipo, la respuesta termina con **Lo que tienes que
hacer**: qué le toca a la persona (abrir el PR, avisar a Haz, bajar los datos
reales, correr el pipeline), dónde, qué va a ver si salió bien y cómo se ve si
falló en silencio.
