# Contrato de datos: DATOS INVENTADOS

datos: inventados

La línea de arriba es la marca que lee el candado de git; sin ella, los JSON de esta carpeta se tratan como datos reales.

`meta.json` y `dashboard.json` de esta carpeta son el contrato del tablero **Past Due Open Orders**: sirven para
probarlo en local y son lo que el portal muestra mientras no lleguen los datos reales.

**Son 100 % inventados, desde cero:** los escribe `python build/generar_contrato.py` con valores al azar
y semilla fija. Nada parte de un corte real, ni la forma.

- **Valores inventados:** 40 clientes ficticios (empresas de demostración: `FABRIKAM HVAC SYSTEMS`, `NORTHWIND AIR SOLUTIONS`…), items `CM-000001…`, órdenes, montos, planeadores y aprobadores con nombres ficticios, Bridge e historial.
- **Lo único que no se inventa** son las reglas del tablero: los códigos de org, divisiones, product lines, sitios y tipos de hold con los que el cálculo asigna responsabilidad. Son lógica, no datos.
- `meta.json` no trae nombres de archivos ni de extractos de origen.
- `build/calculo.py` (en la copia local, `generar_datos.py`) es el cálculo del tablero; `generar_contrato.py` lo corre sobre las fuentes inventadas
  en una carpeta temporal que se borra al terminar.

`meta.json` trae `"demo": true`; el tablero lo avisa con una banda.

Los datos reales no van en esta carpeta: el portal los lee de `PORTAL-DATA/pastdue-open-orders/`; todavía no hay pipeline que la llene.
