# Datos inventados — no son de ningún sistema

datos: inventados

La línea de arriba es la marca que lee el candado de git; sin ella, los archivos de esta carpeta se tratan
como datos reales.

`source/` lo escribe `generar_demo.py` con números aleatorios y semilla fija: mismas columnas que la fuente real, ningún valor real.

Si aquí aparece un archivo con datos reales, no debe commitearse: los reales van en `data_real/`, que está
en `.gitignore`.
