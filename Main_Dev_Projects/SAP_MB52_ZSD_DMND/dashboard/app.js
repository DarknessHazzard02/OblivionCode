// Made by: Hazzard
"use strict";
/* ============================================================
   CONFIG — todo lo editable vive aqui. No tocar la logica abajo.
   ============================================================ */
const CONFIG = {
  dashboardName: "mb52-zsd-dmnd",
  portalUrl: "/logistics/",
  dataUrls: ["./data/"],   // portafolio: solo datos inventados
  lang: { enabled: ["es", "en"], default: "es" },
  freshness: { warnDays: 1, criticalDays: 3 },
  maxDiasEntreFuentes: 1,     // inventario y demanda con mas de esto entre cortes -> aviso
  topN: 15,
  detail: { pageSize: 25, pageSizes: [25, 50, 100, 250, 500, 1000] },   // filas por pagina: minimo 25, maximo 1000

  visuals: {
    kpi: { info: {
      es: { medida: "Materiales por situación de cobertura.", calculo: "COUNT(material) que cumple la condición de cada tarjeta; el % es sobre los materiales con demanda.", filtros: "Todos los filtros y selecciones, salvo la de las tarjetas.", granularidad: "Material." },
      en: { medida: "Materials by coverage situation.", calculo: "COUNT(material) meeting each card's condition; % is over materials with demand.", filtros: "All filters and selections except the cards' own.", granularidad: "Material." } } },
    status: { info: {
      es: { medida: "Materiales por estatus de cobertura.", calculo: "COUNT(material) por estatus, según la base de inventario elegida (Unrestricted o Total).", filtros: "Filtros del panel y selección de las otras gráficas.", granularidad: "Material (todas las plantas y almacenes de MB52 sumados)." },
      en: { medida: "Materials by coverage status.", calculo: "COUNT(material) by status, per the selected inventory basis (Unrestricted or Total).", filtros: "Panel filters and the other charts' selection.", granularidad: "Material (all MB52 plants and storage locations summed)." } } },
    semana: { info: {
      es: { medida: "Cuándo se queda sin inventario cada material.", calculo: "Fecha de faltante = primer día en que demanda vencida + demanda acumulada desde la fecha de análisis ≥ inventario. Inmediato = ya no alcanza hoy.", filtros: "Solo materiales con fecha de faltante dentro del horizonte de 3 meses.", granularidad: "Semana (lunes a domingo)." },
      en: { medida: "When each material runs out of stock.", calculo: "Stockout date = first day on which past-due + cumulative demand from the analysis date ≥ inventory. Immediate = already short today.", filtros: "Only materials with a stockout date inside the 3-month horizon.", granularidad: "Week (Monday to Sunday)." } } },
    top: { info: {
      es: { medida: "Faltante en unidades.", calculo: "MAX(0, Demanda total 3M − Inventario).", filtros: "Los 15 materiales con mayor faltante en la selección actual.", granularidad: "Material, en su unidad base: no se compara entre unidades distintas." },
      en: { medida: "Shortfall in units.", calculo: "MAX(0, Total 3M demand − Inventory).", filtros: "Top 15 materials by shortfall in the current selection.", granularidad: "Material, in its base unit: not comparable across units." } } },
    ubic: { info: {
      es: { medida: "Dónde está el inventario disponible de los materiales filtrados.", calculo: "SUM(Unrestricted) de MB52 por ubicación resumida (catálogo Base).", filtros: "Siempre Unrestricted, sin importar la base elegida. Fuera de US90 todo cae en Blank.", granularidad: "Ubicación resumida." },
      en: { medida: "Where the filtered materials' available stock sits.", calculo: "SUM(Unrestricted) from MB52 by summarized location (Base catalog).", filtros: "Always Unrestricted regardless of the selected basis. Outside US90 everything falls into Blank.", granularidad: "Summarized location." } } }
  },

  documentation: {
    es: {
      purpose: "Cruza el inventario actual (SAP MB52) contra la demanda (SAP ZSD_DMND) para mostrar qué materiales se quedan sin inventario, cuándo, y cuáles no tienen inventario que cubra su demanda. Es la versión en tablero del Excel MB52_SD48_Analysis (hoja Final), con el mismo cálculo salvo la regla de demanda (ver limitaciones).",
      transformations: [
        "MB52: cada renglón se asigna a una ubicación resumida con el catálogo Base (planta + almacén). Lo que no está en el catálogo cae en Blank.",
        "MB52: Unrestricted = disponible; Total = Unrestricted + Quality Inspection + Blocked. Se suman todas las plantas y almacenes por material.",
        "ZSD_DMND: se descartan renglones sin fecha. La demanda es la suma de los requerimientos (Qty_Valor negativo) por material y fecha; las recepciones (ShipNt, PchOrd, PurRqs, PlOrd, PrdOrd, QM lot) no cuentan.",
        "Horizonte: P1 = vencido + 1er mes desde la fecha de análisis; P2 = 2º mes; P3 = 3er mes.",
        "Fecha de análisis = fecha de archivo más reciente de MB52. Días hábiles = lunes a sábado dentro de los 3 meses."
      ],
      measures: [
        "Demanda total 3M = P1 + P2 + P3.",
        "Demanda diaria promedio = Demanda total 3M / días hábiles de 3 meses.",
        "Días de cobertura promedio = piso(Inventario / demanda diaria), topado a los días hábiles.",
        "% de cobertura = Inventario / Demanda total 3M, topado en 101% (se muestra como > 100%).",
        "Fecha de faltante = primer día en que la demanda vencida más la acumulada desde la fecha de análisis alcanza el inventario.",
        "Días SAP de cobertura = días hábiles desde la fecha de análisis hasta la fecha de faltante, menos 1.",
        "Faltante (unidades) = MAX(0, Demanda total 3M − Inventario). Lo agrega el tablero."
      ],
      rules: [
        "Sin demanda: demanda total 3M = 0.",
        "Faltante inmediato: inventario ≤ 0, o la demanda vencida ya es mayor o igual al inventario.",
        "Bajo cobertura 3M: el inventario no alcanza la demanda total de 3 meses.",
        "Cubierto 3M: el inventario cubre toda la demanda de 3 meses.",
        "Almacén = solo US90 / ZLD1 (Direct Material)."
      ],
      limitations: [
        "La demanda no es igual a la del Excel MB52_SD48_Analysis: el notebook toma el absoluto del neto de Qty_Valor por fecha y así cuenta recepciones como demanda. Aquí solo cuentan requerimientos. Tampoco se restan las recepciones futuras al inventario: el faltante es contra el inventario de hoy.",
        "Inventario y demanda pueden venir de cortes de días distintos: revisa las fechas en la tabla de fuentes.",
        "Las cantidades están en la unidad base de cada material: sumarlas entre materiales solo da un orden de magnitud.",
        "No considera inventario en tránsito ni devoluciones de MB52.",
        "MB52 trae varias plantas, pero el catálogo de ubicaciones solo cubre US90."
      ]
    },
    en: {
      purpose: "Crosses current inventory (SAP MB52) against demand (SAP ZSD_DMND) to show which materials run out, when, and which ones have no inventory covering their demand. It is the dashboard version of the MB52_SD48_Analysis workbook (Final sheet), with the same calculation except for the demand rule (see limitations).",
      transformations: [
        "MB52: each row is mapped to a summarized location using the Base catalog (plant + storage location). Anything not in the catalog falls into Blank.",
        "MB52: Unrestricted = available; Total = Unrestricted + Quality Inspection + Blocked. All plants and storage locations are summed per material.",
        "ZSD_DMND: rows without a date are dropped. Demand is the sum of requirements (negative Qty_Valor) per material and date; receipts (ShipNt, PchOrd, PurRqs, PlOrd, PrdOrd, QM lot) are not counted.",
        "Horizon: P1 = past due + 1st month from the analysis date; P2 = 2nd month; P3 = 3rd month.",
        "Analysis date = latest MB52 file date. Workable days = Monday to Saturday within the 3 months."
      ],
      measures: [
        "Total 3M demand = P1 + P2 + P3.",
        "Average daily demand = Total 3M demand / 3-month workable days.",
        "Average coverage days = floor(Inventory / daily demand), capped at the workable days.",
        "Coverage % = Inventory / Total 3M demand, capped at 101% (shown as > 100%).",
        "Stockout date = first day on which past-due plus cumulative demand from the analysis date reaches the inventory.",
        "SAP coverage days = workable days from the analysis date to the stockout date, minus 1.",
        "Shortfall (units) = MAX(0, Total 3M demand − Inventory). Added by the dashboard."
      ],
      rules: [
        "No demand: total 3M demand = 0.",
        "Immediate shortage: inventory ≤ 0, or past-due demand already meets or exceeds inventory.",
        "Below rolling 3M coverage: inventory does not reach the 3-month demand.",
        "Covered rolling 3M: inventory covers the full 3-month demand.",
        "Warehouse = US90 / ZLD1 (Direct Material) only."
      ],
      limitations: [
        "Demand differs from the MB52_SD48_Analysis workbook: the notebook takes the absolute value of the net Qty_Valor per date and so counts receipts as demand. Here only requirements count. Future receipts are not added to inventory either: shortfall is against today's inventory.",
        "Inventory and demand may come from different days' extracts: check the dates in the sources table.",
        "Quantities are in each material's base unit: summing across materials only gives an order of magnitude.",
        "Stock in transfer and MB52 returns are not considered.",
        "MB52 includes several plants, but the location catalog only covers US90."
      ]
    }
  }
};

const I18N = {
  es: {
    backToPortal: "Volver al Portal", pageTitle: "Cobertura de Inventario vs Demanda",
    pageSub: "SAP MB52 × ZSD_DMND · faltantes y fecha de afectación.",
    updated: "Actualizado", extracted: "Extraído el", filters: "Filtros", clearFilters: "Limpiar Filtros",
    documentation: "Documentación", source: "Fuente", rows: "filas", rowsPerPage: "Filas por Página", showing: "Mostrando", of: "de",
    noData: "Sin datos para los filtros seleccionados.", loading: "Cargando datos…",
    copy_pn: "Copiar número de parte", copy_fail: "No se pudo copiar", copy_all: "Copiar números de parte", copied_all: "{n} copiados",
    search: "Buscar…", seleccionarTodo: "Seleccionar Todo", seleccionados: "seleccionados",
    sinValor: "(Sin Dato)", seleccionadaOculta: "seleccionada no se ve con esta búsqueda.",
    seleccionadasOcultas: "seleccionadas no se ven con esta búsqueda.",
    f_status: "Estatus", f_fecha: "Fecha de Faltante", f_MRP: "Controlador MRP",
    f_Material_Type: "Tipo de Material", f_Material_Group: "Grupo de Material",
    f_q: "Búsqueda", f_semana: "Semana", f_Material: "Material", f_ubic: "Ubicación", f_kpi: "Tarjeta",
    desde: "Desde", hasta: "Hasta", fueraRango: "materiales sin fecha de faltante quedan fuera del rango.",
    basis: "Inventario Base", basisUn: "Disponible (Unrestricted)", basisTot: "Total (Unr. + QI + Bloq.)",
    analysisDate: "Fecha de Análisis", workDays: "Días Hábiles 3M", horizon: "Horizonte hasta",
    k_imm: "Faltante Inmediato", k_below: "Bajo Cobertura 3M", k_sinInv: "Con Demanda y sin Inventario",
    k_d30: "Se Agotan en el 1er Mes", k_ok: "Cubiertos 3M", k_ofDemand: "de los materiales con demanda.",
    v_status: "Materiales por Estatus de Cobertura",
    v_semana: "Fecha de Afectación del Faltante", v_semana_sub: "Materiales por semana en que se acaba el inventario.",
    v_top: "Mayor Faltante en Unidades", v_top_sub: "Top 15 · demanda 3M menos inventario · unidad base del material.",
    v_ubic: "Inventario Disponible por Ubicación", v_ubic_sub: "Unrestricted de MB52 de los materiales filtrados.",
    inmediato: "Inmediato", materiales: "materiales", unidades: "unidades",
    detail: "Cobertura por Material (Vista Final)", buscarMat: "Buscar Material o Descripción…",
    c_Material: "Material", c_Material_Description: "Descripción", c_status: "Estatus",
    c_stockout: "Fecha de Faltante", c_sapDays: "Días SAP de Cobertura", c_inv: "Inventario",
    c_faltante: "Faltante (Unidades)", c_covPct: "% de Cobertura", c_MRP: "MRP",
    "c_Warehouse Available Inventory": "Inventario en Almacén", c_Unrestricted: "Disponible (Unrestricted)",
    c_Total_Inventory: "Inventario Total", "c_Warehouse Share of Available Inventory": "% del Disponible en Almacén",
    "c_Non-Warehouse Available Inventory": "Disponible Fuera de Almacén",
    "c_Past_Due_+_Period_1_Demand": "Demanda Vencida + P1", c_Period_2_Demand: "Demanda P2", c_Period_3_Demand: "Demanda P3",
    c_Total_Demand_Exposure: "Demanda Total 3M", c_Average_Daily_Demand: "Demanda Diaria Promedio",
    "c_Warehouse Average Coverage Days": "Días Cobertura Almacén", c_Available_Average_Days_Coverage: "Días Cobertura Disponible",
    c_Total_Average_Days_Coverage: "Días Cobertura Total", "c_Warehouse Demand Coverage %": "% Cobertura Almacén",
    "c_Available_Demand_Coverage_%": "% Cobertura Disponible", "c_Total_Demand_Coverage_%": "% Cobertura Total",
    c_Unrestricted_Stockout_Date: "Fecha Faltante (Disponible)", c_Total_Inventory_Stockout_Date: "Fecha Faltante (Total)",
    c_Available_SAP_Days_Coverage: "Días SAP Cobertura (Disponible)", c_Total_SAP_Days_Coverage: "Días SAP Cobertura (Total)",
    c_Unrestricted_Status: "Estatus (Disponible)", c_Total_Inventory_Status: "Estatus (Total)",
    c_Material_Type: "Tipo de Material", c_Material_Group: "Grupo de Material",
    purpose: "Propósito", sources: "Fuentes de Datos", transformations: "Transformaciones",
    measures: "Diccionario de Medidas", rules: "Reglas de Negocio", limitations: "Limitaciones Conocidas",
    contact: "Contacto", qc: "Controles de Calidad del Cálculo",
    s_fuente: "Fuente", s_sistema: "Sistema", s_ruta: "Ruta", s_archivo: "Archivo", s_extraido: "Extraído el",
    s_actualizado: "Actualizado", s_filas: "Filas",
    qc_sinMapear: "Combinaciones Planta/Almacén sin Ubicación en el Catálogo (Caen en Blank)",
    qc_totalMenor: "Materiales con Inventario Total Menor que el Disponible",
    qc_materiales: "Materiales en la Vista Final", qc_sd48: "Renglones de ZSD_DMND con Fecha",
    i_medida: "Medida", i_calculo: "Cálculo", i_filtros: "Filtros", i_gran: "Granularidad",
    degradedTitle: "Datos incompletos — el tablero está en modo degradado.",
    degradedStructure: "No llegó el catálogo de estatus. Las gráficas van en orden alfabético y sin color por severidad; las tarjetas de estatus no se calculan. La tabla de detalle SÍ es confiable.",
    errorTitle: "No se pudieron leer los datos del tablero.",
    errorDetail: "No respondió ninguna de las rutas de datos. Nada de lo que se ve es confiable hasta que carguen.",
    faltaFuente: "Falta una fuente de datos.",
    semiTitle: "Datos semi-ficticios — forma real, identidades inventadas.",
    semiDetail: "Salen de un corte real con clientes, materiales, documentos y personas cambiados, y los montos movidos ±15 %. Sirven para analizar con datos parecidos a los reales; no para decidir.",
    demoTitle: "Datos inventados — no son de SAP.",
    demoDetail: "Sirven para probar el tablero: la forma es la del reporte, los números no son reales.",
    cortesTitle: "Inventario y demanda son de cortes distintos.",
    cortesDetail: "El cruce compara días diferentes; un material puede verse en faltante (o cubierto) solo por el desfase.",
    diag: "Diagnóstico", diagTitle: "Diagnóstico del Último Redibujo",
    m_sub: "Demanda por fecha (barras) y demanda acumulada contra el inventario (líneas).",
    m_sinDemanda: "Este material no tiene demanda dentro del horizonte.",
    m_acum: "Demanda Acumulada", m_dia: "Demanda del Día", m_inv: "Inventario", m_vencida: "Vencida"
  },
  en: {
    backToPortal: "Back to the Portal", pageTitle: "Inventory Coverage vs Demand",
    pageSub: "SAP MB52 × ZSD_DMND · shortages and impact date.",
    updated: "Updated", extracted: "Extracted on", filters: "Filters", clearFilters: "Clear Filters",
    documentation: "Documentation", source: "Source", rows: "rows", rowsPerPage: "Rows per Page", showing: "Showing", of: "of",
    noData: "No data for the selected filters.", loading: "Loading data…",
    copy_pn: "Copy part number", copy_fail: "Could not copy", copy_all: "Copy part numbers", copied_all: "{n} copied",
    search: "Search…", seleccionarTodo: "Select All", seleccionados: "selected",
    sinValor: "(No Value)", seleccionadaOculta: "selected item is hidden by this search.",
    seleccionadasOcultas: "selected are hidden by this search.",
    f_status: "Status", f_fecha: "Stockout Date", f_MRP: "MRP Controller",
    f_Material_Type: "Material Type", f_Material_Group: "Material Group",
    f_q: "Search", f_semana: "Week", f_Material: "Material", f_ubic: "Location", f_kpi: "Card",
    desde: "From", hasta: "To", fueraRango: "materials without a stockout date fall outside the range.",
    basis: "Inventory Basis", basisUn: "Available (Unrestricted)", basisTot: "Total (Unr. + QI + Blocked)",
    analysisDate: "Analysis Date", workDays: "3M Workable Days", horizon: "Horizon Until",
    k_imm: "Immediate Shortage", k_below: "Below Rolling 3M Coverage", k_sinInv: "With Demand and No Inventory",
    k_d30: "Run Out in the 1st Month", k_ok: "Covered Rolling 3M", k_ofDemand: "of materials with demand.",
    v_status: "Materials by Coverage Status",
    v_semana: "Shortage Impact Date", v_semana_sub: "Materials by the week their inventory runs out.",
    v_top: "Largest Shortfall in Units", v_top_sub: "Top 15 · 3M demand minus inventory · material base unit.",
    v_ubic: "Available Inventory by Location", v_ubic_sub: "MB52 Unrestricted of the filtered materials.",
    inmediato: "Immediate", materiales: "materials", unidades: "units",
    detail: "Coverage by Material (Final View)", buscarMat: "Search Material or Description…",
    c_Material: "Material", c_Material_Description: "Material_Description", c_status: "Status",
    c_stockout: "Stockout Date", c_sapDays: "SAP Coverage Days", c_inv: "Inventory",
    c_faltante: "Shortfall (Units)", c_covPct: "Coverage %", c_MRP: "MRP",
    "c_Warehouse Available Inventory": "Warehouse Available Inventory", c_Unrestricted: "Unrestricted",
    c_Total_Inventory: "Total_Inventory", "c_Warehouse Share of Available Inventory": "Warehouse Share of Available Inventory",
    "c_Non-Warehouse Available Inventory": "Non-Warehouse Available Inventory",
    "c_Past_Due_+_Period_1_Demand": "Past_Due_+_Period_1_Demand", c_Period_2_Demand: "Period_2_Demand", c_Period_3_Demand: "Period_3_Demand",
    c_Total_Demand_Exposure: "Total_Demand_Exposure", c_Average_Daily_Demand: "Average_Daily_Demand",
    "c_Warehouse Average Coverage Days": "Warehouse Average Coverage Days", c_Available_Average_Days_Coverage: "Available_Average_Days_Coverage",
    c_Total_Average_Days_Coverage: "Total_Average_Days_Coverage", "c_Warehouse Demand Coverage %": "Warehouse Demand Coverage %",
    "c_Available_Demand_Coverage_%": "Available_Demand_Coverage_%", "c_Total_Demand_Coverage_%": "Total_Demand_Coverage_%",
    c_Unrestricted_Stockout_Date: "Unrestricted_Stockout_Date", c_Total_Inventory_Stockout_Date: "Total_Inventory_Stockout_Date",
    c_Available_SAP_Days_Coverage: "Available_SAP_Days_Coverage", c_Total_SAP_Days_Coverage: "Total_SAP_Days_Coverage",
    c_Unrestricted_Status: "Unrestricted_Status", c_Total_Inventory_Status: "Total_Inventory_Status",
    c_Material_Type: "Material_Type", c_Material_Group: "Material_Group",
    purpose: "Purpose", sources: "Data Sources", transformations: "Transformations",
    measures: "Measure Dictionary", rules: "Business Rules", limitations: "Known Limitations",
    contact: "Contact", qc: "Calculation Quality Checks",
    s_fuente: "Source", s_sistema: "System", s_ruta: "Path", s_archivo: "File", s_extraido: "Extracted on",
    s_actualizado: "Updated", s_filas: "Rows",
    qc_sinMapear: "Plant/Storage Location Combinations Missing from the Catalog (Fall into Blank)",
    qc_totalMenor: "Materials with Total Inventory Below Available",
    qc_materiales: "Materials in the Final View", qc_sd48: "ZSD_DMND Rows with a Date",
    i_medida: "Measure", i_calculo: "Calculation", i_filtros: "Filters", i_gran: "Granularity",
    degradedTitle: "Incomplete data — this dashboard is running degraded.",
    degradedStructure: "The status catalog did not arrive. Charts are alphabetical and without severity colors; status cards are not computed. The detail table IS reliable.",
    errorTitle: "The dashboard data could not be read.",
    errorDetail: "None of the data paths responded. Nothing on screen is reliable until the data loads.",
    faltaFuente: "A data source is missing.",
    semiTitle: "Semi-fictitious data — real shape, made-up identities.",
    semiDetail: "Built from a real cut with customers, materials, documents and people replaced, and amounts shifted ±15%. Good for analysis on realistic data; not for decisions.",
    demoTitle: "Made-up data — not from SAP.",
    demoDetail: "They are for testing the dashboard: the layout is the report's, the numbers are not real.",
    cortesTitle: "Inventory and demand come from different extracts.",
    cortesDetail: "The cross compares different days; a material may look short (or covered) only because of the gap.",
    diag: "Diagnostics", diagTitle: "Last Redraw Diagnostics",
    m_sub: "Demand by date (bars) and cumulative demand against inventory (lines).",
    m_sinDemanda: "This material has no demand inside the horizon.",
    m_acum: "Cumulative Demand", m_dia: "Daily Demand", m_inv: "Inventory", m_vencida: "Past Due"
  }
};

/* ============================================================
   ESTADO
   ============================================================ */
let META = {};
let rawData = [];
let DEMANDA = {};
let UBIC = {};
let lang = leerLS("dash_lang") || CONFIG.lang.default;
if (!CONFIG.lang.enabled.includes(lang)) lang = CONFIG.lang.default;
let basis = "un";
let pageSize = (() => { const v = +leerLS("mb52_page_size"); return CONFIG.detail.pageSizes.includes(v) ? v : CONFIG.detail.pageSize; })();
const filterState = { panel: {}, desde: "", hasta: "", q: "", crossfilter: null };
const sortState = [];
let currentPage = 1;
let cargaFallo = false;
const DIAG = { etapas: {}, visuales: {} };

const t = k => (I18N[lang] && I18N[lang][k] !== undefined) ? I18N[lang][k] : k;

/* ============================================================
   NUMEROS COPIABLES — ⧉ al lado de cada numero que se busca en SAP u Oracle
   ============================================================ */
/* navigator.clipboard solo existe en HTTPS o en localhost. El portal se abre
   por HTTP en la red de la planta: sin el metodo viejo, el boton no hace nada. */
async function copiarTexto(txt) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(txt);
      return true;
    }
  } catch (e) { /* se intenta el metodo viejo */ }
  const ta = document.createElement("textarea");
  ta.value = txt; ta.setAttribute("readonly", "");
  ta.style.position = "fixed"; ta.style.opacity = "0";
  document.body.appendChild(ta); ta.select();
  let ok = false;
  try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
  ta.remove();
  return ok;
}
/* El boton guarda el valor exacto del dato en data-pn: sin espacios ni texto de al lado.
   Se arma con nodos (textContent), asi el valor nunca pasa por innerHTML. */
function pnBoton(v) {
  const b = document.createElement("button");
  b.type = "button"; b.className = "pn-copy"; b.dataset.pn = String(v);
  b.title = t("copy_pn"); b.setAttribute("aria-label", t("copy_pn")); b.textContent = "⧉";
  return b;
}
function pnNodo(v) {
  const f = document.createDocumentFragment();
  if (v === null || v === undefined || v === "") { f.append("–"); return f; }
  const s = document.createElement("span"); s.className = "pn"; s.textContent = String(v);
  f.append(s, pnBoton(v));
  return f;
}
function avisoCopia(b, ok, textoOk, original) {
  b.classList.toggle("is-copied", ok);
  b.textContent = ok ? (textoOk || "✓") : "✕";
  b.title = ok ? (b.dataset.pn || textoOk || "") : t("copy_fail");
  setTimeout(() => { b.classList.remove("is-copied"); b.textContent = original; b.title = t("copy_pn"); }, 1200);
}
/* En fase de CAPTURA (el `true` del final): corre antes que el click del
   renglon, que abre el detalle o pone un filtro cruzado. Asi copiar no dispara
   nada mas, y seleccionar el numero con el mouse tampoco. */
document.addEventListener("click", e => {
  const b = e.target.closest(".pn-copy");
  if (b) {
    e.preventDefault(); e.stopPropagation();
    copiarTexto(b.dataset.pn).then(ok => avisoCopia(b, ok, "✓", "⧉"));
    return;
  }
  if (e.target.closest(".pn") && String(window.getSelection() || "").trim())
    e.stopPropagation();
}, true);
function leerLS(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function guardarLS(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* sin storage: no pasa nada */ } }
const $ = id => document.getElementById(id);

/* ============================================================
   ESTATUS: orden, rol y color salen de meta.filters.status
   ============================================================ */
const ST = { lista: [], rolDe: {}, degradado: false };
function initEstatus() {
  const cat = (META.filters && META.filters.status) || [];
  if (cat.length) {
    ST.lista = cat;
    ST.degradado = false;
  } else {
    const vals = [...new Set(rawData.flatMap(r => [r.Unrestricted_Status, r.Total_Inventory_Status]).filter(Boolean))].sort();
    ST.lista = vals.map(v => ({ valor: v, rol: null, es: v, en: v }));
    ST.degradado = vals.length > 0;
  }
  ST.rolDe = {};
  ST.lista.forEach(s => { ST.rolDe[s.valor] = s.rol; });
}
const nombreEstatus = v => { const s = ST.lista.find(x => x.valor === v); return s ? (s[lang] || s.valor) : v; };
const rolEstatus = v => ST.rolDe[v] || null;
function colorRol(rol, i) {
  if (rol === "critical") return cssVar("--c-critical");
  if (rol === "warn") return cssVar("--c-warn");
  if (rol === "ok") return cssVar("--c-ok");
  if (rol === "neutral") return cssVar("--c-neutral");
  return cssVar(`--c-cat-${Math.min((i || 0) + 1, 5)}`);
}

/* ============================================================
   UTILIDADES
   ============================================================ */
function cssVar(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
function conAlfa(hex, a) {
  const h = hex.replace("#", "");
  if (h.length !== 6) return hex;
  const n = parseInt(h, 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}
const valorCrudo = v => (v === null || v === undefined) ? "" : v;
const ISO = /^\d{4}-\d{2}-\d{2}$/;
/* Fechas como texto ISO: se arman y comparan en UTC para que la zona horaria no las corra un dia. */
function isoAUTC(iso) { const [y, m, d] = iso.split("-").map(Number); return Date.UTC(y, m - 1, d); }
function utcAISO(ms) { return new Date(ms).toISOString().slice(0, 10); }
function lunesDe(iso) { const ms = isoAUTC(iso); const dow = (new Date(ms).getUTCDay() + 6) % 7; return utcAISO(ms - dow * 864e5); }
function hoyISO() { const d = new Date(); return utcAISO(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())); }
function diasEntre(a, b) { return Math.round((isoAUTC(b) - isoAUTC(a)) / 864e5); }

function fmtNum(v, dec) {
  if (v === null || v === undefined || v === "" || Number.isNaN(+v)) return "–";
  const n = +v;
  const s = Math.abs(n).toLocaleString("en-US", { minimumFractionDigits: dec || 0, maximumFractionDigits: dec || 0 });
  return n < 0 ? `(${s})` : s;
}
function fmtPct(v) {
  if (v === null || v === undefined || v === "") return "–";
  if (+v > 1) return "> 100%";
  return (v * 100).toFixed(1) + "%";
}
function fmtFecha(iso) {
  if (!iso || !ISO.test(iso)) return "–";
  const [y, m, d] = iso.split("-");
  return lang === "es" ? `${d}/${m}/${y}` : `${m}/${d}/${y}`;
}
function fmtCorta(iso) {
  const [, m, d] = iso.split("-");
  const mes = new Date(Date.UTC(2000, +m - 1, 1)).toLocaleString(lang === "es" ? "es-MX" : "en-US", { month: "short", timeZone: "UTC" });
  const corto = mes.replace(".", "");
  return `${+d} ${corto.charAt(0).toUpperCase()}${corto.slice(1)}`;   // "19 oct" -> "19 Oct"
}
function abbr(n) {
  const a = Math.abs(n);
  if (a >= 1e9) return (n / 1e9).toFixed(1) + "B";
  if (a >= 1e6) return (n / 1e6).toFixed(1) + "M";
  if (a >= 1e3) return (n / 1e3).toFixed(1) + "K";
  return Math.round(n).toLocaleString("en-US");
}

/* ============================================================
   DATOS — campos que dependen de la base de inventario elegida
   ============================================================ */
function derivar() {
  const un = basis === "un";
  const hoy = META.analysis_date;
  rawData.forEach(r => {
    r.status = un ? r.Unrestricted_Status : r.Total_Inventory_Status;
    r.stockout = un ? r.Unrestricted_Stockout_Date : r.Total_Inventory_Stockout_Date;
    r.sapDays = un ? r.Available_SAP_Days_Coverage : r.Total_SAP_Days_Coverage;
    r.inv = un ? r.Unrestricted : r.Total_Inventory;
    r.covPct = un ? r["Available_Demand_Coverage_%"] : r["Total_Demand_Coverage_%"];
    r.faltante = r.Total_Demand_Exposure > 0 ? Math.max(0, r.Total_Demand_Exposure - r.inv) : 0;
    r.semana = !r.stockout ? "" : (r.stockout === hoy ? "INM" : lunesDe(r.stockout));
  });
}

/* ============================================================
   KPIs — la condicion va por ROL de estatus, nunca por el texto
   ============================================================ */
const KPIS = [
  { id: "imm", label: "k_imm", rol: "critical", pred: r => rolEstatus(r.status) === "critical" },
  { id: "below", label: "k_below", rol: "warn", pred: r => rolEstatus(r.status) === "warn" },
  { id: "sinInv", label: "k_sinInv", rol: "critical", pred: r => r.Total_Demand_Exposure > 0 && r.inv <= 0 },
  { id: "d30", label: "k_d30", rol: "warn",
    pred: r => !!r.stockout && r.stockout !== META.analysis_date && META.periodos && r.stockout < META.periodos.p1_fin },
  { id: "ok", label: "k_ok", rol: "ok", pred: r => rolEstatus(r.status) === "ok" }
];

/* ============================================================
   FILTRADO — una sola puerta de redibujo
   ============================================================ */
function matchesPanel(r) {
  for (const [f, vals] of Object.entries(filterState.panel)) {
    if (vals && vals.length && !vals.includes(valorCrudo(r[f]))) return false;
  }
  if (filterState.desde || filterState.hasta) {
    if (!r.stockout) return false;
    if (filterState.desde && r.stockout < filterState.desde) return false;
    if (filterState.hasta && r.stockout > filterState.hasta) return false;
  }
  if (filterState.q) {
    const q = filterState.q.toLowerCase();
    if (!String(r.Material).toLowerCase().includes(q) &&
        !String(r.Material_Description || "").toLowerCase().includes(q)) return false;
  }
  return true;
}
function matchesCrossfilter(r, cf) {
  if (!cf) return true;
  if (cf.field === "kpi") return cf.values.some(id => { const k = KPIS.find(x => x.id === id); return k && k.pred(r); });
  if (cf.field === "ubic") return cf.values.some(u => UBIC[r.Material] && UBIC[r.Material][u]);
  return cf.values.includes(valorCrudo(r[cf.field]));
}
/* exceptField: el visual que origino la seleccion se dibuja sin ella (y atenua lo no seleccionado). */
function getFilteredData(exceptField) {
  const cf = filterState.crossfilter;
  const usarCf = cf && cf.field !== exceptField ? cf : null;
  return rawData.filter(r => matchesPanel(r) && matchesCrossfilter(r, usarCf));
}
function comparar(va, vb) {
  const na = va === null || va === undefined || va === "", nb = vb === null || vb === undefined || vb === "";
  if (na || nb) return na === nb ? 0 : (na ? 1 : -1);          // vacios siempre al final
  if (typeof va === "number" && typeof vb === "number") return va - vb;
  return String(va).localeCompare(String(vb), "en", { numeric: true });
}
function getSortedData() {
  const d = getFilteredData();
  if (!sortState.length) return d;
  return d.sort((a, b) => {
    for (const { field, dir } of sortState) {
      const c = comparar(a[field], b[field]);
      if (c) return dir === "asc" ? c : -c;
    }
    return 0;
  });
}
function medir(nombre, fn) {
  const t0 = performance.now(); fn(); void document.body.offsetHeight;
  DIAG.etapas[nombre] = Math.round(performance.now() - t0);
}
function applyFilters() {
  const t0 = performance.now();
  medir("kpis", renderKPIs);
  CHARTS.forEach(c => medir(c.id, () => c.update()));
  medir("tabla", renderTable);
  renderChips(); updateFilterBadge(); renderNotaFechas(); syncURL();
  DIAG.etapas.total = Math.round(performance.now() - t0);
}
function setCrossfilter(field, value, multi) {
  const cf = filterState.crossfilter;
  if (cf && cf.field === field) {
    const tiene = cf.values.includes(value);
    if (multi) cf.values = tiene ? cf.values.filter(v => v !== value) : cf.values.concat(value);
    else cf.values = (tiene && cf.values.length === 1) ? [] : [value];   // segundo click deselecciona
    if (!cf.values.length) filterState.crossfilter = null;
  } else {
    filterState.crossfilter = { field, values: [value] };
  }
  currentPage = 1;
  applyFilters();
}
function limpiarTodo() {
  filterState.panel = {}; filterState.desde = ""; filterState.hasta = ""; filterState.q = "";
  filterState.crossfilter = null; currentPage = 1;
  $("fDesde").value = ""; $("fHasta").value = ""; $("tblBuscar").value = "";
  construirFiltros(); applyFilters();
}

/* ============================================================
   PANEL DE FILTROS
   ============================================================ */
const panelEl = $("filterPanel");
$("btnFilterOpen").addEventListener("click", () => { panelEl.classList.add("is-open"); redibujarCharts(); });
$("btnFilterClose").addEventListener("click", () => { panelEl.classList.remove("is-open"); redibujarCharts(); });
document.addEventListener("keydown", e => {
  if (e.key !== "Escape") return;
  panelEl.classList.remove("is-open"); cerrarModal(); closeDoc();
});
$("btnClear").addEventListener("click", limpiarTodo);

function countActiveFilters() {
  let n = Object.values(filterState.panel).filter(v => v && v.length).length;
  if (filterState.desde || filterState.hasta) n++;
  if (filterState.q) n++;
  return n + (filterState.crossfilter ? 1 : 0);
}
function updateFilterBadge() {
  const n = countActiveFilters(), b = $("filterBadge");
  b.textContent = n; b.hidden = n === 0;
}
function etiquetaCampoValor(f, v) {
  if (f === "status") return nombreEstatus(v);
  if (f === "semana") return v === "INM" ? t("inmediato") : fmtFecha(v);
  if (f === "kpi") { const k = KPIS.find(x => x.id === v); return k ? t(k.label) : v; }
  return etiquetaValor(f, v);
}
function renderChips() {
  const box = $("chips"); box.textContent = "";
  const add = (label, onX) => {
    const c = document.createElement("span"); c.className = "chip";
    c.textContent = label + " ";                     // valores de datos/URL: siempre textContent
    const x = document.createElement("span"); x.className = "chip__x"; x.textContent = "✕";
    x.addEventListener("click", onX); c.appendChild(x); box.appendChild(c);
  };
  Object.entries(filterState.panel).forEach(([f, vals]) => {
    if (!vals || !vals.length) return;
    if (vals.length > 3) {
      add(`${t("f_" + f)}: ${vals.length} ${t("seleccionados")}`, () => {
        delete filterState.panel[f]; currentPage = 1; construirFiltros(); applyFilters(); });
      return;
    }
    vals.forEach(v => add(`${t("f_" + f)}: ${etiquetaCampoValor(f, v)}`, () => {
      filterState.panel[f] = filterState.panel[f].filter(x => x !== v);
      if (!filterState.panel[f].length) delete filterState.panel[f];
      currentPage = 1; construirFiltros(); applyFilters();
    }));
  });
  if (filterState.desde || filterState.hasta) {
    add(`${t("f_fecha")}: ${fmtFecha(filterState.desde) } → ${fmtFecha(filterState.hasta)}`, () => {
      filterState.desde = ""; filterState.hasta = ""; $("fDesde").value = ""; $("fHasta").value = "";
      currentPage = 1; applyFilters();
    });
  }
  if (filterState.q) add(`${t("f_q")}: ${filterState.q}`, () => {
    filterState.q = ""; $("tblBuscar").value = ""; currentPage = 1; applyFilters(); });
  const cf = filterState.crossfilter;
  if (cf) {
    const vals = cf.values.length > 3 ? `${cf.values.length} ${t("seleccionados")}`
      : cf.values.map(v => etiquetaCampoValor(cf.field, v)).join(", ");
    add(`${t("f_" + cf.field)}: ${vals}`, () => { filterState.crossfilter = null; currentPage = 1; applyFilters(); });
  }
}
function syncURL() {
  const p = new URLSearchParams();
  if (basis !== "un") p.set("base", basis);
  Object.entries(filterState.panel).forEach(([f, v]) => v && v.length && p.set(f, v.join("|")));
  if (filterState.desde) p.set("desde", filterState.desde);
  if (filterState.hasta) p.set("hasta", filterState.hasta);
  if (filterState.q) p.set("q", filterState.q);
  history.replaceState(null, "", p.toString() ? "?" + p : location.pathname);
}
/* Lista blanca de NOMBRES y de VALORES: un valor solo entra si existe en el catalogo del campo. */
function readURL() {
  const campos = new Set([...document.querySelectorAll(".filter-group[data-field]")].map(g => g.dataset.field));
  new URLSearchParams(location.search).forEach((v, k) => {
    if (k === "base" && (v === "un" || v === "tot")) basis = v;
    else if ((k === "desde" || k === "hasta") && ISO.test(v)) filterState[k] = v;
    else if (k === "q") filterState.q = v.slice(0, 60);
    else if (campos.has(k)) {
      const validos = new Set(opcionesDe(k).map(o => o.v));
      const vals = v.split("|").filter(x => validos.has(x));
      if (vals.length) filterState.panel[k] = vals;
    }
  });
  $("fDesde").value = filterState.desde; $("fHasta").value = filterState.hasta; $("tblBuscar").value = filterState.q;
}

const FILTRO_SELECT_ALL = 5;
const FILTRO_PLEGABLE = 12;
const panelUI = { tocado: {}, busca: {} };

function etiquetaValor(campo, valor) {
  if (valorCrudo(valor) === "") return t("sinValor");
  if (campo === "status") return nombreEstatus(valor);
  return String(valor).replace(/\s+/g, " ").trim() || String(valor);
}
function opcionesDe(campo) {
  const cuenta = new Map();
  rawData.forEach(r => {
    const v = valorCrudo(r[campo]);
    cuenta.set(v, (cuenta.get(v) || 0) + 1);
  });
  if (campo === "status") {
    return ST.lista.map(s => ({ v: s.valor, txt: etiquetaValor(campo, s.valor), n: cuenta.get(s.valor) || 0 }));
  }
  return [...cuenta.keys()]
    .map(v => ({ v, txt: etiquetaValor(campo, v), n: cuenta.get(v) }))
    .sort((a, b) => a.v === "" ? 1 : b.v === "" ? -1 : a.txt.localeCompare(b.txt, lang, { numeric: true }));
}
function construirFiltros() {
  document.querySelectorAll(".filter-group[data-field]").forEach(g => {
    const campo = g.dataset.field;
    const ops = opcionesDe(campo);
    const sel = filterState.panel[campo] || [];
    const plegable = ops.length > FILTRO_PLEGABLE;
    const buscable = ops.length > FILTRO_SELECT_ALL;
    const abierto = panelUI.tocado[campo] === undefined ? (!plegable || sel.length > 0) : panelUI.tocado[campo];
    g.classList.toggle("filter-group--plegable", plegable);
    g.classList.toggle("filter-group--abierto", abierto);
    g.textContent = "";

    const cab = document.createElement("div"); cab.className = "filter-group__label";
    if (plegable) { const ch = document.createElement("span"); ch.className = "filter-group__chev"; ch.textContent = "▶"; cab.appendChild(ch); }
    const tit = document.createElement("span"); tit.textContent = t("f_" + campo); cab.appendChild(tit);
    const cn = document.createElement("span");
    cn.className = "filter-group__n" + (sel.length ? " filter-group__n--activo" : "");
    cn.textContent = sel.length ? `${sel.length}/${ops.length}` : ops.length;
    cab.appendChild(cn);
    if (plegable) cab.addEventListener("click", () => {
      panelUI.tocado[campo] = !g.classList.contains("filter-group--abierto");
      g.classList.toggle("filter-group--abierto", panelUI.tocado[campo]);
    });
    g.appendChild(cab);

    if (buscable) {
      const b = document.createElement("input"); b.type = "search"; b.className = "filter-buscar";
      b.placeholder = `${t("search").replace("…", "")} ${t("f_" + campo).toLowerCase()}…`;
      b.value = panelUI.busca[campo] || "";
      b.addEventListener("input", () => {
        panelUI.busca[campo] = b.value;
        if (b.value) { panelUI.tocado[campo] = true; g.classList.add("filter-group--abierto"); }
        pintar();
      });
      g.appendChild(b);
    }
    const cuerpo = document.createElement("div"); cuerpo.className = "filter-group__cuerpo"; g.appendChild(cuerpo);
    const caja = document.createElement("div"); caja.className = "filter-opts"; cuerpo.appendChild(caja);
    const pie = document.createElement("div"); cuerpo.appendChild(pie);

    function marcar(valores, prender) {
      const ahora = new Set(filterState.panel[campo] || []);
      valores.forEach(v => prender ? ahora.add(v) : ahora.delete(v));
      if (ahora.size) filterState.panel[campo] = [...ahora]; else delete filterState.panel[campo];
      currentPage = 1; construirFiltros(); applyFilters();
    }
    function pintar() {
      const q = (panelUI.busca[campo] || "").trim().toLowerCase();
      const lista = q ? ops.filter(o => o.txt.toLowerCase().includes(q)) : ops;
      caja.textContent = "";
      if (!lista.length) { const d = document.createElement("div"); d.className = "filter-vacio"; d.textContent = t("noData"); caja.appendChild(d); }
      if (ops.length > FILTRO_SELECT_ALL && lista.length) {
        const marcadas = lista.filter(o => sel.includes(o.v)).length;
        const l = document.createElement("label"); l.className = "filter-opt filter-opt--todos";
        const i = document.createElement("input"); i.type = "checkbox";
        i.checked = marcadas === lista.length; i.indeterminate = marcadas > 0 && marcadas < lista.length;
        i.addEventListener("change", () => marcar(lista.map(o => o.v), i.checked));
        const sp = document.createElement("span");
        sp.textContent = q ? `${t("seleccionarTodo")} (${lista.length})` : t("seleccionarTodo");
        l.append(i, sp); caja.appendChild(l);
      }
      lista.forEach(o => {
        const l = document.createElement("label"); l.className = "filter-opt"; l.title = o.txt;
        const i = document.createElement("input"); i.type = "checkbox"; i.checked = sel.includes(o.v);
        i.addEventListener("change", () => marcar([o.v], i.checked));
        const s = document.createElement("span"); s.textContent = o.txt;
        const n = document.createElement("span"); n.className = "filter-opt__n"; n.textContent = o.n.toLocaleString("en-US");
        l.append(i, s, n); caja.appendChild(l);
      });
      const ocultas = sel.filter(v => !lista.some(o => o.v === v)).length;
      pie.textContent = "";
      if (ocultas) { const d = document.createElement("div"); d.className = "filter-vacio";
        d.textContent = `${ocultas} ${t(ocultas === 1 ? "seleccionadaOculta" : "seleccionadasOcultas")}`; pie.appendChild(d); }
    }
    pintar();
  });
}

/* Rango de fechas de faltante: acotado a lo que existe en los datos */
function initFechas() {
  const fechas = rawData.flatMap(r => [r.Unrestricted_Stockout_Date, r.Total_Inventory_Stockout_Date]).filter(Boolean).sort();
  ["fDesde", "fHasta"].forEach(id => {
    if (fechas.length) { $(id).min = fechas[0]; $(id).max = fechas[fechas.length - 1]; }
    $(id).addEventListener("change", () => {
      const v = $(id).value;
      filterState[id === "fDesde" ? "desde" : "hasta"] = ISO.test(v) ? v : "";
      currentPage = 1; applyFilters();
    });
  });
}
function renderNotaFechas() {
  const nota = $("fechasNota");
  if (!filterState.desde && !filterState.hasta) { nota.textContent = ""; return; }
  const sinFecha = getFilteredDataSinFechas().filter(r => !r.stockout).length;
  nota.textContent = sinFecha ? `${sinFecha.toLocaleString("en-US")} ${t("fueraRango")}` : "";
}
function getFilteredDataSinFechas() {
  const d = filterState.desde, h = filterState.hasta;
  filterState.desde = ""; filterState.hasta = "";
  const out = getFilteredData();
  filterState.desde = d; filterState.hasta = h;
  return out;
}

let tBuscar;
$("tblBuscar").addEventListener("input", e => {
  clearTimeout(tBuscar);
  tBuscar = setTimeout(() => { filterState.q = e.target.value.trim().slice(0, 60); currentPage = 1; applyFilters(); }, 200);
});

/* Base de inventario: interruptor de dos estados */
$("basisToggle").addEventListener("click", e => {
  const b = e.target.closest("button[data-basis]"); if (!b) return;
  if (b.dataset.basis === basis) return;
  basis = b.dataset.basis;
  pintarBase(); derivar(); construirFiltros(); currentPage = 1; applyFilters();
});
function pintarBase() {
  document.querySelectorAll("#basisToggle button[data-basis]").forEach(b =>
    b.classList.toggle("is-active", b.dataset.basis === basis));
}
function renderToolbarInfo() {
  const el = $("toolbarInfo"); el.textContent = "";
  if (!META.analysis_date) return;
  const partes = [
    [t("analysisDate"), fmtFecha(META.analysis_date)],
    [t("workDays"), String(META.workable_days_3m)],
    [t("horizon"), fmtFecha(META.periodos && META.periodos.p3_fin)]
  ];
  partes.forEach(([k, v], i) => {
    if (i) el.appendChild(document.createTextNode(" · "));
    el.appendChild(document.createTextNode(k + ": "));
    const b = document.createElement("b"); b.textContent = v; el.appendChild(b);
  });
}

/* ============================================================
   KPIs
   ============================================================ */
function renderKPIs() {
  const row = $("kpiRow"); row.textContent = "";
  const data = getFilteredData("kpi");
  const conDemanda = data.filter(r => r.Total_Demand_Exposure > 0).length;
  const cf = filterState.crossfilter;
  KPIS.forEach(k => {
    const usaEstatus = k.id === "imm" || k.id === "below" || k.id === "ok";
    // Sin datos se pinta "–", nunca 0: un cero dice "no hay faltantes", que no es lo que paso.
    const n = (cargaFallo || (usaEstatus && ST.degradado)) ? null : data.filter(k.pred).length;
    const card = document.createElement("div");
    card.className = `card kpi kpi--${k.rol}`;
    if (cf && cf.field === "kpi" && cf.values.includes(k.id)) card.classList.add("is-active");
    const v = document.createElement("div"); v.className = "kpi__value"; v.textContent = n === null ? "–" : n.toLocaleString("en-US");
    const l = document.createElement("div"); l.className = "kpi__label"; l.textContent = t(k.label);
    const s = document.createElement("div"); s.className = "kpi__sub";
    s.textContent = (n !== null && conDemanda) ? `${(n / conDemanda * 100).toFixed(1)}% ${t("k_ofDemand")}` : "–";
    card.append(v, l, s);
    card.addEventListener("click", e => setCrossfilter("kpi", k.id, e.ctrlKey || e.metaKey));
    row.appendChild(card);
  });
  // El i del bloque de tarjetas va en la primera tarjeta
  const primera = row.firstElementChild;
  if (primera) { const h = document.createElement("div"); h.className = "card__header"; h.style.margin = "0"; primera.prepend(h); attachInfo(primera, "kpi"); }
}

/* ============================================================
   GRAFICAS (Chart.js local). Cada una expone update().
   ============================================================ */
Chart.register(ChartDataLabels);
Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
Chart.defaults.font.size = 11;
Chart.defaults.animation.duration = 240;
Chart.defaults.plugins.legend.display = false;

function crearChart(id, field, cfg) {
  const canvas = $(id);
  const box = canvas.parentElement;
  const vacio = box.querySelector(".empty-state");
  const obj = { id, field, chart: null, claves: [] };
  obj.update = () => {
    const data = getFilteredData(field);
    const r = cfg.calcular(data);
    obj.claves = r.claves;
    const cf = filterState.crossfilter;
    const sel = cf && cf.field === field ? cf.values : null;
    const colores = r.colores.map((c, i) => (sel && !sel.includes(r.claves[i])) ? conAlfa(c, 0.25) : c);
    vacio.hidden = r.valores.some(v => v > 0);
    DIAG.visuales[id] = { puntos: r.valores.length, conValor: r.valores.filter(v => v > 0).length };
    if (!obj.chart) {
      obj.chart = new Chart(canvas, {
        type: "bar",
        data: { labels: r.etiquetas, datasets: [{ data: r.valores, backgroundColor: colores, borderRadius: 3, maxBarThickness: 46 }] },
        options: Object.assign({
          responsive: true, maintainAspectRatio: false,
          onClick: (e, els) => {
            if (!els.length) return;
            setCrossfilter(field, obj.claves[els[0].index], e.native && (e.native.ctrlKey || e.native.metaKey));
          },
          onHover: (e, els) => { e.native.target.style.cursor = els.length ? "pointer" : "default"; }
        }, cfg.opciones())
      });
      canvas.addEventListener("dblclick", e => {
        const els = obj.chart.getElementsAtEventForMode(e, "nearest", { intersect: true }, false);
        if (!els.length && filterState.crossfilter) { filterState.crossfilter = null; currentPage = 1; applyFilters(); }
      });
    } else {
      obj.chart.data.labels = r.etiquetas;
      obj.chart.data.datasets[0].data = r.valores;
      obj.chart.data.datasets[0].backgroundColor = colores;
      Object.assign(obj.chart.options, cfg.opciones());
      obj.chart.update();
    }
  };
  return obj;
}
const ejeCfg = () => ({ grid: { color: conAlfa(cssVar("--c-border"), 0.6) }, ticks: { color: cssVar("--c-text-muted"), callback: function (v) { return abbr(v); } } });
const ejeCat = () => ({ grid: { display: false }, ticks: { color: cssVar("--c-text"), autoSkip: false } });
const labelsCfg = (fmt, align) => ({
  anchor: "end", align: align || "end", clamp: true, offset: 2, color: cssVar("--c-text"),
  font: { weight: "600", size: 11 }, formatter: (v) => v > 0 ? fmt(v) : ""
});

const CHARTS = [
  crearChart("chStatus", "status", {
    calcular: data => {
      const cuenta = {}; data.forEach(r => { cuenta[r.status] = (cuenta[r.status] || 0) + 1; });
      const claves = ST.lista.map(s => s.valor);
      return { claves, etiquetas: claves.map(nombreEstatus), valores: claves.map(k => cuenta[k] || 0),
               colores: claves.map((k, i) => colorRol(rolEstatus(k), i)) };
    },
    opciones: () => {
      return { indexAxis: "y", layout: { padding: { right: 70 } },
        scales: { x: Object.assign(ejeCfg(), { beginAtZero: true }), y: ejeCat() },
        plugins: { datalabels: Object.assign(labelsCfg(v => v.toLocaleString("en-US")), { clamp: false }),
          tooltip: { callbacks: { label: c => ` ${c.raw.toLocaleString("en-US")} ${t("materiales")}` } } } };
    }
  }),
  crearChart("chSemana", "semana", {
    calcular: data => {
      const cuenta = {}; data.forEach(r => { if (r.semana) cuenta[r.semana] = (cuenta[r.semana] || 0) + 1; });
      const claves = ["INM"];
      if (META.analysis_date && META.periodos) {
        let s = lunesDe(META.analysis_date);
        const fin = META.periodos.p3_fin;
        while (s < fin) { claves.push(s); s = utcAISO(isoAUTC(s) + 7 * 864e5); }
      }
      return { claves, etiquetas: claves.map(k => k === "INM" ? t("inmediato") : fmtCorta(k)),
               valores: claves.map(k => cuenta[k] || 0),
               colores: claves.map(k => k === "INM" ? cssVar("--c-critical") : cssVar("--c-warn")) };
    },
    opciones: () => ({ layout: { padding: { top: 18 } },
      scales: { y: Object.assign(ejeCfg(), { beginAtZero: true }), x: Object.assign(ejeCat(), { ticks: { color: cssVar("--c-text"), autoSkip: false, maxRotation: 0, font: { size: 10 } } }) },
      plugins: { datalabels: labelsCfg(v => v.toLocaleString("en-US")),
        tooltip: { callbacks: {
          title: c => c[0].dataIndex === 0 ? t("inmediato") : `${t("f_semana")} ${fmtFecha(CHARTS[1].claves[c[0].dataIndex])}`,
          label: c => ` ${c.raw.toLocaleString("en-US")} ${t("materiales")}` } } } })
  }),
  crearChart("chTop", "Material", {
    calcular: data => {
      const top = data.filter(r => r.faltante > 0).sort((a, b) => b.faltante - a.faltante).slice(0, CONFIG.topN);
      CHARTS_TOP_DESC = top.map(r => r.Material_Description || "");
      return { claves: top.map(r => r.Material), etiquetas: top.map(r => r.Material), valores: top.map(r => r.faltante),
               colores: top.map(r => colorRol(rolEstatus(r.status))) };
    },
    opciones: () => ({ indexAxis: "y", layout: { padding: { right: 56 } },
      scales: { x: Object.assign(ejeCfg(), { beginAtZero: true }), y: Object.assign(ejeCat(), { ticks: { color: cssVar("--c-text"), autoSkip: false, font: { family: cssVar("--font-mono"), size: 10 } } }) },
      plugins: { datalabels: Object.assign(labelsCfg(abbr), { clamp: false }),
        tooltip: { callbacks: {
          title: c => `${c[0].label} · ${CHARTS_TOP_DESC[c[0].dataIndex] || ""}`,
          label: c => ` ${t("c_faltante")}: ${fmtNum(c.raw)}` } } } })
  }),
  crearChart("chUbic", "ubic", {
    calcular: data => {
      const suma = {}, mats = {};
      data.forEach(r => {
        const u = UBIC[r.Material]; if (!u) return;
        Object.entries(u).forEach(([loc, v]) => { suma[loc] = (suma[loc] || 0) + v; mats[loc] = (mats[loc] || 0) + 1; });
      });
      const claves = ((META.filters && META.filters.ubicaciones) || Object.keys(suma)).slice()
        .sort((a, b) => (suma[b] || 0) - (suma[a] || 0));
      CHARTS_UBIC_MATS = claves.map(k => mats[k] || 0);
      return { claves, etiquetas: claves, valores: claves.map(k => Math.max(0, suma[k] || 0)),
               colores: claves.map(() => cssVar("--c-cat-2")) };
    },
    opciones: () => ({ indexAxis: "y", layout: { padding: { right: 56 } },
      scales: { x: Object.assign(ejeCfg(), { beginAtZero: true }), y: ejeCat() },
      plugins: { datalabels: Object.assign(labelsCfg(abbr), { clamp: false }),
        tooltip: { callbacks: { label: c => ` ${fmtNum(c.raw)} ${t("unidades")} · ${CHARTS_UBIC_MATS[c.dataIndex].toLocaleString("en-US")} ${t("materiales")}` } } } })
  })
];
let CHARTS_TOP_DESC = [];
let CHARTS_UBIC_MATS = [];
function redibujarCharts() { setTimeout(() => CHARTS.forEach(c => c.chart && c.chart.resize()), 260); }

/* ============================================================
   TABLA DE DETALLE
   ============================================================ */
function columnasTabla() {
  const sufijo = basis === "un" ? " (Unrestricted)" : " (Total)";
  return [
    { field: "Material", type: "text", pn: true },
    { field: "Material_Description", type: "desc" },
    { field: "status", type: "status", sufijo },
    { field: "stockout", type: "date", sufijo },
    { field: "sapDays", type: "int", sufijo },
    { field: "inv", type: "num", total: true, sufijo },
    { field: "Warehouse Available Inventory", type: "num", total: true },
    { field: "Past_Due_+_Period_1_Demand", type: "num", total: true },
    { field: "Period_2_Demand", type: "num", total: true },
    { field: "Period_3_Demand", type: "num", total: true },
    { field: "Total_Demand_Exposure", type: "num", total: true },
    { field: "faltante", type: "num", total: true, barra: true },
    { field: "covPct", type: "pct", sufijo },
    { field: "Average_Daily_Demand", type: "dec" },
    { field: "MRP", type: "text" }
  ];
}
const etiquetaCol = c => t("c_" + c.field) + (c.sufijo || "");
function celda(r, c) {
  const v = r[c.field];
  switch (c.type) {
    case "num": return fmtNum(v);
    case "int": return fmtNum(v);
    case "dec": return fmtNum(v, 1);
    case "pct": return fmtPct(v);
    case "date": return fmtFecha(v);
    case "status": return nombreEstatus(v);
    default: return v === null || v === undefined || v === "" ? "–" : String(v);
  }
}
function renderTable() {
  const cols = columnasTabla();
  const data = getSortedData();
  const size = pageSize;
  const pages = Math.max(1, Math.ceil(data.length / size));
  currentPage = Math.min(currentPage, pages);
  const slice = data.slice((currentPage - 1) * size, currentPage * size);
  const maxBarra = Math.max(1, ...data.map(r => r.faltante || 0));

  const head = $("detailHead"); head.textContent = "";
  cols.forEach(c => {
    const th = document.createElement("th");
    const s = sortState.find(x => x.field === c.field);
    th.textContent = etiquetaCol(c);
    const ind = document.createElement("span"); ind.className = "sort-ind";
    ind.textContent = s ? (s.dir === "asc" ? "▲" : "▼") : "▲"; th.appendChild(ind);
    if (s) th.classList.add("is-sorted");
    th.addEventListener("click", e => { toggleSort(c.field, e.shiftKey); renderTable(); });
    head.appendChild(th);
  });

  const body = $("detailBody"); body.textContent = "";
  if (!data.length) {
    const tr = document.createElement("tr"); const td = document.createElement("td");
    td.colSpan = cols.length; td.className = "empty-state"; td.textContent = t("noData");
    tr.appendChild(td); body.appendChild(tr);
  }
  slice.forEach(r => {
    const tr = document.createElement("tr");
    tr.addEventListener("click", () => abrirModal(r));
    cols.forEach(c => {
      const td = document.createElement("td");
      if (["num", "int", "dec", "pct"].includes(c.type)) td.className = "num";
      if (c.type === "date") td.className = "date";
      if (c.type === "desc") { td.className = "desc"; td.title = r[c.field] || ""; }
      if (["num", "int", "dec"].includes(c.type) && r[c.field] < 0) td.classList.add("neg");
      if (c.type === "status") {
        const p = document.createElement("span"); p.className = `pill pill--${rolEstatus(r.status) || "neutral"}`;
        p.textContent = celda(r, c); td.appendChild(p);
      } else if (c.barra) {
        const w = document.createElement("span"); w.className = "bar-cell";
        const b = document.createElement("span"); b.className = "bar-cell__bar";
        b.style.width = `${Math.round((r[c.field] || 0) / maxBarra * 60)}px`;
        const txt = document.createElement("span"); txt.textContent = celda(r, c);
        w.append(b, txt); td.appendChild(w);
      } else if (c.pn) td.appendChild(pnNodo(r[c.field]));
      else td.textContent = celda(r, c);
      tr.appendChild(td);
    });
    body.appendChild(tr);
  });

  const foot = $("detailFoot"); foot.textContent = "";
  if (data.length) {
    const tr = document.createElement("tr");
    cols.forEach((c, i) => {
      const td = document.createElement("td");
      if (i === 0) td.textContent = "Total";
      if (c.total) { td.className = "num"; td.textContent = fmtNum(data.reduce((s, r) => s + (+r[c.field] || 0), 0)); }
      tr.appendChild(td);
    });
    foot.appendChild(tr);
  }
  renderPager(data.length, pages);
  $("rowCount").textContent = `${data.length.toLocaleString("en-US")} ${t("rows")}`;
  DIAG.visuales.tabla = { filas: slice.length, total: data.length };
}
function toggleSort(field, shift) {
  const i = sortState.findIndex(s => s.field === field);
  if (!shift) { const keep = i >= 0 ? sortState[i] : null; sortState.length = 0; if (keep) sortState.push(keep); }
  const j = sortState.findIndex(s => s.field === field);
  if (j < 0) sortState.push({ field, dir: "asc" });
  else if (sortState[j].dir === "asc") sortState[j].dir = "desc";
  else sortState.splice(j, 1);
}
function renderPager(total, pages) {
  const size = pageSize;
  const from = total ? (currentPage - 1) * size + 1 : 0;
  const to = Math.min(currentPage * size, total);
  $("pagerRange").textContent = `${t("showing")} ${from.toLocaleString("en-US")}–${to.toLocaleString("en-US")} ${t("of")} ${total.toLocaleString("en-US")}`;
  const box = $("pagerPages"); box.textContent = "";
  const btn = (label, page, disabled, active) => {
    const b = document.createElement("button"); b.textContent = label; b.disabled = !!disabled;
    if (active) b.classList.add("is-active");
    b.addEventListener("click", () => { currentPage = page; renderTable(); });
    box.appendChild(b);
  };
  btn("‹", currentPage - 1, currentPage === 1);
  const win = [];
  for (let p = 1; p <= pages; p++) if (p === 1 || p === pages || Math.abs(p - currentPage) <= 1) win.push(p);
  win.forEach((p, i) => {
    if (i && p - win[i - 1] > 1) { const s = document.createElement("span"); s.textContent = "…"; box.appendChild(s); }
    btn(p, p, false, p === currentPage);
  });
  btn("›", currentPage + 1, currentPage === pages);
}

/* Filas por pagina: solo valores de la lista; se recuerda por navegador */
function initPageSize() {
  const sel = $("pageSize"); sel.textContent = "";
  CONFIG.detail.pageSizes.forEach(n => {
    const o = document.createElement("option"); o.value = n; o.textContent = n.toLocaleString("en-US");
    if (n === pageSize) o.selected = true;
    sel.appendChild(o);
  });
}
$("pageSize").addEventListener("change", e => {
  const v = +e.target.value;
  if (!CONFIG.detail.pageSizes.includes(v)) return;
  // Conserva la primera fila visible: se queda en la pagina que la contiene
  const primera = (currentPage - 1) * pageSize;
  pageSize = v; currentPage = Math.floor(primera / pageSize) + 1;
  guardarLS("mb52_page_size", v); renderTable();
});
initPageSize();

/* ============================================================
   EXPORTACION — la vista Final completa (mismas columnas del Excel)
   sobre el conjunto filtrado y ordenado. Cada valor pasa por un
   formateador que cubre todos los tipos: nada de arrays ni objetos.
   ============================================================ */
const FECHAS_EXPORT = new Set(["Unrestricted_Stockout_Date", "Total_Inventory_Stockout_Date"]);
function columnasExport() { return (META._columnas || []).filter(c => c !== "_i"); }
function valorExport(c, v) {
  if (v === null || v === undefined || v === "") return "";
  if (FECHAS_EXPORT.has(c)) return ISO.test(v) ? v : "";
  if (typeof v === "number") return v;
  return String(v);
}
function exportRows() {
  const cols = columnasExport();
  return getSortedData().map(r => {
    const o = {};
    cols.forEach(c => { o[t("c_" + c)] = valorExport(c, r[c]); });
    return o;
  });
}
function nombreArchivo(ext) {
  const d = new Date(), p = n => String(n).padStart(2, "0");
  const stamp = `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}`;
  return `${CONFIG.dashboardName}_cobertura-por-material_${stamp}.${ext}`;
}
/* Copia todos los numeros de la vista con los filtros puestos, sin repetidos, uno por renglon,
   para pegarlos directo en la seleccion multiple de SAP. */
$("btnCopyPn").addEventListener("click", e => {
  const b = e.currentTarget;
  const lista = [...new Set(getSortedData().map(r => r.Material).filter(v => v !== null && v !== undefined && v !== ""))];
  if (!lista.length) return;
  const txt = b.querySelector("[data-i18n]");
  copiarTexto(lista.join("\r\n")).then(ok => {
    b.classList.toggle("is-copied", ok);
    txt.textContent = ok ? t("copied_all").replace("{n}", lista.length.toLocaleString("en-US")) : t("copy_fail");
    setTimeout(() => { b.classList.remove("is-copied"); txt.textContent = t("copy_all"); }, 1600);
  });
});
$("btnCsv").addEventListener("click", () => {
  const rows = exportRows(); if (!rows.length) return;
  const headers = Object.keys(rows[0]);
  const csv = [headers.map(csvCelda).join(","), ...rows.map(r => headers.map(h => csvCelda(r[h])).join(","))].join("\r\n");
  descargar(new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" }), nombreArchivo("csv"));
});
$("btnXlsx").addEventListener("click", () => {
  const rows = exportRows(); if (!rows.length) return;
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.json_to_sheet(rows);
  ws["!autofilter"] = { ref: ws["!ref"] };
  ws["!cols"] = Object.keys(rows[0]).map(h => ({ wch: Math.min(40, Math.max(h.length + 2, ...rows.slice(0, 200).map(r => String(r[h]).length + 2))) }));
  XLSX.utils.book_append_sheet(wb, ws, "Final");
  const fuentes = META.fuentes || [];
  const meta = [
    ["Dashboard", CONFIG.dashboardName],
    [t("updated"), META.generated_at || ""],
    [t("analysisDate"), META.analysis_date || ""],
    [t("workDays"), META.workable_days_3m || ""],
    [t("basis"), t(basis === "un" ? "basisUn" : "basisTot")],
    [t("rows"), rows.length],
    [t("filters"), [...$("chips").querySelectorAll(".chip")].map(c => c.textContent.replace("✕", "").trim()).join(" | ")],
    [],
    [t("s_fuente"), t("s_sistema"), t("s_archivo"), t("s_extraido"), t("s_actualizado"), t("s_filas")],
    ...fuentes.map(f => [lang === "en" ? f.nombre_en : f.nombre, f.sistema, f.archivo, f.extraido_el, f.actualizado, f.filas])
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(meta), "Metadata");
  XLSX.writeFile(wb, nombreArchivo("xlsx"));
});
function descargar(blob, name) {
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

/* ============================================================
   FRESCURA — "Extraido el" de la fuente mas vieja manda el semaforo
   ============================================================ */
function renderFreshness() {
  const fuentes = META.fuentes || [];
  $("metaUpdated").textContent = META.generated_at || "–";
  $("ftrUpdated").textContent = META.generated_at || "–";
  $("ftrSources").textContent = fuentes.map(f => (lang === "en" ? f.nombre_en : f.nombre)).join(", ") || "–";
  const el = $("metaFreshness");
  const conFecha = fuentes.filter(f => f.extraido_el && ISO.test(f.extraido_el));
  if (!conFecha.length) { el.className = "freshness freshness--critical"; el.textContent = `⚠ ${t("extracted")}: –`; return; }
  const vieja = conFecha.reduce((a, b) => a.extraido_el < b.extraido_el ? a : b);
  const dias = diasEntre(vieja.extraido_el, hoyISO());
  const lvl = fuentes.some(f => f.falta) || dias > CONFIG.freshness.criticalDays ? "critical"
    : dias > CONFIG.freshness.warnDays ? "warn" : "ok";
  el.className = `freshness freshness--${lvl}`;
  el.textContent = `${lvl === "critical" ? "⚠ " : ""}${t("extracted")}: `;
  const b = document.createElement("b"); b.textContent = fmtFecha(vieja.extraido_el); el.appendChild(b);
  el.title = fuentes.map(f => `${lang === "en" ? f.nombre_en : f.nombre}: ${f.extraido_el ? fmtFecha(f.extraido_el) + " (" + diasEntre(f.extraido_el, hoyISO()) + "d)" : "–"}`).join("\n");
}

/* ============================================================
   BANDA DE AVISOS
   ============================================================ */
function renderBanner() {
  const el = $("banner");
  const avisos = [];
  if (cargaFallo) avisos.push(["critical", t("errorTitle"), t("errorDetail")]);
  else {
    if (META.semi) avisos.push(["warn", t("semiTitle"), t("semiDetail")]);
    else if (META.demo) avisos.push(["warn", t("demoTitle"), t("demoDetail")]);
    if (ST.degradado) avisos.push(["critical", t("degradedTitle"), t("degradedStructure")]);
    (META.fuentes || []).filter(f => f.falta).forEach(f => avisos.push(["critical", t("faltaFuente"), lang === "en" ? f.nombre_en : f.nombre]));
    const fechas = (META.fuentes || []).map(f => f.extraido_el).filter(f => f && ISO.test(f)).sort();
    if (fechas.length > 1 && diasEntre(fechas[0], fechas[fechas.length - 1]) > CONFIG.maxDiasEntreFuentes) {
      const det = (META.fuentes || []).map(f => `${lang === "en" ? f.nombre_en : f.nombre}: ${fmtFecha(f.extraido_el)}`).join(" · ");
      avisos.push(["warn", t("cortesTitle"), `${det}. ${t("cortesDetail")}`]);
    }
  }
  if (!avisos.length) { el.hidden = true; el.className = "banner"; return; }
  const nivel = avisos.some(a => a[0] === "critical") ? "critical" : "warn";
  el.className = `banner banner--${nivel}`;
  el.textContent = "";
  const ic = document.createElement("span"); ic.className = "banner__icon"; ic.textContent = "⚠";
  const body = document.createElement("div"); body.className = "banner__body";
  avisos.forEach(([, tit, det]) => {
    const a = document.createElement("span"); a.className = "banner__title"; a.textContent = tit;
    const b = document.createElement("span"); b.className = "banner__detail"; b.textContent = det;
    body.append(a, b);
  });
  el.append(ic, body);
  el.hidden = false;
}

/* ============================================================
   ICONO i POR VISUAL
   ============================================================ */
function attachInfo(cardEl, visualId) {
  const info = CONFIG.visuals[visualId] && CONFIG.visuals[visualId].info[lang];
  const header = cardEl.querySelector(".card__header");
  if (!info || !header) return;
  cardEl.querySelectorAll(".info-btn, .info-popover").forEach(e => e.remove());
  const btn = document.createElement("button");
  btn.className = "info-btn"; btn.textContent = "ⓘ"; btn.setAttribute("aria-label", "Info");
  const pop = document.createElement("div"); pop.className = "info-popover"; pop.hidden = true;
  const cerrar = document.createElement("button"); cerrar.className = "info-popover__close"; cerrar.textContent = "✕";
  pop.appendChild(cerrar);
  [["i_medida", info.medida], ["i_calculo", info.calculo, true], ["i_filtros", info.filtros], ["i_gran", info.granularidad]].forEach(([k, v, formula]) => {
    const row = document.createElement("div"); row.className = "info-popover__row";
    const key = document.createElement("div"); key.className = "info-popover__key"; key.textContent = t(k);
    const val = document.createElement(formula ? "span" : "div"); if (formula) val.className = "info-popover__formula";
    val.textContent = v; row.append(key, val); pop.appendChild(row);
  });
  btn.addEventListener("click", e => { e.stopPropagation(); pop.hidden = !pop.hidden; });
  pop.addEventListener("click", e => e.stopPropagation());
  cerrar.addEventListener("click", () => { pop.hidden = true; });
  header.appendChild(btn); cardEl.appendChild(pop);
}
document.addEventListener("click", () => document.querySelectorAll(".info-popover").forEach(p => { p.hidden = true; }));
document.addEventListener("keydown", e => { if (e.key === "Escape") document.querySelectorAll(".info-popover").forEach(p => { p.hidden = true; }); });
function attachInfos() {
  attachInfo($("cardStatus"), "status"); attachInfo($("cardSemana"), "semana");
  attachInfo($("cardTop"), "top"); attachInfo($("cardUbic"), "ubic");
}

/* ============================================================
   DOCUMENTACION Y DIAGNOSTICO
   ============================================================ */
function h3(txt) { const h = document.createElement("h3"); h.textContent = txt; return h; }
function lista(items) { const ul = document.createElement("ul"); (items || []).forEach(i => { const li = document.createElement("li"); li.textContent = i; ul.appendChild(li); }); return ul; }
function tablaDoc(cab, filas) {
  const tb = document.createElement("table"); tb.className = "tbl";
  const th = document.createElement("thead"); const tr = document.createElement("tr");
  cab.forEach(c => { const x = document.createElement("th"); x.textContent = c; tr.appendChild(x); });
  th.appendChild(tr); tb.appendChild(th);
  const bd = document.createElement("tbody");
  filas.forEach(f => { const r = document.createElement("tr"); f.forEach(v => { const td = document.createElement("td"); td.textContent = v === null || v === undefined ? "–" : String(v); r.appendChild(td); }); bd.appendChild(r); });
  tb.appendChild(bd); return tb;
}
function renderDoc() {
  const d = CONFIG.documentation[lang] || {};
  const body = $("docBody"); body.textContent = "";
  $("docTitle").textContent = t("documentation");
  const p = document.createElement("p"); p.textContent = d.purpose;
  body.append(h3(t("purpose")), p, h3(t("sources")));
  body.appendChild(tablaDoc([t("s_fuente"), t("s_sistema"), t("s_ruta"), t("s_archivo"), t("s_extraido"), t("s_actualizado"), t("s_filas")],
    (META.fuentes || []).map(f => [lang === "en" ? f.nombre_en : f.nombre, f.sistema, f.tabla, f.archivo, fmtFecha(f.extraido_el), f.actualizado, (f.filas || 0).toLocaleString("en-US")])));
  body.append(h3(t("transformations")), lista(d.transformations), h3(t("measures")), lista(d.measures),
              h3(t("rules")), lista(d.rules), h3(t("limitations")), lista(d.limitations), h3(t("qc")));
  const c = META.counts || {}, a = META.avisos || {};
  body.appendChild(tablaDoc(["", ""], [
    [t("qc_materiales"), (c.materiales || 0).toLocaleString("en-US")],
    [t("qc_sd48"), (c.sd48_filas_con_fecha || 0).toLocaleString("en-US")],
    [t("qc_sinMapear"), a.ubicaciones_sin_mapear],
    [t("qc_totalMenor"), a.total_menor_que_unrestricted]
  ]));
  const ct = document.createElement("p"); ct.textContent = "Contoso BI Team · Contoso Motors Americas";
  body.append(h3(t("contact")), ct);
}
const docPanel = $("docPanel"), docOv = $("docOverlay");
function openDoc() { renderDoc(); docPanel.classList.add("is-open"); docOv.hidden = false; }
function closeDoc() { docPanel.classList.remove("is-open"); docOv.hidden = true; }
$("btnDoc").addEventListener("click", openDoc);
$("btnDocClose").addEventListener("click", closeDoc);
docOv.addEventListener("click", closeDoc);

/* Lo que quedo en pantalla, medido, para diagnosticar sin abrir la consola */
$("btnDiag").addEventListener("click", () => {
  const lineas = [`${t("diagTitle")} · ${new Date().toLocaleString()}`, "", "ms:"];
  Object.entries(DIAG.etapas).forEach(([k, v]) => lineas.push(`  ${k}: ${v}`));
  lineas.push("", "visuales:");
  CHARTS.forEach(c => {
    const box = $(c.id).parentElement, rc = box.getBoundingClientRect(), dv = DIAG.visuales[c.id] || {};
    lineas.push(`  ${c.id}: ${dv.puntos} barras, ${dv.conValor} con valor · ${getComputedStyle(box).display} ${Math.round(rc.width)}x${Math.round(rc.height)}px`);
  });
  const tb = $("detailTable").getBoundingClientRect(), dt = DIAG.visuales.tabla || {};
  lineas.push(`  tabla: ${dt.filas} filas pintadas de ${dt.total} · ${Math.round(tb.width)}x${Math.round(tb.height)}px`);
  lineas.push("", `rawData: ${rawData.length} · base: ${basis} · lang: ${lang}`, `filtros: ${JSON.stringify(filterState)}`);
  const body = $("docBody"); body.textContent = "";
  $("docTitle").textContent = t("diag");
  const pre = document.createElement("div"); pre.className = "diag-box"; pre.textContent = lineas.join("\n");
  body.appendChild(pre);
  docPanel.classList.add("is-open"); docOv.hidden = false;
});

/* ============================================================
   MODAL DEL MATERIAL — demanda por fecha contra inventario
   ============================================================ */
let chMaterial = null;
function abrirModal(r) {
  $("modalTitle").textContent = `${r.Material} · ${r.Material_Description || ""}`;
  $("modalTitle").appendChild(pnBoton(r.Material));
  const grid = $("modalGrid"); grid.textContent = "";
  [[t("c_status") + (basis === "un" ? " (Unrestricted)" : " (Total)"), nombreEstatus(r.status)],
   [t("c_stockout"), fmtFecha(r.stockout)], [t("c_sapDays"), fmtNum(r.sapDays)], [t("c_faltante"), fmtNum(r.faltante)],
   [t("c_Unrestricted"), fmtNum(r.Unrestricted)], [t("c_Total_Inventory"), fmtNum(r.Total_Inventory)],
   [t("c_Warehouse Available Inventory"), fmtNum(r["Warehouse Available Inventory"])], [t("c_Total_Demand_Exposure"), fmtNum(r.Total_Demand_Exposure)]
  ].forEach(([k, v]) => {
    const d = document.createElement("div"); d.className = "modal__dato";
    const s = document.createElement("span"); s.textContent = k; const b = document.createElement("b"); b.textContent = v;
    d.append(s, b); grid.appendChild(d);
  });
  const serie = DEMANDA[r.Material] || [];
  const hoy = META.analysis_date;
  const vencida = serie.filter(([d]) => d < hoy).reduce((s, [, a]) => s + a, 0);
  const futuras = serie.filter(([d]) => d >= hoy);
  const etiquetas = [t("m_vencida"), ...futuras.map(([d]) => fmtFecha(d))];
  const dia = [vencida, ...futuras.map(([, a]) => a)];
  let acum = 0; const acumulada = dia.map(v => (acum += v));
  const vacio = $("chMaterial").parentElement.querySelector(".empty-state");
  vacio.hidden = acum > 0;
  const datos = {
    labels: etiquetas,
    datasets: [
      { type: "bar", label: t("m_dia"), data: dia, backgroundColor: conAlfa(cssVar("--c-cat-2"), 0.6), order: 3 },
      { type: "line", label: t("m_acum"), data: acumulada, borderColor: cssVar("--c-critical"), backgroundColor: cssVar("--c-critical"), pointRadius: 2, tension: 0, order: 1 },
      { type: "line", label: `${t("m_inv")} (${basis === "un" ? "Unrestricted" : "Total"})`, data: dia.map(() => r.inv), borderColor: cssVar("--c-ok"), borderDash: [6, 4], pointRadius: 0, order: 2 }
    ]
  };
  const opciones = { responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: true, position: "bottom" }, datalabels: { display: false },
      tooltip: { callbacks: { label: c => ` ${c.dataset.label}: ${fmtNum(c.raw)}` } } },
    scales: { y: Object.assign(ejeCfg(), { beginAtZero: true }), x: { ticks: { color: cssVar("--c-text-muted"), maxRotation: 0, autoSkip: true, autoSkipPadding: 12 }, grid: { display: false } } } };
  if (chMaterial) chMaterial.destroy();
  chMaterial = new Chart($("chMaterial"), { type: "bar", data: datos, options: opciones });
  $("modal").hidden = false;
}
function cerrarModal() { $("modal").hidden = true; }
$("btnModalClose").addEventListener("click", cerrarModal);
$("modal").addEventListener("click", e => { if (e.target.id === "modal") cerrarModal(); });

/* ============================================================
   IDIOMA — no resetea filtros ni selecciones
   ============================================================ */
function applyLang() {
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
  $("tblBuscar").placeholder = t("buscarMat");
  document.querySelectorAll("#langToggle button").forEach(b => b.classList.toggle("is-active", b.dataset.lang === lang));
  attachInfos();
  renderFreshness(); renderBanner(); renderToolbarInfo();
  if (rawData.length || cargaFallo) { construirFiltros(); applyFilters(); }
  if (docPanel.classList.contains("is-open")) renderDoc();
}
$("langToggle").addEventListener("click", e => {
  const b = e.target.closest("button[data-lang]"); if (!b) return;
  lang = b.dataset.lang; guardarLS("dash_lang", lang); applyLang();
});
if (CONFIG.lang.enabled.length < 2) $("langToggle").hidden = true;

/* ============================================================
   CARGA — portal primero, ./data/ en local. Sin datos de respaldo:
   si no llega nada, se dice.
   ============================================================ */
async function leerJSON(nombre) {
  for (const base of CONFIG.dataUrls) {
    try {
      const r = await fetch(base + nombre, { cache: "no-cache" });
      if (r.ok) return await r.json();
    } catch (e) { /* siguiente ruta */ }
  }
  throw new Error(nombre);
}
async function init() {
  $("btnPortal").href = CONFIG.portalUrl;
  pintarBase();
  applyLang();
  const t0 = performance.now();
  try {
    const [meta, dash] = await Promise.all([leerJSON("meta.json"), leerJSON("dashboard.json")]);
    META = meta || {};
    const cols = dash.final.columns;
    META._columnas = cols;
    rawData = dash.final.rows.map(fila => { const o = {}; cols.forEach((c, i) => { o[c] = fila[i]; }); return o; });
    DEMANDA = dash.demanda || {};
    UBIC = dash.ubicaciones || {};
  } catch (e) {
    cargaFallo = true;
  }
  DIAG.etapas.carga = Math.round(performance.now() - t0);
  $("loading").hidden = true;
  initEstatus();
  readURL();
  pintarBase();
  derivar();
  initFechas();
  construirFiltros();
  applyLang();
}
init();

let rt;
addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => CHARTS.forEach(c => c.chart && c.chart.resize()), 150); });
