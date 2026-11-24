# Dónde se esconde el rastro, por formato

Referencia de consulta. Léela cuando trabajes con un formato que no esté cubierto en el
cuerpo de la skill, o cuando el script reporte algo y necesites entender qué es.

## Contenido

- [Office y Visio (paquetes OOXML)](#office-y-visio-paquetes-ooxml)
- [PDF](#pdf)
- [Imágenes](#imágenes)
- [SVG](#svg)
- [HTML](#html)
- [CSV y texto plano](#csv-y-texto-plano)
- [Git](#git)

---

## Office y Visio (paquetes OOXML)

`.docx`, `.xlsx`, `.pptx`, `.vsdx`, `.dotx`, `.potx`, `.xlsm` son archivos zip. Buscar
cadenas en el archivo tal cual no encuentra nada: hay que descomprimir y revisar parte por
parte.

| Dónde | Qué guarda |
|---|---|
| `docProps/core.xml` | `dc:creator`, `cp:lastModifiedBy`, `dc:title`, `dc:subject`, `dc:description`, `cp:keywords` |
| `docProps/app.xml` | `Application`, `AppVersion`, `Company`, `Manager`, `Template` |
| `docProps/custom.xml` | propiedades personalizadas; las plantillas viejas dejan cosas aquí |
| `word/settings.xml` | `w:proofState`, rutas de plantilla, a veces el nombre de usuario en `w:rsid` |
| `word/document.xml` | comentarios, control de cambios con nombre de autor |
| `xl/workbook.xml` | rutas absolutas en referencias externas, que delatan la máquina |
| `visio/pages/*.xml` | nombres de usuario en formas creadas a mano |
| `_rels/*.rels` | rutas absolutas a archivos vinculados |

**Lo que más se olvida:** control de cambios y comentarios. Traen nombre de autor y fecha,
se ven en el documento y sobreviven a cualquier limpieza de metadatos. Acéptalos o
recházalos antes de entregar.

**Plantillas:** un archivo construido a partir de una plantilla hereda todo `docProps` de
la plantilla original, incluido el autor. Si tomaste la plantilla de una librería o de
internet, ahí va el nombre de un desconocido.

---

## PDF

Cuatro lugares distintos, y las propiedades del documento solo muestran el primero.

1. **Diccionario Info** — `/Author`, `/Producer`, `/Creator`, `/Title`, `/Keywords`.
   Es lo único que enseña el visor.
2. **Metadatos XMP** — un bloque XML incrustado, normalmente con la misma información
   duplicada. Puede quedar desincronizado del Info y seguir delatando la herramienta.
3. **Comentario de cabecera** — la tercera línea del archivo, tipo
   `% Written by <herramienta> <versión>`. Invisible en cualquier visor, evidente en un
   editor de texto.
4. **Objetos internos** — un segundo `/Producer` dentro del catálogo, rutas de fuentes
   incrustadas, nombres de subconjuntos de fuente.

**Al parchar por bytes, la sustitución tiene que ser exactamente del mismo largo.** La
tabla xref del final guarda la posición absoluta de cada objeto; si mueves un byte, todas
las posiciones quedan corridas y el archivo deja de abrir. Por eso se rellena con espacios
en lugar de borrar.

**No uses guardado incremental para limpiar.** Añade una revisión encima y deja intacto lo
anterior, así que el dato que querías quitar sigue en el archivo. Reescribe completo.

---

## Imágenes

| Formato | Dónde |
|---|---|
| `.png` | chunks `tEXt`, `iTXt`, `zTXt`; suelen traer el software que la generó |
| `.jpg` | EXIF completo: cámara, software, **y coordenadas GPS** si salió de un teléfono |
| `.tiff` | EXIF e IPTC |
| `.webp` | chunk `EXIF` |

Para capturas de pantalla, revisa además lo que se ve: barras de tareas con nombres de
archivo, pestañas del navegador, notificaciones, nombres de usuario en la esquina.
Eso no lo detecta ningún script.

---

## SVG

Texto plano, así que es fácil de revisar y fácil de olvidar.

- Comentarios `<!-- -->` que dejó la herramienta de dibujo.
- Metadatos `<metadata>` con bloques RDF y Dublin Core.
- Atributos con prefijo del editor: `inkscape:`, `sodipodi:`, `figma:`.
- `<title>` y `<desc>`, que además son los que lee un lector de pantalla.

---

## HTML

- Comentarios de plantilla o de generador.
- `<meta name="generator">`.
- Rutas absolutas del sistema de archivos en `src` o `href`, que delatan el nombre de
  usuario de la máquina.
- Código muerto y bloques comentados con notas internas.

---

## CSV y texto plano

No tienen metadatos, pero sí tienen dos problemas propios:

- **Filas de más:** encabezados repetidos, totales pegados abajo, filas de prueba.
- **Datos que no deberían salir:** nombres de proveedor, montos, números de parte reales.
  `CONTRIBUIR.md` los prohíbe en el repositorio, y en un entregable hacia afuera hay que
  preguntarse lo mismo.

---

## Git

- Líneas de atribución en el mensaje de commit o en la descripción del Pull Request.
- `user.name` y `user.email` mal configurados: revisa con `git config --local --list` antes
  del primer commit en un clon nuevo.
- Archivos que se colaron: `.env`, credenciales, rutas locales en archivos de configuración.
- Ramas con nombre que revela algo que no debería.
