---
name: "gizmo-core-sop-kpis"
description: "CORE methodology (Control, Optimize, Redesign, Evolve) and CTCO structure to diagnose and automate manual manufacturing and planning processes, plus S&OP and inventory KPI definitions (OEE, schedule adherence, days of coverage, shortages, aging, FPY, supply-demand netting, downtime Pareto, excess control, line balancing). Use it to evaluate or automate a process or a manual Excel, propose a BI solution, define or calculate a planning, production or inventory KPI, or analyze a schedule or inventory. / Metodología CORE y CTCO para diagnosticar y automatizar procesos manuales, y definiciones de KPIs de S&OP e inventario. Úsala para evaluar o automatizar un proceso, proponer una solución de BI, definir o calcular un KPI, o analizar un programa o un inventario."
---

# CORE and S&OP KPIs / CORE y KPIs de S&OP

## English

**When to use:** improving or automating a process, proposing a BI solution, defining or computing a KPI, analyzing a schedule or inventory.

**Steps**
1. If the request is vague, restate it as Context / Task / Constraints / Output and confirm.
2. Place the process in its CORE phase:
   - **Control:** sources, schema, nulls, duplicates, business goal.
   - **Optimize:** automate and remove redundancy.
   - **Redesign:** star schema, DAX, dashboard.
   - **Evolve:** Fabric, Delta, monitoring, S&OP.
3. Never jump to Redesign or Evolve while Control is unsolved.
4. For every KPI, state formula, grain, source and what counts as good.
5. Close the proposal with measurable impact: hours saved, sources consolidated, overproduction reduced, stoppages avoided.

**Key formulas**
- OEE = Availability × Performance × Quality.
- Schedule adherence = Σ min(actual, plan) / Σ plan.
- Coverage = available inventory / average daily demand.
- An extreme (minimum, first shortage) is validated against its own definition, never by a sum reconciliation.
- Inter-plant transfers come as two legs with the same document number: match them by document number, never by quantity, and remove both legs.

**Reference:** read `references/core-sop-kpis.en.html` for the full KPI table and the operational analysis checklist.

## Español

**Cuándo usarla:** mejorar o automatizar un proceso, proponer una solución de BI, definir o calcular un KPI, analizar un programa o un inventario.

**Pasos**
1. Si la petición es vaga, reestructúrala en Context / Task / Constraints / Output y confirma.
2. Ubica el proceso en su fase de CORE:
   - **Controlar:** fuentes, esquema, nulos, duplicados, objetivo de negocio.
   - **Optimizar:** automatizar y quitar redundancia.
   - **Rediseñar:** modelo estrella, DAX, tablero.
   - **Evolucionar:** Fabric, Delta, monitoreo, S&OP.
3. Nunca saltes a Rediseñar ni a Evolucionar sin resolver Controlar.
4. De cada KPI di la fórmula, el grano, la fuente y qué cuenta como bueno.
5. Cierra la propuesta con impacto medible: horas ahorradas, fuentes consolidadas, exceso de producción reducido, paros evitados.

**Fórmulas clave**
- OEE = Disponibilidad × Rendimiento × Calidad.
- Adherencia = Σ min(real, plan) / Σ plan.
- Cobertura = inventario disponible / demanda diaria promedio.
- Un extremo (mínimo, primer faltante) se valida contra su propia definición, nunca con un cuadre de sumas.
- Los traspasos entre plantas vienen como dos patas con el mismo número de documento: se cruzan por número de documento, nunca por cantidad, y se quitan las dos patas.

**Referencia:** lee `references/core-kpis-sop.es.html` para la tabla completa de KPIs y el checklist de análisis operativo.

## Close / Cierre

End with "What you need to do" / "Lo que tienes que hacer": numbered steps, each with where, what success looks like, and what a silent failure looks like.
