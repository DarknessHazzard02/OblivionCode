---
name: datos-semi-ficticios
description: Cómo se generan y validan los datos de un proyecto de Haz sin meter datos reales a git - datos 100 % inventados para lo publicado, semi-ficticios (forma real, identidades inventadas) para desarrollo local, el CONTRATO.md obligatorio de cada carpeta de datos, la validación valor por valor y el reporte de faltantes, inconsistentes, fuera de rango y duplicados. Úsala SIEMPRE que se creen datos de demo, se arme un generar_demo.py, se agregue una carpeta data/ o demo/, se pida "datos de prueba", "datos inventados", "seudonimizar", "anonimizar", o cuando el candado detenga un commit por datos sin contrato.
---

# Datos semi-ficticios

## 1. Tres tipos de datos

| Tipo | Qué es | Dónde vive | ¿Va a git? |
|---|---|---|---|
| **Inventados** | Generados desde cero con la forma del contrato | `demo/source/`, `data/` | Sí, con `CONTRATO.md` |
| **Semi-ficticios** | Forma real (columnas, tipos, distribuciones, relaciones); identidades inventadas | `data_semi/` | Solo si el contrato lo dice y pasaron la validación |
| **Reales** | Cualquier export de un sistema | `data_real/`, `Output/`, la ruta de `config.local.json` | **Nunca** |

Lo que se publica (portafolio, tablero público) es **100 % inventado**.

## 2. `CONTRATO.md` (plantilla en `_comun/plantillas/docs/CONTRATO.md`)

```markdown
# Contrato de datos — <Proyecto>
datos: inventados          # inventados | semi-ficticios
generador: generar_demo.py
semilla: 42
columnas:
  - Plant: texto, catálogo Plant_A..Plant_D
  - Material: texto, patrón MAT-#####
  - OnHand: entero ≥ 0
  - NeedByDate: fecha ISO
relaciones: Material → catálogo de materiales (1:N)
```

Sin contrato, el candado detiene el commit y la carpeta se trata como real.

## 3. Generar

- Semilla fija (`random.seed(42)`, `numpy.random.default_rng(42)`): mismo resultado en cada corrida.
- Identidades del patrón del contrato: `Plant_A`, `Vendor_017`, `MAT-00412`, nombres de una lista ficticia.
- Distribuciones creíbles: lognormal para cantidades, estacionalidad semanal, 2–5 % de nulos **declarados** para probar el modo degradado.
- Fechas relativas a una fecha base fija del contrato, no a "hoy".

## 4. Semi-ficticio: seudonimizar

1. Leer el real **solo en local**, desde `config.local.json`.
2. Mapear cada identidad a un seudónimo estable: `HMAC-SHA256(secreto_local, valor)` → `Vendor_<n>`. El secreto vive en `config.local.json`, nunca en el repo.
3. Cifras: escalar por un factor aleatorio por entidad (±20 %) para conservar la forma sin el valor.
4. Quitar texto libre (comentarios, notas) y datos personales: no se seudonimizan, se eliminan.

## 5. Validar valor por valor

Antes de usar un semi-ficticio se reporta, **con conteos**:

| Chequeo | Debe dar |
|---|---|
| Columnas y tipos contra el contrato | Iguales |
| Filas | Iguales al real |
| Ninguna identidad real sobrevive | 0 coincidencias del real en el semi |
| Faltantes, inconsistentes, fuera de rango, duplicados | Reportados por columna |
| Llaves de relación | Mismo número de huérfanos que el real |

Si una sola identidad real aparece, el archivo se borra y se regenera.
