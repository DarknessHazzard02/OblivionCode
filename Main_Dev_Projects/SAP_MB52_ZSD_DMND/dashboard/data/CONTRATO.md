# Contrato de datos: DATOS INVENTADOS

datos: inventados

La línea de arriba es la marca que lee el candado de git; sin ella, los JSON de esta carpeta se tratan como datos reales.

`meta.json` y `dashboard.json` de esta carpeta son el contrato del tablero **Inventory Coverage vs Demand**: sirven para
probarlo en local y son lo que el portal muestra mientras no lleguen los datos reales.

**Son 100 % inventados, desde cero:** los escribe `python build/generar_contrato.py` con valores al azar
y semilla fija. Nada parte de un corte real, ni la forma.

- **Valores inventados:** materiales `CM-000001…`, descripciones "<pieza> <sigla>-NNNN", grupos `MG-10*`, MRP `E0*`, 5 clientes ficticios (`FABRIKAM HVAC SYSTEMS`…) y documentos `OB…`.
- **Lo único que no se inventa** son las reglas del tablero: la planta y los almacenes del catálogo de ubicaciones del cálculo. Son lógica, no datos.
- `meta.json` no trae nombres de archivos ni de extractos de origen.
- `build/calculo.py` (en la copia local, `generar_datos.py`) es el cálculo del tablero; `generar_contrato.py` lo corre sobre las fuentes inventadas
  en una carpeta temporal que se borra al terminar.

`meta.json` trae `"demo": true`; el tablero lo avisa con una banda.

Los datos reales no van en esta carpeta: el portal los lee de `PORTAL-DATA/sap-mb52-zsd-dmnd/`, que llena el pipeline `PL_MB52_ZSD_DMND` de `Fabric-Repo` (falta su actividad Copy a esa carpeta).
