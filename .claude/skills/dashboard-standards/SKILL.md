---
name: dashboard-standards
description: Estándares obligatorios para construir dashboards del equipo de BI, de la capa de datos a la pantalla - contrato de datos y meta.json, prohibición de defaults silenciosos, modo degradado visible, caché y validación de la última milla; y del lado visual tokens de color (tema la empresa y alterno), cross-filter entre todas las gráficas, panel de filtros colapsable, tabla de detalle paginada con export a CSV y Excel, data labels, bilingüe ES/EN, panel de documentación, frescura de datos, botón de regreso al portal, y cómo se programa el correo que manda ese tablero por Office365Email desde Fabric. Úsala SIEMPRE que se mencione dashboard, tablero, reporte visual, gráfica, chart, KPI, visualización de datos, panel de control o landing page analítica, y también cuando solo se pida "una gráfica de X" o "una tabla de Y" sin decir la palabra dashboard, o cuando se prepare el JSON o la tabla que alimenta un tablero. También cuando un tablero muestre números de parte, SKU o materiales (todos llevan botón de copiar). Aplica igual al modificar un dashboard existente, y cuando se pida un correo, reporte por mail, envío programado o notificación con datos de un tablero.
---

# Estándares de Dashboards — equipo de BI

Reglas obligatorias. Si algo no está aquí, pregunta antes de inventar.

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

## PASO 0 — Preguntar ANTES de escribir código

No empieces a construir sin resolver estas cinco preguntas:

1. **Idioma** — ¿inglés, español, o ambos?
   Si es *ambos*, se implementa el toggle ES/EN en el encabezado de **cada pestaña** del dashboard.
2. **Umbral de frescura** — ¿a partir de cuántos días los datos se consideran viejos?
   Varía por dashboard. Default sugerido: ámbar a 1 día, rojo a 3.
3. **Origen de los datos** — ¿archivos estáticos, API, o consulta directa?
   Y por **cada fuente**, la pregunta que no se salta: **¿de dónde sale su fecha
   de extracción?** De archivo sale del nombre; de una API o una consulta tiene
   que venir en un metadato que escriba el cargador. **Si no lo sabes, pregunta**
   — no la deduzcas de una columna de fecha que parezca servir (sección 8).
4. **¿Cuál es la URL que dice si el tablero está al día?** Una sola, la que ve el
   usuario. Si no la puedes nombrar, no sabes qué estás construyendo (sección 13).
5. **¿Qué pasa cuando falta un dato?** La respuesta correcta nunca es "poner un
   valor razonable" (sección 14).

Luego:
- Copia `assets/theme.css` y arranca desde `assets/boilerplate.html`. Ese esqueleto ya cumple todas las reglas de este documento — no lo reconstruyas desde cero.
- Llena el bloque `CONFIG` que está arriba del script. Ahí van portal, umbrales, idioma y metadatos de fuentes.

---

## 1. Colores

Todo sale de las variables CSS de `theme.css`. **Cero hex hardcodeados en el código.**
Tema por defecto: `<html data-theme="corporativo">`. Tema `alt` (navy/cobre) solo para audiencia externa.

- Máximo 5 series categóricas (`--c-cat-1` … `--c-cat-5`); el resto se agrupa en "Otros" con `--c-cat-other`.
- La misma categoría lleva el mismo color en toda la página. No reordenar entre visuales.
- Rojo/ámbar/verde (`--c-critical`, `--c-warn`, `--c-ok`) **solo** para estatus, nunca para categorías.
- Escalas `--c-seq-*` solo para medidas continuas.
- Contraste mínimo 4.5:1 para texto.

---

## 2. Interactividad — regla no negociable

**Todas las gráficas se filtran entre sí.** Click en una columna, barra, rebanada o punto → TODOS los demás visuales (incluidos KPIs y tabla de detalle) se recalculan al instante. No existe visual de solo lectura.

| Evento | Comportamiento |
|---|---|
| Hover | Tooltip + resto de elementos con clase `.dimmed` |
| Click | Cross-filter global; segundo click deselecciona |
| Ctrl/Cmd + click | Selección múltiple |
| Click en leyenda | Muestra/oculta esa serie |
| Doble click en fondo | Limpia toda la selección |

**Arquitectura obligatoria** — un solo estado, una sola función de redibujo. Nunca acoplar gráfica con gráfica:

```js
const filterState = { panel: {}, crossfilter: null };

function applyFilters() {          // única puerta de redibujo
  const data = getFilteredData();
  renderKPIs(data);
  charts.forEach(c => c.update(data));
  renderTable(data);
  renderChips();
  syncURL();
}
```

- El visual que originó la selección **atenúa** lo no seleccionado; los demás se **redibujan** con los datos filtrados.
- La selección aparece como chip removible en el encabezado.
- **Limpiar filtros** resetea `panel` y `crossfilter` juntos.
- Animaciones máximo 240ms (`--t-base`). Redibujo en `resize` con debounce de 150ms.
- Sin datos tras filtrar → `<div class="empty-state">`. Nunca un canvas en blanco.

---

## 2 bis. ⛔ El manejador se engancha al ROL, no al contenedor

Costó cuatro despliegues. El tablero se quedaba en blanco de las pestañas para
abajo al picar un toggle, y todo apuntaba a rendimiento.

El toggle vivía dentro del `<nav>` de pestañas —se veía bien ahí— y el manejador
de pestañas escuchaba a **todos** los botones del nav:

```js
document.querySelectorAll("#tabs button").forEach(b => {
  b.onclick = () => {
    tabActiva = b.dataset.tab;                  // undefined: el toggle no lo tiene
    p.hidden = p.dataset.pane !== tabActiva;    // ninguno coincide → todos ocultos
```

Los botones del toggle llevan `data-univ`, no `data-tab`. Al picarlos disparaba
**también** el manejador de pestañas, `tabActiva` quedaba en `undefined` y los
tres paneles se ocultaban. El redibujo corría perfecto: quedaba escrito detrás de
un `display: none`.

```js
// mal: atrapa cualquier control que alguien meta en ese contenedor mañana
document.querySelectorAll("#tabs button")

// bien: el rol es lo que define quién responde
document.querySelectorAll("#tabs button[data-tab]")
```

Y el estado que decide qué se ve **nunca puede quedar vacío en silencio**. Es la
sección 14 aplicada a la interfaz: un default silencioso que apaga la pantalla.

```js
if (!tabActiva) {                 // red, no adorno
  tabActiva = "mrp";
  console.error("tabActiva quedó vacío; se regresa a mrp");
}
```

Dejar el tablero en blanco es el peor resultado posible: **parece que no hay
datos**. Ante un estado imposible, se vuelve al que sí funciona y se dice.

### Lo que despistó, y por qué

Vale la pena tenerlo presente, porque cada síntoma parecía descartar la causa
real:

| Lo que se veía | Lo que sugería | Lo que era |
|---|---|---|
| Se rompe en las dos direcciones | volumen, memoria | los dos botones estaban en el nav |
| Recargar con el parámetro en la URL funciona | caché, descarga | sin click, el estado no se corrompe |
| Los tiempos salen en 223 ms sin errores | el reloj está mal medido | el dibujo sí corría; quedaba oculto |
| Da igual 268 que 4,814 filas | algo no escala | nunca fue volumen |
| Ninguna pestaña se veía resaltada | detalle cosmético | **era el síntoma directo** |

Ese último renglón es la moraleja: el detalle "cosmético" que nadie reporta suele
ser la única huella limpia de la causa.

---

## 2 ter. Si no lo puedes reproducir, instruméntalo

Cuatro intentos de arreglar aquello fueron conjeturas, porque en local no se
reproducía y no había forma de ver el navegador donde sí pasaba. Cada conjetura
costó un despliegue.

**Cuando el síntoma solo ocurre en la máquina de otro, el tablero tiene que poder
contar qué le pasó.** No con `console.log`: nadie abre la consola, y pedirlo por
chat cuesta más que construirlo.

Un botón en el encabezado que reporte, del último redibujo:

- **cuánto tardó cada etapa**, midiendo con el layout forzado (`void
  document.body.offsetHeight` antes de parar el reloj). Sin eso el reloj se
  detiene cuando acaba el JavaScript y deja fuera justo lo que suele costar.
- **qué quedó en pantalla**: cuántas filas escribió cada visual, cuántos
  caracteres de HTML, y el `display` **calculado** y el alto real de cada
  contenedor.

Ese segundo bloque es el que resuelve. «Se dibujó vacío» y «se dibujó y está
tapado» se ven idénticos desde fuera, y llevan a arreglos opuestos:

```
matrix rows: 300 · matrix html: 1,764,778 chars   → el DOM sí se escribió
pane mrp: none, 0px                               → pero está oculto
tab: undefined                                    → y ahí está la causa
```

Tres líneas en una captura, después de cuatro despliegues adivinando.

Se mide el `display` **calculado**, no la propiedad `hidden`: la propiedad dice
lo que el código quiso hacer, el `display` dice lo que el usuario ve.

### El estetoscopio compartido: `/shared/js/diagnostico.js`

**Todo tablero del portal trae el botón 🩺.** Si el tablero no tiene uno propio
(`id="btnDiag"`), carga el compartido, que no necesita nada del tablero:

```html
<script src="/shared/js/diagnostico.js"></script>   <!-- en el <head> -->
```

Pone un botón discreto abajo a la derecha que reporta, en la computadora de
quien abre la página: cuánto tardó la página y **cada `/api/`** (con su peso
comprimido y sin comprimir, y cuál fue la más lenta), filas por tabla, gráficas
sin tamaño, contenedores visibles con alto 0 (sin contar los de otras pestañas),
la fecha del dato del encabezado y los errores de JavaScript. Con un botón
**Copiar** para que te manden el reporte. `tests/test_rutas.py` falla si un
tablero llega sin estetoscopio.

---

### ⛔ Que tu CSS exista no quiere decir que aplique

Dos del mismo día, las dos invisibles al leer el código:

**Un `<span>` es `inline`, y un inline ignora `width` y `height`.** La barra de
cada renglón se pintaba con `<span class="…__fill" style="width:60%">` dentro de
otro span: `display: inline`, **0×0**, la barra simplemente no existía. Las
barras de la mitad de arriba se salvaban de casualidad porque su contenedor era
`flex`, que blockifica a sus hijos. `display: block` no sobra nunca en un span
al que le pones medidas.

**Un token inventado no falla: no hace nada.** Se usó `var(--radius-sm)` en un
tablero donde ese token **no existe** —el archivo usa `3px` literal—. CSS resuelve
una variable indefinida a nada y sigue de largo: sin borde redondeado, sin
advertencia. **Antes de usar un token, compruébalo:**

```js
getComputedStyle(document.documentElement).getPropertyValue("--radius-sm")  // "" = no existe
```

> **Mide el resultado, no el código.** `getComputedStyle(el).display` y
> `el.getBoundingClientRect()` contestan en un segundo lo que leer el CSS no
> contesta nunca. Un elemento de `0×0` o un `display: none` inesperado saltan
> solos; a ojo, no.

## 3. Ícono de información por gráfica

**Cada visual lleva un ícono ⓘ** en la esquina superior derecha de su tarjeta.

- Aparece al hacer **hover** sobre la tarjeta (opacidad 0 → 1, `--t-fast`). En touch siempre visible.
- Al **click** abre un popover con el resumen del cálculo:
  - **Medida** — qué se está midiendo, en lenguaje de negocio.
  - **Cálculo** — la fórmula o lógica en una o dos líneas (`SUM(costo_flete) / COUNT(DISTINCT embarque)`).
  - **Filtros aplicados** — exclusiones fijas del visual (ej. "excluye embarques cancelados").
  - **Granularidad** — a qué nivel está agregado.
- Máximo ~60 palabras. Si necesita más, ahí va un enlace a la sección correspondiente del panel de documentación.
- Se cierra con Esc, con click fuera, o con la ✕.
- El texto vive en el objeto `CONFIG.visuals[id].info`, bilingüe si el dashboard lo es. Nunca hardcodeado en el HTML.

---

## 4. Bilingüe (ES / EN)

Si en el Paso 0 se respondió "ambos":

- Toggle `ES | EN` en el encabezado de **cada pestaña**, alineado a la derecha.
- Todo el texto visible sale de un diccionario `I18N = { es: {...}, en: {...} }`. **Cero strings sueltos en el HTML.**
- Traducir: títulos de página y de visual, etiquetas de eje, nombres de filtro, encabezados de tabla, textos de los ⓘ, panel de documentación, estados vacíos y botones.
- **No traducir**: nombres propios de planta, códigos de material, números de parte, ni los datos mismos.
- Los formatos siguen al idioma: fechas `DD/MM/YYYY` en ES, `MM/DD/YYYY` en EN. El separador de miles se queda como coma en ambos.
- La selección se guarda en `localStorage` y persiste entre pestañas y sesiones.
- Cambiar de idioma **no** resetea filtros ni selecciones.

---

## 5. Panel de filtros

### Estructura

- Panel lateral izquierdo colapsable. Ancho `--filter-panel-w` / `--filter-panel-w-collapsed`.
- **Arranca SIEMPRE colapsado.** Lo primero que se ve al abrir es el área de visuales.
- Se expande con click en el ícono de embudo; se colapsa con el mismo botón o con Esc.
- **El ícono lleva la palabra "Filtros" al lado.** Un embudo dibujado se entiende;
  un carácter como `▤` no. Si el usuario tiene que adivinar qué abre ese botón,
  el ícono no está haciendo su trabajo.
- Colapsado muestra el embudo y un **badge con el total de filtros activos**.
- Al expandirse empuja el contenido (no lo tapa) y las gráficas se redibujan.
- Orden fijo: **Alcance → Periodo → categorías cortas → categorías largas**.
  Lo que cambia el universo entero va primero; lo que tiene cientos de opciones,
  al final.
- Botón **Limpiar filtros** fijo al fondo del panel.
- Los filtros activos se reflejan como chips en el encabezado y se sincronizan a
  la URL como query params.

### ⛔ El panel tiene su propio scroll — el contenido no lo puede estirar

`Limpiar filtros` va anclado al borde inferior del panel. Si el panel crece con
su contenido, ese borde se va con él:

```
561 proveedores × 26 px  =  14,586 px de un solo grupo
panel completo           =  81 pantallas de alto
"Limpiar filtros"        =  a 62,000 px de scroll — existe y es inalcanzable
```

El panel se fija al alto de la ventana y **el scroll vive en su cuerpo**:

```css
.filter-panel.is-open {
  position: sticky; top: 0; align-self: flex-start;
  height: calc(100vh - var(--header-height));
}
.filter-panel.is-open .filter-panel__body { height: 100%; overflow-y: auto; }
```

**Sin `overscroll-behavior: contain`.** Atrapa la rueda: al llegar al final de
una lista el scroll no sigue al panel y hay que sacar el cursor del recuadro
para poder bajar. Sirve para que un panel flotante no mueva la página de atrás;
aquí se espera lo contrario.

### Cada opción es una fila, no texto corrido

Un `<label>` sin estilo es **inline**: las opciones se acomodan como un párrafo
y el grupo se vuelve ilegible. Cinco opciones llegaron a ocupar 424 px así.

```css
.filter-opt { display: flex; align-items: center; gap: 7px; height: 26px; }
.filter-opt span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
```

El nombre completo va en el `title`. Truncar sin dejar cómo leerlo entero
obliga a adivinar cuál de dos proveedores parecidos es cuál.

### Los dos umbrales

| Opciones | Qué gana |
|---|---|
| más de **5** | buscador y **Seleccionar todo** |
| más de **12** | además arranca plegado, y su lista se topa a ~7 filas con scroll |

Son dos umbrales y no uno: con seis opciones ya cansa marcarlas a mano, pero
plegar un grupo de seis solo agrega un click.

**El buscador va FUERA del cuerpo plegable**, o sea visible con el grupo
cerrado. Si vive adentro, para buscar hay que adivinar primero que el
encabezado se despliega — y entonces el buscador no existe para quien no lo
adivine. Al escribir, el grupo se abre solo.

**Seleccionar todo aplica a lo que se está viendo.** Con una búsqueda puesta,
marca los resultados visibles, y la etiqueta lo dice: `Seleccionar todo (13)`.
Marcar en silencio 548 opciones que no caben en pantalla es la forma rápida de
filtrar algo que nadie quería.

### ⛔ El orden es alfabético y NO se mueve

Tentador: ordenar por monto y subir lo seleccionado al principio. Se ve bien en
una captura. **Al usarlo, la lista se reacomoda debajo del cursor cada vez que
marcas algo** y pierdes de vista dónde ibas.

Orden alfabético, fijo, y lo seleccionado se queda donde está. Un orden aburrido
y estable se busca mejor. Los catálogos que vienen del `meta` conservan **su**
orden (el del proceso), que tampoco cambia.

Si la búsqueda esconde algo que estaba marcado, **hay que decirlo**: un filtro
puesto que no aparece en ningún lado es peor que no tenerlo.

### Contar filtros, no valores

- El **badge** cuenta *filtros puestos*, no valores. Un grupo con tres
  proveedores marcados es **un** filtro. Sumando valores, "Seleccionar todo"
  dejaba el badge en `561`.
- Los **chips**: uno por valor hasta tres; de ahí en adelante uno que resume
  (`Proveedor: 561 seleccionados`) cuya ✕ limpia el grupo entero. Un chip por
  valor tapaba el encabezado completo.
- El encabezado de cada grupo muestra `seleccionadas/total`: `Estatus (3/5)`.

### Interruptor de dos estados, no casilla

Cuando las dos opciones son igual de válidas y ninguna es "lo normal", va un
interruptor con las dos a la vista:

```
[ Toda la planta ][ Solo logística ]     en vez de     [x] Solo logística
```

Una casilla apagada no dice contra qué está apagada.

### ⛔ Se filtra por el VALOR, se muestra la ETIQUETA

El error que más caro sale en esta sección. Un grupo vacío se pinta como
`(sin aprobador)` o `–`, y si ese texto es lo que se guarda como filtro, se
buscan filas cuyo campo valga literalmente `"(sin aprobador)"` — que no existe
ninguna. **Click en esa barra deja la tabla vacía y parece que no hay datos.**

La opción guarda el valor crudo (`""`), la etiqueta es solo para pintar, y el
comparador normaliza `null` y `undefined` a `""` para que los dos filtren igual.

Lo mismo aplica a los espacios: si un valor viene como `" QTEK MEXICO"`, se
**muestra** limpio —si no, se ordena antes que todo por su espacio inicial— pero
se **filtra** con el valor original.

### Filtros de fecha

Van como rango `desde` / `hasta` con `<input type="date">`, acotados al mínimo y
máximo que existen en los datos. Una fila **sin esa fecha** no cae en ningún
rango y desaparece al filtrar: eso es correcto —no se puede afirmar que esté
dentro— pero **tiene que verse**, así que el grupo dice cuántas se quedaron
fuera.

Si el tablero tiene dos fechas que contestan preguntas distintas (cuándo entró
vs cuándo vence), van como **dos filtros separados**, no como uno con selector.

### El atributo `hidden` no basta

`hidden` oculta a través de la hoja del navegador, así que **cualquier regla de
autor que ponga `display` se lo come**. `theme.css` ya declara el caso para los
elementos que trae; **si agregas uno que se prenda y apague con `hidden`, tienes
que declararlo también**:

```css
.mi-elemento[hidden] { display: none; }
```

Ya pasó dos veces: el badge se veía con 0 filtros, y el `.empty-state` quedaba
pintado encima de las gráficas aunque sí hubiera datos.

> Y al probarlo, **mide el `display` calculado, no la propiedad `hidden`**. La
> propiedad confirma lo que el código quiso hacer; solo el `display` dice lo que
> el usuario ve.

---

## 6. Tabla de detalle

Todo dashboard lleva una tabla de detalle **al final de la página**, a ancho completo (12 columnas), con el granular de los datos.

**Paginación**
- **10 filas por página**, siempre. Sin scroll infinito.
- Controles al pie: `‹ Anterior · 1 2 3 … n · Siguiente ›` y el rango visible (`Mostrando 1–10 de 1,248`).
- Al cambiar cualquier filtro, regresa a la página 1.

**Ordenamiento**
- **Todos** los encabezados son ordenables por click, con indicador de dirección (▲/▼).
- Ciclo: asc → desc → sin orden.
- Ordena el dataset **completo**, no solo la página visible.
- Shift + click para ordenar por una segunda columna.
- El orden activo se conserva al cambiar de página y al cambiar de idioma.

**Formato**
- Header sticky, fondo `--c-primary`.
- Texto izquierda, números derecha (`.num`), fechas centro (`.date`).
- Totales en `<tfoot>`, en negrita — calculados sobre **todo** el conjunto filtrado, no sobre la página actual.
- Barras de datos en la celda de la medida principal.
- Más de 8 columnas → congelar la primera.

---

## 6 bis. ⛔ Todo número de parte se puede copiar

**** Donde un tablero muestre un número de parte
(SKU, material, item, componente) —tabla, matriz, árbol, tarjeta, tooltip fijo—
va con su botón de copiar **⧉** al lado. Y si el tablero filtra por números de
parte, un botón **"⧉ Copiar números de parte"** copia todos los de la vista, uno
por renglón, para pegarlos directo en la selección múltiple de SAP.

Por qué: el flujo real es "veo el número en el tablero → lo busco en SAP". Sin
el botón, la gente lo selecciona con el mouse, se lleva un espacio o medio texto
de al lado, o el click en el renglón le abre otra cosa.

### Cómo se hace (la versión de Horizontals, que ya funciona)

```css
.pn { user-select: text; cursor: text; }
.pn-copy { border: 0; background: transparent; padding: 0 2px; margin-left: 2px;
  cursor: pointer; color: var(--c-text-muted); font-size: 11px; line-height: 1;
  opacity: .55; vertical-align: baseline; }
.pn-copy:hover { opacity: 1; color: var(--c-primary); }
.pn-copy.is-copied { opacity: 1; color: var(--c-ok); }
```

```js
/* navigator.clipboard solo existe en HTTPS o en localhost. El portal se abre
   por HTTP en la red de la planta: sin el metodo viejo, el boton no hace nada. */
async function copiarTexto(txt) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(txt);
      return true;
    }
  } catch (e) { /* se intenta el metodo viejo */ }
  const ta = document.createElement("textarea");
  ta.value = txt; ta.setAttribute("readonly", "");
  ta.style.position = "fixed"; ta.style.opacity = "0";
  document.body.appendChild(ta); ta.select();
  let ok = false;
  try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
  ta.remove();
  return ok;
}

/* El numero con su boton. El valor pasa por esc() en LOS DOS lugares: viene
   de los datos y entra a un innerHTML. */
const pnHtml = v => (v == null || v === "") ? "–"
  : `<span class="pn">${esc(v)}</span><button type="button" class="pn-copy" data-pn="${
      esc(v)}" title="${esc(t("copy_pn"))}" aria-label="${esc(t("copy_pn"))}">⧉</button>`;

/* En fase de CAPTURA (el `true` del final): corre antes que el click del
   renglon, que expande la fila o pone un filtro cruzado. Asi copiar no dispara
   nada mas, y seleccionar el numero con el mouse tampoco. */
document.addEventListener("click", e => {
  const b = e.target.closest(".pn-copy");
  if (b) {
    e.preventDefault(); e.stopPropagation();
    copiarTexto(b.dataset.pn).then(ok => {
      b.classList.toggle("is-copied", ok);
      b.textContent = ok ? "✓" : "✕";
      b.title = ok ? b.dataset.pn : t("copy_fail");
      setTimeout(() => {
        b.classList.remove("is-copied"); b.textContent = "⧉"; b.title = t("copy_pn");
      }, 1200);
    });
    return;
  }
  if (e.target.closest(".pn") && String(window.getSelection() || "").trim())
    e.stopPropagation();
}, true);
```

Y en el diccionario I18N: `copy_pn` ("Copiar número de parte" / "Copy part number"),
`copy_fail` ("No se pudo copiar" / "Could not copy"), y para el botón de todos
`copy_all` y `copied_all` ("{n} copiados").

### Las reglas

- **Se copia el valor exacto del dato**, no el texto de pantalla: sin espacios,
  sin la descripción, sin "…" de un texto truncado. Por eso va en `data-pn`.
- **El botón da respuesta:** ✓ si copió, ✕ si no. Un botón que no avisa parece
  roto aunque haya funcionado.
- **"Copiar todos" copia lo de la vista con los filtros puestos, sin repetidos**
  (una matriz trae un renglón por planta), uno por renglón.
- **En SVG (gráficas)** el número no lleva botón: va en el tooltip y en la tabla
  de detalle, donde sí se copia. Lo que importa es que exista UN lugar en
  pantalla donde copiarlo.
- **La exportación a CSV y Excel no cambia:** el número va limpio, sin el ⧉.

### Cómo se comprueba

Con el tablero abierto: clic en un ⧉ y pegar en el Bloc de notas. Bien: sale
solo el número, y el renglón no se expandió ni se filtró nada. Mal en silencio:
el portal abierto por IP con HTTP, y el botón sin `copiarTexto` con el método
viejo: en localhost funciona, y en la planta no hace nada.

## 7. Exportación (CSV y Excel)

Ambos botones van **arriba de la tabla de detalle**, alineados a la derecha, dentro de la misma tarjeta:

```html
<div class="card__header">
  <h3 class="card__title" data-i18n="detail">Detalle</h3>
  <div class="export-group">
    <span class="btn-export__count">1,248 filas</span>
    <button class="btn-export" id="btnCsv">⤓ CSV</button>
    <button class="btn-export" id="btnXlsx">⤓ Excel</button>
  </div>
</div>
```

Reglas comunes:
- Exportan **el dataset completo filtrado**, no solo las 10 filas visibles.
- Respetan el orden activo de la tabla.
- Encabezados con el nombre de negocio, en el idioma activo.
- Números sin formato de presentación (sin `$`, sin `K`/`M`, sin separador de miles) para que Excel los lea como números. Fechas en `YYYY-MM-DD`.
- Nombre del archivo: `{nombre-dashboard}_{YYYYMMDD-HHmm}.{csv|xlsx}`.

### ⛔ El export NO pasa por tu formateador de pantalla, y por eso miente

El export metía el valor **crudo** en la celda:

```js
o[t(c.label)] = c.type === "date" ? String(r[c.field]).slice(0,10) : r[c.field];
```

`customer` y `plant` son **arrays** —un material surte a varios clientes desde
varias plantas—. Medido sobre 2,640 filas:

| | qué pasaba |
|---|---|
| **Excel** | SheetJS no serializa un array: celda **vacía SIEMPRE**, también en las 1,860 filas que sí traían cliente |
| **CSV** | `String(["A","B"])` daba `"A,B"` —sin el espacio de la pantalla— y un array vacío daba blanco en 780 filas |

En Excel se perdía entero; en CSV a medias. Por eso se reportó como "a veces sí".

> **El export usa el MISMO formateador que la pantalla, o uno propio que cubra
> todos los tipos.** Un `if` para fechas y el valor crudo para todo lo demás
> funciona hasta el día que una columna deja de ser escalar.

La única diferencia deliberada es la ausencia: en pantalla es un guion, en el
archivo es la **celda vacía**. Un `–` en una hoja de cálculo es texto que nadie
puede sumar ni filtrar.

**Cómo se comprueba antes de que lo reporte alguien:** los tipos de la primera
fila exportada.

```js
Object.entries(exportRows()[0]).map(([k,v]) => [k, Array.isArray(v) ? "ARRAY" : typeof v])
```

Cualquier cosa que no sea `string` o `number` va a salir mal en Excel.

### ⛔ Y ponle nombre propio a cada tabla

`Detail` no dice nada, y un tablero con tres tablas de detalle baja tres archivos
casi con el mismo nombre. Nombra la tabla por su granularidad —"MRP balance by
material, plant and day"— y mete ese mismo nombre en el archivo descargado.

Específicos:
- **CSV** — UTF-8 **con BOM** (`\uFEFF` al inicio). Sin el BOM, Excel rompe los acentos y la ñ.
- **Excel** — con SheetJS (`xlsx`). Header en negrita con fondo `--c-primary`, panel congelado en la fila 1, autofiltro activado, anchos de columna ajustados al contenido. Una segunda hoja llamada `Metadata` con: fecha de generación, filtros aplicados, fechas de las fuentes y conteo de filas.

---

## 8. Frescura de los datos

**Tres relojes distintos, y confundirlos es el error más caro de esta lista.**

| Indicador | Qué contesta | De dónde sale |
|---|---|---|
| **Extraído el** | ¿los datos son de hoy? | la fecha del **nombre del archivo** |
| **Actualizado** | ¿corrió el proceso? | cuándo se escribió la tabla / corrió el job |
| **Datos al** | ¿hasta cuándo llegan los registros? | el máximo de la fecha de negocio |

**El que manda es "Extraído el"**, y es el que va con semáforo.

### De dónde sale, según el tipo de fuente

Hay **tres casos, y no se parecen**. Identifica cuál es cada fuente antes de
escribir nada:

**a) La fuente es un archivo** → la fecha va en el **nombre**. Cada sistema usa
su propio patrón; no lo generalices:

```
MMDnnn_USALL_ZMMMD04_2026-07-02_06-05-58.txt   YYYY-MM-DD
SDDnnn_..._2026-08-13_12-56-13AM.csv           YYYY-MM-DD + AM/PM
COOIS_Headers_08.13.2026.xlsx                  MM.DD.YYYY
```

**b) La fuente es una consulta a una base o una API** → no hay nombre de archivo
que valga. La fecha tiene que ir en un **metadato que escriba el cargador**, en
una columna suya, en el momento de la extracción.

```
ZMM (archivo)   ->  EXECUTION_DATE   sacado del nombre
PGI (API)       ->  fecha_reporte    escrito por el cargador
```

**c) La fuente parece un catálogo** → la pregunta no es dónde está su fecha,
es **si de verdad no tiene**.

Un catálogo va sin fecha **solo si nada lo escribe**: una lista de motivos de
rechazo que alguien subió una vez y no se toca. Si un proceso lo actualiza —un
dataflow, un notebook, un copy job— entonces **tiene fecha, y esa fecha se puede
caer**. Que el contenido cambie poco no lo hace estático.

No lo adivines por el nombre ni porque "es un catálogo". Pregúntaselo a la tabla:

```sql
DESCRIBE HISTORY <tabla>
```

Si salen versiones con timestamps distintos, **algo la escribe y no es un
catálogo**. `DESCRIBE DETAIL` te da el `lastModified`, que es la fecha que va al
contrato.

>
> Salió cuando alguien preguntó "¿de dónde sale esta lista?", no cuando falló.
> Un `DESCRIBE HISTORY` de treinta segundos, el día que se escribió el contrato,
> lo habría evitado.

En los tres casos, **léela de la tabla, no del origen.** La carpeta dice qué se
*descargó*; la tabla dice qué se *cargó*. Si la descarga trae el archivo de hoy
pero la carga falla, mirar la carpeta reporta "fresco" y es mentira.

### ⛔ Si no sabes de dónde sale esa fecha, PREGUNTA

No la deduzcas. Estas son las tres salidas fáciles y las tres están mal:

| Atajo | Por qué está mal |
|---|---|
| Usar la fecha de hoy | inventa frescura que no existe |
| Usar el `modifyTime` del archivo | el job que copia reescribe todo con el mismo timestamp |
| Usar una columna de fecha del negocio | *emisión*, *vencimiento*, *pago*, *arribo* hablan del dato, no de la extracción — una factura que vence el año que viene haría decir "datos al 2027" |
| Declararla catálogo para no buscarla | apaga la alarma en vez de resolverla: una fuente sin fecha **nunca** se ve vieja, aunque lleve meses caída |

Antes de escoger una columna, **pregunta qué significa**. Ya pasó: se tomó
`Fecha_Carga` creyendo que era la carga a la tabla, y era **cuándo el proveedor
subió la factura al portal**. Nada que ver.

Y antes de inventar un campo nuevo, **revisa si el cargador ya lo escribe**.
También pasó: `fecha_reporte` llevaba años en las tablas de PGI, documentada en
un comentario, y se construyó un rodeo para calcular lo mismo, peor.

Si de plano no existe el dato, **la fuente sale sin fecha y marcada** — y se
levanta como pendiente que el cargador la escriba. Nunca se rellena.

### Por qué las tres, y no una

**Que "Extraído el" y "Actualizado" se separen es la alarma.** Si el proceso de
origen deja de entregar archivos, la carga sigue corriendo todos los días sobre
el mismo archivo viejo: la tabla se reescribe, el pipeline sale verde, y el
tablero jura que está fresco.

```
ZMM_MD04    Extraído el: 2026-08-11    Actualizado: 
                        ↑ el archivo es de hace 3 días
```

Con un solo reloj eso es invisible. Es la falla silenciosa clásica: nada truena,
solo se queda viejo.

**Se toma la fuente más vieja, no la más reciente** — es la que define qué tan
confiable es el conjunto.

### El detalle por fuente es obligatorio

No basta con una fecha global. **Cada fuente lleva la suya**, y se ve en dos
lugares:

1. **Tooltip** al pasar el mouse sobre el indicador — el desglose completo, sin
   abrir nada.
2. **Tabla en el panel de documentación**, con una fila por fuente:
   `Fuente · Sistema · Tabla · Extraído el · Actualizado · Datos al · Filas`.

⛔ **Nunca repartas la misma fecha entre varias fuentes.** Es peor que no mostrar
nada: parece información y no lo es. Si una fuente no tiene fecha propia, va
vacía o marcada como catálogo — nunca prestada de otra.

Una fuente que **no existe** se declara igual, marcada en rojo. Que falte tiene
que verse en el tablero, no desaparecer de la lista.

**Cómo se hace.** El indicador es un `<span class="freshness" id="metaFreshness">`
y su `title` se arma con `META.fuentes.map(...)`, una línea por fuente: nombre,
extraído y días, datos al, y las marcas de catálogo o FALTA. El boilerplate ya lo
trae (`renderFreshness`); el molde más completo del portal es Canada
(`<tablero>/index.html`, `renderFrescura`). Las páginas que no tienen
`meta.json` (ACE, DataStage) usan `pintarFechaDato(id, fecha, prefijo, antes,
detalle)` de `/shared/js/fecha-dato.js`, con `detalle = [{nombre, fecha}, ...]`.

### Cuando una tabla se alimenta de varios archivos

Se toma **el más viejo**. Las facturas vienen de cinco reportes, uno por
estatus; si el estatus 5 se quedó de ayer, la tabla reporta ayer. Una tabla no
está más fresca que el peor de sus reportes.

- Semáforo sobre "Datos al", con umbral **configurable por dashboard**:

```js
const FRESHNESS = { warnDays: 1, criticalDays: 3 };  // ajustar por dashboard
```

  Dentro del umbral → `--c-ok`. Pasando `warnDays` → `--c-warn`. Pasando `criticalDays` → `--c-critical` + ícono de advertencia.
- Hover sobre "Datos al" → tooltip con el desglose fuente por fuente y su antigüedad en días.
- El desglose completo vive en el panel de documentación.
- Si los datos vienen de API o consulta directa en vivo, se muestra solo "Actualizado" y se omite "Datos al".

---

## 9. Panel de documentación

Botón **📖 Documentación** al final de la página, junto al footer. Abre un panel lateral derecho (o modal en pantallas chicas) con:

1. **Propósito** — qué responde este dashboard y para quién.
2. **Fuentes de datos** — tabla con: nombre de la fuente, sistema de origen (SAP, Fabric, SharePoint, archivo manual), ruta o tabla, frecuencia de actualización y fecha del último corte.
3. **Transformaciones** — qué se limpió, unió, filtró o derivó entre el origen y lo que se ve.
4. **Diccionario de medidas** — cada KPI y cada visual con su definición y fórmula (es la versión larga de los ⓘ).
5. **Reglas de negocio** — exclusiones, criterios de asignación, tipos de cambio, redondeos.
6. **Limitaciones conocidas** — qué NO cubre este dashboard, para evitar malinterpretaciones.
7. **Contacto** — equipo de BI + fecha de última revisión del documento.

Todo el contenido sale de `CONFIG.documentation`, bilingüe si aplica. Se escribe pensando en quien retome esto en un año sin contexto.

---

## 10. Encabezado, navegación y pie de página

**Encabezado** (de izquierda a derecha):
`[← Back to the Portal] · Título del dashboard · chips de filtros activos · Actualizado / Datos al · [ES|EN]`

- **Back to the Portal** siempre presente, primer elemento, con flecha izquierda.
  Lleva al portal de **su departamento** (Trade Compliance, Logistics o S&OP).
  La URL va en `CONFIG.portalUrl`, **nunca hardcodeada en el HTML**:
  ```js
  const PORTAL_URL = "/logistics/";   // "/trade-compliance/", "/logistics/" o "/sop/"; nunca una URL completa
  ```
- **Se tiene que ver aunque se colapse el menú lateral.** Si el botón vive dentro
  de un sidebar que se colapsa a ancho 0, desaparece con él. El script compartido
  `/shared/js/back-to-portal.js` ya lo resuelve: con `.sidebar.collapsed` lo pone
  flotando abajo a la izquierda, y elige el portal por la carpeta del tablero.
- Si hay pestañas, van debajo del encabezado, y el toggle de idioma se repite en cada una.

**Pie de página** — siempre, en todos los dashboards:

```
equipo de BI · la empresa
Fuente: {fuentes} · Actualizado: {fecha} · [📖 Documentación]
```

---

## 11. Layout

```
┌──────────────────────────────────────────────────┐
│ ← Portal │ Título │ chips │ Actualizado │ ES|EN  │
├────┬─────────────────────────────────────────────┤
│ ▤  │ Fila KPI (máx 5)                            │
│ f  ├─────────────────────────────────────────────┤
│ i  │ Grid 12 columnas · cada visual en .card ⓘ  │
│ l  ├─────────────────────────────────────────────┤
│ t  │ Tabla de detalle (10 filas, paginada)       │
│ ▸  │   [1,248 filas] [⤓CSV] [⤓Excel]            │
├────┴─────────────────────────────────────────────┤
│ equipo de BI · Actualizado · 📖 Documentación│
└──────────────────────────────────────────────────┘
```

- Grid de 12 columnas, gap `--grid-gap`.
- Cada visual en un `.card` con título arriba a la izquierda y ⓘ arriba a la derecha.
- Títulos en lenguaje de negocio: "Fletes extraordinarios por planta", no "Suma de Costo".
- KPIs con valor, etiqueta y variación vs. periodo anterior (flecha + % en color de semáforo).
- Se debe ver correcto en 1366×768.

---

## 12. Data labels y formato de números

**Data labels: visibles siempre que sea posible.** Activados por defecto en todo tipo de gráfica. Ocultarlos requiere una razón concreta.

Cuando el espacio no alcanza, intentar en este orden antes de ocultar:
1. Abreviar el valor (`1.2M` en vez de `1,234,567`)
2. Sacar el label fuera de la barra
3. Reducir a 10px mínimo
4. En líneas saturadas: solo primer punto, último, máximo y mínimo
5. En pie/dona: labels afuera con línea guía

Solo entonces, si aún se traslapan, ocultar el de menor valor. **Nunca rotarlos en diagonal.**
El label del elemento bajo el cursor siempre se muestra completo y por encima.

Formato:
- Miles con coma, decimales con punto.
- Abreviaturas: `1.2K`, `3.4M`, `1.1B`. Los ejes siempre abreviados.
- Porcentajes con 1 decimal.
- Moneda con prefijo `$` y sufijo de divisa cuando conviven monedas (`$1.2M USD`).
- Negativos entre paréntesis, clase `.neg`.
- Nulos como `–`. Nunca `0`, `null` ni vacío.
- `font-variant-numeric: tabular-nums` en tablas.

---

## 13. El contrato de datos — antes de escribir la transformación

**El orden correcto es al revés del intuitivo.** Primero se define el archivo que
el tablero necesita, se escribe **a mano con datos inventados**, y se construye
el tablero contra él, en local. Hasta entonces se toca el pipeline.

Ventaja: el tablero existe y se ve funcionando antes de tocar Fabric. Y cuando
llegue el dato real, si no encaja, el problema está en un solo lugar.

### `meta.json` es obligatorio

Todo tablero de archivos estáticos lleva un `meta.json` con, mínimo:

```json
{
  "generated_at": "",
  "fuente": "Fabric · nombre_del_notebook_que_lo_produjo",
  "counts":  { "...": 0 },
  "filters": { "categorias": [...], "plantas": [...] },
  "fuentes": [
    { "nombre": "ZMM_MD04 · órdenes abiertas", "nombre_en": "...",
      "sistema": "SAP", "tabla": "sap_zmm_md04_vigente",
      "extraido_el": "2026-08-14",        // del NOMBRE del archivo
      "actualizado": "",  // cuándo se escribió la tabla
      "dato_al":     "2026-08-13",        // la fecha de negocio más reciente
      "filas": 6090, "falta": false }
  ],
  "pestanas_sin_actualizar": {}
}
```

- `generated_at` alimenta "Actualizado"; **`fuentes` es obligatorio** y alimenta
  todo lo de la sección 8. Una entrada por fuente, siempre — incluidas las que
  faltan, con `falta: true`.
- `fuente` dice **qué notebook** lo produjo. Quien retome esto en un año empieza ahí.
- `pestanas_sin_actualizar` vacío = todo bien. Con contenido, dispara el aviso.

### Nada de listas duras en el HTML

Las categorías, su **orden**, sus **colores** y los nombres de los filtros salen
de `meta`, no de un array escrito en el script. Y la lógica se ancla a un **rol
estable**, nunca al texto visible:

```js
// mal: se rompe cuando alguien renombra la categoría
if (fila.cubeta === "LA · con factura") { ... }

// bien: el texto puede cambiar, el rol no
if (CUB.rolDe[fila.cubeta] === "con_factura") { ... }
```

Si mañana el área agrega una categoría, aparece sola. Con la lista dura, la
categoría nueva simplemente **no se ve** — y eso no da error en ningún lado.

### Los filtros de negocio viven en el tablero, no en el pipeline

Excluir proveedores, materiales o plantas dentro del notebook esconde la
decisión donde nadie la va a encontrar. Va como filtro visible en el panel,
prendido por default si conviene, pero **apagable**.

---

## 13 bis. ⛔ Declararlo en una capa no es que llegue a la otra

**Tres veces en un día, el mismo error con tres caras.** Ninguna dio
error en consola; las tres se encontraron midiendo el resultado pintado.

**1. El campo publicado que nunca llegó a la fila.** Se publicó `originGroup` en
cada SKU y se declaró la dimensión en `meta`. El panel pintó sus nueve valores
perfectamente… y `buildRows` no copiaba el campo a la fila. Filtrar por `EMBR`
daba **cero filas** y `Unassigned` devolvía **el universo entero**.

**2. La llave que no casaba por una mayúscula.** El publicador escribía
`skus_sin_originGroup` y el tablero buscaba `skus_sin_origingroup`. Resultado: la
opción `Unassigned` **no aparecía**, y esos materiales —la mayoría— quedaban
inalcanzables por cualquier filtro.

**3. La propiedad que se cayó en un `map`.** `meta` declaraba `colapsado: true` y
el panel lo ignoraba, porque el código armaba sus grupos así:

```js
DIMS().map(d => ({ rol: d.rol, label: d.label, opciones: … }))
```

Ese `map` **reconstruye** el objeto con los campos que nombra. Cualquier
propiedad nueva de la dimensión se pierde ahí, en silencio.

### Las reglas

> **Un campo nuevo cruza TRES capas, y hay que tocarlas las tres:** lo escribe el
> publicador, lo declara `meta`, y **lo copia la fila** que el filtro compara.
> Saltarse la tercera no rompe nada visible: el filtro se pinta lleno y no
> encuentra nada.

> **Desconfía de todo `map` que reconstruya un objeto campo por campo.** Es un
> punto de fuga silencioso. Si el objeto viene del contrato de datos, propaga lo
> que no conoces (`...d`) o nombra explícitamente lo nuevo.

> **Una llave que se arma en un lado y se lee en otro se normaliza en los dos.**
> `skus_sin_${rol.toLowerCase()}` sirve de nada si quien la escribe usa el rol
> tal cual. Normaliza al escribir, no solo al leer.

### Cómo se cazan, y cuesta un minuto

No basta con abrir el tablero y ver el filtro ahí. **Márcalo y cuenta filas:**

```js
// el filtro pinta valores, pero ¿alguna fila los tiene?
rawData.filter(r => r.miCampoNuevo).length        // 0 = nunca llegó a la fila
new Set(rawData.map(r => r.miCampoNuevo)).size    // 1 = todas nulas
```

Un filtro que se pinta bien y devuelve cero es indistinguible de uno que filtra
bien y no hay datos. La única diferencia está en el conteo.

## 13 ter. ⛔ Un guardia con una sola cota no detecta que la MÉTRICA esté rota

Era imposible: se había medido a mano que el cruce daba 77%. La métrica estaba
mal:

```python
cruzadas = salida.filter(F.col("qty_107").isNotNull()).count()   # ⛔
```

`qty_107` ya venía de un `coalesce(col, 0.0)`, así que **nunca era nula**. Se
estaban contando filas que tienen un valor, no filas que cruzaron. Y el guardia
del 40% no iba a dispararse jamás: **una red que no atrapa nada.**

### Las dos reglas

> **No midas sobre una columna que ya pasó por `coalesce`, `fillna` o un
> `otherwise` con default.** Deja de distinguir "no había dato" de "el dato es
> cero", que es justo lo que la métrica pregunta. Guarda un flag explícito
> tomado del valor CRUDO, antes de rellenar:
> `.withColumn("cruzo", F.col("origen_col").isNotNull())`

> **Cuando conozcas el rango esperado, acota por los DOS lados.** Un resultado
> *demasiado bueno* es tan sospechoso como uno malo, y es la única forma de que
> el guardia detecte que se rompió la métrica y no el dato:

```python
if pct < 0.40:  errores.append("el cruce se desplomó, revisa la llave")
if pct > 0.99:  errores.append("100% es demasiado bueno; revisa que la métrica "
                               "no mire una columna que nunca es nula")
```

Es el mismo error de la § 13 bis por otra puerta: **un filtro que se pinta lleno
y devuelve cero se ve igual que uno correcto**, y una métrica que siempre da
100% se ve igual que un cruce perfecto. Solo el conteo los distingue.

---

## 14. Ningún default silencioso, y el modo degradado

**Si falta un dato, el resultado es nulo y se cuenta aparte.** Nunca un valor
"razonable".

Asumir un factor de conversión de 1 mantuvo un tablero **458× inflado durante
dos años**, porque los números se veían creíbles. Un total incompleto y marcado
es honesto; un total completo y equivocado es una decisión mal tomada.

- Falta el factor → la medida sale nula y la fila entra en un conteo
  `filas_sin_medida` que el tablero muestra.
- Falta una categoría → no se inventa "Otros" ni "Desconocido": o la regla
  clasifica a todos, o la excepción está escrita por nombre.

### La banda de aviso

Cuando el tablero puede dibujar pero **no con todo**, se dice arriba del
encabezado, en una banda a ancho completo. Nunca un `console.warn`: nadie abre
la consola.

| Situación | Color | Texto |
|---|---|---|
| Faltó `meta.cubetas` / la estructura misma | `--c-critical` | qué se perdió y qué sigue siendo confiable |
| Una pestaña no se actualizó hoy | `--c-warn` | cuál, y de cuándo son sus datos |
| Todo bien | *no se pinta nada* | — |

La banda dice **qué se perdió y qué sí es confiable**, no solo "hubo un error".
Y el tablero **sigue dibujando** con lo que tenga: degradado y avisado le gana a
pantalla en blanco.

### El caché es parte del problema

Un tablero que muestra "Actualizado: hoy" con datos de ayer es peor que uno
caído. Los JSON se sirven con:

```
Cache-Control: no-cache
ETag: <sello de generated_at>
```

`no-cache` no significa "no guardes", significa "revalida siempre". El navegador
conserva la copia y el servidor responde `304` si no cambió — rápido y correcto.
**Sin esto, el usuario ve datos viejos y el tablero le jura que están frescos.**

---

## 15. La última milla es la única validación que cuenta

La pregunta no es *"¿la tabla quedó bien?"* sino **"¿lo que ve el usuario está al
día?"**. Son capas distintas y pueden estar en desacuerdo días enteros.

```
/api/<tablero>/meta.json  →  ¿generated_at es de hoy?
```

Todo lo demás —el pipeline en verde, la tabla con el conteo correcto, los
archivos en el storage— sirve para saber **dónde** se rompió, no **si** se rompió.

Y de eso sale la regla operativa: **el paso que publica tiene que poder fallar en
rojo.** Si la publicación vive dentro del proceso que calcula, una credencial
mala deja los archivos a medio camino y el pipeline reporta éxito. Que la
publicación sea su propia actividad, con su propia conexión, es lo que convierte
una falla silenciosa en una falla visible.

Y la misma pregunta va **antes** de mergear, no solo después de desplegar:
ningún cambio a un notebook que ya publica se mergea sin haberlo corrido una vez
completo y sin haber mirado el `generated_at` que dejó. El detalle, con el caso
que nos costó un día de datos viejos, en `fabric-sap-ingesta` § 7 quinquies.

### 15 bis. Publicar al Blob NO es publicar el tablero

> **Historia corta:** el Blob viejo (`dashboard-data`, con llave) se
> apagó y el portal pasó a un servidor local que lee `<carpeta-portal>`. **> el portal vive otra vez en Azure** (App Service `<app-service-portal>`), y lee del Storage
> `<storage-portal>`, contenedor `portal-data`, **sin llaves**. Mientras el servidor local
> siga en uso, cada pipeline publica a los dos (sección 16). Lo que sigue explica las
> cinco piezas del portal y sigue valiendo; donde diga `dashboard-data` léase
> `portal-data`. **Qué revisa IT y qué no puede llevar el código está en
> `portal-seguridad`**, que va junto con esta al armar cualquier tablero.

El portal es una app **Flask** (`<org>/<repo-portal>`, `app.py`). Los archivos
del Blob no se sirven solos: cada tablero necesita sus **tres rutas dadas de
alta a mano**. Sin eso, el pipeline sale verde, el `dataWritten` cuadra al byte,
los JSON están en `dashboard-data/<tablero>/` — y `/api/<tablero>/meta.json`
contesta **404**. 

Un tablero nuevo son cinco cosas en el portal, ninguna opcional:

| | |
|---|---|
| `<tablero>/index.html` | el HTML, servido de disco. La carpeta se llama **exactamente** como la dirección `/<tablero>/` |
| `<tablero>/data/dashboard/*.json` | el **contrato** (datos inventados), la caída a disco |
| `<TABLERO>_ARCHIVOS` + los dos lectores | lista blanca y `_leer_blob_*` con el prefijo del contenedor |
| Las tres rutas | `/<tablero>/`, `/api/<tablero>/<nombre>`, `/<tablero>/<path>` |
| La tarjeta en `index.html` del portal | si no, existe pero nadie llega |

⛔ **La dirección y la carpeta se llaman igual.** `/openorder/` vivía en `<tablero>/dashboard/`: con Flask en local abría bien, y en el servidor de IT `/openorder/` dio **404** y solo abría la ruta de la carpeta. Un tablero cuya dirección no coincide con su carpeta se ve bien en local y truena al desplegar. Nada de subcarpetas tipo `<algo>/dashboard/`: el HTML va en `<tablero>/index.html` y el contrato en `<tablero>/data/dashboard/`. La prueba `test_cada_tablero_vive_en_la_carpeta_de_su_direccion` del portal lo detiene; si la quitas o la saltas, el error vuelve.

Y en el tablero, `CONFIG.dataUrls = ["/api/<tablero>/", "./"]` — el portal
primero, `./` para abrir el HTML suelto en local. Un `fetch("./meta.json")`
pelado funciona en la carpeta del proyecto y da 404 en el portal.

**Copia el bloque de tablero B, no el del tablero A.** El primero usa
el lector **sellado** (ETag desde `meta.json`, cache por contenido); el segundo
hace `jsonify` del archivo completo en cada petición. Con un JSON de 3 MB eso es
parsear y re-serializar megabytes para devolver los mismos bytes.

⛔ **La lista blanca no es decorativa.** El nombre llega por la URL: sin ella un
`/api/<tablero>/../../.env` sale por la puerta. Compruébalo — tiene que dar 404.

**Cómo se verifica antes de mergear**, con el portal corriendo en local
(`PORT=5177 python app.py`, que lee el `.env` y pega al Blob de verdad):

```
curl -s -D - -o m.json http://localhost:5177/api/<tablero>/meta.json   # 200 + ETag
curl -s http://localhost:5177/api/data-source                          # last_source: blob
curl -o /dev/null -w "%{http_code}" ".../api/<tablero>/../../.env"     # 404
```

Que la suma de los `size_download` cuadre con el `dataWritten` de la actividad
Copy es la prueba de punta a punta: los mismos bytes que salieron de OneLake son
los que le llegan al navegador. Y con `AZURE_BLOB_CONNECTION_STRING=` vacío se
prueba la caída a disco, que es lo que la gente ve el día que el Blob falle.

---

## 13 quater. Un catálogo no manda en el semáforo

Hay fuentes que no son el dato: son **catálogos** —el Material Master con la
unidad base, una tabla de tipos de cambio, un mapa de plantas—. Aportan una
columna que casi nunca cambia.

Si el semáforo las trata igual que a las transaccionales, un catálogo olvidado
pinta el tablero de rojo y pone **"Datos"** cuando el dato es de
**hoy**. El tablero miente sobre su propia frescura, y una banda roja permanente
deja de leerse a la semana — justo cuando haga falta que alguien la lea.

La fuente se declara `"catalogo": true` en su entrada de `meta.fuentes`, y el
tablero:

- **no la usa** para el `Datos al` del encabezado, que sale de las
  transaccionales (si solo hubiera catálogos, se usan esos: una fecha mala es
  mejor que ninguna);
- **la topa en amarillo**, nunca en rojo — salvo `falta: true`, que sí es rojo
  porque entonces no hay con qué resolver la columna;
- **la deja en la lista de fuentes** con su fecha y su atraso, y la banda dice
  cuál es catálogo.

⛔ No es esconderla. Una fuente que desaparece del semáforo se pudre sin que
nadie lo note; lo que se quita es que **hable por las demás**.

---

## 16. Ninguna credencial dentro de un notebook. Ninguna.

> **el portal vive en Azure** y lee sus datos del Storage
> `<storage-portal>` (contenedor `portal-data`). Mientras el servidor local siga
> en uso, cada pipeline publica a **los dos**: `<carpeta-portal>` por el gateway y
> Azure con la Workspace identity. Ninguno de los dos lleva llave.

⛔ **El notebook nunca sube nada a un storage.** Escribe su resultado en OneLake
y ahí termina. De publicarlo se encargan actividades **Copy** al final del
pipeline, apuntando a **conexiones de Fabric**.

```
notebook  →  Files/dashboard/<tablero>/     (OneLake, sin credencial)
             │
             ├─ Copy "Publicar a PORTAL-BI"            →  <carpeta-portal>/<tablero>   (gateway)
             └─ Copy "Publicar a Azure (portal-data)"  →  portal-data/<tablero>   (Workspace identity)
```

Las dos Copy cuelgan del **mismo** notebook, con *On success*, y corren en
paralelo. **Sin la de Azure, el tablero no tiene datos en el portal nuevo**,
aunque el pipeline salga verde.

> **Es una actividad `Copy` del pipeline, no un `Copy Job`.** El *Copy Job* es
> un item aparte de Fabric, con su propio calendario, y se usa para traer
> archivos de un origen externo (un share on-prem, por ejemplo). Publicar la
> salida de un notebook es una actividad dentro del mismo pipeline.

### El molde: `<pipeline de referencia>`

En el repo `<org>/<repo-fabric>` (rama base **`fabric`**), workspace
**BI Team**. Ya trae las dos Copy funcionando. Se clona su actividad y
cambian dos cosas: la carpeta de origen (`dashboard/<tablero>`) y la de destino
(`<tablero>`, igual al nombre de la carpeta del tablero en el portal).

Las conexiones del workspace BI Team — son **identificadores, no
secretos**:

| | GUID |
|---|---|
| Lakehouse `<lakehouse>` (conexión) | `<GUID>` |
| `artifactId` del lakehouse | `<GUID>` |
| Azure Storage `<storage-portal>-portal-data` (Workspace identity) | `<GUID>` |

La de Azure **no lleva llave**: entra con la identidad del workspace, que tiene
el rol *Storage Blob Data Contributor* sobre el Storage, y el Storage la deja
pasar por *trusted workspace access*. No se marca la casilla de gateways.

```jsonc
{
 "name": "Publicar a Azure (portal-data)",
 "type": "Copy",
 "dependsOn": [{ "activity": "<el notebook que escribe>",
                 "dependencyConditions": ["Succeeded"] }],
 "policy": { "timeout": "0.12:00:00", "retry": 0, "retryIntervalInSeconds": 30,
             "secureInput": false, "secureOutput": false },
 "typeProperties": {
  "source": {
   "type": "BinarySource",
   "formatSettings": { "type": "BinaryReadSettings" },
   // `AzureBlobStorageReadSettings` aunque el origen sea el lakehouse: OneLake
   // esta respaldado por blob y Fabric lo escribe asi. No lo "corrijas".
   "storeSettings": { "type": "AzureBlobStorageReadSettings",
                      "recursive": true, "wildcardFileName": "*.json" },
   "datasetSettings": {
    "type": "Binary",
    "typeProperties": { "location": { "type": "LakehouseLocation",
                                      "folderPath": "dashboard/<tablero>" } },
    "connectionSettings": {
     "name": "<lakehouse>",
     "properties": {
      "type": "Lakehouse",
      "typeProperties": { "artifactId": "<GUID>",
                          "workspaceId": "<GUID>",
                          "rootFolder": "Files" },
      "externalReferences": { "connection": "<GUID>" },
      "annotations": [] } },
    "annotations": [] } },
  "sink": {
   "type": "BinarySink",
   "storeSettings": { "type": "AzureBlobStorageWriteSettings" },
   "datasetSettings": {
    "type": "Binary",
    // Sin `fileName`: conserva los nombres de archivo.
    "typeProperties": { "location": { "type": "AzureBlobStorageLocation",
                                      "container": "portal-data",
                                      "folderPath": "<tablero>" } },
    "externalReferences": { "connection": "<GUID>" },
    "annotations": [] } },
  "enableStaging": false
 }
}
```

Tres detalles que importan, en las dos Copy:

- **`Binary`, nunca `DelimitedText`.** Binary copia byte por byte y conserva el
  nombre. DelimitedText *parsea y reescribe* el archivo — un JSON pasado por ahí
  se corrompe.
- **Sin nombre de archivo en el destino.** Si le pones uno, renombra todo a ese
  nombre en vez de conservar los nombres de archivo.
- **Pon el wildcard `*.json` aunque la carpeta solo tenga JSONs.** Sin él se
  publica lo que sea que aparezca ahí — un archivo de prueba que alguien dejó,
  un `.crc` — y nadie se entera.

### Cómo se comprueba

| | Bien | Mal en silencio |
|---|---|---|
| La corrida | *Publicar a Azure (portal-data)* sale verde, con **Run start de hoy** | ves el Output de una corrida vieja: el panel muestra la última que encontró |
| El portal en Azure | el tablero abre con la fecha de hoy y **sin** el aviso de "copia del repo" | el pipeline salió verde pero el tablero sigue vacío: falta la Copy de Azure, o va a otra carpeta que la del tablero |

> **Para buscar un molde en el repo, baja la rama completa de un jalón:**
> `gh api repos/<owner>/<repo>/tarball/<rama> > repo.tar.gz` y busca en local.
> Pedir los archivos uno por uno con `gh api contents/...` sobre un repo de
> Fabric son cientos de llamadas y se queda colgado.

### Las tres razones, en orden de importancia

**1. La integración con Git publica los Base parameters en texto plano.**
Comprobado en un workspace de prueba con una cuenta desechable: Fabric escribe
el **valor** al repositorio. Las conexiones no — solo guardan a cuál apuntar:

```
Base parameter  ->  "value": "VALOR-DE-PRUEBA-NO-ES-UN-SECRETO-123"
Conexión        ->  "connection": "<GUID>"
```

Un notebook con la llave adentro **impide conectar el workspace a Git**, o peor,
la filtra sin que nadie lo note.

**2. El Copy falla en rojo; el notebook no.** Con la subida dentro del notebook,
una credencial mala deja los JSON en OneLake y el pipeline sigue verde. Así
estuvo un tablero dos días sirviendo datos viejos.

**3. Rotar la llave deja de ser un proyecto.** Cada notebook con la llave adentro
es un lugar más que actualizar, y ninguno avisa cuando se queda con la vieja.

### Cómo rotar una llave sin tumbar nada

Azure da **dos llaves** por cuenta justo para esto:

1. Ver cuál está en uso.
2. **Regenerar la otra** — la que nadie usa. No se cae nada.
3. Mover todos los consumidores a la nueva.
4. Comprobar uno por uno.
5. **Hasta entonces**, regenerar la expuesta.
6. Vigilar 24 h: un consumidor que no estaba en la lista se cae **aquí**, no antes.

Regenerar la que está en uso tumba todo hasta que termines de actualizar.

> Al copiar una llave o una cadena de conexión, usa **el ícono de copiar**, nunca
> selección con el mouse. Se copia cortada, y el error que sale después
> (`AuthenticationFailed`) no menciona que esté incompleta. Ya pasó dos veces.

---

## 17. El correo programado — un tablero que llega solo

Un tablero espera a que alguien lo abra. Un correo llega. Cuando el dato tiene
dueño y acción —"a este cliente hay que asignarle un OM", "esto se vence el
viernes"— el correo es lo que hace que se atienda.

Se arma con **dos items** y ninguno de los dos manda solo:

```
notebook  →  arma el HTML y lo devuelve por notebook.exit()
pipeline  →  lo manda con una actividad Office365Email
```

Referencia viva: `<tablero>_04_correo_diario` + `<pipeline de correo>`, y el
que lo precedió, `<tablero>_04_correo_semanal` + `<pipeline de correo>`.

El notebook termina así, y el pipeline lee las tres llaves:

```python
notebookutils.notebook.exit(json.dumps(
    {"asunto": asunto, "html": html, "para": PARA}, ensure_ascii=False))
```

```json
"to":      "@json(activity('Armar el correo').output.result.exitValue).para",
"subject": "@json(activity('Armar el correo').output.result.exitValue).asunto",
"body":    "@json(activity('Armar el correo').output.result.exitValue).html"
```

### Los destinatarios van en el NOTEBOOK

```python
DESTINATARIOS = [
    "persona@example.com",
    "persona@example.com",
]
PARA = ";".join(DESTINATARIOS)
```

En el pipeline se pueden escribir, y es peor: hay que abrir el item en Fabric
para saber quién lo recibe, y no queda rastro de cuándo cambió. En el notebook
la lista viaja con el código, entra por PR y el diff enseña **un renglón por
persona** — por eso una lista y no una cadena con `;`, donde sumar un correo se
ve como un cambio ilegible.

### ⛔ Outlook no es un navegador

**Es el motor de Word.** Ignora hojas de estilo, `flex`, `grid`, el `padding` de
un enlace, `height` sobre un `<div>` y `background` en CSS. Nada truena: el
correo se ve bien en Gmail y llega deformado a la mitad de la empresa.

Lo que **sí** respeta son los atributos de HTML de toda la vida:

| Se quiere | ⛔ No | ✅ Sí |
|---|---|---|
| Una barra vertical | `<div style="background:#D0433C;height:87px">` | `<tr height="87"><td height="87" bgcolor="#D0433C"></td></tr>` |
| Una barra horizontal | `<td style="background:#D0433C;width:60%">` | `<td width="60%" bgcolor="#D0433C">` |
| Un botón | `<a style="padding:11px 22px;background:#00806A">` | `<td bgcolor="#00806A"><a style="display:inline-block;padding:11px 22px">` |
| Una línea divisoria | `border-left:2px dashed` | una celda rellena de 2 px |
| Cualquier layout | `<div>` con `flex` | tablas anidadas y `width="%"` |

### ⛔ Una barra VERTICAL no lleva nada adentro, y su altura se dice UNA vez

Esta es la regla que más caro ha salido, así que va con el caso completo.

Una barra horizontal puede llevar `&nbsp;` con `style="font-size:0;line-height:0"`
—si no, el espacio impone una altura mínima y las barras chicas salen todas
iguales— y así lleva años funcionando. **En una barra vertical eso mismo la
parte en dos.**

Un correo diario llegó al Outlook de escritorio con todas las barras partidas: una franja blanca a media barra, a la
misma altura en todas las columnas. La celda se veía así, con la altura dicha
de tres maneras a la vez:

```html
<!-- ⛔ tres alturas y un parrafo de alto cero adentro -->
<td height="66" bgcolor="#E8A317" style="height:66px;font-size:0;line-height:0">&nbsp;</td>
```

```html
<!-- ✅ la celda vacia, y la altura solo como atributo -->
<tr height="66"><td height="66" bgcolor="#E8A317"></td></tr>
```

**Lo que hace única a esta falla: no se puede reproducir fuera de la máquina que
la sufre.** El correo que llegó partido se renderizó BIEN en tres motores —Word
tamaño carta, Word a 22 pulgadas de ancho y Chromium— y las alturas llegaban
intactas (la barra de $4.2M llegaba como `height:82.5pt`, o sea los 110 px que
pedía el código). No es que el HTML esté mal: es que Word resuelve distinto un
párrafo de alto cero dentro de una celda alta, y el resultado cambia de máquina
a máquina.

Por eso no sirve de nada validar una gráfica vertical en un render propio. Si
la altura se dice una sola vez y la celda va vacía, no hay nada que resolver.

Entonces, para cualquier gráfica de barras verticales en un correo:

- La altura va **solo como atributo**, en el `<tr>` **y** en el `<td>`. Ni
  `style="height:..."`, ni `line-height`, ni `font-size:0`.
- La celda de la barra va **vacía**: sin `&nbsp;`, sin `<div>`, sin nada.
- Lo mismo para las líneas verticales (la de HOY, por ejemplo), que son una
  barra de 2 px de ancho.
- El ancla al piso sigue siendo un **renglón espaciador arriba**: hueco + barra
  suman siempre el mismo alto. `vertical-align:bottom` no alinea nada aquí.
- Las barras **horizontales** se quedan como están. Ahí el `&nbsp;` con
  `font-size:0` sí funciona, y no se mueve lo que ya sirve.

### ⛔ Ninguna imagen

Un PNG lo bloquea Outlook por defecto: el destinatario ve un cuadro vacío justo
donde iba el número que le importa, y no sabe que le falta algo.

**Las gráficas se dibujan con celdas de tabla.** Es más feo por dentro y se ve
siempre. Una barra es un `<td>` con `bgcolor` y un ancho en `%`; el valor va en
la celda de al lado, en texto.

### Un correo vacío miente

Si la fuente viene vacía, **truena a propósito**:

```python
if not DET:
    raise SystemExit(f"{TABLA} vino vacia: no se manda correo.")
```

Un reporte en blanco se lee como *"no hay nada vencido"*, que es una afirmación
de negocio muy distinta de *"no pude leer la tabla"*. Al tronar, salta la
actividad de aviso en vez de salir un correo que desinforma.

### El correo que no llega no deja hueco

Nadie nota la ausencia de un correo. Por eso el pipeline lleva **una segunda
actividad Office365Email** colgada del `Failed` de la primera:

```json
"dependsOn": [{"activity": "Armar el correo",
               "dependencyConditions": ["Failed"]}]
```

Va a quien mantiene el reporte —no a la lista de distribución— y dice qué falló
y qué NO recibió nadie.

### El asunto lleva el número

```
Past Due 2026-09-09 · $8.1M vencido en 288 lineas · $6.1M vence en 7 dias
```

Un asunto fijo se vuelve invisible a la semana. Con el número, se decide si se
abre sin abrirlo — y el histórico de la bandeja se vuelve una serie de tiempo.

### El botón lleva el filtro puesto

```
.../openorder/?tab=pd&due=Past+Due
```

Quien le pica cae **viendo lo mismo que el correo**. Sin los parámetros aterriza
en el universo completo y tiene que reconstruir a mano el recorte que acaba de
leer.

### La firma dice que hay gente atrás

```
🤖 equipo de BI · la empresa
   Generated and sent automatically. If something looks off, reach out to us.
```

### El horario va DESPUÉS del pipeline que publica

Y en la **misma zona horaria**, escrita igual. `Central Standard Time` es la de
EE.UU. y observa horario de verano; `Central Standard Time (Mexico)` no lo hace
desde 2022. Hoy se llevan una hora, y en cada cambio de estación se mueven sin
que nadie toque nada.

Ya costó: dos pipelines puestos "a las 06:00" corrían con 1.5 h de diferencia, y
el tablero leyó el archivo del día anterior durante semanas.

```
06:30  el pipeline que carga la fuente
07:00  el que publica los JSON del tablero
08:00  el correo
```

### La vista previa corre el código del notebook

No una copia. Se ejecuta `notebook-content.py` con un `spark` de mentira que
devuelve las filas de un JSON ya bajado:

```python
class Spark:
    def table(self, nombre): return DF(FILAS)
entorno = {"__name__": "__main__", "spark": Spark(), "notebookutils": Utils()}
exec(compile(src, NB, "exec"), entorno)
```

Mantener un generador aparte para las pruebas se siente más rápido y dura dos
días: un arreglo entra en una copia y no en la otra, y la vista previa deja de
parecerse a lo que se manda. Con esto, lo que se ve es lo que sale.

Para que funcione, el notebook **no importa nada de `pyspark` que no use**: un
`from pyspark.sql import functions as F` sin usar rompe la vista previa sin
aportar nada.

### Checklist del correo

- [ ] El notebook **arma**; el pipeline **manda**. El notebook no envía nada.
- [ ] Los destinatarios están en el notebook, en una lista, uno por renglón
- [ ] Cero `<div>` con `height`, cero `background` en CSS, cero `flex`, cero imágenes
- [ ] Las barras usan `height=` y `bgcolor=` como **atributos**
- [ ] Las barras **verticales** van con la celda vacía y la altura dicha una sola vez
- [ ] Fuente vacía → truena, no manda un correo en blanco
- [ ] Hay una actividad de aviso colgada del `Failed`
- [ ] El asunto lleva el número del día
- [ ] El botón lleva los parámetros del filtro
- [ ] El calendario corre después del pipeline que publica, y en su misma zona
- [ ] Se revisó **en Outlook**, no solo en Gmail

---

## 18. Entregable

`index.html` + la lógica en un `app.js` aparte (cargado con `<script src>`), y los
tokens de `theme.css` en su hoja de estilos o en `<style>`. **Sin JS inline ni `onclick=`
en un tablero nuevo**: la CSP del portal va a quitar `'unsafe-inline'` de `script-src`
(`portal-seguridad` § 5). El `boilerplate.html` todavía trae el script inline: al
arrancar, pásalo a `app.js` y cambia los `onclick` por `addEventListener`.
El bloque `CONFIG` va al inicio del script, claramente separado de la lógica. Los datos
**no** van en el HTML: se leen de `meta.json` y del JSON del tablero por `CONFIG.dataUrls`.

**Fechas `YYYY-MM-DD`: nunca `new Date(texto)` para pintarlas.** El navegador las toma
como medianoche UTC y en México se pintan un día antes (`2026-10-13` → `12/10/2026`).
Se arman del texto o se comparan como texto ISO.

---

## Checklist antes de entregar

- [ ] El export pasa por un formateador que cubre TODOS los tipos: ninguna celda
      lleva un array ni un objeto (§ 7)
- [ ] Cada tabla y su archivo descargado tienen nombre propio, no "Detail" (§ 7)
- [ ] Un campo nuevo cruza las TRES capas: lo escribe el publicador, lo declara
      `meta`, y **lo copia la fila** que el filtro compara (§ 13 bis)
- [ ] Marcaste cada filtro nuevo y **contaste filas**: un filtro que se pinta
      lleno y devuelve cero se ve igual que uno correcto sin datos (§ 13 bis)
- [ ] Ningún `map` que reconstruya objetos del contrato se está comiendo una
      propiedad nueva (§ 13 bis)
- [ ] Las llaves que se arman en un lado y se leen en otro se normalizan en los
      DOS (§ 13 bis)
- [ ] Mediste `getComputedStyle` y `getBoundingClientRect` de lo que dibujaste:
      ningún elemento en 0×0 ni `display` inesperado (§ 2 ter)
- [ ] Los tokens CSS que usaste EXISTEN en este tablero; uno inventado no falla,
      simplemente no hace nada (§ 2 ter)
- [ ] Se preguntaron las cinco del Paso 0 antes de empezar
- [ ] Existe `meta.json` con `generated_at`, `fuente`, `counts`, `filters` y `fuentes`
- [ ] Cada fuente trae **su propia** fecha de extracción — del nombre del archivo, de un metadato del cargador, o del `lastModified` de la tabla. Ninguna prestada de otra fuente
- [ ] Toda fuente declarada **catálogo** pasó por un `DESCRIBE HISTORY`: si algo la escribe, no es catálogo y lleva fecha
- [ ] El semáforo va sobre la fuente **más vieja**, y el desglose se ve en el tooltip y en el panel 📖
- [ ] Cero listas de categorías escritas a mano en el HTML; la lógica va por rol, no por texto
- [ ] Ningún dato faltante se rellena con un valor "razonable" — sale nulo y contado
- [ ] La banda de modo degradado probada con un `meta.json` al que le falta la estructura
- [ ] Los JSON se sirven con `Cache-Control: no-cache` y ETag
- [ ] **Cero credenciales en notebooks y en Base parameters** — la publicación va por una actividad Copy con conexión de Fabric
- [ ] El pipeline publica con **dos** Copy (a `<carpeta-portal>` y a Azure `portal-data`), clonadas de `<pipeline de referencia>` (§ 16)
- [ ] Se abrió la URL de la última milla y `generated_at` era de hoy
- [ ] Cero colores hex fuera de las variables CSS
- [ ] Panel de filtros arranca colapsado, con badge de conteo
- [ ] El panel tiene su propio scroll y "Limpiar filtros" se ve sin bajar
- [ ] Cada opción es una fila de 26 px, truncada, con el nombre completo en el title
- [ ] Grupos de más de 5 opciones traen buscador y "Seleccionar todo"; los de más de 12 arrancan plegados
- [ ] El buscador se ve con el grupo cerrado
- [ ] El orden de las opciones NO cambia al seleccionar
- [ ] Se filtra por el valor crudo, no por la etiqueta — probado con un grupo vacío
- [ ] Todo lo que se prende y apaga con `hidden` tiene su regla `[hidden] { display: none }`
- [ ] Ningún manejador se engancha a un contenedor: se engancha al rol (`[data-tab]`, no `button` a secas)
- [ ] El estado que decide qué panel se ve tiene red: si queda vacío, vuelve al panel por defecto y lo dice
- [ ] Si el tablero manda correo, pasó el checklist de la sección 17 — **revisado en Outlook**
- [ ] Trae el estetoscopio 🩺: el compartido (`/shared/js/diagnostico.js`) o uno propio que reporte tiempos **y** qué quedó en pantalla (§ 2 ter)
- [ ] Al pasar el mouse por la fecha del encabezado se ve **cada archivo con su fecha** (§ 8)
- [ ] Click en cualquier elemento de cualquier gráfica filtra todo lo demás (probado visual por visual)
- [ ] Cada gráfica tiene su ⓘ con el resumen del cálculo
- [ ] Data labels visibles donde el espacio lo permite
- [ ] Tabla de detalle a 10 filas, paginada, con todos los encabezados ordenables
- [ ] Export CSV (con BOM) y Excel (con hoja Metadata), ambos sobre el dataset filtrado completo
- [ ] "Actualizado" y "Datos al" presentes, con semáforo según umbral configurado
- [ ] Botón Back to the Portal apuntando al portal de **su departamento**, y visible aunque se colapse el menú (§ 10)
- [ ] Panel de documentación completo y útil para alguien sin contexto
- [ ] Footer con crédito al equipo de BI
- [ ] Si es bilingüe: cero strings sueltos, toggle en cada pestaña, persistencia en localStorage
- [ ] Estados vacíos manejados en cada visual
- [ ] Se ve bien en 1366×768 y al redimensionar
