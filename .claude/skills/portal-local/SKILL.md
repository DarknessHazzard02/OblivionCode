---
name: portal-local
description: Vista previa local del Portal BI antes de aprobar un cambio - arma o rehace una copia del repo repo-portal en C:\Users\<usuario>\Documents\Portal-Local (sin .git, con su venv), le monta encima los tableros que todavía no están en el repo (tarjeta, lista blanca y rutas), corre las pruebas de rutas y la levanta en http://127.0.0.1:8080 con iniciar_portal.cmd; en cada corrida rearma y sobreescribe Documents\Portal-Local.zip (solo datos inventados) para levantarla en otro equipo de la empresa. Úsala SIEMPRE que se haga un cambio para el Portal que necesite aprobación o un PR y se quiera ver antes - un tablero nuevo o modificado, una tarjeta, una sección como Sneak peek, app.py, una rama o PR del portal - y cuando se mencione portal local, copia del portal, vista previa, preview, "verlo antes de aprobar", "cómo se ve en el portal", probar el portal, Portal-Local, portal_local.py, iniciar_portal.cmd, levantar el portal, zip del portal o llevar el portal a otro equipo.
---

# Portal BI en local, para ver un cambio antes de aprobarlo

Cada cambio al portal llega a `main` por PR (Regla 6). Esta skill sirve para **verlo funcionando
dentro del portal antes** de pedir la aprobación o de mergear. No reemplaza al PR ni a la revisión
de Haz; es para que lo que se manda a revisión ya se haya visto.

| | |
|---|---|
| Repo del portal (solo se lee) | `C:\Users\<usuario>\Documents\GitHub\repo-portal` |
| Copia local | `C:\Users\<usuario>\Documents\Portal-Local` — **sin `.git`**: desde ahí no se puede subir nada |
| Tableros que aún no están en el repo | `Portal-Local\_local\tableros.json` |
| Páginas del portal cambiadas solo en local | `Portal-Local\_local\reemplazos\` (misma ruta que en el repo) + `reemplazos.json` |
| Script | `~/.claude/skills/portal-local/scripts/portal_local.py` |
| URL | `http://127.0.0.1:8080/` (solo este equipo) |

## Cuándo usar cada modo

| Lo que se quiere ver | Comando |
|---|---|
| Un tablero que vive en otro repo (aún no está en el portal) | agrégalo a `tableros.json` y corre `python portal_local.py` |
| Un cambio en el repo del portal, sin commitear o en la rama actual | `python portal_local.py` |
| Una rama o PR del portal sin cambiar de rama en el repo | `git -C <repo> fetch` y luego `python portal_local.py --rama origin/<rama>` |
| Lo mismo, y dejarlo corriendo | agrega `--servir` |
| Levantar la copia ya armada (aquí o en otro equipo) | `.\iniciar_portal.cmd` desde la carpeta de la copia |
| Llevar la copia a otro equipo de la empresa | ya está: cada corrida rearma `Documents\Portal-Local.zip` |
| Rehacer la copia sin tocar el zip | `python portal_local.py --sin-zip` |

El script, en orden:

1. **Rehace la copia** desde el repo (o desde la rama con `git archive`, sin checkout). Borra lo de
   la copia que no venga del repo, salvo `venv/` y `_local/`. Lo que se editó a mano en la copia
   se pierde, a propósito: la copia no es lugar para trabajar.
2. **Aplica los reemplazos de `_local/reemplazos/`** (se salta con `--sin-reemplazos`). Ver la
   sección de reemplazos, abajo.
3. **Monta los tableros de `tableros.json`.** Copia `codigo` a `<slug>/` y los JSON a
   `<slug>/data/dashboard/`, que es la caída local del portal. Inserta en `app.py` el bloque de
   lista blanca, rutas y CSP estricta (mismo patrón que ATP Rule) y pone la tarjeta al final de
   la lista de `<portal>/index.html`. Con `estado` distinto de `"Active"`, la tarjeta cae en
   **Sneak peek**.
4. Crea el `venv` si no existe e instala `requirements.txt`, con las versiones fijas del portal.
5. **Prueba** `/logistics/`, `/sop/` y, por cada tablero montado: su página, su API, que
   `..%2F..%2Fapp.py` dé 404 y que `data/` no se sirva como estático.
6. Si las pruebas pasan, **rearma `Documents\Portal-Local.zip`** y sobreescribe el anterior
   (ver "Llevarlo a otro equipo").

Si el portal cambió y no encuentra dónde insertar (`SHARED STATIC` en `app.py`, o el final de
la lista `dashboards`), **se detiene**. Montar a medias deja un portal que "carga" sin el tablero.

## Agregar un tablero a `tableros.json`

```json
{
  "slug": "mi-tablero",
  "origen": "C:\\<servidor>\<carpeta>",
  "codigo": ["index.html", "app.js", "estilos.css"],
  "archivos": ["meta.json", "dashboard.json"],
  "datos_reales": ["data_real"],
  "datos_demo": ["data"],
  "portal": "logistics",
  "tarjeta": { "titulo": "...", "desc": "...", "desc_en": "...", "categoria": "Order Management",
               "tag": "SAP / ...", "tagColor": "blue", "url": "/mi-tablero/index.html",
               "estado": "Beta", "bandera": "📊" }
}
```

- `categoria` tiene que existir en ese portal (`grid-<categoria>`); si no, la tarjeta no sale.
  En Logistics: `Trade Compliance`, `Order Management`, `Cost`. En S&OP: `Dashboards`.
- `portal` es `logistics` o `sop`. El botón de regreso del tablero (`portalUrl` en su `app.js`)
  tiene que apuntar a ese mismo portal.
- El tablero tiene que pedir sus datos a `/api/<slug>/` y regresar al portal con `/logistics/` (o
  `/sop/`). Las librerías van por `/shared/...` del portal, no con su propia copia.
- Sin manejadores `on*=` en su HTML ni en su JS: se monta con CSP estricta.
- Cuando el tablero ya entró al repo del portal, **se quita de `tableros.json`**. El script se
  detiene si ve las dos cosas, para no tapar la versión del repo.

## Levantarlo: `iniciar_portal.cmd`

Cada corrida del script deja `iniciar_portal.cmd` en la raíz de la copia (sale de
`plantillas/iniciar_portal.cmd`). Todo es relativo a la carpeta, así que funciona igual en
cualquier usuario o equipo Windows con Python 3:

```powershell
cd <carpeta del portal>
.\iniciar_portal.cmd          # puerto 8080
.\iniciar_portal.cmd 8090     # otro puerto
```

- Hace falta el `.\`: ni PowerShell ni el `cmd` de este equipo buscan en la carpeta actual. También
  funciona con doble clic.
- La primera vez en un equipo crea `venv\` e instala `requirements.txt` (5 paquetes con versión
  fija, desde internet). Después ya no instala nada.
- Escucha solo en `127.0.0.1`, revisa que el puerto esté libre y abre el navegador solo.
- Si algo falla (sin Python, sin internet la primera vez, puerto ocupado), lo dice y se detiene.

## Llevarlo a otro equipo: `Portal-Local.zip`

Cada corrida del script rearma **`C:\Users\<usuario>\Documents\Portal-Local.zip`**, siempre con ese
nombre y sin fecha, y **sobreescribe el anterior**. No hace falta pedirlo aparte.

```bash
python portal_local.py                         # rehace la copia y el zip
python portal_local.py --sin-zip               # rehace la copia y deja el zip como estaba
python portal_local.py --zip "D:\ruta\x.zip"   # el zip en otro lugar
```

- Solo se arma si las pruebas pasan. Primero se escribe aparte y al final reemplaza al anterior: si
  algo truena a medias, el zip anterior sigue completo.
- Adentro va la carpeta `Portal-Local\`.
- **No lleva** `venv\`, porque no sirve en otro equipo, ni `_local\`, que trae rutas de este usuario.
  Los reemplazos y los tableros ya van aplicados en la copia.
- **Solo datos inventados.** Con `--reales` el zip **no se rearma**: el anterior, con datos
  inventados, se queda como estaba. También se niega si algún tablero montado
  no trae `"demo": true` o si aparece `data_real` o `config.local.json` en la copia.
- ⛔ Regla 4: el zip va **solo a un equipo de la empresa y por un canal de la empresa** (OneDrive
  o Teams de la empresa). Nunca a USB, correo, nube personal ni a un equipo personal: es código del
  equipo y se ve como fuga aunque traiga datos inventados.
- En el otro equipo: descomprimir, entrar a `Portal-Local\` y correr `.\iniciar_portal.cmd`.
  Ahí solo se levanta: `portal_local.py` y `tableros.json` apuntan a rutas de este equipo, así que
  la copia se rehace aquí y se vuelve a mandar.

## Reemplazos: cambiar una página del portal solo en local

Sirven para cambios del portal que se quieren ver sin tocar el repo, como una sección nueva o el
botón de idioma. El archivo va en `_local/reemplazos/` con **la misma ruta que en el repo**
(`sop/index.html`, `logistics/index.html`, `index.html`). Se parte de una copia del archivo del
repo y se edita esa copia.

- La primera vez que el script lo aplica, guarda en `reemplazos.json` la huella de la versión
  del repo de la que salió.
- **Si después el repo cambia ese archivo, el script se detiene.** Aplicar el reemplazo taparía
  el cambio del repo con una versión vieja. Hay que llevar el cambio del repo al reemplazo y correr
  `--rebasar <ruta>` para tomar la huella nueva.
- Las tarjetas de `tableros.json` se insertan **después** de los reemplazos, así que el reemplazo
  tiene que conservar el final de la lista `dashboards` (`];` seguido del bloque `RENDER DASHBOARDS`).
- Con el botón de idioma, la tarjeta lleva `desc_en`. Sin ella, en inglés se ve la descripción en
  español y la consola lo avisa.
- Un reemplazo **no llega al portal de verdad**. Si se aprueba, el mismo cambio va por rama y PR
  al repo, y luego se borra de `_local/reemplazos/` (y su renglón de `reemplazos.json`).

Reemplazos activos hoy:

| Archivo | Qué cambia |
|---|---|
| `sop/index.html` | sección **Sneak peek**: los tableros que no son `Active` se van ahí, como en Logistics |
| `logistics/index.html` | botón **ES/EN** (llave `dash_lang`, igual que S&OP), `desc_en` en cada tarjeta |
| `index.html` | botón **ES/EN** en la pantalla de divisiones |

## ⛔ Datos: inventados por default

- Sin `--reales`, el script monta `datos_demo`. Es lo que pide el repo y lo que basta para ver el
  cambio en el portal.
- Con `--reales` usa la primera carpeta de `datos_reales` que traiga todos los `archivos` y, si
  no hay, los inventados. Lo dice en la línea `Montado: ... datos REALES / inventados`.
- La skill `entregar-tablero` (sección 4) dice que **ver un tablero del portal con datos reales
  en local lo hace Haz**, y solo cuando los inventados no alcanzan. Antes de usar `--reales`
  hay que avisarlo: es copiar datos de OneLake a otra carpeta del equipo (Reglas 4 y 5). La copia
  vive fuera de OneDrive y de todo repo. **El asistente no abre esos JSON**, ni con
  `get_page_text` ni con capturas del tablero: revisa la banda, la consola y los conteos.
- Para dejar la copia sin datos reales, vuelve a correr el script sin `--reales`.

## Cómo comprobar que de verdad salió

| Qué | Bien | Falló en silencio |
|---|---|---|
| Salida del script | `Pruebas: todo bien` y un `Montado:` por tablero | un tablero de `tableros.json` sin su renglón `Montado:` |
| `http://127.0.0.1:8080/logistics/` | la tarjeta en su sección, o en Sneak peek si no es Active, y el contador sube | la tarjeta no aparece: `categoria` sin sección (la consola lo dice) |
| El tablero | carga, sin errores en la consola, con el botón de regreso al portal | carga en blanco: no pide sus datos a `/api/<slug>/` |
| La banda | "Datos inventados" si se montó demo | sin banda y con demo: el tablero no marca `"demo"` en su `meta.json` |
| Que no se mezcle con el repo | `git -C <repo> status` igual que antes de correrlo | cualquier cambio en el repo: el script no debe escribir ahí |

## Al cerrar, lo que le toca a la persona

Cierra con `Lo que tienes que hacer` (Regla 2). Casi siempre trae:

1. Correr `python portal_local.py --servir` (o `actualizar` el tablero primero, si sus datos se
   generan aparte) y abrir `http://127.0.0.1:8080/logistics/`.
2. Revisar la tarjeta y el tablero con la tabla de arriba, renglón por renglón.
3. Si se ve bien: abrir o actualizar el PR del cambio. La copia no se entrega ni se sube.
