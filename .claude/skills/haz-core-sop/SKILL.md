---
name: haz-core-sop
description: Metodología CORE de Haz (Controlar, Optimizar, Rediseñar, Evolucionar) para diagnosticar y automatizar procesos manuales de manufactura y planeación, más las definiciones de KPIs de S&OP e inventario que usa (OEE, Schedule Adherence, días de cobertura, faltantes, aging, FPY, netting supply-demand, Pareto de paros) y el contexto de Oracle MNA. Úsala cuando se pida evaluar, mejorar o automatizar un proceso o un Excel manual, proponer una solución de BI, diseñar o calcular un KPI de planeación, producción o inventario, armar un tablero de S&OP, netting o shortages, o cuando se mencione CORE, S&OP, MPS, intercompany, cobertura, faltantes, OEE, adherencia al plan, MNA o Custom Item Supply Demand.
---

# CORE y KPIs de S&OP

Para trabajo del equipo, la construcción del tablero sigue `dashboard-standards`; esta skill aporta el **qué medir y por qué**.

## 1. Metodología CORE

Checklist para cualquier proceso que hoy vive en Excel manual. Recorrerla en orden y decir en qué fase está el proceso.

| Fase | Pregunta | Entregable típico |
|---|---|---|
| **C — Controlar** | ¿Los datos de entrada son confiables, de una sola fuente y con dueño? | Inventario de fuentes, contrato de datos, validaciones de esquema, reglas de calidad |
| **O — Optimizar** | ¿Qué pasos manuales y repetitivos se pueden quitar? | VBA, Power Automate, Python ETL, extracción programada |
| **R — Rediseñar** | ¿El reporte estático puede ser un modelo y un tablero interactivo? | Modelo en estrella, medidas DAX, tablero con filtros cruzados |
| **E — Evolucionar** | ¿Escala? ¿Se integra al ciclo S&OP? | Lakehouse en Fabric, pipelines, mejora continua, alertas |

Reglas:
- No saltar a R o E si C no está resuelto: un tablero sobre datos sin control solo automatiza el caos.
- Cada propuesta cierra con **impacto medible**: horas/semana ahorradas, fuentes consolidadas (ej. 10 → 3), % de exceso de producción reducido, paros evitados.
- Ruta de herramientas habitual: Excel/VBA → Python/Power Automate → Power BI en estrella → Fabric.

## 2. KPIs

Definir siempre: fórmula, grano (día/semana, planta, línea, material), fuente y qué cuenta como "bueno".

| KPI | Fórmula | Notas |
|---|---|---|
| **OEE** | Disponibilidad × Rendimiento × Calidad | Disponibilidad = tiempo operando / tiempo planeado; Rendimiento = (piezas × ciclo ideal) / tiempo operando; Calidad = piezas buenas / piezas totales |
| **Schedule Adherence** | Σ min(real, plan) / Σ plan, por línea y periodo | No dejar que la sobreproducción de un día compense el faltante de otro |
| **Días de cobertura** | Inventario disponible / demanda diaria promedio | Declarar ventana de demanda (forward vs histórica) |
| **Faltantes (shortages)** | Requerimiento neto > disponible en fecha de necesidad | Mostrar fecha del primer faltante y material crítico |
| **Aging** | Días desde recepción/último movimiento, en cubetas | Cubetas típicas 0–30, 31–60, 61–90, >90 |
| **FPY** | Piezas buenas a la primera / piezas que entraron | Por estación; el rendimiento total es el producto |
| **Netting supply–demand** | Disponible + supply abierto − demanda abierta, acumulado por fecha | Ver MNA abajo |
| **Pareto de paros** | Minutos de paro por causa, ordenado, % acumulado | El 80/20 manda la acción |

## 3. Contexto Oracle

- **MNA** = pantalla de Oracle *Custom Item Supply Demand*: lista unida de jobs abiertos y órdenes abiertas por item. Es la base del netting.
- Archivo de trabajo relacionado: *Supply - Demand Netting & Coverage*.
- Consultas a Oracle: reglas de `haz-estandares-codigo` (sin comentario inicial, sin `;` final).

## 4. Portafolio objetivo

Tableros a los que apunta el trabajo: producción, inventario y faltantes, disponibilidad de material, schedule adherence, OEE y paros, calidad/yield, demanda vs supply, desempeño S&OP y cockpit de KPIs gerenciales. Al proponer algo nuevo, ubicarlo en esta lista y reutilizar modelos existentes antes de crear otro.
