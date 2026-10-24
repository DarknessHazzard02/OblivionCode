// Made by: Hazzard
"use strict";
/* ============================================================
   CONFIG — todo lo editable vive aqui. No tocar la logica abajo.
   ============================================================ */
const CONFIG = {
  dashboardName: "pastdue-open-orders",
  portalUrl: "/sop/",
  dataUrls: ["./data/"],   // portafolio: solo datos inventados
  lang: { enabled: ["es", "en"], default: "es" },
  freshness: { warnDays: 1, criticalDays: 3 },
  topRazones: 12,
  topFamilias: 50,
  detail: { pageSize: 25, pageSizes: [25, 50, 100, 250, 500, 1000] },
  rangos: ["1", "2-5", "6-15", "16-30", "31-60", "61-90", "91-180", "181+"],
  razonesSitio: ["PLANT PAST DUE", "CUSTOMER RELATED", "WITNESS"],

  visuals: {
    kpi: { info: {
      es: { medida: "Past due en dólares.", calculo: "SUM(Total $) de las líneas con estatus PAST DUE (mes actual, meses previos y D72). 1 día de gracia y On Hold se muestran aparte.", filtros: "Todos los filtros y selecciones, salvo la de las tarjetas.", granularidad: "Línea de orden." },
      en: { medida: "Past due in dollars.", calculo: "SUM(Total $) of lines with PAST DUE status (current month, prior months and D72). 1-day grace and On Hold are shown separately.", filtros: "All filters and selections except the cards' own.", granularidad: "Order line." } } },
    sitioTabla: { info: {
      es: { medida: "Executive Summary: past due por sitio responsable.", calculo: "SUM(Total $) por sitio y por razón capturada (Contoso PD = PLANT PAST DUE). Las dos últimas columnas comparan contra Request Date y Promise Date.", filtros: "Filtros del panel y selección de las gráficas.", granularidad: "Sitio (responsabilidad final después de la macro y los ajustes manuales)." },
      en: { medida: "Executive Summary: past due by responsible site.", calculo: "SUM(Total $) by site and by reason (Contoso PD = PLANT PAST DUE). The last two columns compare against Request Date and Promise Date.", filtros: "Panel filters and chart selections.", granularidad: "Site (final responsibility after the macro and manual adjustments)." } } },
    razonSitio: { info: {
      es: { medida: "Past Due Reason By Site.", calculo: "SUM(Total $) apilado por razón: Contoso PD, Customer Related y Witness.", filtros: "Filtros del panel y selección de las otras gráficas.", granularidad: "Sitio." },
      en: { medida: "Past Due Reason By Site.", calculo: "SUM(Total $) stacked by reason: Contoso PD, Customer Related and Witness.", filtros: "Panel filters and other charts' selection.", granularidad: "Site." } } },
    fechas: { info: {
      es: { medida: "Past due contra la fecha del cliente y contra la promesa.", calculo: "SUM(Total $) de las líneas past due cuya Request Date (o Promise Date) ya pasó a la fecha de corte.", filtros: "Filtros del panel y selección de las otras gráficas.", granularidad: "Sitio." },
      en: { medida: "Past due against the customer date and against the promise.", calculo: "SUM(Total $) of past-due lines whose Request Date (or Promise Date) is before the cut-off date.", filtros: "Panel filters and other charts' selection.", granularidad: "Site." } } },
    diaria: { info: {
      es: { medida: "Daily Past Due Trend.", calculo: "Past due de cada día, del historial capturado (manual/historial.csv) más el corte de hoy calculado.", filtros: "Solo responde al alcance y al filtro de división: el historial no guarda el detalle por línea.", granularidad: "Día hábil × división." },
      en: { medida: "Daily Past Due Trend.", calculo: "Each day's past due, from the captured history (manual/historial.csv) plus today's computed cut.", filtros: "Only follows the scope and the division filter: the history keeps no line detail.", granularidad: "Workday × division." } } },
    unDia: { info: {
      es: { medida: "Past Due < 1 Day.", calculo: "Dólares en el día de gracia: líneas cuya Schedule Ship Date cae en el último día hábil.", filtros: "Solo alcance y división.", granularidad: "Día hábil × división." },
      en: { medida: "Past Due < 1 Day.", calculo: "Dollars inside the grace day: lines whose Schedule Ship Date falls on the last workday.", filtros: "Scope and division only.", granularidad: "Workday × division." } } },
    mensual: { info: {
      es: { medida: "Monthly Past Due Trend.", calculo: "Último valor diario de cada mes (cierre de mes).", filtros: "Solo alcance y división.", granularidad: "Mes × división." },
      en: { medida: "Monthly Past Due Trend.", calculo: "Last daily value of each month (month close).", filtros: "Scope and division only.", granularidad: "Month × division." } } },
    hold: { info: {
      es: { medida: "Not On Hold vs On Hold By Plant.", calculo: "SUM(Total $) past due apilado por On Hold (Order Holds de CTR o AX Hold).", filtros: "Filtros del panel y selección de las otras gráficas.", granularidad: "Sitio." },
      en: { medida: "Not On Hold vs On Hold By Plant.", calculo: "Past-due SUM(Total $) stacked by On Hold (CTR Order Holds or AX Hold).", filtros: "Panel filters and other charts' selection.", granularidad: "Site." } } },
    plantaDiv: { info: {
      es: { medida: "Past Due By Plant (IMD vs HVACR).", calculo: "SUM(Total $) past due apilado por división.", filtros: "Filtros del panel y selección de las otras gráficas.", granularidad: "Sitio." },
      en: { medida: "Past Due By Plant (IMD vs HVACR).", calculo: "Past-due SUM(Total $) stacked by division.", filtros: "Panel filters and other charts' selection.", granularidad: "Site." } } },
    categoria: { info: {
      es: { medida: "Past Due Reasons (categoría).", calculo: "SUM(Total $) por categoría de la razón (catálogo manual/razones_categoria.csv). Undefined = la razón no está en el catálogo o la línea no tiene razón.", filtros: "Filtros del panel y selección de las otras gráficas.", granularidad: "Categoría." },
      en: { medida: "Past Due Reasons (category).", calculo: "SUM(Total $) by reason category (manual/razones_categoria.csv). Undefined = reason not in the catalog or the line has no reason.", filtros: "Panel filters and other charts' selection.", granularidad: "Category." } } },
    razon: { info: {
      es: { medida: "Razones con más past due.", calculo: "SUM(Total $) por razón: hold, método de pick up, freight terms o NO (sin inventario).", filtros: "Las 12 razones con más dólares en la selección actual.", granularidad: "Razón." },
      en: { medida: "Reasons with the most past due.", calculo: "SUM(Total $) by reason: hold, pick-up method, freight terms or NO (no inventory).", filtros: "Top 12 reasons by dollars in the current selection.", granularidad: "Reason." } } },
    familia: { info: {
      es: { medida: "Past Due Sales $ By Prod Family.", calculo: "SUM(Total $) por ProdLine (sales); el % es sobre el total past due de la selección.", filtros: "Top 50 familias de la selección actual.", granularidad: "ProdLine (sales)." },
      en: { medida: "Past Due Sales $ By Prod Family.", calculo: "SUM(Total $) by ProdLine (sales); % is over the selection's past-due total.", filtros: "Top 50 families in the current selection.", granularidad: "ProdLine (sales)." } } },
    rango: { info: {
      es: { medida: "Antigüedad del past due.", calculo: "Días = fecha de corte − Schedule Ship Date, agrupados como Sheet2 (columnas Y:Z).", filtros: "Filtros del panel y selección de las otras gráficas.", granularidad: "Rango de días." },
      en: { medida: "Past-due aging.", calculo: "Days = cut-off date − Schedule Ship Date, bucketed like Sheet2 (columns Y:Z).", filtros: "Panel filters and other charts' selection.", granularidad: "Day range." } } },
    bridge: { info: {
      es: { medida: "Bridge: número de marketing contra el past due del reporte.", calculo: "Marketing (manual) − líneas que el reporte no cuenta (día de gracia, Invoice Hold, HVAC Tier1, Entered, NLA) − ajustes manuales = past due del reporte. La diferencia no explicada es lo que sobra.", filtros: "Solo alcance y división.", granularidad: "División." },
      en: { medida: "Bridge: marketing number against the report's past due.", calculo: "Marketing (manual) − lines the report does not count (grace day, Invoice Hold, HVAC Tier1, Entered, NLA) − manual adjustments = report past due. The unexplained difference is what is left.", filtros: "Scope and division only.", granularidad: "Division." } } },
    bridgeCh: { info: {
      es: { medida: "De dónde sale la diferencia.", calculo: "Cada concepto del Bridge en dólares, por división.", filtros: "Solo alcance y división.", granularidad: "Concepto × división." },
      en: { medida: "Where the difference comes from.", calculo: "Each Bridge item in dollars, by division.", filtros: "Scope and division only.", granularidad: "Item × division." } } },
    ajustes: { info: {
      es: { medida: "Ajustes de responsabilidad capturados a mano.", calculo: "Cada renglón de manual/ajustes_responsabilidad.csv y si encontró su línea (orden + línea + item).", filtros: "Ninguno: se ven todos.", granularidad: "Ajuste." },
      en: { medida: "Hand-entered responsibility adjustments.", calculo: "Each row of manual/ajustes_responsabilidad.csv and whether it matched its line (order + line + item).", filtros: "None: all are shown.", granularidad: "Adjustment." } } }
  },

  documentation: {
    es: {
      purpose: "Reemplaza al archivo Past Due Open Orders: toma el Open Orders y las pestañas grises (inventario, tránsito, holds, pick up, override, MEPD), aplica las fórmulas de detailtab, la macro de asignación (Orgs_Assignment, Customerr, ovrwrite, Not_PD) y los ajustes manuales, y muestra el past due por sitio responsable, sus razones y su tendencia.",
      transformations: [
        "Estatus de origen (columna AZ): PERIOD que empieza con PAST DUE_PRIOR = Past Due Prior Month; con PAST DUE = Past Due Current Month; lo demás = Not Past Due.",
        "Inventario disponible para la línea (BD) = On-Hand de la org e item − cantidad de las líneas de la misma org e item con Schedule Ship Date anterior. Inventory on hand = YES si cubre la línea completa.",
        "Tránsito (BM) = In Transit (Oracle, destino) + AX Intransit (RVT-MS) + D72 manual. On hand + tránsito (CA) = disponible + tránsito.",
        "Holds (BH) = Hold Type de Order Holds por orden; si no hay, el de AX Hold. On Hold si la orden está en cualquiera de los dos.",
        "Razón (BQ) = hold → método de Customer Pick Up → freight terms que dan Customer/Commercial → NO si no hay inventario. Categoría (BR) desde el catálogo de razones.",
        "Macro: reasigna la responsabilidad (POM sales) por product line, item, planner, org, inventario y tránsito, en el mismo orden que el botón del archivo; luego Customer/Commercial para clientes de la lista y holds con inventario; luego Intransit/Logistic; al final Not_PD.",
        "Ajustes manuales (Sheet2): la responsabilidad que mandan Canadá y las plantas reemplaza a la de la macro, por orden + línea + item. La razón capturada por el sitio (p. ej. WITNESS) reemplaza a la calculada."
      ],
      measures: [
        "Past due = SUM(Total $) con estatus Past Due Prior Month, Past Due Current Month, D72 Past Due Prior Month o D72 Past Due Current Month.",
        "Contoso PD = past due con razón PLANT PAST DUE; Customer Related = CUSTOMER RELATED; Witness = WITNESS (capturado por el sitio).",
        "Días de atraso = fecha de corte − Schedule Ship Date; rango como Sheet2 (1, 2-5, 6-15, 16-30, 31-60, 61-90, 91-180, 181+).",
        "Past due vs Request Date: Request Date anterior al corte. Past due vs Promise Date: Promise Date anterior al corte y no anterior a Request Date (sin promesa, toma Request Date)."
      ],
      rules: [
        "Día de gracia: 1 día hábil sobre Schedule Ship Date. Si el corte es lunes, cubre viernes, sábado y domingo. Esas líneas pasan a 1 DAY PAST DUE y no cuentan como past due.",
        "No cuentan como past due: responsabilidad CMS IO Plant NLA (eliminaciones), grupo HVAC Tier1 OEM, OrderStatus INVOICE_HOLD y OrderStatus ENTERED.",
        "D72: el past due de la org D72 se marca aparte (D72 Past Due …) pero sí suma.",
        "Override SO en la división HVACR → Customer/Commercial (no en IMD).",
        "El reporte (Executive Summary) usa solo las divisiones marcadas en manual/divisiones.csv (IMD y HVACR). El interruptor Alcance muestra también las demás."
      ],
      limitations: [
        "Captura manual: divisiones, catálogo de razones, freight terms, clientes Customer/Commercial y especiales, responsabilidad por item, ajustes de Canadá/plantas, tránsito D72, razón por sitio, Bridge (número de marketing) e historial diario. Se editan a mano en la carpeta manual/ de la fuente; el tablero solo los lee.",
        "Día de gracia: el archivo original tiene dos reglas distintas (columna BL resta 1 día fijo; columna CE usa la fecha de orden y 1-2 días según el día de la semana). Aquí se usa la regla del proceso: 1 día hábil sobre Schedule Ship Date.",
        "Las fórmulas se calculan una vez, con la org original. En el Excel se recalculan mientras corre la macro (p. ej. cuando C71 pasa a C71-2).",
        "La tendencia diaria y mensual sale del historial: si no se guarda el historial del día, el punto de hoy se ve pero mañana no estará.",
        "Las fuentes reales llegan como Excel/CSV/correo; por ahora hay que guardarlas como CSV con los nombres de demo/CONTRATO.md."
      ]
    },
    en: {
      purpose: "Replaces the Past Due Open Orders workbook: takes the Open Orders report and the grey tabs (inventory, in-transit, holds, pick up, override, MEPD), applies the detailtab formulas, the assignment macro (Orgs_Assignment, Customerr, ovrwrite, Not_PD) and the manual adjustments, and shows past due by responsible site, its reasons and its trend.",
      transformations: [
        "Source status (column AZ): PERIOD starting with PAST DUE_PRIOR = Past Due Prior Month; with PAST DUE = Past Due Current Month; anything else = Not Past Due.",
        "Inventory available for the line (BD) = On-Hand of the org and item − quantity of lines with the same org and item and an earlier Schedule Ship Date. Inventory on hand = YES if it covers the full line.",
        "In-transit (BM) = In Transit (Oracle, destination) + AX Intransit (RVT-MS) + D72 manual. On hand + in-transit (CA) = available + in-transit.",
        "Holds (BH) = Order Holds Hold Type by order; otherwise the AX Hold one. On Hold if the order is in either.",
        "Reason (BQ) = hold → Customer Pick Up method → freight terms giving Customer/Commercial → NO if no inventory. Category (BR) from the reason catalog.",
        "Macro: reassigns responsibility (POM sales) by product line, item, planner, org, inventory and in-transit, in the same order as the workbook button; then Customer/Commercial for listed customers and holds with inventory; then Intransit/Logistic; finally Not_PD.",
        "Manual adjustments (Sheet2): the responsibility sent by Canada and the plants replaces the macro's, by order + line + item. The reason filled by the site (e.g. WITNESS) replaces the computed one."
      ],
      measures: [
        "Past due = SUM(Total $) with status Past Due Prior Month, Past Due Current Month, D72 Past Due Prior Month or D72 Past Due Current Month.",
        "Contoso PD = past due with reason PLANT PAST DUE; Customer Related = CUSTOMER RELATED; Witness = WITNESS (filled by the site).",
        "Days late = cut-off date − Schedule Ship Date; buckets as Sheet2 (1, 2-5, 6-15, 16-30, 31-60, 61-90, 91-180, 181+).",
        "Past due vs Request Date: Request Date before the cut-off. Past due vs Promise Date: Promise Date before the cut-off and not before Request Date (no promise: Request Date)."
      ],
      rules: [
        "Grace day: 1 workday on Schedule Ship Date. On a Monday cut-off it covers Friday, Saturday and Sunday. Those lines become 1 DAY PAST DUE and are not counted as past due.",
        "Not counted as past due: responsibility CMS IO Plant NLA (eliminations), group HVAC Tier1 OEM, OrderStatus INVOICE_HOLD and OrderStatus ENTERED.",
        "D72: org D72 past due is flagged separately (D72 Past Due …) but it does count.",
        "Override SO in the HVACR division → Customer/Commercial (not in IMD).",
        "The report (Executive Summary) only uses the divisions flagged in manual/divisiones.csv (IMD and HVACR). The Scope switch shows the others too."
      ],
      limitations: [
        "Manual capture: divisions, reason catalog, freight terms, Customer/Commercial and special customers, responsibility by item, Canada/plant adjustments, D72 in-transit, reason by site, Bridge (marketing number) and daily history. They are edited by hand in the source's manual/ folder; the dashboard only reads them.",
        "Grace day: the original workbook has two different rules (column BL subtracts a fixed day; column CE uses the order date and 1-2 days by weekday). This uses the process rule: 1 workday on Schedule Ship Date.",
        "Formulas are computed once, with the original org. In Excel they recalculate while the macro runs (e.g. when C71 becomes C71-2).",
        "Daily and monthly trends come from the history: if the day's history is not saved, today's point shows but will be gone tomorrow.",
        "Real sources arrive as Excel/CSV/email; for now they must be saved as CSV with the names in demo/CONTRATO.md."
      ]
    }
  }
};

const I18N = {
  es: {
    backToPortal: "Volver al Portal", pageTitle: "Past Due Open Orders",
    pageSub: "Past due por sitio responsable · razones · tendencia.",
    updated: "Actualizado", extracted: "Extraído el", filters: "Filtros", clearFilters: "Limpiar Filtros",
    documentation: "Documentación", source: "Fuente", rows: "filas", rowsPerPage: "Filas por Página", showing: "Mostrando", of: "de",
    noData: "Sin datos para los filtros seleccionados.", noHist: "No hay historial capturado para esta división.", loading: "Cargando datos…",
    copy_pn: "Copiar número de parte", copy_fail: "No se pudo copiar", copy_all: "Copiar números de parte", copied_all: "{n} copiados",
    search: "Buscar…", seleccionarTodo: "Seleccionar Todo", seleccionados: "seleccionados",
    sinValor: "(Sin Dato)", seleccionadaOculta: "seleccionada no se ve con esta búsqueda.",
    seleccionadasOcultas: "seleccionadas no se ven con esta búsqueda.",
    vw_resumen: "Resumen Ejecutivo", vw_tendencias: "Tendencias", vw_razones: "Razones y Familias",
    vw_bridge: "Bridge", vw_manual: "Captura Manual",
    alcance: "Alcance", scopePd: "Reporte (IMD + HVACR)", scopeTodas: "Todas las Divisiones",
    corte: "Corte", gracia: "Día de Gracia desde", lineas: "líneas",
    f_division: "División", f_pd: "Estatus Past Due", f_sitio: "Sitio", f_razon_sitio: "Razón (Sitio)",
    f_on_hold: "On Hold", f_rango: "Días de Atraso", f_org: "Org", f_resp: "Responsabilidad",
    f_prodline_sales: "Familia (ProdLine Sales)", f_cliente: "Cliente", f_q: "Búsqueda", f_kpi: "Tarjeta",
    f_categoria: "Categoría", f_razon: "Razón",
    k_pd: "Past Due Total", k_contoso: "Contoso PD (Planta)", k_cliente: "Customer Related", k_witness: "Witness",
    k_unDia: "En Día de Gracia (No Cuenta)", k_hold: "Past Due On Hold", k_del: "del past due", k_lineas: "líneas",
    contosoPd: "Contoso PD", customerRel: "Customer Related", witness: "Witness", total: "Total",
    vsCrd: "vs Request Date", vsProm: "vs Promise Date", sitio: "Sitio",
    v_sitioTabla: "Past Due por Sitio", v_sitioTabla_sub: "Executive Summary · clic en un sitio para filtrar.",
    v_razonSitio: "Past Due Reason by Site", v_razonSitio_sub: "Contoso PD, Customer Related y Witness por sitio.",
    v_fechas: "Past Due contra Request Date y Promise Date", v_fechas_sub: "Por sitio · líneas past due cuya fecha del cliente o de la promesa ya pasó.",
    v_diaria: "Daily Past Due Trend", v_diaria_sub: "Past due de cada día hábil por división.",
    v_unDia: "Past Due < 1 Day", v_unDia_sub: "Dólares en el día de gracia.",
    v_mensual: "Monthly Past Due Trend", v_mensual_sub: "Cierre de cada mes por división.",
    v_hold: "Not On Hold vs On Hold by Plant", v_hold_sub: "Past due por sitio, apilado por On Hold.",
    v_plantaDiv: "Past Due by Plant", v_plantaDiv_sub: "Past due por sitio, apilado por división.",
    v_categoria: "Past Due Reasons", v_categoria_sub: "Por categoría de la razón.",
    v_razon: "Razones con Más Past Due", v_razon_sub: "Top 12 razones en dólares.",
    v_familia: "Past Due Sales $ by Prod Family", v_familia_sub: "Top 50 familias · % del past due de la selección.",
    v_rango: "Antigüedad", v_rango_sub: "Past due por días de atraso sobre Schedule Ship Date.",
    v_bridge: "Bridge contra Marketing", v_bridge_sub: "Del número de marketing al past due del reporte.",
    v_bridgeCh: "Conceptos del Bridge", v_bridgeCh_sub: "Dólares por concepto y división.",
    v_fuentesMan: "Archivos de Captura Manual", v_fuentesMan_sub: "Lo que el tablero leyó de manual/ en este corte.",
    v_ajustes: "Ajustes de Responsabilidad", v_ajustes_sub: "Canadá y plantas · por orden + línea + item.",
    tagManual: "✎ Manual", manualTitle: "Captura Manual",
    manualDetail: "Estos datos NO vienen de Oracle ni de AX: se escriben a mano en la carpeta manual/ de la fuente (lo que en el Excel vive en Sheet2, Executive Summary Reference y Bridge). Hay que revisarlos en cada corte; el tablero los usa tal como están.",
    bridgeManual: "El número de marketing y las líneas de afiliadas se capturan a mano en manual/bridge_manual.csv. Lo demás sale del cálculo.",
    b_marketing: "Número de Marketing", b_UN_DIA: "− Día de Gracia (1 Day Past Due)", b_INVOICE_HOLD: "− Invoice Hold",
    b_HVAC_TIER1: "− HVAC Tier1 OEM", b_ENTERED: "− Órdenes Entered", b_NLA: "− NLA (Eliminaciones)",
    b_noExplicado: "− Diferencia No Explicada", b_reporte: "= Past Due del Reporte", b_sinMarketing: "Sin Número de Marketing Capturado",
    a_order: "Orden", a_line: "Línea", a_item: "Item", a_resp: "Responsabilidad", a_motivo: "Motivo", a_aprobo: "Aprobó",
    a_fecha: "Fecha", a_aplicado: "Aplicado", a_si: "Sí", a_no: "No Encontró la Línea",
    fm_archivo: "Archivo", fm_filas: "Filas", fm_fecha: "Modificado", fm_estado: "Estado", fm_ok: "Leído", fm_falta: "Falta", fm_noHay: "No Existe",
    detail: "Detalle por Línea", vistaDetalle: "Vista", buscarLinea: "Buscar Orden, Item o Cliente…",
    p_general: "Past Due (Todas las Responsabilidades)", p_t1: "1 · CMS IO Plant Northgate", p_t2: "2 · CMS IO Plant Valle Alto",
    p_t3: "3 · CMS IO Plant PLT1", p_t4: "4 · CMS IO Plant PLT2", p_t5: "5 · CMS IO Plant Asia", p_t6: "6 · Intransit/Logistic",
    p_t7: "7 · Distribución (Mesa Verde + Riverton)", p_t8: "8 · Buyout", p_t9: "9 · Customer/Commercial",
    p_t10: "10 · Holds y Customer Pick Up", p_custDet: "Customer Past Due Details", p_buyDet: "Buyout Past Due Details",
    p_todas: "Todas las Líneas (Incluye No Past Due)",
    p_sub_pd: "Solo Líneas Past Due", p_sub_todas: "Todas las Líneas del Alcance",
    c_division: "División", c_mktdiv: "Mkt DIV", c_org: "Org", c_grupo: "Group", c_cliente: "Cliente", c_orden: "Orden", c_linea: "Línea",
    c_item: "Item", c_desc: "Descripción", c_prodline: "ProdLine", c_prodline_sales: "ProdLine (Sales)", c_ssd: "Schedule Ship Date",
    c_req: "Request Date", c_prom: "Promise Date", c_ordenada: "Date Ordered", c_estatus_orden: "OrderStatus", c_qty: "Cantidad",
    c_total: "Total $", c_resp_origen: "POM Original", c_resp: "Responsabilidad", c_sitio: "Sitio", c_pd_origen: "Estatus Original",
    c_pd: "Estatus Past Due", c_motivo: "Por Qué No Cuenta", c_pd_crd: "PD vs Request", c_pd_prom: "PD vs Promise", c_dias: "Días",
    c_rango: "Rango", c_ship_status: "Shipment Status", c_oh_ship: "On Hand (Org)", c_oh_all: "On Hand (Todas)", c_disp: "Disponible",
    c_oh: "Inventory on Hand", c_transito_qty: "En Tránsito", c_transito: "Intransit?", c_oh_int: "OH + Tránsito?", c_holds: "Holds",
    c_on_hold: "On Hold", c_cpu: "Customer Pick Up", c_override: "Override SO", c_freight: "Freight Terms", c_razon: "Razón",
    c_categoria: "Categoría", c_razon_sitio: "Razón (Sitio)", c_especial: "Cliente Especial", c_manual: "Manual", c_comentario: "Comentario",
    c_incluida: "En Reporte",
    mo_UN_DIA: "Día de Gracia", mo_NLA: "NLA", mo_HVAC_TIER1: "HVAC Tier1 OEM", mo_INVOICE_HOLD: "Invoice Hold", mo_ENTERED: "Entered",
    man_ajuste: "Ajuste", man_razon: "Razón Sitio",
    purpose: "Propósito", sources: "Fuentes de Datos", transformations: "Transformaciones",
    measures: "Diccionario de Medidas", rules: "Reglas de Negocio", limitations: "Limitaciones Conocidas",
    contact: "Contacto", qc: "Controles de Calidad del Cálculo",
    s_fuente: "Fuente", s_sistema: "Sistema", s_archivo: "Archivo", s_extraido: "Extraído el", s_filas: "Filas", s_manual: "Manual",
    qc_filas: "Líneas del Open Orders", qc_sinSsd: "Líneas sin Schedule Ship Date", qc_undef: "Líneas Past Due con Razón Fuera del Catálogo",
    qc_respVacia: "Líneas Past Due sin Responsabilidad", qc_sinCat: "Mkt DIV sin Renglón en divisiones.csv", qc_ajustes: "Ajustes Manuales sin su Línea",
    i_medida: "Medida", i_calculo: "Cálculo", i_filtros: "Filtros", i_gran: "Granularidad",
    errorTitle: "No se pudieron leer los datos del tablero.",
    errorDetail: "No respondió ninguna de las rutas de datos. Nada de lo que se ve es confiable hasta que carguen.",
    faltaFuente: "Falta una fuente de datos.", faltaManual: "Falta un archivo de captura manual.",
    semiTitle: "Datos semi-ficticios — forma real, identidades inventadas.",
    semiDetail: "Salen de un corte real con clientes, materiales, documentos y personas cambiados, y los montos movidos ±15 %. Sirven para analizar con datos parecidos a los reales; no para decidir.",
    demoTitle: "Datos inventados — no son de Oracle ni de AX.",
    demoDetail: "Sirven para probar el tablero: la forma es la del reporte, los números no son reales.",
    ajustesTitle: "Hay ajustes manuales que no encontraron su línea.",
    ajustesDetail: "ajustes de manual/ajustes_responsabilidad.csv no se aplicaron: la orden, línea o item ya no está en el Open Orders. Revísalos en Captura manual.",
    catTitle: "Hay divisiones sin catálogo.", catDetail: "no están en manual/divisiones.csv y quedan fuera del reporte:",
    respTitle: "Hay past due sin responsabilidad.", respDetail: "líneas past due quedaron sin sitio (Org H05/R01 o sin regla). Aparecen como 'Sin asignar'.",
    diag: "Diagnóstico", diagTitle: "Diagnóstico del Último Redibujo",
    m_sub: "Cómo se llegó a la responsabilidad y al estatus de esta línea.",
    otros: "Otras", sinRazon: "(Sin Razón)"
  },
  en: {
    backToPortal: "Back to the Portal", pageTitle: "Past Due Open Orders",
    pageSub: "Past due by responsible site · reasons · trend.",
    updated: "Updated", extracted: "Extracted on", filters: "Filters", clearFilters: "Clear Filters",
    documentation: "Documentation", source: "Source", rows: "rows", rowsPerPage: "Rows per Page", showing: "Showing", of: "of",
    noData: "No data for the selected filters.", noHist: "No captured history for this division.", loading: "Loading data…",
    copy_pn: "Copy part number", copy_fail: "Could not copy", copy_all: "Copy part numbers", copied_all: "{n} copied",
    search: "Search…", seleccionarTodo: "Select All", seleccionados: "selected",
    sinValor: "(No Value)", seleccionadaOculta: "selected item is hidden by this search.",
    seleccionadasOcultas: "selected are hidden by this search.",
    vw_resumen: "Executive Summary", vw_tendencias: "Trends", vw_razones: "Reasons & Families",
    vw_bridge: "Bridge", vw_manual: "Manual Capture",
    alcance: "Scope", scopePd: "Report (IMD + HVACR)", scopeTodas: "All Divisions",
    corte: "Cut-Off", gracia: "Grace Day from", lineas: "lines",
    f_division: "Division", f_pd: "Past Due Status", f_sitio: "Site", f_razon_sitio: "Reason (Site)",
    f_on_hold: "On Hold", f_rango: "Days Late", f_org: "Org", f_resp: "Responsibility",
    f_prodline_sales: "Family (ProdLine Sales)", f_cliente: "Customer", f_q: "Search", f_kpi: "Card",
    f_categoria: "Category", f_razon: "Reason",
    k_pd: "Total Past Due", k_contoso: "Contoso PD (Plant)", k_cliente: "Customer Related", k_witness: "Witness",
    k_unDia: "In Grace Day (Not Counted)", k_hold: "Past Due On Hold", k_del: "of past due", k_lineas: "lines",
    contosoPd: "Contoso PD", customerRel: "Customer Related", witness: "Witness", total: "Total",
    vsCrd: "vs Request Date", vsProm: "vs Promise Date", sitio: "Site",
    v_sitioTabla: "Past Due by Site", v_sitioTabla_sub: "Executive Summary · click a site to filter.",
    v_razonSitio: "Past Due Reason by Site", v_razonSitio_sub: "Contoso PD, Customer Related and Witness by site.",
    v_fechas: "Past Due Against Request Date and Promise Date", v_fechas_sub: "By site · past-due lines whose customer or promise date has passed.",
    v_diaria: "Daily Past Due Trend", v_diaria_sub: "Past due of each workday by division.",
    v_unDia: "Past Due < 1 Day", v_unDia_sub: "Dollars inside the grace day.",
    v_mensual: "Monthly Past Due Trend", v_mensual_sub: "Month close by division.",
    v_hold: "Not On Hold vs On Hold by Plant", v_hold_sub: "Past due by site, stacked by On Hold.",
    v_plantaDiv: "Past Due by Plant", v_plantaDiv_sub: "Past due by site, stacked by division.",
    v_categoria: "Past Due Reasons", v_categoria_sub: "By reason category.",
    v_razon: "Reasons with the Most Past Due", v_razon_sub: "Top 12 reasons in dollars.",
    v_familia: "Past Due Sales $ by Prod Family", v_familia_sub: "Top 50 families · % of the selection's past due.",
    v_rango: "Aging", v_rango_sub: "Past due by days late on Schedule Ship Date.",
    v_bridge: "Bridge Against Marketing", v_bridge_sub: "From the marketing number to the report's past due.",
    v_bridgeCh: "Bridge Items", v_bridgeCh_sub: "Dollars by item and division.",
    v_fuentesMan: "Manual Capture Files", v_fuentesMan_sub: "What the dashboard read from manual/ for this cut.",
    v_ajustes: "Responsibility Adjustments", v_ajustes_sub: "Canada and plants · by order + line + item.",
    tagManual: "✎ Manual", manualTitle: "Manual Capture",
    manualDetail: "This data does NOT come from Oracle or AX: it is typed by hand in the source's manual/ folder (what lives in Sheet2, Executive Summary Reference and Bridge in the workbook). Review it on every cut; the dashboard uses it as is.",
    bridgeManual: "The marketing number and the affiliate lines are typed by hand in manual/bridge_manual.csv. Everything else comes from the calculation.",
    b_marketing: "Marketing Number", b_UN_DIA: "− Grace Day (1 Day Past Due)", b_INVOICE_HOLD: "− Invoice Hold",
    b_HVAC_TIER1: "− HVAC Tier1 OEM", b_ENTERED: "− Entered Orders", b_NLA: "− NLA (Eliminations)",
    b_noExplicado: "− Unexplained Difference", b_reporte: "= Report Past Due", b_sinMarketing: "No Marketing Number Captured",
    a_order: "Order", a_line: "Line", a_item: "Item", a_resp: "Responsibility", a_motivo: "Reason", a_aprobo: "Approved by",
    a_fecha: "Date", a_aplicado: "Applied", a_si: "Yes", a_no: "Line Not Found",
    fm_archivo: "File", fm_filas: "Rows", fm_fecha: "Modified", fm_estado: "Status", fm_ok: "Read", fm_falta: "Missing", fm_noHay: "Not Present",
    detail: "Detail by Line", vistaDetalle: "View", buscarLinea: "Search Order, Item or Customer…",
    p_general: "Past Due (All Responsibilities)", p_t1: "1 · CMS IO Plant Northgate", p_t2: "2 · CMS IO Plant Valle Alto",
    p_t3: "3 · CMS IO Plant PLT1", p_t4: "4 · CMS IO Plant PLT2", p_t5: "5 · CMS IO Plant Asia", p_t6: "6 · Intransit/Logistic",
    p_t7: "7 · Distribution (Mesa Verde + Riverton)", p_t8: "8 · Buyout", p_t9: "9 · Customer/Commercial",
    p_t10: "10 · Holds and Customer Pick Up", p_custDet: "Customer Past Due Details", p_buyDet: "Buyout Past Due Details",
    p_todas: "All Lines (Includes Not Past Due)",
    p_sub_pd: "Past-Due Lines Only", p_sub_todas: "All Lines in Scope",
    c_division: "Division", c_mktdiv: "Mkt DIV", c_org: "Org", c_grupo: "Group", c_cliente: "Customer", c_orden: "Order", c_linea: "Line",
    c_item: "Item Number", c_desc: "Item Desc", c_prodline: "ProdLine", c_prodline_sales: "ProdLine (Sales)", c_ssd: "Schedule Ship Date",
    c_req: "Request Date", c_prom: "Promise Date", c_ordenada: "Date Ordered", c_estatus_orden: "OrderStatus", c_qty: "Ordered Quantity",
    c_total: "Total $", c_resp_origen: "Original POM", c_resp: "Responsibility", c_sitio: "Site", c_pd_origen: "Original Status",
    c_pd: "Past Due Status", c_motivo: "Why It Doesn't Count", c_pd_crd: "PD vs Request", c_pd_prom: "PD vs Promise", c_dias: "Days",
    c_rango: "Range", c_ship_status: "Shipment Status", c_oh_ship: "On Hand (Org)", c_oh_all: "On Hand (All)", c_disp: "Available",
    c_oh: "Inventory on Hand", c_transito_qty: "In Transit", c_transito: "Intransit?", c_oh_int: "OH + In-Transit?", c_holds: "Holds",
    c_on_hold: "On Hold", c_cpu: "Customer Pick Up", c_override: "Override SO", c_freight: "Freight Terms", c_razon: "Reason",
    c_categoria: "Category", c_razon_sitio: "Reason (Site)", c_especial: "Special Customer", c_manual: "Manual", c_comentario: "Comment",
    c_incluida: "In Report",
    mo_UN_DIA: "Grace Day", mo_NLA: "NLA", mo_HVAC_TIER1: "HVAC Tier1 OEM", mo_INVOICE_HOLD: "Invoice Hold", mo_ENTERED: "Entered",
    man_ajuste: "Adjustment", man_razon: "Site Reason",
    purpose: "Purpose", sources: "Data Sources", transformations: "Transformations",
    measures: "Measure Dictionary", rules: "Business Rules", limitations: "Known Limitations",
    contact: "Contact", qc: "Calculation Quality Checks",
    s_fuente: "Source", s_sistema: "System", s_archivo: "File", s_extraido: "Extracted on", s_filas: "Rows", s_manual: "Manual",
    qc_filas: "Open Orders Lines", qc_sinSsd: "Lines without Schedule Ship Date", qc_undef: "Past-Due Lines with a Reason Outside the Catalog",
    qc_respVacia: "Past-Due Lines without Responsibility", qc_sinCat: "Mkt DIV Missing from divisiones.csv", qc_ajustes: "Manual Adjustments without Their Line",
    i_medida: "Measure", i_calculo: "Calculation", i_filtros: "Filters", i_gran: "Granularity",
    errorTitle: "The dashboard data could not be read.",
    errorDetail: "None of the data paths responded. Nothing on screen is reliable until the data loads.",
    faltaFuente: "A data source is missing.", faltaManual: "A manual capture file is missing.",
    semiTitle: "Semi-fictitious data — real shape, made-up identities.",
    semiDetail: "Built from a real cut with customers, materials, documents and people replaced, and amounts shifted ±15%. Good for analysis on realistic data; not for decisions.",
    demoTitle: "Made-up data — not from Oracle or AX.",
    demoDetail: "They are for testing the dashboard: the layout is the report's, the numbers are not real.",
    ajustesTitle: "Some manual adjustments did not find their line.",
    ajustesDetail: "adjustments in manual/ajustes_responsabilidad.csv were not applied: the order, line or item is no longer in Open Orders. Review them in Manual capture.",
    catTitle: "Some divisions have no catalog row.", catDetail: "are not in manual/divisiones.csv and are left out of the report:",
    respTitle: "Some past due has no responsibility.", respDetail: "past-due lines ended without a site (Org H05/R01 or no rule). They show as 'Sin asignar'.",
    diag: "Diagnostics", diagTitle: "Last Redraw Diagnostics",
    m_sub: "How this line got its responsibility and status.",
    otros: "Others", sinRazon: "(No Reason)"
  }
};

/* ============================================================
   ESTADO
   ============================================================ */
let META = {};
let rawData = [];
let HIST = [];
let BRIDGE = [];
let AJUSTES = [];
let PDSET = new Set();
let lang = leerLS("dash_lang") || CONFIG.lang.default;
if (!CONFIG.lang.enabled.includes(lang)) lang = CONFIG.lang.default;
let view = "resumen";
let scope = "pd";
let preset = "general";
let pageSize = (() => { const v = +leerLS("pastdue_page_size"); return CONFIG.detail.pageSizes.includes(v) ? v : CONFIG.detail.pageSize; })();
const filterState = { panel: {}, q: "", crossfilter: null };
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
function isoAUTC(iso) { const [y, m, d] = iso.split("-").map(Number); return Date.UTC(y, m - 1, d); }
function utcAISO(ms) { return new Date(ms).toISOString().slice(0, 10); }
function hoyISO() { const d = new Date(); return utcAISO(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())); }
function diasEntre(a, b) { return Math.round((isoAUTC(b) - isoAUTC(a)) / 864e5); }

function fmtNum(v, dec) {
  if (v === null || v === undefined || v === "" || Number.isNaN(+v)) return "–";
  const n = +v;
  const s = Math.abs(n).toLocaleString("en-US", { minimumFractionDigits: dec || 0, maximumFractionDigits: dec || 0 });
  return n < 0 ? `(${s})` : s;
}
function fmtUsd(v) { return v === null || v === undefined ? "–" : (v < 0 ? "-$" : "$") + fmtNum(Math.abs(v)); }
function abbr(n) {
  const a = Math.abs(n);
  if (a >= 1e9) return (n / 1e9).toFixed(1) + "B";
  if (a >= 1e6) return (n / 1e6).toFixed(2) + "M";
  if (a >= 1e3) return (n / 1e3).toFixed(0) + "K";
  return Math.round(n).toLocaleString("en-US");
}
const usdAbbr = n => (n < 0 ? "-$" : "$") + abbr(Math.abs(n));
function fmtFecha(iso) {
  if (!iso || !ISO.test(iso)) return "–";
  const [y, m, d] = iso.split("-");
  return lang === "es" ? `${d}/${m}/${y}` : `${m}/${d}/${y}`;
}
function fmtMes(ym) {
  const [y, m] = ym.split("-");
  const s = new Date(Date.UTC(+y, +m - 1, 1)).toLocaleString(lang === "es" ? "es-MX" : "en-US", { month: "short", year: "2-digit", timeZone: "UTC" }).replace(".", "");
  return s.charAt(0).toUpperCase() + s.slice(1);   // "oct 26" -> "Oct 26": etiqueta en Proper
}
const esPD = r => PDSET.has(r.pd);
const sumar = (data, pred) => data.reduce((s, r) => s + ((!pred || pred(r)) ? (+r.total || 0) : 0), 0);
function porClave(data, clave, pred) {
  const m = {};
  data.forEach(r => { if (pred && !pred(r)) return; const k = valorCrudo(r[clave]); m[k] = (m[k] || 0) + (+r.total || 0); });
  return m;
}
function sitiosOrden(presentes) {
  const base = META.sitios || [];
  const extra = [...presentes].filter(s => !base.includes(s)).sort();
  return base.filter(s => presentes.has(s)).concat(extra);
}
function divisiones() { return [...new Set(rawData.filter(enAlcance).map(r => r.division))].sort(); }
function colorCat(i) { return cssVar(`--c-cat-${(i % 5) + 1}`); }
const COLOR_RAZON = { "PLANT PAST DUE": "--c-critical", "CUSTOMER RELATED": "--c-cat-2", "WITNESS": "--c-cat-5" };

/* ============================================================
   KPIs
   ============================================================ */
const KPIS = [
  { id: "pd", label: "k_pd", rol: "critical", pred: r => esPD(r) },
  { id: "contoso", label: "k_contoso", rol: "critical", pred: r => esPD(r) && r.razon_sitio === "PLANT PAST DUE" },
  { id: "cliente", label: "k_cliente", rol: "warn", pred: r => esPD(r) && r.razon_sitio === "CUSTOMER RELATED" },
  { id: "witness", label: "k_witness", rol: "warn", pred: r => esPD(r) && r.razon_sitio === "WITNESS" },
  { id: "unDia", label: "k_unDia", rol: "ok", pred: r => r.pd === "1 DAY PAST DUE" },
  { id: "hold", label: "k_hold", rol: "warn", pred: r => esPD(r) && r.on_hold === "ON HOLD" }
];

/* ============================================================
   FILTRADO — una sola puerta de redibujo
   ============================================================ */
const enAlcance = r => scope === "todas" || r.incluida;
function matchesPanel(r) {
  if (!enAlcance(r)) return false;
  for (const [f, vals] of Object.entries(filterState.panel)) {
    if (vals && vals.length && !vals.includes(valorCrudo(r[f]))) return false;
  }
  if (filterState.q) {
    const q = filterState.q.toLowerCase();
    if (!String(r.orden).toLowerCase().includes(q) && !String(r.item).toLowerCase().includes(q) &&
        !String(r.cliente || "").toLowerCase().includes(q)) return false;
  }
  return true;
}
function matchesCrossfilter(r, cf) {
  if (!cf) return true;
  if (cf.field === "kpi") return cf.values.some(id => { const k = KPIS.find(x => x.id === id); return k && k.pred(r); });
  return cf.values.includes(valorCrudo(r[cf.field]));
}
/* exceptField: el visual que origino la seleccion se dibuja sin ella (y atenua lo no seleccionado). */
function getFilteredData(exceptField) {
  const cf = filterState.crossfilter;
  const usarCf = cf && cf.field !== exceptField ? cf : null;
  return rawData.filter(r => matchesPanel(r) && matchesCrossfilter(r, usarCf));
}
/* El historial solo sabe de division: responde al alcance y al filtro de division, nada mas. */
function divisionesHist() {
  const sel = filterState.panel.division;
  return divisiones().filter(d => !sel || !sel.length || sel.includes(d));
}
function comparar(va, vb) {
  const na = va === null || va === undefined || va === "", nb = vb === null || vb === undefined || vb === "";
  if (na || nb) return na === nb ? 0 : (na ? 1 : -1);
  if (typeof va === "number" && typeof vb === "number") return va - vb;
  return String(va).localeCompare(String(vb), "en", { numeric: true });
}
function medir(nombre, fn) {
  const t0 = performance.now(); fn(); void document.body.offsetHeight;
  DIAG.etapas[nombre] = Math.round(performance.now() - t0);
}
function applyFilters() {
  const t0 = performance.now();
  medir("kpis", renderKPIs);
  CHARTS.filter(c => c.view === view).forEach(c => medir(c.id, () => c.update()));
  if (view === "resumen") medir("tblSitio", renderTablaSitio);
  if (view === "bridge") medir("bridge", renderBridge);
  if (view === "manual") medir("manual", renderManual);
  if (!$("detailCard").hidden) medir("tabla", renderTable);
  renderChips(); updateFilterBadge(); syncURL();
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
  filterState.panel = {}; filterState.q = ""; filterState.crossfilter = null; currentPage = 1;
  $("tblBuscar").value = "";
  construirFiltros(); applyFilters();
}

/* ============================================================
   VISTAS Y ALCANCE
   ============================================================ */
const VISTAS_CON_DETALLE = new Set(["resumen", "tendencias", "razones"]);
function pintarVista() {
  document.querySelectorAll("#viewTabs button").forEach(b => b.classList.toggle("is-active", b.dataset.view === view));
  document.querySelectorAll("section.view").forEach(s => { s.hidden = s.dataset.view !== view; });
  $("detailCard").hidden = !VISTAS_CON_DETALLE.has(view);
}
$("viewTabs").addEventListener("click", e => {
  const b = e.target.closest("button[data-view]"); if (!b || b.dataset.view === view) return;
  view = b.dataset.view; pintarVista(); applyFilters();
  CHARTS.filter(c => c.view === view && c.chart).forEach(c => c.chart.resize());
});
$("scopeToggle").addEventListener("click", e => {
  const b = e.target.closest("button[data-scope]"); if (!b || b.dataset.scope === scope) return;
  scope = b.dataset.scope; pintarScope(); construirFiltros(); currentPage = 1; applyFilters();
});
function pintarScope() {
  document.querySelectorAll("#scopeToggle button").forEach(b => b.classList.toggle("is-active", b.dataset.scope === scope));
}
function renderToolbarInfo() {
  const el = $("toolbarInfo"); el.textContent = "";
  if (!META.fecha_corte) return;
  const partes = [[t("corte"), fmtFecha(META.fecha_corte)], [t("gracia"), fmtFecha(META.gracia && META.gracia.desde)],
                  [t("lineas"), rawData.length.toLocaleString("en-US")]];
  partes.forEach(([k, v], i) => {
    if (i) el.appendChild(document.createTextNode(" · "));
    el.appendChild(document.createTextNode(k + ": "));
    const b = document.createElement("b"); b.textContent = v; el.appendChild(b);
  });
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
  if (filterState.q) n++;
  return n + (filterState.crossfilter ? 1 : 0);
}
function updateFilterBadge() {
  const n = countActiveFilters(), b = $("filterBadge");
  b.textContent = n; b.hidden = n === 0;
}
function etiquetaCampoValor(f, v) {
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
  if (view !== "resumen") p.set("vista", view);
  if (scope !== "pd") p.set("alcance", scope);
  if (preset !== "general") p.set("detalle", preset);
  Object.entries(filterState.panel).forEach(([f, v]) => v && v.length && p.set(f, v.join("|")));
  if (filterState.q) p.set("q", filterState.q);
  history.replaceState(null, "", p.toString() ? "?" + p : location.pathname);
}
/* Lista blanca de NOMBRES y de VALORES: un valor solo entra si existe en el catalogo del campo. */
function readURL() {
  const campos = new Set([...document.querySelectorAll(".filter-group[data-field]")].map(g => g.dataset.field));
  const vistas = new Set([...document.querySelectorAll("#viewTabs button")].map(b => b.dataset.view));
  new URLSearchParams(location.search).forEach((v, k) => {
    if (k === "vista" && vistas.has(v)) view = v;
    else if (k === "alcance" && (v === "pd" || v === "todas")) scope = v;
    else if (k === "detalle" && PRESETS.some(p => p.id === v)) preset = v;
    else if (k === "q") filterState.q = v.slice(0, 60);
    else if (campos.has(k)) {
      const validos = new Set(opcionesDe(k).map(o => o.v));
      const vals = v.split("|").filter(x => validos.has(x));
      if (vals.length) filterState.panel[k] = vals;
    }
  });
  $("tblBuscar").value = filterState.q;
}

const FILTRO_SELECT_ALL = 5;
const FILTRO_PLEGABLE = 12;
const panelUI = { tocado: {}, busca: {} };

function etiquetaValor(campo, valor) {
  if (valorCrudo(valor) === "") return t("sinValor");
  return String(valor).replace(/\s+/g, " ").trim() || String(valor);
}
function opcionesDe(campo) {
  const cuenta = new Map();
  rawData.filter(enAlcance).forEach(r => {
    const v = valorCrudo(r[campo]);
    cuenta.set(v, (cuenta.get(v) || 0) + 1);
  });
  let claves = [...cuenta.keys()];
  if (campo === "sitio") claves = sitiosOrden(new Set(claves));
  else if (campo === "rango") claves = ["", ...CONFIG.rangos].filter(k => cuenta.has(k)).concat(claves.filter(k => k !== "" && !CONFIG.rangos.includes(k)));
  else claves.sort((a, b) => a === "" ? 1 : b === "" ? -1 : String(a).localeCompare(String(b), lang, { numeric: true }));
  return claves.map(v => ({ v, txt: etiquetaValor(campo, v), n: cuenta.get(v) }));
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

let tBuscar;
$("tblBuscar").addEventListener("input", e => {
  clearTimeout(tBuscar);
  tBuscar = setTimeout(() => { filterState.q = e.target.value.trim().slice(0, 60); currentPage = 1; applyFilters(); }, 200);
});

/* ============================================================
   KPIs
   ============================================================ */
function renderKPIs() {
  const row = $("kpiRow"); row.textContent = "";
  const data = getFilteredData("kpi");
  const totalPd = sumar(data, esPD);
  const cf = filterState.crossfilter;
  KPIS.forEach(k => {
    // Sin datos se pinta "–", nunca $0: un cero dice "no hay past due", que no es lo que paso.
    const lineas = cargaFallo ? null : data.filter(k.pred);
    const v = lineas === null ? null : sumar(lineas);
    const card = document.createElement("div");
    card.className = `card kpi kpi--${k.rol}`;
    if (cf && cf.field === "kpi" && cf.values.includes(k.id)) card.classList.add("is-active");
    const ve = document.createElement("div"); ve.className = "kpi__value"; ve.textContent = v === null ? "–" : usdAbbr(v);
    if (v !== null) ve.title = fmtUsd(v);
    const l = document.createElement("div"); l.className = "kpi__label"; l.textContent = t(k.label);
    const s = document.createElement("div"); s.className = "kpi__sub";
    if (lineas === null) s.textContent = "–";
    else if (k.id === "pd" || k.id === "unDia") s.textContent = `${lineas.length.toLocaleString("en-US")} ${t("k_lineas")}.`;   // linea del KPI: frase con punto
    else s.textContent = totalPd ? `${(v / totalPd * 100).toFixed(1)}% ${t("k_del")} · ${lineas.length.toLocaleString("en-US")} ${t("k_lineas")}.` : "–";
    card.append(ve, l, s);
    card.addEventListener("click", e => setCrossfilter("kpi", k.id, e.ctrlKey || e.metaKey));
    row.appendChild(card);
  });
  const primera = row.firstElementChild;
  if (primera) { const h = document.createElement("div"); h.className = "card__header"; h.style.margin = "0"; primera.prepend(h); attachInfo(primera, "kpi"); }
}

/* ============================================================
   GRAFICAS (Chart.js local). Cada una expone update().
   calcular() devuelve { claves, etiquetas, datasets: [{ label, data, color }] }
   ============================================================ */
Chart.register(ChartDataLabels);
Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
Chart.defaults.font.size = 11;
Chart.defaults.animation.duration = 240;
Chart.defaults.plugins.legend.display = false;

function crearChart(id, vista, field, cfg) {
  const canvas = $(id);
  const box = canvas.parentElement;
  const vacio = box.querySelector(".empty-state");
  const obj = { id, view: vista, field, chart: null, claves: [] };
  obj.update = () => {
    const data = cfg.historial ? null : getFilteredData(field);
    const r = cfg.calcular(data);
    obj.claves = r.claves;
    const cf = filterState.crossfilter;
    const sel = field && cf && cf.field === field ? cf.values : null;
    const datasets = r.datasets.map(ds => {
      const base = Array.isArray(ds.color) ? ds.color : r.claves.map(() => ds.color);
      const colores = base.map((c, i) => (sel && !sel.includes(r.claves[i])) ? conAlfa(c, 0.25) : c);
      return Object.assign({ borderRadius: cfg.tipo === "doughnut" ? 0 : 3, maxBarThickness: 46 }, ds,
        { backgroundColor: cfg.tipo === "line" ? ds.color : colores, borderColor: cfg.tipo === "line" ? ds.color : undefined });
    });
    const hayValor = datasets.some(ds => ds.data.some(v => v));
    vacio.hidden = hayValor;
    DIAG.visuales[id] = { puntos: r.claves.length, series: datasets.length, conValor: hayValor };
    if (!obj.chart) {
      obj.chart = new Chart(canvas, {
        type: cfg.tipo || "bar",
        data: { labels: r.etiquetas, datasets },
        options: Object.assign({
          responsive: true, maintainAspectRatio: false,
          onClick: (e, els) => {
            if (!field || !els.length) return;
            setCrossfilter(field, obj.claves[els[0].index], e.native && (e.native.ctrlKey || e.native.metaKey));
          },
          onHover: (e, els) => { e.native.target.style.cursor = (field && els.length) ? "pointer" : "default"; }
        }, cfg.opciones())
      });
      canvas.addEventListener("dblclick", e => {
        const els = obj.chart.getElementsAtEventForMode(e, "nearest", { intersect: true }, false);
        if (!els.length && filterState.crossfilter) { filterState.crossfilter = null; currentPage = 1; applyFilters(); }
      });
    } else {
      obj.chart.data.labels = r.etiquetas;
      obj.chart.data.datasets = datasets;
      Object.assign(obj.chart.options, cfg.opciones());
      obj.chart.update();
    }
  };
  return obj;
}
const ejeCfg = () => ({ grid: { color: conAlfa(cssVar("--c-border"), 0.6) }, ticks: { color: cssVar("--c-text-muted"), callback: function (v) { return usdAbbr(v); } } });
const ejeCat = () => ({ grid: { display: false }, ticks: { color: cssVar("--c-text"), autoSkip: false } });
const leyenda = () => ({ display: true, position: "bottom", labels: { boxWidth: 12, color: cssVar("--c-text") } });
const tipUsd = () => ({ callbacks: { label: c => ` ${c.dataset.label ? c.dataset.label + ": " : ""}${fmtUsd(c.raw)}` } });
/* Etiqueta de total al final de una barra apilada: solo la ultima serie la pinta */
function labelTotal(horizontal) {
  return {
    display: ctx => ctx.datasetIndex === ctx.chart.data.datasets.length - 1,
    anchor: "end", align: "end", clamp: false, offset: 2, color: cssVar("--c-text"), font: { weight: "600", size: 11 },
    formatter: (v, ctx) => {
      const tot = ctx.chart.data.datasets.reduce((s, ds, i) => s + (ctx.chart.isDatasetVisible(i) ? (+ds.data[ctx.dataIndex] || 0) : 0), 0);
      return tot ? usdAbbr(tot) : "";
    }
  };
}
const labelSimple = () => ({ anchor: "end", align: "end", clamp: false, offset: 2, color: cssVar("--c-text"),
  font: { weight: "600", size: 11 }, formatter: v => v ? usdAbbr(v) : "" });

/* Sitios presentes en el past due filtrado, en el orden del Executive Summary */
function sitiosDe(data) { return sitiosOrden(new Set(data.filter(esPD).map(r => r.sitio))); }

const CHARTS = [
  crearChart("chRazonSitio", "resumen", "sitio", {
    calcular: data => {
      const claves = sitiosDe(data);
      const datasets = CONFIG.razonesSitio.map(rz => {
        const m = porClave(data, "sitio", r => esPD(r) && r.razon_sitio === rz);
        return { label: t({ "PLANT PAST DUE": "contosoPd", "CUSTOMER RELATED": "customerRel", "WITNESS": "witness" }[rz]),
                 data: claves.map(k => m[k] || 0), color: cssVar(COLOR_RAZON[rz]) };
      });
      return { claves, etiquetas: claves, datasets };
    },
    opciones: () => ({ indexAxis: "y", layout: { padding: { right: 64 } },
      scales: { x: Object.assign(ejeCfg(), { stacked: true, beginAtZero: true }), y: Object.assign(ejeCat(), { stacked: true }) },
      plugins: { legend: leyenda(), datalabels: labelTotal(true), tooltip: tipUsd() } })
  }),
  crearChart("chFechas", "resumen", "sitio", {
    calcular: data => {
      const claves = sitiosDe(data);
      const crd = porClave(data, "sitio", r => esPD(r) && r.pd_crd === "PAST DUE");
      const prom = porClave(data, "sitio", r => esPD(r) && r.pd_prom === "PAST DUE");
      return { claves, etiquetas: claves, datasets: [
        { label: t("vsCrd"), data: claves.map(k => crd[k] || 0), color: cssVar("--c-cat-1") },
        { label: t("vsProm"), data: claves.map(k => prom[k] || 0), color: cssVar("--c-cat-4") }] };
    },
    opciones: () => ({ layout: { padding: { top: 18 } },
      scales: { y: Object.assign(ejeCfg(), { beginAtZero: true }), x: Object.assign(ejeCat(), { ticks: { color: cssVar("--c-text"), autoSkip: false, maxRotation: 0, font: { size: 10 } } }) },
      plugins: { legend: leyenda(), datalabels: Object.assign(labelSimple(), { font: { size: 9, weight: "600" }, rotation: 0 }), tooltip: tipUsd() } })
  }),
  crearChart("chDiaria", "tendencias", null, {
    historial: true, tipo: "bar",
    calcular: () => serieHist(2),
    opciones: () => ({ layout: { padding: { top: 8 } },
      scales: { y: Object.assign(ejeCfg(), { stacked: true, beginAtZero: true }), x: { stacked: true, grid: { display: false }, ticks: { color: cssVar("--c-text-muted"), maxRotation: 0, autoSkip: true, autoSkipPadding: 14 } } },
      plugins: { legend: leyenda(), datalabels: { display: false }, tooltip: tipUsd() } })
  }),
  crearChart("chUnDia", "tendencias", null, {
    historial: true, tipo: "bar",
    calcular: () => serieHist(3),
    opciones: () => ({ scales: { y: Object.assign(ejeCfg(), { stacked: true, beginAtZero: true }), x: { stacked: true, grid: { display: false }, ticks: { color: cssVar("--c-text-muted"), maxRotation: 0, autoSkip: true, autoSkipPadding: 14 } } },
      plugins: { legend: leyenda(), datalabels: { display: false }, tooltip: tipUsd() } })
  }),
  crearChart("chMensual", "tendencias", null, {
    historial: true, tipo: "bar",
    calcular: () => serieMensual(),
    opciones: () => ({ layout: { padding: { top: 18 } },
      scales: { y: Object.assign(ejeCfg(), { stacked: true, beginAtZero: true }), x: { stacked: true, grid: { display: false }, ticks: { color: cssVar("--c-text") } } },
      plugins: { legend: leyenda(), datalabels: labelTotal(false), tooltip: tipUsd() } })
  }),
  crearChart("chHold", "tendencias", "sitio", {
    calcular: data => {
      const claves = sitiosDe(data);
      const no = porClave(data, "sitio", r => esPD(r) && r.on_hold !== "ON HOLD");
      const si = porClave(data, "sitio", r => esPD(r) && r.on_hold === "ON HOLD");
      return { claves, etiquetas: claves, datasets: [
        { label: "NOT ON HOLD", data: claves.map(k => no[k] || 0), color: cssVar("--c-cat-1") },
        { label: "ON HOLD", data: claves.map(k => si[k] || 0), color: cssVar("--c-warn") }] };
    },
    opciones: () => ({ indexAxis: "y", layout: { padding: { right: 64 } },
      scales: { x: Object.assign(ejeCfg(), { stacked: true, beginAtZero: true }), y: Object.assign(ejeCat(), { stacked: true }) },
      plugins: { legend: leyenda(), datalabels: labelTotal(true), tooltip: tipUsd() } })
  }),
  crearChart("chPlantaDiv", "tendencias", "sitio", {
    calcular: data => {
      const claves = sitiosDe(data);
      const divs = [...new Set(data.filter(esPD).map(r => r.division))].sort();
      return { claves, etiquetas: claves, datasets: divs.map((d, i) => {
        const m = porClave(data, "sitio", r => esPD(r) && r.division === d);
        return { label: d, data: claves.map(k => m[k] || 0), color: colorCat(i) };
      }) };
    },
    opciones: () => ({ indexAxis: "y", layout: { padding: { right: 64 } },
      scales: { x: Object.assign(ejeCfg(), { stacked: true, beginAtZero: true }), y: Object.assign(ejeCat(), { stacked: true }) },
      plugins: { legend: leyenda(), datalabels: labelTotal(true), tooltip: tipUsd() } })
  }),
  crearChart("chCategoria", "razones", "categoria", {
    tipo: "doughnut",
    calcular: data => {
      const m = porClave(data, "categoria", esPD);
      const claves = Object.keys(m).sort((a, b) => m[b] - m[a]);
      const col = { "Plant Past Due": "--c-critical", "Customer": "--c-cat-2", "Witness": "--c-cat-5", "Others": "--c-cat-3", "Undefined": "--c-neutral" };
      return { claves, etiquetas: claves, datasets: [{ label: "", data: claves.map(k => m[k]), color: claves.map((k, i) => col[k] ? cssVar(col[k]) : colorCat(i)) }] };
    },
    opciones: () => ({ cutout: "55%",
      plugins: { legend: leyenda(), tooltip: tipUsd(),
        datalabels: { color: cssVar("--c-text-invert"), font: { weight: "600", size: 11 },
          formatter: (v, ctx) => { const tot = ctx.dataset.data.reduce((s, x) => s + x, 0); return tot && v / tot > 0.04 ? `${(v / tot * 100).toFixed(0)}%` : ""; } } } })
  }),
  crearChart("chRazon", "razones", "razon", {
    calcular: data => {
      const m = porClave(data, "razon", esPD);
      const claves = Object.keys(m).sort((a, b) => m[b] - m[a]).slice(0, CONFIG.topRazones);
      return { claves, etiquetas: claves.map(k => k === "" ? t("sinRazon") : (k.length > 38 ? k.slice(0, 36) + "…" : k)),
               datasets: [{ label: "", data: claves.map(k => m[k]), color: cssVar("--c-cat-2") }] };
    },
    opciones: () => ({ indexAxis: "y", layout: { padding: { right: 64 } },
      scales: { x: Object.assign(ejeCfg(), { beginAtZero: true }), y: ejeCat() },
      plugins: { datalabels: labelSimple(), tooltip: { callbacks: { title: c => CHARTS_RAZON_TXT(c[0].dataIndex), label: c => ` ${fmtUsd(c.raw)}` } } } })
  }),
  crearChart("chFamilia", "razones", "prodline_sales", {
    calcular: data => {
      const m = porClave(data, "prodline_sales", esPD);
      const tot = Object.values(m).reduce((s, v) => s + v, 0);
      const claves = Object.keys(m).sort((a, b) => m[b] - m[a]).slice(0, CONFIG.topFamilias);
      FAMILIA_TOT = tot;
      // Alto segun cuantas familias haya: 50 barras no caben en la altura fija de las demas
      $("chFamilia").parentElement.style.height = `${Math.max(260, claves.length * 17 + 70)}px`;
      return { claves, etiquetas: claves.map(k => k || t("sinValor")), datasets: [{ label: "", data: claves.map(k => m[k]), color: cssVar("--c-cat-1") }] };
    },
    opciones: () => ({ indexAxis: "y", layout: { padding: { right: 96 } },
      scales: { x: Object.assign(ejeCfg(), { beginAtZero: true }), y: Object.assign(ejeCat(), { ticks: { color: cssVar("--c-text"), autoSkip: false, font: { size: 10 } } }) },
      plugins: { datalabels: Object.assign(labelSimple(), { formatter: v => v ? `${usdAbbr(v)} · ${(FAMILIA_TOT ? v / FAMILIA_TOT * 100 : 0).toFixed(1)}%` : "" }),
        tooltip: tipUsd() } })
  }),
  crearChart("chRango", "razones", "rango", {
    calcular: data => {
      const m = porClave(data, "rango", esPD);
      const claves = CONFIG.rangos.filter(k => m[k]).concat(Object.keys(m).filter(k => !CONFIG.rangos.includes(k) && m[k]));
      return { claves, etiquetas: claves.map(k => k || t("sinValor")),
               datasets: [{ label: "", data: claves.map(k => m[k]), color: claves.map((k, i) => cssVar(i < 2 ? "--c-warn" : "--c-critical")) }] };
    },
    opciones: () => ({ layout: { padding: { top: 18 } },
      scales: { y: Object.assign(ejeCfg(), { beginAtZero: true }), x: ejeCat() },
      plugins: { datalabels: labelSimple(), tooltip: tipUsd() } })
  }),
  crearChart("chBridge", "bridge", null, {
    historial: true,
    calcular: () => {
      const b = calcularBridge();
      const claves = ["UN_DIA", "INVOICE_HOLD", "HVAC_TIER1", "ENTERED", "NLA", ...b.manualConceptos, "NO_EXPLICADO"];
      const etiqueta = k => k === "NO_EXPLICADO" ? t("b_noExplicado") : (t("b_" + k) !== "b_" + k ? t("b_" + k) : `− ${k}`);
      return { claves, etiquetas: claves.map(etiqueta), datasets: b.divs.map((d, i) => ({
        label: d, data: claves.map(k => k === "NO_EXPLICADO" ? (b.porDiv[d].noExplicado || 0) : (b.porDiv[d].conceptos[k] || 0)), color: colorCat(i) })) };
    },
    opciones: () => ({ indexAxis: "y", layout: { padding: { right: 64 } },
      scales: { x: Object.assign(ejeCfg(), { stacked: true }), y: Object.assign(ejeCat(), { stacked: true }) },
      plugins: { legend: leyenda(), datalabels: labelTotal(true), tooltip: tipUsd() } })
  })
];
let FAMILIA_TOT = 0;
function CHARTS_RAZON_TXT(i) { const c = CHARTS.find(x => x.id === "chRazon"); const k = c ? c.claves[i] : ""; return k || t("sinRazon"); }
function redibujarCharts() { setTimeout(() => CHARTS.forEach(c => c.chart && c.chart.resize()), 260); }

/* Historial: [fecha, division, past_due, un_dia] */
function serieHist(col) {
  const divs = divisionesHist();
  const fechas = [...new Set(HIST.filter(h => divs.includes(h[1])).map(h => h[0]))].sort();
  const m = {}; HIST.forEach(h => { m[h[0] + "|" + h[1]] = h[col]; });
  return { claves: fechas, etiquetas: fechas.map(fmtFecha), datasets: divs.map((d, i) => ({
    label: d, data: fechas.map(f => m[f + "|" + d] || 0), color: colorCat(i) })) };
}
function serieMensual() {
  const divs = divisionesHist();
  const ultimo = {};
  HIST.forEach(h => { if (!divs.includes(h[1])) return; const k = h[0].slice(0, 7) + "|" + h[1]; if (!ultimo[k] || ultimo[k][0] < h[0]) ultimo[k] = h; });
  const meses = [...new Set(Object.keys(ultimo).map(k => k.split("|")[0]))].sort();
  return { claves: meses, etiquetas: meses.map(fmtMes), datasets: divs.map((d, i) => ({
    label: d, data: meses.map(mm => (ultimo[mm + "|" + d] || [0, 0, 0])[2]), color: colorCat(i) })) };
}

/* ============================================================
   EXECUTIVE SUMMARY — tabla por sitio
   ============================================================ */
function renderTablaSitio() {
  const data = getFilteredData("sitio");
  const tb = $("tblSitio"); tb.textContent = "";
  const cols = [["sitio", "sitio"], ["PLANT PAST DUE", "contosoPd"], ["CUSTOMER RELATED", "customerRel"], ["WITNESS", "witness"],
                ["total", "total"], ["crd", "vsCrd"], ["prom", "vsProm"]];
  const th = document.createElement("thead"); const trh = document.createElement("tr");
  cols.forEach(([, k]) => { const x = document.createElement("th"); x.textContent = t(k); trh.appendChild(x); });
  th.appendChild(trh); tb.appendChild(th);
  const bd = document.createElement("tbody");
  const sitios = sitiosDe(data);
  const cf = filterState.crossfilter;
  const sel = cf && cf.field === "sitio" ? cf.values : [];
  const valores = s => {
    const d = data.filter(r => esPD(r) && r.sitio === s);
    return [sumar(d, r => r.razon_sitio === "PLANT PAST DUE"), sumar(d, r => r.razon_sitio === "CUSTOMER RELATED"),
            sumar(d, r => r.razon_sitio === "WITNESS"), sumar(d), sumar(d, r => r.pd_crd === "PAST DUE"), sumar(d, r => r.pd_prom === "PAST DUE")];
  };
  const tot = [0, 0, 0, 0, 0, 0];
  sitios.forEach(s => {
    const v = valores(s); v.forEach((x, i) => { tot[i] += x; });
    const tr = document.createElement("tr"); if (sel.includes(s)) tr.classList.add("is-sel");
    const td0 = document.createElement("td"); td0.className = "click"; td0.textContent = s;
    td0.addEventListener("click", e => setCrossfilter("sitio", s, e.ctrlKey || e.metaKey));
    tr.appendChild(td0);
    v.forEach(x => { const td = document.createElement("td"); td.className = "num"; td.textContent = fmtUsd(x); tr.appendChild(td); });
    bd.appendChild(tr);
  });
  if (!sitios.length) {
    const tr = document.createElement("tr"); const td = document.createElement("td"); td.colSpan = cols.length;
    td.className = "empty-state"; td.textContent = t("noData"); tr.appendChild(td); bd.appendChild(tr);
  }
  tb.appendChild(bd);
  if (sitios.length) {
    const tf = document.createElement("tfoot"); const tr = document.createElement("tr"); tr.className = "fila-total";
    const td0 = document.createElement("td"); td0.textContent = "TOTAL"; tr.appendChild(td0);
    tot.forEach(x => { const td = document.createElement("td"); td.className = "num"; td.textContent = fmtUsd(x); tr.appendChild(td); });
    tf.appendChild(tr); tb.appendChild(tf);
  }
}

/* ============================================================
   BRIDGE — marketing (manual) contra el past due del reporte
   ============================================================ */
const MOTIVOS = ["UN_DIA", "INVOICE_HOLD", "HVAC_TIER1", "ENTERED", "NLA"];
function calcularBridge() {
  const divs = divisionesHist();
  const data = rawData.filter(r => enAlcance(r) && divs.includes(r.division));
  const manualConceptos = [...new Set(BRIDGE.filter(b => b[0] !== "MARKETING").map(b => b[0]))];
  const porDiv = {};
  divs.forEach(d => {
    const dd = data.filter(r => r.division === d);
    const marketing = BRIDGE.filter(b => b[0] === "MARKETING" && b[1] === d).reduce((s, b) => s + b[2], 0);
    const tieneMkt = BRIDGE.some(b => b[0] === "MARKETING" && b[1] === d);
    const conceptos = {};
    MOTIVOS.forEach(m => { conceptos[m] = sumar(dd, r => r.motivo === m && r.pd_origen !== "NOT PAST DUE"); });
    manualConceptos.forEach(c => { conceptos[c] = BRIDGE.filter(b => b[0] === c && b[1] === d).reduce((s, b) => s + b[2], 0); });
    const reporte = sumar(dd, esPD);
    const restado = Object.values(conceptos).reduce((s, v) => s + v, 0);
    porDiv[d] = { marketing, tieneMkt, conceptos, reporte, noExplicado: tieneMkt ? marketing - restado - reporte : null };
  });
  return { divs, porDiv, manualConceptos };
}
function renderBridge() {
  const b = calcularBridge();
  const tb = $("tblBridge"); tb.textContent = "";
  const th = document.createElement("thead"); const trh = document.createElement("tr");
  ["", ...b.divs, t("total")].forEach(x => { const e = document.createElement("th"); e.textContent = x; trh.appendChild(e); });
  th.appendChild(trh); tb.appendChild(th);
  const bd = document.createElement("tbody");
  const fila = (label, getter, clase, manual) => {
    const tr = document.createElement("tr"); if (clase) tr.className = clase;
    const td0 = document.createElement("td"); td0.textContent = label + " ";
    if (manual) { const s = document.createElement("span"); s.className = "tag-manual"; s.textContent = t("tagManual"); td0.appendChild(s); }
    tr.appendChild(td0);
    let tot = 0, hayNull = false;
    b.divs.forEach(d => { const v = getter(b.porDiv[d]); if (v === null) hayNull = true; else tot += v;
      const td = document.createElement("td"); td.className = "num"; td.textContent = v === null ? t("b_sinMarketing") : fmtUsd(v); tr.appendChild(td); });
    const td = document.createElement("td"); td.className = "num"; td.textContent = hayNull ? "–" : fmtUsd(tot); tr.appendChild(td);
    bd.appendChild(tr);
  };
  fila(t("b_marketing"), p => p.tieneMkt ? p.marketing : null, "", true);
  MOTIVOS.forEach(m => fila(t("b_" + m), p => -p.conceptos[m]));
  b.manualConceptos.forEach(c => fila(`− ${c}`, p => -p.conceptos[c], "", true));
  fila(t("b_noExplicado"), p => p.noExplicado === null ? null : -p.noExplicado);
  fila(t("b_reporte"), p => p.reporte, "fila-resultado");
  tb.appendChild(bd);
  const nota = BRIDGE.filter(x => x[3]).map(x => `${x[0]} · ${x[1]}: ${x[3]}`);
  tb.title = nota.join("\n");
}

/* ============================================================
   CAPTURA MANUAL — archivos leidos y ajustes de responsabilidad
   ============================================================ */
function tablaSimple(tb, cab, filas) {
  tb.textContent = "";
  const th = document.createElement("thead"); const tr = document.createElement("tr");
  cab.forEach(c => { const x = document.createElement("th"); x.textContent = c; tr.appendChild(x); });
  th.appendChild(tr); tb.appendChild(th);
  const bd = document.createElement("tbody");
  filas.forEach(f => {
    const r = document.createElement("tr");
    f.forEach(v => { const td = document.createElement("td");
      if (v && typeof v === "object") { const p = document.createElement("span"); p.className = `pill pill--${v.rol}`; p.textContent = v.txt; td.appendChild(p); }
      else td.textContent = v === null || v === undefined || v === "" ? "–" : String(v);
      r.appendChild(td); });
    bd.appendChild(r);
  });
  tb.appendChild(bd);
}
function renderManual() {
  const man = (META.fuentes || []).filter(f => f.manual);
  tablaSimple($("tblFuentesMan"), [t("fm_archivo"), t("fm_filas"), t("fm_fecha"), t("fm_estado")],
    man.map(f => [f.archivo, (f.filas || 0).toLocaleString("en-US"), fmtFecha(f.extraido_el),
      f.falta ? { rol: "critical", txt: t("fm_falta") } : (f.existe ? { rol: "ok", txt: t("fm_ok") } : { rol: "neutral", txt: t("fm_noHay") })]));
  tablaSimple($("tblAjustes"), [t("a_order"), t("a_line"), t("a_item"), t("a_resp"), t("a_motivo"), t("a_aprobo"), t("a_fecha"), t("a_aplicado")],
    AJUSTES.map(a => [a[0], a[1], a[2], a[3], a[4], a[5], fmtFecha(a[6]), a[7] ? { rol: "ok", txt: t("a_si") } : { rol: "critical", txt: t("a_no") }]));
}

/* ============================================================
   TABLA DE DETALLE — las pestanas 1-10 del archivo como vistas
   ============================================================ */
const C = (field, type, extra) => Object.assign({ field, type }, extra || {});
const COLS_BASE = [C("division", "text"), C("item", "mono", { pn: true }), C("cliente", "text"), C("orden", "mono"), C("linea", "text"), C("ssd", "date"), C("qty", "num", { total: true })];
const PRESETS = [
  { id: "general", pd: true, filtro: () => true,
    cols: [C("division", "text"), C("sitio", "text"), C("resp", "text"), C("cliente", "text"), C("orden", "mono"), C("linea", "text"), C("item", "mono", { pn: true }),
           C("ssd", "date"), C("dias", "num"), C("rango", "text"), C("total", "usd", { total: true }), C("pd", "pd"), C("razon", "text"),
           C("razon_sitio", "text"), C("on_hold", "text"), C("manual", "manual")] },
  { id: "t1", pd: true, filtro: r => r.resp === "CMS IO Plant Northgate", cols: [...COLS_BASE, C("oh_ship", "num"), C("oh_all", "num"), C("total", "usd", { total: true })] },
  { id: "t2", pd: true, filtro: r => r.resp === "CMS IO Plant Valle Alto", cols: [...COLS_BASE, C("oh_ship", "num"), C("oh_all", "num"), C("total", "usd", { total: true })] },
  { id: "t3", pd: true, filtro: r => r.resp === "CMS IO Plant PLT1", cols: [...COLS_BASE, C("comentario", "text"), C("total", "usd", { total: true })] },
  { id: "t4", pd: true, filtro: r => r.resp === "CMS IO Plant PLT2", cols: [...COLS_BASE, C("comentario", "text"), C("transito", "text"), C("total", "usd", { total: true })] },
  { id: "t5", pd: true, filtro: r => r.resp === "CMS IO Plant Asia", cols: [...COLS_BASE, C("comentario", "text"), C("transito", "text"), C("total", "usd", { total: true })] },
  { id: "t6", pd: true, filtro: r => r.resp === "Intransit/Logistic", cols: [...COLS_BASE, C("comentario", "text"), C("transito", "text"), C("total", "usd", { total: true })] },
  { id: "t7", pd: true, filtro: r => r.resp === "CMS IO Distribution Mesa Verde" || r.resp === "CMS IO Distribution Riverton",
    cols: [...COLS_BASE, C("resp", "text"), C("comentario", "text"), C("transito", "text"), C("total", "usd", { total: true })] },
  { id: "t8", pd: true, filtro: r => r.resp === "Buyout", cols: [...COLS_BASE, C("comentario", "text"), C("transito", "text"), C("total", "usd", { total: true })] },
  { id: "t9", pd: true, filtro: r => r.resp === "Customer/Commercial",
    cols: [...COLS_BASE, C("comentario", "text"), C("transito", "text"), C("on_hold", "text"), C("cpu", "text"), C("total", "usd", { total: true })] },
  { id: "t10", pd: true, filtro: r => !!r.cpu && ["Backordered", "Ready to Release", "Released to Warehouse", "Staged/Pick Confirmed", ""].includes(r.ship_status || ""),
    cols: [C("division", "text"), C("item", "mono", { pn: true }), C("cliente", "text"), C("orden", "mono"), C("linea", "text"), C("ssd", "date"),
           C("holds", "text"), C("cpu", "text"), C("on_hold", "text"), C("total", "usd", { total: true })] },
  { id: "custDet", pd: true, filtro: r => r.resp === "Customer/Commercial",
    cols: [C("item", "mono", { pn: true }), C("org", "text"), C("cliente", "text"), C("division", "text"), C("total", "usd", { total: true })] },
  { id: "buyDet", pd: true, filtro: r => r.resp === "Buyout",
    cols: [C("item", "mono", { pn: true }), C("org", "text"), C("estatus_orden", "text"), C("oh", "text"), C("total", "usd", { total: true })] },
  { id: "todas", pd: false, filtro: () => true,
    cols: [C("division", "text"), C("org", "text"), C("cliente", "text"), C("orden", "mono"), C("linea", "text"), C("item", "mono", { pn: true }), C("ssd", "date"),
           C("estatus_orden", "text"), C("total", "usd", { total: true }), C("pd_origen", "text"), C("pd", "pd"), C("motivo", "motivo"),
           C("resp_origen", "text"), C("resp", "text"), C("manual", "manual")] }
];
const NOMBRE_PRESET = { general: "p_general", t1: "p_t1", t2: "p_t2", t3: "p_t3", t4: "p_t4", t5: "p_t5", t6: "p_t6", t7: "p_t7",
  t8: "p_t8", t9: "p_t9", t10: "p_t10", custDet: "p_custDet", buyDet: "p_buyDet", todas: "p_todas" };
const presetActual = () => PRESETS.find(p => p.id === preset) || PRESETS[0];
function initPresets() {
  const sel = $("presetSel"); const v = preset; sel.textContent = "";
  PRESETS.forEach(p => { const o = document.createElement("option"); o.value = p.id; o.textContent = t(NOMBRE_PRESET[p.id]); if (p.id === v) o.selected = true; sel.appendChild(o); });
}
$("presetSel").addEventListener("change", e => {
  if (!PRESETS.some(p => p.id === e.target.value)) return;
  preset = e.target.value; sortState.length = 0; currentPage = 1; renderTable(); syncURL();
});
function datosDetalle() {
  const p = presetActual();
  const d = getFilteredData().filter(r => (!p.pd || esPD(r)) && p.filtro(r));
  if (!sortState.length) return d.sort((a, b) => (b.total || 0) - (a.total || 0));
  return d.sort((a, b) => {
    for (const { field, dir } of sortState) { const c = comparar(a[field], b[field]); if (c) return dir === "asc" ? c : -c; }
    return 0;
  });
}
function celda(r, c) {
  const v = r[c.field];
  switch (c.type) {
    case "num": return fmtNum(v);
    case "usd": return fmtUsd(v);
    case "date": return fmtFecha(v);
    case "motivo": return v ? t("mo_" + v) : "";
    case "manual": return v ? t("man_" + v) : "";
    default: return v === null || v === undefined || v === "" ? "–" : String(v);
  }
}
function renderTable() {
  const p = presetActual();
  const cols = p.cols;
  const data = datosDetalle();
  const size = pageSize;
  const pages = Math.max(1, Math.ceil(data.length / size));
  currentPage = Math.min(currentPage, pages);
  const slice = data.slice((currentPage - 1) * size, currentPage * size);
  $("presetSub").textContent = `${t(NOMBRE_PRESET[p.id])} · ${t(p.pd ? "p_sub_pd" : "p_sub_todas")}`;

  const head = $("detailHead"); head.textContent = "";
  cols.forEach(c => {
    const th = document.createElement("th");
    const s = sortState.find(x => x.field === c.field);
    th.textContent = t("c_" + c.field);
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
      if (c.type === "num" || c.type === "usd") td.className = "num";
      if (c.type === "date") td.className = "date";
      if (c.type === "mono") td.style.fontFamily = "var(--font-mono)";
      if (c.type === "pd") {
        const pl = document.createElement("span");
        pl.className = `pill pill--${esPD(r) ? "critical" : (r.pd === "1 DAY PAST DUE" ? "warn" : "ok")}`;
        pl.textContent = r.pd; td.appendChild(pl);
      } else if (c.type === "manual" && r.manual) {
        const pl = document.createElement("span"); pl.className = "pill pill--manual"; pl.textContent = "✎ " + celda(r, c);
        pl.title = r.comentario || ""; td.appendChild(pl);
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
      if (c.total) { td.className = "num"; const s = data.reduce((a, r) => a + (+r[c.field] || 0), 0); td.textContent = c.type === "usd" ? fmtUsd(s) : fmtNum(s); }
      tr.appendChild(td);
    });
    foot.appendChild(tr);
  }
  renderPager(data.length, pages);
  $("rowCount").textContent = `${data.length.toLocaleString("en-US")} ${t("rows")}`;
  DIAG.visuales.tabla = { filas: slice.length, total: data.length, preset };
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
  const primera = (currentPage - 1) * pageSize;
  pageSize = v; currentPage = Math.floor(primera / pageSize) + 1;
  guardarLS("pastdue_page_size", v); renderTable();
});
initPageSize();

/* ============================================================
   EXPORTACION — la vista de detalle elegida, todas sus filas filtradas
   ============================================================ */
const FECHAS_EXPORT = new Set(["ssd", "req", "prom", "ordenada"]);
function valorExport(c, v) {
  if (v === null || v === undefined || v === "") return "";
  if (FECHAS_EXPORT.has(c)) return ISO.test(v) ? v : "";
  if (typeof v === "number" || typeof v === "boolean") return v;
  return String(v);
}
function exportRows() {
  const cols = presetActual().cols.map(c => c.field).filter((f, i, a) => a.indexOf(f) === i);
  return datosDetalle().map(r => { const o = {}; cols.forEach(c => { o[t("c_" + c)] = valorExport(c, r[c]); }); return o; });
}
function nombreArchivo(ext) {
  const d = new Date(), p = n => String(n).padStart(2, "0");
  const stamp = `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}`;
  return `${CONFIG.dashboardName}_${preset}_${stamp}.${ext}`;
}
/* Copia todos los numeros de la vista con los filtros puestos, sin repetidos, uno por renglon,
   para pegarlos directo en la seleccion multiple de SAP. */
$("btnCopyPn").addEventListener("click", e => {
  const b = e.currentTarget;
  const lista = [...new Set(datosDetalle().map(r => r.item).filter(v => v !== null && v !== undefined && v !== ""))];
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
  XLSX.utils.book_append_sheet(wb, ws, "Detalle");
  const meta = [
    ["Dashboard", CONFIG.dashboardName],
    [t("updated"), META.generated_at || ""],
    [t("corte"), META.fecha_corte || ""],
    [t("vistaDetalle"), t(NOMBRE_PRESET[preset])],
    [t("alcance"), t(scope === "pd" ? "scopePd" : "scopeTodas")],
    [t("rows"), rows.length],
    [t("filters"), [...$("chips").querySelectorAll(".chip")].map(c => c.textContent.replace("✕", "").trim()).join(" | ")],
    [],
    [t("s_fuente"), t("s_sistema"), t("s_archivo"), t("s_extraido"), t("s_filas"), t("s_manual")],
    ...(META.fuentes || []).map(f => [lang === "en" ? f.nombre_en : f.nombre, f.sistema, f.archivo, f.extraido_el || "", f.filas, f.manual ? "SI" : ""])
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(meta), "Metadata");
  XLSX.writeFile(wb, nombreArchivo("xlsx"));
});
function descargar(blob, name) {
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

/* ============================================================
   FRESCURA — la fuente de sistema mas vieja manda el semaforo
   (las de captura manual no cuentan: no tienen fecha de extraccion)
   ============================================================ */
function renderFreshness() {
  const fuentes = (META.fuentes || []).filter(f => !f.manual);
  $("metaUpdated").textContent = META.generated_at || "–";
  $("ftrUpdated").textContent = META.generated_at || "–";
  $("ftrSources").textContent = fuentes.filter(f => f.existe).map(f => (lang === "en" ? f.nombre_en : f.nombre)).join(", ") || "–";
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
  el.title = conFecha.map(f => `${lang === "en" ? f.nombre_en : f.nombre}: ${fmtFecha(f.extraido_el)} (${diasEntre(f.extraido_el, hoyISO())}d)`).join("\n");
}

/* ============================================================
   BANDA DE AVISOS
   ============================================================ */
function renderBanner() {
  const el = $("banner");
  const avisos = [];
  const q = META.qc || {};
  if (cargaFallo) avisos.push(["critical", t("errorTitle"), t("errorDetail")]);
  else {
    if (META.semi) avisos.push(["warn", t("semiTitle"), t("semiDetail")]);
    else if (META.demo) avisos.push(["warn", t("demoTitle"), t("demoDetail")]);
    (META.fuentes || []).filter(f => f.falta).forEach(f => avisos.push(["critical", t(f.manual ? "faltaManual" : "faltaFuente"), f.archivo]));
    if (q.ajustes_sin_match) avisos.push(["warn", t("ajustesTitle"), `${q.ajustes_sin_match} ${t("ajustesDetail")}`]);
    if (q.mktdiv_sin_catalogo && q.mktdiv_sin_catalogo.length) avisos.push(["warn", t("catTitle"), `${q.mktdiv_sin_catalogo.join(", ")} ${t("catDetail")}`]);
    if (q.sitio_otro_pd) avisos.push(["warn", t("respTitle"), `${q.sitio_otro_pd} ${t("respDetail")}`]);
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
const INFO_CARDS = { cardSitioTabla: "sitioTabla", cardRazonSitio: "razonSitio", cardFechas: "fechas", cardDiaria: "diaria",
  cardUnDia: "unDia", cardMensual: "mensual", cardHold: "hold", cardPlantaDiv: "plantaDiv", cardCategoria: "categoria",
  cardRazon: "razon", cardFamilia: "familia", cardRango: "rango", cardBridge: "bridge", cardBridgeCh: "bridgeCh", cardAjustes: "ajustes" };
function attachInfos() { Object.entries(INFO_CARDS).forEach(([card, id]) => attachInfo($(card), id)); }

/* ============================================================
   DOCUMENTACION Y DIAGNOSTICO
   ============================================================ */
function h3(txt) { const h = document.createElement("h3"); h.textContent = txt; return h; }
function lista(items) { const ul = document.createElement("ul"); (items || []).forEach(i => { const li = document.createElement("li"); li.textContent = i; ul.appendChild(li); }); return ul; }
function tablaDoc(cab, filas) {
  const tb = document.createElement("table"); tb.className = "tbl";
  tablaSimple(tb, cab, filas);
  return tb;
}
function renderDoc() {
  const d = CONFIG.documentation[lang] || {};
  const body = $("docBody"); body.textContent = "";
  $("docTitle").textContent = t("documentation");
  const p = document.createElement("p"); p.textContent = d.purpose;
  body.append(h3(t("purpose")), p, h3(t("sources")));
  body.appendChild(tablaDoc([t("s_fuente"), t("s_sistema"), t("s_archivo"), t("s_extraido"), t("s_filas")],
    (META.fuentes || []).map(f => [lang === "en" ? f.nombre_en : f.nombre, f.manual ? { rol: "manual", txt: "✎ " + t("s_manual") } : f.sistema,
      f.archivo, fmtFecha(f.extraido_el), (f.filas || 0).toLocaleString("en-US")])));
  body.append(h3(t("transformations")), lista(d.transformations), h3(t("measures")), lista(d.measures),
              h3(t("rules")), lista(d.rules), h3(t("limitations")), lista(d.limitations), h3(t("qc")));
  const q = META.qc || {};
  body.appendChild(tablaDoc(["", ""], [
    [t("qc_filas"), (q.filas || 0).toLocaleString("en-US")],
    [t("qc_sinSsd"), q.sin_ssd], [t("qc_undef"), q.razon_undefined], [t("qc_respVacia"), q.resp_vacia_pd],
    [t("qc_sinCat"), (q.mktdiv_sin_catalogo || []).join(", ") || "0"], [t("qc_ajustes"), q.ajustes_sin_match]
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

$("btnDiag").addEventListener("click", () => {
  const lineas = [`${t("diagTitle")} · ${new Date().toLocaleString()}`, "", "ms:"];
  Object.entries(DIAG.etapas).forEach(([k, v]) => lineas.push(`  ${k}: ${v}`));
  lineas.push("", "visuales:");
  CHARTS.forEach(c => {
    const box = $(c.id).parentElement, rc = box.getBoundingClientRect(), dv = DIAG.visuales[c.id] || {};
    lineas.push(`  ${c.id} [${c.view}]: ${dv.puntos ?? "-"} puntos, ${dv.series ?? "-"} series, con valor: ${dv.conValor ?? "-"} · ${Math.round(rc.width)}x${Math.round(rc.height)}px`);
  });
  const dt = DIAG.visuales.tabla || {};
  lineas.push(`  tabla: ${dt.filas} filas pintadas de ${dt.total} · vista ${dt.preset}`);
  lineas.push("", `rawData: ${rawData.length} · historial: ${HIST.length} · vista: ${view} · alcance: ${scope} · lang: ${lang}`,
              `filtros: ${JSON.stringify(filterState)}`);
  const body = $("docBody"); body.textContent = "";
  $("docTitle").textContent = t("diag");
  const pre = document.createElement("div"); pre.className = "diag-box"; pre.textContent = lineas.join("\n");
  body.appendChild(pre);
  docPanel.classList.add("is-open"); docOv.hidden = false;
});

/* ============================================================
   MODAL DE LA LINEA — la traza de la asignacion
   ============================================================ */
function abrirModal(r) {
  $("modalTitle").textContent = `${r.orden} · ${t("c_linea")} ${r.linea} · ${r.item}`;
  if (r.item) $("modalTitle").appendChild(pnBoton(r.item));
  const grid = $("modalGrid"); grid.textContent = "";
  [["cliente", r.cliente], ["division", r.division], ["org", r.org], ["total", fmtUsd(r.total)],
   ["resp_origen", r.resp_origen || "–"], ["resp", r.resp || "–"], ["sitio", r.sitio], ["manual", r.manual ? "✎ " + t("man_" + r.manual) : "–"],
   ["pd_origen", r.pd_origen], ["pd", r.pd], ["motivo", r.motivo ? t("mo_" + r.motivo) : "–"], ["dias", r.dias],
   ["ssd", fmtFecha(r.ssd)], ["req", fmtFecha(r.req)], ["prom", fmtFecha(r.prom)], ["estatus_orden", r.estatus_orden],
   ["oh", `${r.oh} · ${fmtNum(r.disp)} / ${fmtNum(r.qty)}`], ["transito", `${r.transito} · ${fmtNum(r.transito_qty)}`], ["oh_int", r.oh_int], ["on_hold", r.on_hold],
   ["holds", r.holds || "–"], ["cpu", r.cpu || "–"], ["override", r.override || "–"], ["freight", r.freight || "–"],
   ["razon", r.razon || "–"], ["categoria", r.categoria], ["razon_sitio", r.razon_sitio], ["comentario", r.comentario || "–"]
  ].forEach(([k, v]) => {
    const d = document.createElement("div"); d.className = "modal__dato";
    const s = document.createElement("span"); s.textContent = t("c_" + k); const b = document.createElement("b"); b.textContent = String(v);
    d.append(s, b); grid.appendChild(d);
  });
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
  $("tblBuscar").placeholder = t("buscarLinea");
  document.querySelectorAll("#langToggle button").forEach(b => b.classList.toggle("is-active", b.dataset.lang === lang));
  attachInfos(); initPresets();
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
   CARGA — portal primero, ./data_real/ y ./data/ en local. Sin datos
   de respaldo: si no llega nada, se dice.
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
  pintarVista(); pintarScope();
  applyLang();
  const t0 = performance.now();
  try {
    const [meta, dash] = await Promise.all([leerJSON("meta.json"), leerJSON("dashboard.json")]);
    META = meta || {};
    PDSET = new Set(META.pd_set || []);
    const cols = dash.detalle.columns;
    rawData = dash.detalle.rows.map(fila => { const o = {}; cols.forEach((c, i) => { o[c] = fila[i]; }); return o; });
    HIST = dash.historial || [];
    BRIDGE = dash.bridge || [];
    AJUSTES = dash.ajustes || [];
  } catch (e) {
    cargaFallo = true;
  }
  DIAG.etapas.carga = Math.round(performance.now() - t0);
  $("loading").hidden = true;
  readURL();
  pintarVista(); pintarScope();
  construirFiltros();
  applyLang();
}
init();

let rt;
addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => CHARTS.forEach(c => c.chart && c.chart.resize()), 150); });
