---
name: formato-textos
description: Reglas de mayúsculas, minúsculas y puntuación para el texto de los tableros (español e inglés) - Proper con conectores en minúscula para títulos, etiquetas, KPIs, botones, filtros, encabezados, ejes, chips, pestañas y meses; oración con punto final para subtítulos, líneas de KPI, avisos, ayudas, popovers y documentación; siglas y transacciones de SAP siempre en mayúsculas; los valores de los datos nunca se tocan. Úsala SIEMPRE que se escriba, revise o corrija texto visible de un tablero (I18N, CONFIG.visuals, documentation, catálogos de meta.json, tooltips, leyendas), cuando se pida "Proper", "mayúsculas", "capitalizar", "formato de texto", "corregir ortografía", "puntos faltantes" o "que se vea estructuralmente correcto", y al terminar cualquier tablero nuevo antes de entregarlo. Skill local de esta máquina: no va al repo del equipo.
---

# Formato de textos de los tableros

Skill **local** (solo esta máquina). Aplica igual en español y en inglés.

## Las tres clases de texto

| Clase | Qué es | Regla |
|---|---|---|
| **Etiqueta** | títulos de página y de gráfica, KPIs, botones, pestañas, filtros, encabezados de tabla, ejes, leyendas, chips, placeholders, meses, catálogos del tablero (estatus traducidos) | **Proper**: mayúscula inicial en cada palabra; los conectores van en minúscula salvo que sean la primera palabra o vayan después de un símbolo |
| **Frase** | subtítulos de gráfica, la línea bajo el número del KPI, avisos de la banda, estados vacíos, popovers ⓘ, documentación, mensajes | **Oración**: mayúscula inicial, el resto como se escribe normalmente, y **punto final** (salvo que cierre con `…`, `:`, `?` o `!`) |
| **Dato** | lo que viene de SAP, Oracle, Y Meadows: nombres de cliente, estatus (`AWAITING_SHIPPING`), notas, códigos | **No se toca.** Se ve igual que en el sistema para poder buscarlo y cruzarlo |

### Excepciones dentro de una etiqueta

- **Siglas, transacciones y códigos se quedan como vienen**: SAP, MB52, ZE_SD48, SDDnnn, YM, PO, SO, OM, QI, MRP, ID, KPI, CSV, 3M, 1er, US10.
- **Después de un símbolo** la palabra va con mayúscula aunque sea conector:
  `( [ { / \ - + = < > ? _ " ' ` : ; . , · |`. Ejemplo: `Sold-To`, `Total (Unr. + QI + Bloq.)`.
  El apóstrofo **dentro** de una palabra no cuenta: `Can't`, no `Can'T`.
- **Palabras que se insertan a media frase** (unidades y conectores sueltos que el código pega a un número:
  `materiales`, `filas`, `de`, `of`, `rows`, `seleccionados`) se quedan en minúscula: forman parte de una frase.
- **Colas de frase**: lo que el código pega después de un número (`28.0% ` + `de los materiales con demanda`)
  va en minúscula y con punto. Si después se le pega algo más (`· 270 líneas`), el punto va al final, en el código.
- **`vs` siempre en minúscula**, aunque abra la etiqueta (`vs Request Date`).
- **Después de `%` el conector sigue en minúscula** (`% de Cobertura`).
- **Una letra mayúscula suelta a media etiqueta es nombre**, no conector: `Control de Órdenes Y Meadows`.
- **Nombres de archivo, rutas y plantillas no se tocan**: `divisiones.csv`, `manual/`, `{n}`, `${x}`.
- **Términos fijos de los sistemas** se escriben siempre igual (`On Hold`, `Request Date`, `Promise Date`,
  `Schedule Ship Date`, `Customer Related`, `Open Orders`, `Executive Summary`): lista `TERMINOS` en `formato.py`.
- **Los conectores de los dos idiomas aplican a todo**: las etiquetas mezclan (`Past Due Reason by Site` en el
  tablero en español).
- **Los títulos de la banda de avisos son oraciones** (`No se pudieron leer los datos del tablero.`), no etiquetas.

### Conectores en minúscula

- **ES**: de, del, la, las, el, los, lo, y, e, o, u, a, al, en, por, para, con, sin, sobre, entre, que, un, una, unos, unas, vs, desde, hasta, según.
- **EN**: of, the, a, an, and, or, nor, by, in, on, at, to, for, per, from, with, without, vs, as, into, than, via.

## Ejemplos

| Antes | Después | Clase |
|---|---|---|
| Faltante inmediato | Faltante Inmediato | etiqueta |
| Bajo cobertura 3M | Bajo Cobertura 3M | etiqueta |
| Con demanda y sin inventario | Con Demanda y sin Inventario | etiqueta |
| Materiales por estatus de cobertura | Materiales por Estatus de Cobertura | etiqueta |
| Se agotan en el 1er mes | Se Agotan en el 1er Mes | etiqueta |
| Fecha de análisis · días hábiles 3M · Horizonte hasta | Fecha de Análisis · Días Hábiles 3M · Horizonte Hasta | etiqueta |
| 19 oct · 4 ene | 19 Oct · 4 Ene | etiqueta |
| Orders received per month | Orders Received per Month | etiqueta |
| Total (Unr. + QI + Bloq.) | Total (Unr. + QI + Bloq.) | etiqueta |
| Materiales por semana en que se acaba el inventario | Materiales por semana en que se acaba el inventario. | frase |
| 28.0% de los materiales con demanda | 28.0% de los materiales con demanda. | frase |
| Sin datos para los filtros seleccionados | Sin datos para los filtros seleccionados. | frase |
| ACME COOLING, INC. · AWAITING_SHIPPING | (igual) | dato |

## Gramática y símbolos

Al pasar el texto, corregir también:

- Acentos (`analisis` → `análisis`, `pestana` → `pestaña` en lo visible; en código y comentarios no importa).
- Punto final que falta en frases; `:` antes de un valor (`Fecha de Análisis: 20/10/2026`); `;` para separar listas largas en una frase.
- Espacios dobles, espacio antes de `,` o `.`, comillas sin cerrar, paréntesis sin cerrar.
- Mismo término en todo el tablero (no `Órdenes` en un lado y `Pedidos` en otro).

## Cómo se aplica

`scripts/formato.py` trae `proper(texto, lang)`, `frase(texto)` y `cola(texto)`:

```bash
python ~/.claude/skills/formato-textos/scripts/formato.py "materiales por estatus de cobertura" es
```

`scripts/aplicar_formato.py` pasa el `I18N` (y con `--config`, los ⓘ y la documentación) de un `app.js`.
Sin `--aplicar` solo imprime la propuesta, llave por llave, para revisarla antes:

```bash
python ~/.claude/skills/formato-textos/scripts/aplicar_formato.py <tablero>/app.js --reglas ~/.claude/skills/formato-textos/reglas/<tablero>.json --config
```

`reglas/<tablero>.json` corrige la clase de una llave cuando el nombre no la dice
(`{"frase": [...], "cola": [...], "igual": [...], "etiqueta": [...], "valores": {"llave": {"es": "...", "en": "..."}}}`).
Hay reglas para SAP_MB52_ZE_SD48, PastDue_OpenOrders y Y_Meadows.

1. Pasar los diccionarios `I18N.es` e `I18N.en`: etiquetas con `proper`, frases con `frase`, y dejar como
   están las palabras de media frase (unidades).
2. `CONFIG.visuals[...].info` y `CONFIG.documentation`: todo es **frase**.
3. Los catálogos que escribe el generador en `meta.filters` (`es` / `en`) son **etiquetas**; sus
   descripciones largas (`desc_es`, `desc_en`) son **frases**.
4. En el código: los meses que arma `toLocaleString` salen en minúscula; capitalizarlos al pintarlos.
   La línea del KPI que se arma con `${pct}% ${t(...)}` lleva su punto.
5. **No** pasar por aquí valores de los datos, nombres de columna originales (`Material_Description`,
   `Past_Due_+_Period_1_Demand`) ni lo que se exporta a CSV/Excel como valor.

## Cómo se comprueba

| Qué | Bien | Mal en silencio |
|---|---|---|
| Captura del tablero en ES y en EN | títulos y etiquetas en Proper, subtítulos con punto | un conector con mayúscula a media etiqueta (`De`, `Of`) |
| Siglas | `SAP`, `MB52`, `3M` intactas | `Sap`, `Mb52` — se coló una sigla como palabra |
| Datos | `ACME COOLING, INC.` igual que en SAP | `Acme Cooling, Inc.`: se formateó un dato y ya no cruza con la fuente |
| Frases compuestas | `61 materiales` | `61 Materiales`: se formateó una unidad de media frase |
