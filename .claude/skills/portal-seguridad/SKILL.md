---
name: portal-seguridad
description: Reglas de seguridad del Portal BI en el servidor local y de lo que se le entrega a IT - de donde lee datos el portal (la carpeta <carpeta-portal> que llena Fabric por el gateway), que puede y que no puede servir (tambien con trucos de rutas de Windows), XSS e innerHTML, inyeccion de formulas en CSV, datos personales y grupos de AD por tablero, librerias sin CDN, encabezados de seguridad, vulnerabilidades, el paquete para IT, y como se evita y se detecta cualquier rastro o firma de herramientas de desarrollo en codigo, commits, rutas y librerias. Usala SIEMPRE que se toque el portal (app.py, una ruta, una lista blanca, un tablero nuevo o existente, una libreria, un <script> o <link>, un fetch, un innerHTML, un tooltip, un filtro que lee la URL, un export a CSV), cuando se publique un tablero, cuando se arme o entregue el paquete para IT, y cuando se mencione servidor local, IP local, IT, revision de seguridad, escaner, vulnerabilidad, CVE, CSP, CDN, jsdelivr, datos personales, datos de empleados, RH, rastro, firma, marca de agua, Co-Authored-By, empaquetar.py o DESPLIEGUE.md. Complementa a dashboard-standards (como se construye el tablero) y a validar-antes-de-entregar (rastros en archivos Word, Excel, PDF).
---

# Seguridad del Portal BI — equipo de BI

Aplica a **quien trabaje con estas reglas** por igual.

El portal ya no vive en Azure. corre en un **servidor local** que
instala IT, y **antes de instalarlo IT pasa el código por un filtro de seguridad**. Todo
lo de esta skill existe para que ese filtro no encuentre nada, y para que lo que
encuentre, si encuentra algo, sea un falso positivo que sepamos explicar.

---

## ⛔ CIERRA SIEMPRE CON LO QUE TIENE QUE HACER UNA PERSONA

Igual que en las demás skills del equipo: toda entrega termina con una sección
`Lo que tienes que hacer`, numerada, y cada punto dice **dónde**, **qué se ve si salió
bien** y **cómo se ve si falló en silencio**.

---

## 1. Cómo está armado ahora

```
Fabric (notebook)  ->  Files/dashboard/<tablero>/        OneLake, sin credenciales
      |
      +- Copy "Publicar a PORTAL-BI" (gateway, conexion 47c0bcee)
      v
<carpeta-compartida>
      |
      +- el portal la lee de PORTAL_DATA_DIR (ruta UNC, solo lectura)
      v
Flask + waitress en 127.0.0.1:8080  ->  IIS (HTTPS + Windows Authentication)  ->  usuarios
```

- **No existe el Blob.** Nada nuevo publica a `dashboard-data` ni usa la conexión
  `70d8be8b…`. Un tablero nuevo se publica con una actividad Copy a
  `<carpeta-portal>/<tablero>`, con destino `FileServerLocation` y la conexión del gateway
  `<GUID>` (la misma de los Copy Jobs de SAP; su ruta ya
  empieza en `110 Power BI - Integrated Logistics`, así que el `folderPath` es relativo).
- **No existe Easy Auth, ni MSAL, ni `/.auth/me`.** Un tablero **no** consulta Fabric
  desde el navegador. Invox lo hacía (GraphQL con el login de Azure) y se quedó sin
  funcionar el día de la migración: hoy es un esqueleto desactivado hasta tener una
  fuente aprobada. Todo tablero lee JSON por `/api/<tablero>/<archivo>`.
- **El portal no guarda secretos.** No necesita ninguna contraseña: el acceso a la
  carpeta lo da la cuenta de servicio. Si algo te pide una llave en el código, está mal.

---

## 2. Los datos solo salen por el API, y solo lo de la lista blanca

Cada tablero tiene en `app.py` su `<TABLERO>_ARCHIVOS` y sus lectores
`_leer_blob_json` / `_leer_blob_crudo_sellado` (el nombre quedó por historia: hoy leen
de `PORTAL_DATA_DIR`). **Un JSON que no está en la lista contesta 404**, aunque exista
en la carpeta.

### ⛔ Las rutas estáticas nunca sirven datos

`/<tablero>/<path:filename>` sirve **solo** `.html .css .js .json .png .jpg .gif .svg .ico
.webp .woff .woff2`, y **nunca** desde `data/`, `notebooks/`, `fuentes/`, `build/`,
`scripts/`, ni archivos o carpetas que empiecen con `.` o `_`.

### ⛔ Toda ruta que sirve archivos pasa por el filtro

No basta con que `_estatico_permitido` exista: **cada** ruta que llama a
`send_from_directory` (o sirve un archivo de cualquier otra forma) tiene que pasar por
él o por `_send_cached`. Una ruta nueva para un tablero con subpáginas es justo donde se
olvida.

### ⛔ El servidor es Windows: el filtro compara la ruta real

Windows ignora el punto o el espacio al final de un nombre de carpeta y acepta la
notación de flujos NTFS. `data./` y `data::$INDEX_ALLOCATION/` **no** coinciden con
`data` en una lista de carpetas cerradas, pero abren `data/`. En la auditoría así se
leyeron `data/`, `fuentes/` y `notebooks/`, incluido un archivo que la API excluía a
propósito.

El filtro:

- rechaza cualquier tramo de la ruta que contenga `:` o termine en punto o espacio;
- decide sobre `os.path.realpath(...)`, no sobre el texto que llegó en la URL.

### Cómo se comprueba

Con el servidor corriendo y **`curl --path-as-is`**. Sin esa bandera, curl y el
navegador limpian el `../` **antes** de mandar la petición, y la prueba sale en 404 sin
haber probado nada — así estaba escrita esta misma checklist hasta la auditoría.

Tienen que dar **404** todas:

```
curl --path-as-is -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8080/<RUTA>

/<tablero>/data/dashboard/meta.json
/<tablero>/data./dashboard/meta.json
/<tablero>/data::$INDEX_ALLOCATION/dashboard/meta.json
/<tablero>/data%20/dashboard/meta.json
/api/<tablero>/../../app.py
/api/<tablero>/..%2f..%2fapp.py
/<tablero>/<cualquier>.py
/<tablero>/.env
/<tablero>/pages/<cualquier>.py          (en cada tablero que tenga pages/)
/api/<tablero>/un_nombre_que_no_esta.json
```

Si no puedes levantar el servidor, **no marques la prueba como hecha**: revisa el código
y dilo en el PR.

---

## 3. Datos personales

- **Se publica lo mínimo.** Si el tablero muestra generaciones o rangos de edad, el
  pipeline publica la **generación o el rango**, no la fecha de nacimiento. Si muestra
  conteos por área, no hace falta el nombre de cada persona.
  **Lo que no se muestra no se manda**: el navegador recibe el JSON completo, y
  cualquiera lo ve con F12 aunque la página no lo pinte.
- **Un tablero con datos de personas tiene su propio grupo de AD.** Estar detrás de la
  autenticación de IIS no basta: eso deja entrar a **todo** el que entra al portal. El
  tablero **y su API** (`/<tablero>/` y `/api/<tablero>/`) se restringen a un grupo de RH
  con URL Authorization en IIS, se habla con IT antes de publicarlo, y el PR lo dice. Un
  tablero así **no** aparece en la lista general del portal.

⛔ Si encuentras datos personales ya commiteados, **no los borres tú del historial**:
avísale a Haz. Reescribir historia es una decisión del equipo, no de una sesión.

---

## 4. Librerías: nada de CDN

Todas las librerías viven en `shared/vendor/` y se cargan con ruta absoluta:

```html
<script src="/shared/vendor/chartjs/chart.umd.min.js"></script>
<script src="/shared/vendor/chartjs/chartjs-plugin-datalabels.min.js"></script>
<script src="/shared/vendor/xlsx/xlsx.full.min.js"></script>
<link rel="stylesheet" href="/shared/vendor/fonts.css">
<link rel="stylesheet" href="/shared/vendor/tabler/tabler-icons.min.css">
```

Nunca `cdn.jsdelivr.net`, `unpkg.com`, `cdnjs`, ni Google Fonts: la CSP del portal los
**bloquea** (el navegador no los carga y el tablero se ve roto) y el escáner de IT los
marca.

### Por qué
Los tableros cargaban **SheetJS 0.18.5** de CDN para el botón de Excel. Esa versión tiene
dos CVE publicados (CVE-2023-30533 y CVE-2024-22363). En la práctica no nos afectaban —
los dos se disparan al **leer** un Excel, y los tableros solo **escriben** — pero un
escáner compara **versiones**, no usos: lo iba a marcar igual y frenar la instalación.
Además, `@tabler/icons-webfont@latest` cargaba "la que sea hoy", sin versión fija.

### Para agregar o subir una librería

1. **Versión exacta**, nunca `@latest`. Revisa que esa versión no tenga CVE abiertos.
2. Descárgala a `shared/vendor/<libreria>/` (con permiso: descargar archivos se pide).
3. Anótala en `shared/vendor/VERSIONES.md`: paquete, versión, licencia, origen y
   **SHA-256**. La carpeta se guarda byte por byte (`shared/vendor/** -text` en
   `.gitattributes`); sin eso git cambia saltos de línea y el hash deja de coincidir.
4. Si la librería pide archivos propios (fuentes, imágenes), bájalos también y
   comprueba en el navegador que cargan.
5. **Nada externo, tampoco imágenes.** Cada imagen de otro dominio le manda a ese
   dominio la IP de cada usuario que abre el tablero, y cuándo. Las banderas de las
   tarjetas salían de `flagcdn.com` hasta la auditoría: se bajan a
   `shared/vendor/banderas/` como cualquier otra librería, y se quita el dominio de
   `img-src` en la CSP.

### Los mapas también: fondo local, no mosaicos

Los mapas de Leaflet usaban mosaicos de CARTO. **CARTO dejó de servirlos sin llave** y
el mapa salió con marcas de agua "API KEY REQUIRED" en todo el fondo; una llave sería
un secreto en el portal y otra dependencia de internet. El fondo ahora se dibuja con
fronteras de países y estados servidas por el propio portal:

```html
<script src="/shared/vendor/leaflet/leaflet.js"></script>
<script src="/shared/vendor/mapas/topojson-client.min.js"></script>
<script src="/shared/js/mapa-base.js"></script>
```
```js
MAP = L.map('map').setView([34, -98], 4);
mapaBase(MAP);          // en vez de L.tileLayer(...)
```

**Un `L.tileLayer` nuevo, de cualquier proveedor, no pasa**: la CSP lo bloquea y el
mapa queda en blanco.

---

## 5. Lo que ya trae el portal, y no se quita

| Qué | Dónde |
|---|---|
| `Content-Security-Policy`: código, estilos y fuentes solo del propio servidor | `CSP` en `app.py` |
| `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, sin `Server` | `_encabezados_seguridad` |
| Estáticos con lista blanca de extensiones y carpetas cerradas | `_estatico_permitido` |
| Lectura de datos que no se sale de `PORTAL_DATA_DIR` y no sirve archivos a medio copiar | `_ruta_datos`, `_descargar` |
| `/api/data-source` sin rutas del servidor ni textos de excepción | `api_data_source` |
| Debug apagado; el servidor de desarrollo solo escucha en `127.0.0.1` | final de `app.py` |
| Dependencias con versión fija | `requirements.txt` |

Si un cambio necesita tocar cualquiera de estos, **se dice en el PR y por qué**.

### Lo que falta, y todo cambio nuevo ya cumple

La auditoría encontró estos huecos. Mientras se cierran, **nada nuevo los
agranda**:

| Qué | Cómo se cumple | Caso |
|---|---|---|
| `servir.py` escucha **solo** en `127.0.0.1` por defecto | valor por defecto en el código, no solo en el `.env`; y el 8080 cerrado en el firewall del servidor | el default era `0.0.0.0`: sin `.env`, se entraba al portal **saltándose la autenticación de IIS** |
| `/api/*` responde con `Cache-Control: private, no-store` | en `_encabezados_seguridad`, para toda ruta de datos | los datos de RH y de negocio quedaban en cachés intermedios y del navegador |
| La CSP **sin** `'unsafe-inline'` en `script-src` | JS en archivos `.js` con `addEventListener`, o un `nonce` por respuesta desde Flask | hoy es necesario porque todos los tableros tienen JS inline y `onclick`; con eso la CSP **no frena ningún XSS**. Un tablero nuevo no agrega JS inline ni `onclick=` |
| Bitácora de accesos con el usuario | `logging` a archivo, o los logs de IIS con el usuario autenticado | solo había `print`: no se podía saber quién consultó los datos de RH |
| Dependencias revisadas contra vulnerabilidades | `pip-audit` / `osv-scanner` (con aprobación de IT, Regla 4), o revisar a mano cada versión de `requirements.txt` antes del PR | Werkzeug 3.1.8; la 3.1.9 corrige un caso de `safe_join` en Windows |
| Sin información interna en lo que llega al navegador | sin nombres de pipelines, notebooks ni personas en comentarios de HTML/JS | los comentarios viajan completos con cada página |

---

## 5 bis. XSS: ningún dato se pinta como HTML

**Todo texto que venga de la URL o de los datos se pinta con `textContent`**, o pasa por
`esc()` de `/shared/js/` antes de entrar a un `innerHTML`. Eso incluye nombres de
proveedor, agente aduanal, buque, cliente, descripciones, valores de filtros, parámetros
de la URL y hasta sus **nombres**.

>
> Los modelos a copiar: `sop-sales`, `confirmaciones`, `import-tracker`, `tablero-rh`,
> `ymeadows` y los chips de Open Order (`textContent`).

Reglas:

- **Un valor de la URL solo se acepta si existe en el catálogo del tablero.** Una fecha,
  solo si cumple `^\d{4}-\d{2}-\d{2}$`. Lo demás se ignora, y lo desconocido **no** se
  muestra en pantalla.
- **`innerHTML`, `insertAdjacentHTML` y `outerHTML` solo con plantillas fijas.** Si la
  plantilla lleva un dato, el dato va con `esc()`. Tooltips de Chart.js y de Leaflet
  (`bindTooltip`, `bindPopup`) también son HTML.
- **Una sola `esc()`**, en `/shared/js/`, que escapa `& < > " '`. No se copia una propia
  en cada tablero: la copia de `cdFill` en 5 páginas del ACE es justo cómo quedaron unas
  seguras y otras no.
- **Nada de `onclick=` con datos** armado como texto; `addEventListener` sobre el nodo.

**Cómo se busca: con el barrido, no a ojo.**

```
python %USERPROFILE%\.claude\skills\portal-seguridad\scripts\revisar_portal.py RUTA-DEL-PORTAL --json barrido.json
```

Recorre **todos** los tableros, también los que nadie nombra, y lista archivo:línea de
cada plantilla, concatenación o `innerHTML` donde entra un dato o un valor de la URL sin
`esc()`, más una tabla por carpeta que incluye las que dan cero. Revisa también lo del
servidor (rutas sin filtro, filtro frente a Windows, host, CSP, caché), CSV, datos
pegados, y la calidad que esconde fallas (errores silenciosos, fechas en UTC, `CONFIG`
con claves que no existen, catálogos copiados que ya no coinciden). Solo usa Python
estándar; no lee el contenido de los datos.

Cómo se validó: sobre el paquete que se entregó a IT encontró las 13 líneas
de XSS que marcó la auditoría. Sobre la rama con las correcciones, las rutas sin filtro,
el filtro de Windows, el `0.0.0.0` y los datos de VMI bajaron a cero, y los XSS bajaron
en cada tablero corregido (ACE de 81 a 7, DataStage de 93 a 14), mientras que los
tableros que nadie tocó se quedaron igual.

**Da pistas, no veredictos.** Cada hallazgo se juzga: `c.field` como respaldo de un
título puede ser un nombre de columna del código, no un dato. Lo que se descarta, se
descarta con la razón escrita en el PR.

**Cómo se prueba:** abre el tablero con `?<parametro>=<img src=x onerror=alert(1)>` en
cada parámetro que lea, y con un nombre de parámetro inventado. Tiene que verse el texto
tal cual, sin ventana de alerta.

### Los CSV exportados tampoco ejecutan nada

Un valor que empieza con `= + - @` (o tabulador o retorno) se evalúa como **fórmula** al
abrir el CSV en Excel, aunque vaya entre comillas. La exportación a CSV pasa cada texto
por la función compartida que le antepone un apóstrofo (`'`) a esos valores. El export a
XLSX con SheetJS no tiene este problema. Números negativos reales se exportan como número,
no como texto.

**La función compartida es una sola y se usa así, en todo tablero que exporte CSV:**

```html
<script src="/shared/js/csv.js"></script>
```
```js
const esc = csvCelda;   // comillas + neutraliza = + - @ + vacío como ""
```

⛔ **Nunca una función de comillas propia** como `v => '"' + String(v).replace(/"/g, '""') + '"'`.
Se ve correcta, exporta bien, y deja pasar la fórmula. Tampoco una copia de `csvNeutral`
dentro del tablero: se separa de la compartida con el tiempo.

**Una actualización puede quitarla sin que nadie lo note.** Pasó en octubre con S&OP
Sales: el PR se armó sobre una copia vieja del `index.html` y, al pegarla, desaparecieron
el `<script>` y `csvCelda`. Antes de mergear la actualización de un tablero, se revisa lo
que el PR **quita**:

```powershell
git diff main...<rama-del-pr> -- <tablero>/index.html | Select-String '^-' | Select-String 'csv\.js|csvCelda|csvNeutral'
```

Tiene que salir vacío. Cómo se comprueba en el navegador (F12, consola, con el tablero
abierto): `csvCelda('=1+1')` devuelve `"'=1+1"`. Si dice `csvCelda is not defined`, falta
el `<script>`.

---

## 6. Rastros de herramientas: cómo llegan al código

Decisión del equipo: **nada de lo que entregamos lleva firma ni mención de herramientas
de desarrollo** — ni de este asistente ni de ningún otro. Estas son las puertas por las
que se cuelan, todas vistas en nuestros repos:

| Puerta | Cómo se ve | Cómo se cierra |
|---|---|---|
| Trailer de commit | `Co-Authored-By: …` al final del mensaje | ajuste `attribution` en tu `settings.json` (abajo) |
| Pie de PR | "Generated with …" en la descripción | el mismo ajuste |
| Comentarios que el asistente escribe sobre sí mismo | *"…no viaja a nadie más ni vuelve a [el asistente]"* | leer los comentarios nuevos antes de commitear |
| Rutas con el nombre de la carpeta de trabajo | `C:\Users\…\<carpeta con el nombre de la herramienta>\…` dentro de un notebook | rutas **relativas** al repo; nunca la ruta de tu máquina |
| Carpetas de configuración de la herramienta | la carpeta oculta de configuración con un `launch.json` adentro, commiteada | no se commitean; si ya están, se quitan del repo |
| Scripts que leen de la instalación de la herramienta | un `_armar.py` que toma el tema de la carpeta de skills de tu perfil | leer del repo de skills clonado, o de una variable de ambiente |
| Guías internas que explican el ajuste | una guía del portal que nombra el archivo de configuración de la herramienta | la explicación vive aquí, en el repo de skills, no en el repo que se entrega |
| Librerías de terceros | la hoja de iconos trae logos de marcas de herramientas | se quitan esas reglas y se anota en `VERSIONES.md` |
| Texto de la interfaz | una frase como *"This dashboard was generated without…"* | redactar sin "generated" |

### Apagar la firma, en cada máquina

En el `settings.json` de tu configuración de usuario de la herramienta:

```json
{ "attribution": { "commit": "", "pr": "" } }
```

**Es por máquina.** Si alguien más no lo tienen, sus commits siguen saliendo
firmados aunque esta skill diga lo contrario.

### Detectarlo antes de que lo vea IT

```
python %USERPROFILE%\.claude\skills\portal-seguridad\scripts\revisar_rastros.py RUTA-DEL-REPO [--base origin/main]
```

Revisa **el contenido de todos los archivos versionados, sus nombres y rutas, y los
mensajes de los commits de tu rama** contra la lista `assets/firmas.txt`. Sale con
código 1 si encuentra algo. Los falsos positivos conocidos (por ejemplo, un empleado
que se llama "Claudemir" en un JSON de datos) se revisan a mano: se reportan, no se
esconden.

Y el portal tiene su propio candado: `empaquetar.py` **no arma el paquete para IT** si
algún archivo del paquete trae un término de esa misma lista. La lista vive **aquí**, no
en el repo del portal, para que el repo que se entrega no la contenga.

### ⛔ El historial de git

Los commits viejos (de antes) traen trailers en el mensaje: 112 en
Portal-BI y 38 en repo-fabric-anterior. El paquete para IT **no lleva historial**, así que
ahí no aparecen. Reescribir el historial de un repo publicado lo decide Haz — el
2026-08-19 decidió no hacerlo en Portal-BI. No lo propongas en cada sesión; si el tema
vuelve, es porque cambió algo (por ejemplo, una mudanza a un repo nuevo).

---

## 7. El paquete para IT

```
python empaquetar.py
```

Desde un checkout **limpio** de `main`, con el repo de skills clonado junto al del portal
(o `REVISION_FIRMAS` apuntando a `assets/firmas.txt`). Deja `portal-bi_<fecha>_<commit>.zip`
y su `.sha256`, y **no lo arma** si encuentra credenciales, datos personales en JSON,
restos de Azure o rastros de herramientas. El paquete no lleva historial, datos, notebooks,
scripts, ni los tableros que no se sirven.

**Prueba el paquete, no el repo:** descomprímelo en una carpeta vacía, apunta
`PORTAL_DATA_DIR` a una carpeta con la estructura de `<carpeta-portal>`, y abre cada tablero.
`/api/data-source` tiene que decir `"source": "blob"` y `files_from_disk` vacío.

Con el ZIP va `DESPLIEGUE.md`: instalación, permisos de la carpeta, IIS con HTTPS y
Windows Authentication.

---

## Checklist antes del PR (portal)

- [ ] Corriste `revisar_portal.py` y cada hallazgo Alta o Media del tablero que tocaste
      está corregido o descartado con su razón en el PR
- [ ] Todo archivo nuevo que publica el notebook está en la lista blanca del tablero
- [ ] Las rutas de "Cómo se comprueba" (sección 2) dan **404** con `curl --path-as-is`,
      incluidas `data./`, `::$INDEX_ALLOCATION` y las de `pages/`. Sin servidor, dilo en el PR
- [ ] Toda ruta nueva que sirve archivos pasa por `_estatico_permitido` o `_send_cached`
- [ ] Ningún dato de la URL ni de los datos entra a `innerHTML`/`insertAdjacentHTML`/tooltips
      sin `esc()`; los valores de la URL se validan contra el catálogo
- [ ] Probaste `?<parametro>=<img src=x onerror=alert(1)>` y no salió la alerta
- [ ] Sin JS inline nuevo ni `onclick=` en el tablero
- [ ] El export a CSV neutraliza los valores que empiezan con `= + - @`
- [ ] Ningún arreglo de datos reales pegado en el HTML; si la API falla, error visible
- [ ] Si el tablero tiene datos de personas: grupo de AD propio en IIS para el tablero **y** su
      `/api/`, hablado con IT, y el JSON solo trae lo que se muestra
- [ ] `git check-ignore -v <tablero>/data/...` muestra la regla `**/data/`
- [ ] Cero `<script>`/`<link>`/`<img>` a otro dominio (CDN, Google Fonts, banderas); lo
      nuevo está en `shared/vendor/` con versión fija y SHA-256 en `VERSIONES.md`
- [ ] Sin comentarios con nombres de personas, pipelines o notebooks en HTML/JS
- [ ] Abriste el tablero y la consola **no** dice `Refused to load … Content Security Policy`
- [ ] Ningún `fetch` a otro dominio; ningún `/.auth/`, MSAL ni GraphQL desde el navegador
- [ ] Ningún `L.tileLayer`: los mapas usan `mapaBase(MAP)`
- [ ] `CONFIG.portalUrl` relativo (`/logistics/` o `/sop/`), nunca una URL completa
- [ ] Los JSON del repo son el contrato con datos **inventados**, con su `CONTRATO.md`; nada real commiteado
- [ ] Si el tablero tiene datos de personas: se publica lo mínimo, y el PR lo dice
- [ ] Ninguna credencial, token ni ruta de tu máquina
- [ ] `revisar_rastros.py` sobre el repo sale limpio, y leíste los comentarios nuevos
- [ ] El mensaje del commit y la descripción del PR no llevan firma

## Checklist antes de entregar a IT

- [ ] `empaquetar.py` armó el paquete sin errores, desde `main` limpio
- [ ] Probaste el ZIP descomprimido, no el repo
- [ ] Va con su `.sha256` y con `DESPLIEGUE.md`
- [ ] Los pasos de Fabric que publican (`Publicar a PORTAL-BI`) corrieron y dejaron
      `meta.json` **de hoy** en `<carpeta-portal>\<tablero>\`
