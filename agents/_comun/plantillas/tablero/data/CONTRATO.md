# Contrato de datos — <Tablero>

datos: inventados
generador: generar_demo.py
semilla: 42
archivos: meta.json, dashboard.json
columnas:
  - Plant: texto, catálogo Plant_A..Plant_D
  - Material: texto, patrón MAT-#####
  - OnHand: entero >= 0
  - NeedByDate: fecha ISO (YYYY-MM-DD)
frescura: meta.json → asOf (fecha del extracto, nunca la de hoy)
