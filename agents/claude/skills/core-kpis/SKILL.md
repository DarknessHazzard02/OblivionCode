---
name: core-kpis
description: Metodología CORE de Haz (Controlar, Optimizar, Rediseñar, Evolucionar) para diagnosticar y automatizar procesos manuales de manufactura y planeación, más las definiciones con fórmula de los KPIs de S&OP e inventario (OEE, Schedule Adherence, días de cobertura, faltantes, aging, FPY, netting supply-demand, Pareto de paros, control de excesos, balanceo de líneas). Úsala cuando se pida evaluar, mejorar o automatizar un proceso o un Excel manual, proponer una solución de BI, diseñar o calcular un KPI, armar un tablero de S&OP, netting o faltantes, o cuando se mencione CORE, CTCO, S&OP, MPS, cobertura, faltantes, OEE o adherencia al plan.
---

# CORE y KPIs de S&OP

La construcción del tablero sigue `tablero-estandar`; esta skill aporta **qué medir y por qué**.

## 1. CORE (se enuncia en 2 a 4 líneas antes de escribir código)

| Fase | Pregunta | Qué se hace | Entregable típico |
|---|---|---|---|
| **C — Controlar** | ¿Los datos de entrada son confiables, de una sola fuente y con dueño? | Auditar fuentes; validar esquema, nulos y duplicados; contrastar contra el objetivo | Inventario de fuentes, `CONTRATO.md`, validaciones |
| **O — Optimizar** | ¿Qué pasos manuales se pueden quitar? | Automatizar; quitar pasos redundantes y lógica verbosa; afinar consultas y joins | VBA, Python ETL, flujo programado |
| **R — Rediseñar** | ¿El reporte estático puede ser un modelo y un tablero? | Modelo estrella, DAX eficiente, pipelines modulares, visuales de decisión | Modelo, medidas, tablero con cross-filter |
| **E — Evolucionar** | ¿Escala y se integra al ciclo S&OP? | Parquet o Delta, monitoreo, alertas, entrega lista para publicar | Lakehouse, pipeline, alertas |

Reglas:
- No saltar a R o E con C sin resolver: un tablero sobre datos sin control automatiza el caos.
- Cada propuesta cierra con **impacto medible**: horas/semana ahorradas, fuentes consolidadas (10 → 3), % de exceso reducido, paros evitados.
- Ruta de herramientas: Excel/VBA → Python/flujos → Power BI en estrella → Fabric.

## 2. KPIs

Se define siempre: **fórmula, grano** (día/semana, planta, línea, material), **fuente** y qué cuenta como "bueno". Cuando se usa una fórmula, se escribe.

| KPI | Fórmula | Notas |
|---|---|---|
| **OEE** | Disponibilidad × Rendimiento × Calidad | Disp. = tiempo operando / planeado; Rend. = (piezas × ciclo ideal) / tiempo operando; Cal. = buenas / totales |
| **Schedule Adherence** | Σ min(real, plan) / Σ plan, por línea y periodo | La sobreproducción de un día no compensa el faltante de otro |
| **Días de cobertura** | Inventario disponible / demanda diaria promedio | Declarar la ventana de demanda (forward o histórica) |
| **Faltantes** | Requerimiento neto > disponible en la fecha de necesidad | Mostrar fecha del primer faltante y el material crítico |
| **Aging** | Días desde recepción o último movimiento, en cubetas | 0–30, 31–60, 61–90, >90 |
| **FPY** | Buenas a la primera / piezas que entraron | Por estación; el rendimiento total es el producto |
| **Netting supply–demand** | Disponible + supply abierto − demanda abierta, acumulado por fecha | La primera fecha con saldo < 0 es la primera fecha factible perdida |
| **Pareto de paros** | Minutos de paro por causa, ordenado, % acumulado | El 80/20 manda la acción |
| **Control de excesos** | (Programado − requerido) / requerido, si > 0 | Mitigar sobreproducción programada |
| **Balanceo de líneas** | Carga por celda / tiempo de ciclo objetivo (takt) | Celdas > 100 % son cuello de botella |

## 3. Qué detectar al revisar un programa o inventario

| Tema | Qué se busca |
|---|---|
| Programación | Conflictos, sobrecargas, insumos faltantes, riesgo de lead time, restricciones de capacidad, y la corrección propuesta |
| Inventario | On-hand, órdenes abiertas, faltantes, cobertura, primera fecha factible, y alternativas |
| SOPs | Pasos clave, roles, prerrequisitos, entradas y salidas, excepciones |
| Error de refresh | Causa, corrección y cómo confirmar que quedó |

## 4. Portafolio de tableros

Producción, inventario y faltantes, disponibilidad de material, schedule adherence, OEE y paros, calidad/yield, demanda vs supply, desempeño S&OP y cockpit de KPIs. Al proponer algo nuevo, ubicarlo aquí y reutilizar modelos antes de crear otro.
