---
name: tablero-celular
description: Cómo se deja un tablero del portal de tableros listo para verse en el celular sin tocar cómo se ve en escritorio - qué significa "listo para celular" (siete criterios medibles a 375 px), el bloque CSS que se pega al final del tablero, los patrones que ya fallaron en el portal (encabezado .hdr__meta que se sale, tabla dentro de overflow hidden, body con overflow-x hidden que tapa el desborde, sidebar abierto que cubre la pantalla, barra de filtros que llega abierta, fila de KPIs de columnas fijas) y el script que mide si pasa. Úsala SIEMPRE que se cree un tablero nuevo, se modifique el encabezado, los KPIs, las tablas o el layout de uno existente, o se mencione celular, teléfono, móvil, mobile, iPhone, Android, tablet, responsive, responsivo, pantalla chica, 375, "se sale de la pantalla", "scroll de lado" o "verlo desde el teléfono". También cuando se pida revisar qué tableros del portal se ven en celular. Complementa a tablero-estandar (cómo se construye) y a probar-tablero (P12 usa el script de esta skill).
---

# Tableros en el celular

> Reglas base (cierre `Lo que tienes que hacer`, credenciales, sin firma de IA, avisar y parar): skill `estandar-hazzard`.

El portal es **escritorio primero**. Esta skill no cambia eso: agrega lo necesario para que un
tablero **también** se lea en un celular, sin mover un pixel de lo que se ve en 1366 o 1280.

---

## ⛔ El escritorio no se toca

Todo lo de celular vive **dentro de** `@media (max-width: 640px)`. Nada fuera de ese bloque cambia.

Por qué: en la app de fletes se "optimizó para el teléfono" el diseño completo y quedó todo
amontonado en la pantalla de trabajo, que es donde de verdad se usa. Lo responsivo se agrega
encima; no reemplaza el diseño de escritorio.

Después de cualquier cambio de esta skill, se abre el tablero a 1366 × 768 y se compara con antes.
Si algo se movió, el cambio está mal.

---

## Qué es "listo para celular"

Se mide a **375 × 812**, con datos cargados. Pasa solo si se cumplen los siete criterios:

| # | Criterio | Cómo se ve cuando falla |
|---|---|---|
| C1 | Nada se sale de la pantalla: `scrollWidth` igual a 375 | la página entera se recorre de lado; casi siempre es el encabezado |
| C2 | Lo ancho (tablas, tiras de pestañas) hace scroll **dentro de su caja** | la tabla empuja la página |
| C3 | Ninguna tabla queda dentro de un contenedor con `overflow-x: hidden` | las columnas de la derecha **no se pueden ver de ninguna forma** |
| C4 | `html` y `body` **no** llevan `overflow-x: hidden` | C1 sale bien en el número pero el contenido está cortado: falla en verde |
| C5 | Al abrir, nada fijo tapa más de media pantalla (sidebar, panel de filtros) | el usuario abre el tablero y ve un menú, no datos |
| C6 | Controles de al menos 28 px de alto (36 px en los nuevos), texto de al menos 10 px | no se le atina a la pestaña o al botón con el dedo |
| C7 | Los filtros **arrancan plegados** y se abren y cierran con un toque | la primera pantalla son 300-400 px de `<select>` y el primer número aparece hasta abajo, sin forma de esconderlos |

Además, a ojo:

- El encabezado cabe en 2 o 3 renglones: Portal + ES/EN, título, fechas.
- Los KPIs van **dos por renglón**, y las gráficas **una por renglón**, a todo lo ancho.
- Las etiquetas de barras horizontales no se cortan al principio. Si se cortan, se abrevian en
  celular; no se encoge la letra.

---

## Cómo se hace

### 1. Tableros con el tema propio (`.hdr`, `.grid`, `.kpi`, `.filter-panel`)

Es casi todo el lado de el área. `theme.css` va **copiado dentro** del `<style>` de cada
tablero, no enlazado. Por eso el bloque de [`assets/celular.css`](assets/celular.css) se pega
**al final de ese `<style>`**, después del tema, para ganar los empates de especificidad.

Qué resuelve, en orden de importancia:

1. **Encabezado.** `.hdr` tiene alto fijo de 60 px y no se acomoda. Al hacerse angosto,
   `.hdr__meta` (Actualizado / Datos al), `.hdr__chips` y `.lang-toggle` se salen por la derecha.
   Fue el defecto principal en casi todos los tableros revisados. El bloque lo pasa a `flex-wrap` con alto
   automático: título en su propio renglón y fechas abajo.
2. **Tablas.** Cualquier `div` o `section` que contenga una tabla hace scroll de lado.
3. **KPIs.** Dos columnas, con los nombres de contenedor que se usan en el portal (`#kpiRow`,
   `.kpi-row`, `.kpis`, `.kpi-grid`, `.kpi-strip`). Si el tablero usa otro nombre, se agrega a la
   lista **en el tablero**, no en la skill.
4. **Grid de 12.** Toda tarjeta pasa a `1 / -1`, sin importar su `span`.
5. **Panel de filtros abierto.** Pasa a ser un cajón encima del contenido, en vez de empujarlo.
6. **Panel de documentación.** Ocupa toda la pantalla.

Comprobado sobre un portal real: los 14 tableros de este tipo
pasaron de un ancho de 411 a 995 px a 375 px exactos, sin un solo elemento fuera.

### 2. Tableros con sidebar (tablero B, tablero C)

No usan el tema. Las reglas son otras:

- **El sidebar arranca cerrado** a 900 px o menos, y se abre con su botón (☰). Se decide en el JS
  al cargar (`if (matchMedia('(max-width: 900px)').matches) sidebar.classList.add('collapsed')`),
  no por CSS. Si se fuerza por CSS, el botón ya no lo puede abrir.
- **Nunca `overflow-x: hidden` en `html` ni en `body`** para "arreglar" el scroll de lado.
  Esconde el síntoma y corta el contenido. Lo que desborda se busca con el script y se arregla
  ahí.
- Las filas de filtros (`.filter-group` con `<select>` lado a lado) pasan a una columna.
- Las tiras de pestañas (`.map-tabs` y similares) hacen scroll dentro de su caja.

tablero C ya cumple casi todo: tiene ☰ y los filtros en columna. tablero B no.

### 3. Barra de filtros arriba del contenido (`.filtros-bar`, `.filter-bar`)

El panel lateral del tema (`.filter-panel`) ya arranca plegado en su tira de 48 px. Pero una
**barra horizontal** de filtros, en celular, se apila en una columna y ocupa la pantalla entera
antes del primer dato. Así estaban tablero C, tablero A y siete páginas del tablero B.

Se arregla con una línea en el `<head>`:

```html
<script src="/shared/js/filtros-plegables.js"></script>
```

- **Qué hace:** a 640 px o menos, la primera `.filtros-bar` o `.filter-bar` de la página arranca
  plegada detrás de un botón.
- **El botón:** si la barra ya trae su etiqueta (`.f-label`, `.filter-bar__label`), esa misma se
  vuelve el botón. Si no trae, se agrega uno ("Filtros" o "Filters", según el `lang` de la
  página).
- **Plegada:** dice cuántos filtros hay puestos, por ejemplo `(2) ▾`.
- **Abierta:** deja de ser sticky.
- **CSS:** el script lo trae adentro; no hay que tocar la hoja del tablero.
- **Escritorio:** no cambia nada.

Un tablero nuevo con barra de filtros arriba lleva esa línea desde el principio.

### 4. Tablero nuevo

Se arranca del `boilerplate.html` de `tablero-estandar` **con el bloque de celular ya pegado**
al final del `<style>`. Cuesta cero hacerlo al principio y mucho hacerlo después, porque cada
tablero termina con sus propios nombres de contenedor.

---

## Cómo se comprueba

[`assets/medir-celular.js`](assets/medir-celular.js) mide los siete criterios y regresa
`pasa: true/false` con la lista de lo que se sale.

**Un tablero**, en el navegador integrado:

1. Portal levantado (skill `preview-local`) y el tablero abierto con `preview_start`.
2. `resize_window` con `preset: "mobile"` y recargar la página.
3. Esperar a que carguen los datos. Sin datos, las tablas miden cero y todo pasa en falso.
4. Mandar el contenido del script con `javascript_tool`.
5. Captura a `scale: 0.5` como evidencia, arriba y después de bajar.
6. `resize_window` con `preset: "desktop"` y otra captura a 1366: tiene que verse igual que
   antes del cambio.

**Todo el portal de una vez:** desde cualquier página del portal se crea un `<iframe>` de
375 × 812 por tablero (el portal manda `SAMEORIGIN`, así que se permite), se espera la carga y se
llama `medirCelular(iframe.contentWindow)`. Las media queries del iframe responden a **su** ancho.
`javascript_tool` corta a los 45 s, así que el ciclo se lanza sin `await` al final, guarda los
resultados en `window.__res` y se lee en otra llamada.

**Para probar un arreglo antes de editar el archivo:** se inyecta el CSS con un `<style>` en el
`contentDocument` del iframe y se mide antes y después. Así se sabe si el bloque alcanza antes de
tocar el repo.

### Lo que engaña

- **`scrollWidth` = 375 no quiere decir que cabe**, si `body` tiene `overflow-x: hidden` (C4). Hay
  que leer también `document.body.scrollWidth` y la lista `desbordan`.
- **Un tablero que contesta 404 o 503 "pasa"**: no tiene nada que se salga. Primero se confirma
  que la página cargó (título, número de textos). Algunos tableros (`<tablero-a>/`, `<tablero-b>/`) siguen en
  el repo pero el portal no los sirve.
- **Los datos inventados de la copia local** hacen las tablas más angostas que en producción. Si
  una tabla mide 560 px con datos de prueba, con los reales va a medir más. Por eso C2 y C3 se
  revisan por regla, no por número.
- **Se mide la pestaña que abre por defecto.** Las demás pestañas pueden tener otra tabla o
  gráfica. En un tablero con pestañas, se mide cada una.
- **`/shared/css/responsive.css` del tablero B menciona un `/shared/js/responsive.js` que no existe.** No
  hay nada que cierre el sidebar en celular aunque el comentario diga que sí.

---

