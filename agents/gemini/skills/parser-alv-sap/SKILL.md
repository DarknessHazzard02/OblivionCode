---
name: parser-alv-sap
description: Cómo leer listas ALV de SAP que llegan como .csv o .txt pero no lo son - encabezados repetidos y truncados, saltos de página, líneas de separación, números europeos (1.234,56), negativos con el signo al final (100-), fechas dd.mm.yyyy y columnas de ancho fijo - con el parser de scripts/sap_parser.py. Úsala SIEMPRE que se lea un export de SAP (MB52, MB51, COOIS, MD04, ME2L, VL06O, SQ00 o una transacción propia) en pandas o PySpark, o cuando un export de SAP dé columnas corridas, números como texto o negativos positivos.
---

# Parser de listas ALV de SAP

Script: `scripts/sap_parser.py` (pandas). Para llevarlo a Delta: `delta-lakehouse` y `sap-fabric-ingesta`.

## Lo que traen y cómo se trata

| Trae | Ejemplo | Tratamiento |
|---|---|---|
| Encabezado repetido en cada página | la fila de títulos cada ~60 líneas | Se toma el primero y se descartan las repeticiones |
| Líneas de separación | `----------`, `|---|` | Se descartan |
| Títulos truncados | `Unrestricted Us` | Se mapean a un nombre limpio en config |
| Números europeos | `1.234,56` | Quitar `.` de miles, `,` → `.` |
| Negativo al final | `100-` | `-100` |
| Fechas | `07.09.2026` | `format="%d.%m.%Y"`; si no casa, nulo **contado** |
| Ancho fijo | columnas alineadas con espacios | Cortes por posición desde el encabezado |
| Totales y subtotales | filas con `*` o vacías en la llave | Se descartan y se cuentan |

## Reglas

- **Nunca** confiar en la detección automática de tipos: todo entra como texto y se tipa explícito.
- El nombre del archivo trae la fecha del extracto: es la **frescura**, no la fecha de hoy.
- El reporte final dice: filas leídas, encabezados repetidos quitados, totales quitados, números que no parsearon (con ejemplo).
- Un `~$archivo.xlsx` (archivo temporal de Excel) en la carpeta se ignora explícitamente.

## Cómo se comprueba

Con un ALV inventado de 3 páginas: el conteo de filas de datos es exacto, `100-` sale `-100`, `1.234,56` sale `1234.56` y ninguna fila de encabezado queda en los datos.
