---
name: apps-estandar
description: Cómo se construye una app del equipo de BI - las que capturan, registran o mueven algo por un flujo (anomalías, solicitudes, aprobaciones, bitácoras, altas), no los tableros de solo lectura. Stack por defecto Flask + SQL Server + HTML/CSS con poco JavaScript, y cuándo se justifica React; estructura del proyecto, IIS con Windows Authentication, roles y permisos, flujo de estatus con historial y antigüedad, folio, bitácora, adjuntos y fotos, pantalla de inicio, buscador, captura en celular, borrador automático, errores que llevan al campo, bilingüe, seguridad para IT, pruebas y guía de instalación. Úsala SIEMPRE que se pida crear, armar, diseñar o modificar una app, aplicación, sistema, herramienta web, formulario de captura, registro, bitácora, flujo de aprobación, portal de captura o CRUD, o cuando se mencione Flask, React, Node, Express, Vite, frontend, backend, pantalla de captura, roles de usuario, supervisor, admin, folio, estatus, workflow, capturar desde celular o tablet, o se pregunte qué lenguaje o tecnología usar para una app. Va junto con apps-base-datos (tablas LOG_<APP>_<TABLA>) y portal-seguridad (lo que revisa IT).
---

# Apps del equipo de BI

Aplica a **quien trabaje con estas reglas** por igual. Un **tablero** muestra
datos (eso es `dashboard-standards`); una **app** los **captura** y los
mueve por un flujo. Esta skill es para lo segundo.

**El molde es `Anomalias-Recibo`** (anomalías de recibo: bloqueos de MIGO y
OS&D), en `<carpeta del proyecto>` mientras no tenga
repo en GitHub. Cuando algo de aquí no quede claro, se copia de ahí. La
excepción en React es FreightHub (`Procurement Fletes`), por su portal de
proveedores.

---

## ⛔ CIERRA SIEMPRE CON LO QUE TIENE QUE HACER UNA PERSONA

Igual que en las demás skills: toda entrega termina con `Lo que tienes que
hacer`, numerada, y cada punto dice **dónde**, **qué se ve si salió bien** y
**cómo se ve si falló en silencio**. En una app casi siempre incluye: cómo
arrancarla (con el `cd` a la carpeta: sin él, `python servir.py` falla desde
`C:\Users\<usuario>`), qué probar con qué rol, y qué pedirle a IT.

## ⛔ Seguridad: las reglas 3, 4 y 5 de `las reglas de seguridad` aplican completas

Ninguna contraseña en la app ni en su configuración, ningún dato real en el
repo, y se avisa antes de lo que IT puede marcar. Lo específico de apps está
en la sección 8.

---

## 1. ⛔ El stack: Flask por defecto

****

| Capa | Por defecto | Por qué |
|---|---|---|
| Servidor | **Python + Flask**, servido con **waitress** | el mismo del Portal BI: IT ya lo conoce, 4 paquetes |
| Pantallas | **HTML armado en el servidor** (plantillas Jinja) + CSS + poco JavaScript | pesa poco en un celular con mala señal; nada que compilar |
| Base | **SQL Server de IT**, tablas `LOG_<APP>_<TABLA>` | ver `apps-base-datos` |
| Entrada | **IIS con Windows Authentication** | la app no guarda contraseñas |

**Todos terminan en HTML, CSS y JavaScript en el navegador.** La diferencia es
quién arma la pantalla: aquí el servidor la manda hecha; con React la arma el
navegador con JavaScript a partir de datos crudos.

### Cuándo se justifica React

**Solo si se cumplen dos de estas tres**, y queda escrito en el README:

1. La pantalla **recalcula mucho mientras el usuario escribe** (comparar
   cotizaciones, sumar bultos, armar una carga).
2. La usan **personas de fuera de la red** (un portal de proveedores).
3. **Muchas pantallas comparten piezas interactivas** complejas.

Si se usa React (como FreightHub, en `Procurement Fletes`), además:

- **Versiones exactas** en `package.json`, sin `^` ni `~`, y se comprueba en
  `package-lock.json`. Un `^` revierte el arreglo de un CVE sin avisar.
- `npm audit` limpio antes de cada entrega.
- A IT se le entrega **lo ya construido** (`npm run build`), no el código fuente
  para que compile.
- `DESPLIEGUE.md` dice que el servidor necesita **Node**, y qué versión.
- **La lección de FreightHub:** tres veces se dio por terminada una función
  que la API tenía y ninguna pantalla llamaba (`approvals.start`,
  `approvals.decide`, `requests.edit`). Con dos capas separadas es fácil. Antes
  de decir "listo": `grep -rn "api.<modulo>.<metodo>" src/components/`.

---

## 2. Estructura del proyecto

```
<App>/
  servir.py                 arranca: waitress (producción) o --dev (Flask, solo 127.0.0.1)
  requirements.txt          versiones exactas
  .env.ejemplo              todas las variables, ninguna con contraseña
  .gitignore                instance/, .env, adjuntos/, *.db, *.xlsx, *.csv, **/data/
  README.md                 qué es, roles, flujo, cómo correrla en local
  DESPLIEGUE.md             para IT (sección 10)
  sql/esquema.sql           ÚNICA definición del esquema (SQL Server)
  <app>/
    __init__.py             create_app: encabezados de seguridad, errores, before_request
    config.py               lee el .env; si falta algo de producción, NO arranca
    db.py                   conexión (pyodbc / sqlite3), consultas con ?, esquema SQLite derivado
    auth.py                 usuario de IIS, roles, puede(accion, registro), CSRF
    modelo.py               reglas: folio, validaciones, flujo de estatus, bitácora
    consultas.py            listado, filtros, CSV, resumen
    adjuntos.py             fotos y documentos
    i18n.py                 todos los textos ES / EN
    semilla.py              catálogos de proceso + datos DEMO inventados
    cli.py                  base (dev), catalogos (prod), revisar
    vistas.py               rutas
    templates/  static/     sin JS en línea; theme.css del equipo
  tests/                    pytest contra SQLite
```

- **La base de desarrollo es SQLite y sale del mismo `sql/esquema.sql`**
  convertido (`IDENTITY` → `AUTOINCREMENT`, `NVARCHAR` → `TEXT`…). Dos
  esquemas escritos a mano se separan en un mes. Una prueba compara que los
  dos tengan las mismas sentencias.
- **Configuración sin defaults silenciosos.** En producción, si falta el
  servidor de SQL o la carpeta de adjuntos, la app **no arranca** y dice qué
  falta. SQLite solo se acepta con `ENTORNO=desarrollo`.
- La carpeta de configuración de la herramienta de desarrollo va en
  `.git/info/exclude`, no en el `.gitignore` (que se entrega y la nombraría).

---

## 3. Cómo corre en el servidor

```
Usuario ──HTTPS + Windows Auth──> IIS ──(URL Rewrite + ARR)──> waitress 127.0.0.1:<puerto>
                                                                  ├─> SQL Server (Trusted_Connection)
                                                                  └─> carpeta de adjuntos
```

- **La app escucha solo en `127.0.0.1`** y `servir.py` se niega a arrancar en
  otra interfaz. El puerto se cierra en el firewall del servidor.
- **El usuario lo pone IIS** en un encabezado (`X-<App>-User` = `{LOGON_USER}`,
  variable de servidor de URL Rewrite). **Solo se le cree si la petición viene
  de 127.0.0.1**; sin encabezado → **401**, nunca un usuario por defecto.
- **En desarrollo** el usuario se escoge en `/dev/usuario` (cookie), y esa
  ruta da 404 en producción. Hay una banda amarilla "DESARROLLO · datos
  inventados" para que nadie confunda la copia local con la real.
- SQL Server con **Windows Authentication** de la cuenta del servicio.
  `config.py` rechaza una cadena con `UID`, `PWD` o `;`.

---

## 4. Roles y permisos

- **El rol vive en la app** (`LOG_<APP>_USUARIO`) y lo asigna el admin desde
  una pantalla. IIS solo entrega el usuario, no sus grupos: consultar AD desde
  la app es otra puerta que IT tiene que revisar. **IIS sí restringe la
  entrada** a un grupo de AD de la app.
- Quien entra por primera vez queda como **Consulta** (solo ver). Los de
  `<APP>_ADMINS` entran como **Admin**, para que alguien pueda arrancar.
- Roles base: **Capturista · Supervisor · Admin · Consulta**, más los que pida
  el proceso (en Anomalías: **Import/Export**, que investiga los OS&D).
- **Una sola función decide:** `puede(accion, registro)`. La usan las rutas
  (403) y las plantillas (qué botones se pintan). El botón oculto no protege
  nada; la ruta sí.
- **El admin respeta el estatus.** Puede todo lo del supervisor, pero no
  "validar" algo cerrado. Y **nadie se quita a sí mismo el rol de admin**.

---

## 5. Flujo de estatus

- **⛔ El estatus nunca se escoge a mano.** Lo cambian las acciones (validar,
  regresar, investigar, cerrar, cancelar). Un selector de estatus en una
  pantalla se lee como "aquí lo cambio".
- **Cada acción es una función en `modelo.py` + un formulario en el detalle**
  que solo aparece si `puede(accion, registro)`. Acción sin pantalla = acción
  que no existe (la lección de FreightHub).
- **Historial de estatus** (`LOG_<APP>_ESTATUS_HISTORIAL`): de ahí sale la
  **antigüedad total y por etapa** (captura, investigación, con el
  responsable). Así se ve dónde se atora.
- **Nada se borra.** Se **cancela** con motivo obligatorio. Se reabre solo
  admin.
- **Control de edición simultánea:** columna `VERSION`; cada formulario la
  manda; el `UPDATE ... WHERE ID = ? AND VERSION = ?` que toca 0 filas es un
  conflicto: *"Otra persona cambió esto mientras lo veías"*.
- **Bitácora** (`LOG_<APP>_BITACORA`) de toda escritura, también catálogos,
  usuarios y exportaciones: quién, cuándo, qué cambió (de → a).

### Folio

`<PREFIJO>-AAAA-NNNNN`, **consecutivo por año** en `LOG_<APP>_FOLIO`. Se toma
con `UPDATE ... SET ULTIMO = ULTIMO + 1` dentro de la misma transacción del
alta: el `UPDATE` bloquea la fila, así que dos capturas simultáneas no
repiten número. No se liga a SAP.

---

## 6. Pantallas: lo que ya aprendimos

Cada punto salió de una queja real al usar la app.

### Inicio

**Lo primero que se ve es un botón grande "+ Nueva …"** y lo que le toca a
cada rol (al supervisor, "Te toca validar"; a Import/Export, "Te toca
investigar"), con su número. Debajo, **"Requieren atención"** (abiertas que
pasaron el umbral de días, las más viejas primero) y lo último capturado.

### Buscador

- Pantalla **aparte** del inicio, con nombre propio ("Buscar anomalías").
- **Pestañas con su número** para las vistas por estatus (Abiertas · Por
  validar · …), no un `<select>` de estatus que parece campo.
- **Un campo por cosa que se busca** (Folio, PO, Factura), no un solo cuadro
  de "folio, factura, PO…".
- Lo demás va en **"Más filtros"**, plegado, y cada filtro dice para qué es:
  "Fecha en que se abrió: del … al …", no "Desde / Hasta" a secas.

### Captura

- **Categoría primero y la lista dependiente se filtra sola** (OS&D → solo
  sus modos de falla). Mientras no hay categoría, la lista está desactivada.
  Las opciones se **reconstruyen**, no se ocultan: Safari en iPhone no oculta
  `<option>`.
- Lo que solo aplica a un caso (sección OS&D, fotos obligatorias) **aparece
  cuando aplica**, y el servidor lo exige igual aunque no haya JavaScript.
- **Catálogo o texto:** el capturista escribe con sugerencias (`datalist`); si
  no existe, se guarda el texto y el **supervisor lo liga al catálogo al
  validar**. Sin ligar no se valida: sin eso no hay KPI.
- **Borrador automático** en el navegador (`localStorage`, con `try/catch`)
  en cada cambio, aviso *"Recuperamos lo que llevabas capturado"* con botón
  para empezar de cero, y aviso del navegador antes de salir a medias. Se
  borra al enviar. Las fotos no se pueden guardar: el aviso lo dice.
- **Un solo envío por clic** (el botón se desactiva): un doble toque son dos
  folios.

### Errores

- **⛔ Nunca un nombre de columna en pantalla.** El aviso dice "Falta un campo
  obligatorio: **Proveedor**", no `proveedor_texto`. Los nombres internos se
  traducen con un mapa campo → etiqueta, y una prueba recorre los errores
  buscando `palabra_con_guion_bajo`.
- **El error lleva al campo:** la pantalla se mueve hasta él, lo marca en rojo
  (`aria-invalid`) y pone el cursor ahí. El formulario regresa con todo lo que
  ya se había escrito.

### Detalle

Todos los campos (no un resumen), el historial con quién y cuándo, la
antigüedad por etapa, los adjuntos y los comentarios. Las acciones que le
tocan a ese usuario van en su propia tarjeta; si no le toca nada, lo dice.

### Antigüedad a la vista

Días abiertos con **semáforo**: amarillo y rojo a partir de umbrales
declarados en `consultas.py` (en Anomalías, 3 y 7). **Solo en las abiertas:**
un plazo que sigue corriendo en algo cerrado confunde (pasó en FreightHub).

### Celular, tablet y escritorio

- Letra base **16 px** (menos de eso, iPhone hace zoom al tocar un campo),
  campos y botones de **46–48 px de alto**.
- En celular la tabla se vuelve **tarjetas**; cero scroll horizontal
  (se mide: `document.documentElement.scrollWidth` = ancho de la ventana).
- `<input type="file" accept="image/*">` abre la cámara. Las fotos se
  **reducen a 2000 px en el navegador** antes de subir, y con eso se va el
  EXIF (incluida la **ubicación GPS**).

### Bilingüe

Todo texto sale de `i18n.py` (`TEXTOS = {"llave": ("ES", "EN")}`). Una prueba
revisa que toda llave usada en plantillas y código exista. Una llave que falta
se pinta tal cual, a propósito, para que se note.

### ⛔ Documentación dentro de la app

**Igual que en los tableros: al pie de toda pantalla va el enlace
"📖 Documentación"**, que abre una página de la propia app (`/documentacion`),
bilingüe, escrita para quien la retome en un año sin contexto. Lleva, en este
orden:

1. **Para qué es**: qué se registra y qué sale de ahí (el KPI).
2. **Cómo avanza un registro**: el flujo de estatus en lenguaje de negocio,
   con las píldoras de color de la app, y que el estatus no se escoge a mano.
3. **Quién hace qué**: un renglón por rol.
4. **Reglas de captura**: qué es obligatorio y sus excepciones, fotos,
   folio, borrador. Las reglas que la gente se salta ("sin la excepción en el
   BOL se pierde el reclamo") van aquí con su porqué.
5. **Los catálogos que deciden algo** (en Anomalías, los modos de falla con su
   categoría, área responsable y documento que no se pide), **leídos de la
   base**, nunca escritos en la plantilla: así la documentación no se desfasa
   cuando el admin cambia un catálogo.
6. **Cómo se calcula** cada número que se ve (antigüedad, semáforo, KPI), con
   los umbrales tomados de las mismas constantes del código.
7. **Lo que NO hace** (no valida contra SAP, no manda correos…). Es lo que
   evita que alguien dé por hecho algo que no existe.
8. **Contacto** y **fecha de última revisión** (`FECHA_REVISION_DOC` en
   `vistas.py`; se cambia en el mismo PR que cambia una regla).

La ven todos los roles, también Consulta. Entra en la prueba de "todas las
pantallas abren con cada rol", y el barrido de nombres internos
(`palabra_con_guion_bajo`) también la recorre.

### Diseño

Tokens de color de `theme.css` (el de `dashboard-standards`), fondos suaves
con `color-mix`, tarjetas redondeadas, estatus como píldoras de color. Nada de
fuentes, íconos ni imágenes de otro dominio.

---

## 7. Adjuntos

- El **tipo se decide por los primeros bytes** (JPG, PNG, WEBP, HEIC, PDF), no
  por la extensión. Un `.exe` renombrado a `.pdf` se rechaza.
- El **nombre en disco lo genera la app** (`AAAA/MM/<uuid>.<ext>`); el
  original solo se guarda para mostrarlo. La ruta real se comprueba con
  `resolve()` dentro de la carpeta.
- Se sirven **solo por una ruta con sesión** (`/adjunto/<id>`), nunca como
  estático. La carpeta no se comparte en la red.
- Límite por archivo y por envío, y si falla a la mitad se borra lo que
  alcanzó a escribirse.
- **Respaldo de la base y de la carpeta en la misma ventana:** una sin la otra
  deja fotos sin registro o registros sin foto.

---

## 8. Seguridad del código (lo que revisa IT)

| Qué | Cómo |
|---|---|
| CSP | `default-src 'self'`, **sin `unsafe-inline`**: cero `<script>` en línea, cero `onclick=`, cero `style=""`. Un ancho dinámico va en `data-pct` y lo aplica el JS |
| Encabezados | `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy`, `Permissions-Policy`, sin `Server`, y `Cache-Control: private, no-store` en todo lo que no es estático |
| XSS | plantillas con autoescape; ningún dato entra a `innerHTML` |
| CSRF | token por usuario (HMAC con llave generada al arrancar, en memoria) + revisión de `Origin` |
| SQL | **todo con `?`**; lo único que se interpola son nombres de tabla escritos en el código |
| URL | filtros validados por formato o contra el catálogo; lo inválido se ignora y **no se pinta** |
| Redirecciones | `next=` solo acepta rutas locales (`/x`, nunca `//x` ni `https://`) |
| CSV | BOM, y `'` antes de valores que empiezan con `= + - @` |
| Dependencias | versiones exactas; revisar cada una contra CVE antes del PR |
| Rastros | nada de firmas de herramientas en código, comentarios, rutas ni commits (`portal-seguridad` § 6) |

La llave de la sesión y la del CSRF se generan al arrancar y viven en memoria:
**no son secretos que se guarden**. Un reinicio solo pide recargar un
formulario abierto.

---

## 9. Pruebas mínimas

Con pytest contra SQLite y datos inventados. Una app no se entrega sin estas:

- [ ] El flujo completo de punta a punta por cada categoría, **cambiando de rol**
- [ ] Cada rol recibe **403** en lo que no le toca (no basta con ocultar el botón)
- [ ] Folio consecutivo y reinicio de año
- [ ] Conflicto de versión: dos personas, la segunda no pisa
- [ ] POST sin token CSRF o de otro `Origin` → 400
- [ ] Encabezado de usuario desde otra IP → 401; sin encabezado → 401
- [ ] `<script>` en un campo se pinta escapado
- [ ] Archivo disfrazado se rechaza; `../` no sale de la carpeta
- [ ] CSV con BOM y fórmulas neutralizadas
- [ ] Ningún aviso de error trae nombres de columna
- [ ] Toda llave de texto existe en ES y EN
- [ ] Configuración de producción sin base → no arranca
- [ ] Todas las pantallas abren (200) con cada rol

**Y en el navegador**, no solo en pruebas: consola sin errores de CSP, celular
sin scroll horizontal, y el flujo recorrido a mano una vez.

---

## 10. La entrega a IT

`DESPLIEGUE.md` lleva, en este orden:

1. Qué es y un diagrama de una línea (sección 3).
2. Requisitos: Python, **ODBC Driver 18**, IIS con URL Rewrite + ARR +
   Windows Authentication, cuenta de servicio, grupo de AD.
3. Base: el DBA corre `sql/esquema.sql`; la cuenta del servicio solo con
   `db_datareader` + `db_datawriter`.
4. Carpeta de adjuntos: la cuenta del servicio con Modificar; los usuarios sin
   acceso directo.
5. Instalar: `venv`, `pip install -r requirements.txt`, `.env`,
   `cli catalogos`, `cli revisar`, servicio de Windows.
6. IIS: HTTPS, Windows Auth sin Anonymous, regla de autorización al grupo,
   proxy a 127.0.0.1, la variable `{LOGON_USER}`, `maxAllowedContentLength`.
7. Firewall: bloquear el puerto de waitress.
8. Qué seguridad ya trae (sección 8), en lenguaje de IT.
9. Cómo comprobar después de instalar.

`cli revisar` es la prueba de la última milla de una app: se conecta, lee
cada tabla, y dice qué falta (tablas, permisos, catálogos vacíos) sin
escribir nada.

---

## Checklist antes del PR

- [ ] Stack Flask, o React con la justificación de dos de tres escrita en el README
- [ ] Tablas `LOG_<APP>_<TABLA>` (ver `apps-base-datos`); esquema único en `sql/esquema.sql`
- [ ] Sin contraseñas: IIS pone el usuario, SQL con Windows Authentication
- [ ] Escucha solo en 127.0.0.1; sin encabezado de usuario → 401
- [ ] Roles en la app, permisos en una sola función, las rutas responden 403
- [ ] El estatus solo lo mueven acciones, y cada acción tiene su pantalla
- [ ] Historial, antigüedad por etapa, bitácora, cancelar en vez de borrar, `VERSION`
- [ ] Inicio con el botón grande; buscador aparte con pestañas y campos separados
- [ ] Listas dependientes que se filtran; borrador automático; un solo envío
- [ ] Errores con la etiqueta del campo y que llevan a él
- [ ] 16 px, 48 px, celular sin scroll horizontal, fotos reducidas sin GPS
- [ ] ES / EN completos; CSP sin `unsafe-inline`; CSV seguro
- [ ] "📖 Documentación" al pie, con las 8 secciones, catálogos leídos de la base y fecha de revisión al día
- [ ] Las pruebas de la sección 9 pasan y se recorrió en el navegador
- [ ] Datos de prueba inventados; nada real en el repo
- [ ] `DESPLIEGUE.md` completo; `cli revisar` funciona
