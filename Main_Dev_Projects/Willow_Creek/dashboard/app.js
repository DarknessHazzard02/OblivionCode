// Made by: Hazzard
"use strict";
/* ============================================================
   CONFIG — todo lo editable vive aqui. No tocar la logica abajo.
   ============================================================ */
const CONFIG = {
  dashboardName: "willow-creek",
  portalUrl: "/logistics/",
  dataUrls: ["./data/"],   // portafolio: solo datos inventados
  lang: { enabled: ["es", "en"], default: "es" },
  freshness: { warnDays: 1, criticalDays: 3 },
  maxDiasEntreFuentes: 1,     // fuentes transaccionales con mas de esto entre cortes -> aviso
  topN: 12,
  detail: { pageSize: 25, pageSizes: [25, 50, 100, 250, 500, 1000] },

  /* Una entrada por pestana. Los filtros van en el orden del estandar:
     alcance -> periodo (fecha) -> categorias cortas -> largas. */
  vistas: {
    ordenes: {
      alcance: ["categoria"], resto: ["hallazgos", "wc_status", "review_status", "sap_status", "om", "mes", "sold_nombre"],
      fecha: "recibido", fechaLabel: "f_recibido",
      buscar: ["po", "so", "so_manual", "sold_id", "sold_nombre", "asunto"],
      charts: ["chCategoria", "chHallazgos", "chMes", "chCliente"],
      archivo: "ordenes-wc-por-po"
    },
    sap: {
      alcance: ["tipo"], resto: ["potyp", "mes", "creado_por", "sold_nombre"],
      fecha: "creado", fechaLabel: "f_creado",
      buscar: ["so", "po", "sold_id", "sold_nombre"],
      charts: ["chSapCliente", "chSapPor"],
      archivo: "so-sap-clientes-wc-sin-wc"
    },
    archivos: {
      alcance: ["marcas"], resto: ["formato", "mes"],
      fecha: "fecha", fechaLabel: "f_fechaArchivo",
      buscar: ["archivo"],
      charts: ["chArchivos"],
      archivo: "reportes-recibidos-willow-creek"
    }
  },

  visuals: {
    kpi_ordenes: { info: {
      es: { medida: "Órdenes de WC (por PO) en cada situación.", calculo: "COUNT(PO) por categoría; el % es sobre las órdenes filtradas.", filtros: "Todos los filtros, salvo la selección de categoría.", granularidad: "PO del cliente, en su última actualización." },
      en: { medida: "WC orders (by PO) in each situation.", calculo: "COUNT(PO) by category; % is over the filtered orders.", filtros: "All filters except the category selection.", granularidad: "Customer PO, at its latest update." } } },
    chCategoria: { info: {
      es: { medida: "Órdenes por situación de proceso.", calculo: "Error = bloqueada, inválida, rechazada, error de WC o de SAP, sin respuesta o éxito sin SO. Capturada a mano = error en WC pero el PO ya está en una SO abierta.", filtros: "Filtros del panel y selección de las otras gráficas.", granularidad: "PO." },
      en: { medida: "Orders by processing situation.", calculo: "Error = blocked, invalid, rejected, WC or SAP error, no response or success without SO. Entered manually = WC error but the PO is already on an open SO.", filtros: "Panel filters and the other charts' selection.", granularidad: "PO." } } },
    chHallazgos: { info: {
      es: { medida: "Cuántas órdenes tienen cada hallazgo.", calculo: "COUNT(PO) con el hallazgo. Una orden puede tener varios: las barras no suman el total.", filtros: "Filtros del panel y selección de las otras gráficas.", granularidad: "PO × hallazgo." },
      en: { medida: "How many orders carry each finding.", calculo: "COUNT(PO) with the finding. An order can have several: bars do not add up to the total.", filtros: "Panel filters and the other charts' selection.", granularidad: "PO × finding." } } },
    chMes: { info: {
      es: { medida: "Órdenes recibidas por mes y su situación.", calculo: "COUNT(PO) por mes de la fecha de recepción en WC, apilado por categoría.", filtros: "Filtros del panel y selección de las otras gráficas.", granularidad: "Mes de recepción." },
      en: { medida: "Orders received per month and their situation.", calculo: "COUNT(PO) by month of the WC received date, stacked by category.", filtros: "Panel filters and the other charts' selection.", granularidad: "Received month." } } },
    chCliente: { info: {
      es: { medida: "Clientes con más órdenes que no salieron limpias.", calculo: "COUNT(PO) con categoría distinta de Procesada, por Sold-To de WC; top 12.", filtros: "Excluye las procesadas sin observaciones.", granularidad: "Cliente (Sold To Name de WC)." },
      en: { medida: "Customers with the most orders that did not go through clean.", calculo: "COUNT(PO) with a category other than Processed, by WC Sold-To; top 12.", filtros: "Excludes orders processed with no findings.", granularidad: "Customer (WC Sold To Name)." } } },
    kpi_sap: { info: {
      es: { medida: "Órdenes abiertas de SAP de clientes WC que no pasaron por WC.", calculo: "COUNT(SO) de WC_FOLLOWUP con Sold-To en ZWCCUST, creadas desde la primera recepción del historial de WC, sin SO ni PO en WC.", filtros: "Todos los filtros, salvo la selección de las tarjetas.", granularidad: "Orden de venta." },
      en: { medida: "Open SAP orders of WC customers that did not go through WC.", calculo: "COUNT(SO) from WC_FOLLOWUP with a Sold-To in ZWCCUST, created since the first received date in the WC history, with no SO or PO in WC.", filtros: "All filters except the cards' selection.", granularidad: "Sales order." } } },
    chSapCliente: { info: {
      es: { medida: "Órdenes capturadas fuera de WC por cliente.", calculo: "COUNT(SO) por Sold-To, apilado por tipo; top 12.", filtros: "Filtros del panel y selección de la otra gráfica.", granularidad: "Cliente." },
      en: { medida: "Orders entered outside WC by customer.", calculo: "COUNT(SO) by Sold-To, stacked by type; top 12.", filtros: "Panel filters and the other chart's selection.", granularidad: "Customer." } } },
    chSapPor: { info: {
      es: { medida: "Quién capturó las órdenes fuera de WC.", calculo: "COUNT(SO) por Created By de SAP, apilado por tipo; top 12.", filtros: "Filtros del panel y selección de la otra gráfica.", granularidad: "Usuario de SAP." },
      en: { medida: "Who entered the orders outside WC.", calculo: "COUNT(SO) by SAP Created By, stacked by type; top 12.", filtros: "Panel filters and the other chart's selection.", granularidad: "SAP user." } } },
    kpi_archivos: { info: {
      es: { medida: "Reportes de Willow Creek recibidos y sus marcas.", calculo: "COUNT(archivo) con cada marca. Consolidado = junta 15 o más fechas de recepción distintas.", filtros: "Todos los filtros, salvo la selección de las tarjetas.", granularidad: "Archivo." },
      en: { medida: "Willow Creek reports received and their flags.", calculo: "COUNT(file) with each flag. Consolidated = holds 15 or more distinct received dates.", filtros: "All filters except the cards' selection.", granularidad: "File." } } },
    chArchivos: { info: {
      es: { medida: "Renglones de cada reporte.", calculo: "COUNT(renglones) por archivo, en orden de corte. Rojo = parece consolidado; ámbar = mucho más grande que la mediana; gris = idéntico a otro.", filtros: "Filtros del panel.", granularidad: "Archivo (corte)." },
      en: { medida: "Rows in each report.", calculo: "COUNT(rows) per file, in cut order. Red = looks consolidated; amber = much larger than the median; grey = identical to another.", filtros: "Panel filters.", granularidad: "File (cut)." } } }
  },

  documentation: {
    es: {
      purpose: "Muestra qué órdenes que llegaron a Willow Creek no se procesaron, cuáles quedaron mal capturadas en SAP y qué otros errores tiene el proceso. Cruza los reportes diarios de Willow Creek contra las órdenes abiertas de SAP (WC_FOLLOWUP, SDD167) y el catálogo de clientes WC (ZWCCUST). También revisa los reportes recibidos para encontrar el que sea distinto (el consolidado mensual).",
      transformations: [
        "Cada reporte de Willow Creek es un corte (fecha y hora del nombre del archivo). Un envío (ID) toma los valores del último corte en que aparece.",
        "Los envíos se agrupan por PO del cliente. Manda la última actualización; si algún envío del PO ya quedó creado en SAP (Success con SO), manda ese: un rechazo posterior suele ser el duplicado del mismo PO.",
        "SO = 0000000000 cuenta como sin SO. Los documentos de SAP se comparan sin ceros a la izquierda.",
        "Para las órdenes que WC no creó, el PO se busca en WC_FOLLOWUP solo con letras y números y sin 'PO' al inicio (238695 = PO238695).",
        "SAP sin WC: órdenes abiertas de WC_FOLLOWUP con Sold-To en ZWCCUST, creadas desde la primera recepción del historial de WC, cuyo SO no viene en WC.",
        "Las notas 'PO: n' se agrupan como 'PO: <n>'."
      ],
      measures: [
        "Órdenes = POs distintos en los reportes de WC.",
        "Días desde recepción = días entre Received Date y la fecha del último reporte.",
        "Intentos = cuántos envíos distintos (ID) trajo el mismo PO.",
        "Hallazgos: ver la tabla de abajo; una orden puede tener varios."
      ],
      rules: [
        "Con error / sin procesar: tiene un hallazgo crítico del proceso (bloqueada, inválida, error de WC, rechazada, error de SAP, sin respuesta, éxito sin SO) y el PO no está en ninguna SO abierta.",
        "Error en WC, capturada a mano en SAP: el mismo caso, pero el PO sí aparece en una SO abierta capturada fuera de WC.",
        "Pendiente: en proceso o esperando revisión, sin error.",
        "Procesada con observaciones: creada en SAP pero con algún hallazgo de nivel crítico o advertencia (p. ej. PO distinto, sin Sold-To, OM distinto, advertencias de SAP).",
        "Procesada: creada en SAP sin hallazgos (o solo informativos).",
        "Los estatus, notas y parejas válidas salen de Reporting Notes (Basecamp)."
      ],
      limitations: [
        "WC_FOLLOWUP solo trae órdenes ABIERTAS: una SO ya surtida no aparece, y por eso 'SO no está abierta' es informativo, no un error.",
        "Una orden capturada a mano con un PO muy distinto al de WC no se encuentra y queda como error.",
        "El historial solo cubre los reportes que hay en la carpeta: lo que pasó antes del primer reporte no se ve.",
        "SDD167 solo se usa para validar que sus órdenes estén en WC_FOLLOWUP (cubre el mes en curso)."
      ]
    },
    en: {
      purpose: "Shows which orders that reached Willow Creek were not processed, which were entered wrong in SAP and what other errors the process has. Crosses the Willow Creek daily reports against SAP open orders (WC_FOLLOWUP, SDD167) and the WC customer catalog (ZWCCUST). It also checks the received reports to find the one that is different (the monthly consolidated one).",
      transformations: [
        "Each Willow Creek report is a cut (date and time from the file name). A submission (ID) takes the values of the last cut it appears in.",
        "Submissions are grouped by customer PO. The latest update wins; if any submission of the PO was already created in SAP (Success with SO), that one wins: a later rejection is usually the duplicate of the same PO.",
        "SO = 0000000000 counts as no SO. SAP documents are compared without leading zeros.",
        "For orders WC did not create, the PO is looked up in WC_FOLLOWUP using only letters and digits and without a leading 'PO' (238695 = PO238695).",
        "SAP without WC: WC_FOLLOWUP open orders with a Sold-To in ZWCCUST, created since the first received date in the WC history, whose SO is not in WC.",
        "'PO: n' notes are grouped as 'PO: <n>'."
      ],
      measures: [
        "Orders = distinct POs in the WC reports.",
        "Days since received = days between Received Date and the date of the latest report.",
        "Attempts = how many distinct submissions (ID) carried the same PO.",
        "Findings: see the table below; an order can have several."
      ],
      rules: [
        "Error / not processed: has a critical process finding (blocked, invalid, WC error, rejected, SAP error, no response, success without SO) and the PO is not on any open SO.",
        "WC error, entered manually in SAP: the same case, but the PO does appear on an open SO entered outside WC.",
        "Pending: in progress or awaiting review, with no error.",
        "Processed with findings: created in SAP but with a critical or warning finding (e.g. different PO, no Sold-To, different OM, SAP warnings).",
        "Processed: created in SAP with no findings (or informational only).",
        "Valid statuses, notes and pairs come from Reporting Notes (Basecamp)."
      ],
      limitations: [
        "WC_FOLLOWUP only has OPEN orders: an already shipped SO does not show up, so 'SO not open' is informational, not an error.",
        "An order entered manually with a PO very different from WC's is not found and stays as an error.",
        "The history only covers the reports in the folder: anything before the first report is not visible.",
        "SDD167 is only used to check that its orders are in WC_FOLLOWUP (it covers the current month)."
      ]
    }
  }
};

const I18N = {
  es: {
    backToPortal: "Volver al Portal", pageTitle: "Control de Órdenes Willow Creek",
    pageSub: "Willow Creek × SAP (WC_FOLLOWUP · SDD167 · ZWCCUST) · órdenes sin procesar y errores.",
    updated: "Actualizado", extracted: "Extraído el", filters: "Filtros", clearFilters: "Limpiar Filtros",
    documentation: "Documentación", source: "Fuente", rows: "filas", rowsPerPage: "Filas por Página", showing: "Mostrando", of: "de",
    noData: "Sin datos para los filtros seleccionados.", loading: "Cargando datos…",
    copy_pn: "Copiar número", copy_fail: "No se pudo copiar",
    search: "Buscar…", seleccionarTodo: "Seleccionar Todo", seleccionados: "seleccionados",
    sinValor: "(Sin Dato)", seleccionadaOculta: "seleccionada no se ve con esta búsqueda.",
    seleccionadasOcultas: "seleccionadas no se ven con esta búsqueda.", si: "Sí", no: "No",
    tab_ordenes: "Órdenes de WC", tab_sap: "SAP sin WC", tab_archivos: "Reportes Recibidos",
    f_categoria: "Situación", f_hallazgos: "Hallazgo", f_wc_status: "WC Status", f_review_status: "Review Status",
    f_sap_status: "SAP Status", f_om: "Order Manager", f_mes: "Mes", f_sold_nombre: "Cliente (Sold-To)",
    f_tipo: "Tipo", f_potyp: "Tipo de PO (POtyp)", f_creado_por: "Creado por", f_marcas: "Marca", f_formato: "Formato",
    f_recibido: "Fecha de Recepción", f_creado: "Fecha de Creación en SAP", f_fechaArchivo: "Fecha del Reporte",
    f_q: "Búsqueda", f_kpi: "Tarjeta", f_archivo: "Archivo",
    desde: "Desde", hasta: "Hasta", fueraRango: "filas sin esa fecha quedan fuera del rango.",
    k_ofTotal: "de las filtradas.", k_sapTotal: "SO Abiertas sin WC", k_bloqueo: "Con Bloqueo de Entrega",
    k_dfue: "Tipo de PO DFUE", k_archTotal: "Reportes Recibidos", k_ninguno: "Ninguno",
    info_ordenes: "Último Reporte", envios: "Envíos", ordenesPO: "Órdenes (PO)",
    info_sap: "Clientes en ZWCCUST", info_sapDesde: "SO Creadas desde",
    v_categoria: "Órdenes por Situación", v_hallazgos: "Hallazgos", v_hallazgos_sub: "Órdenes con cada hallazgo · una orden puede tener varios.",
    v_mes: "Órdenes Recibidas por Mes", v_mes_sub: "Por mes de recepción en WC, apilado por situación.",
    v_cliente: "Clientes con Más Órdenes con Problema", v_cliente_sub: "Órdenes que no quedaron como Procesada · top 12.",
    v_sapCliente: "SO Fuera de WC por Cliente", v_sapPor: "SO Fuera de WC por Usuario de SAP",
    v_archivos: "Renglones por Reporte", v_archivos_sub: "Cada barra es un archivo, en orden de corte.",
    ordenes: "órdenes", so: "SO", archivos: "archivos", renglones: "renglones",
    detail_ordenes: "Órdenes de WC por PO (Última Actualización)", detail_sap: "SO Abiertas de Clientes WC que No Pasaron por WC",
    detail_archivos: "Reportes de Willow Creek Recibidos",
    buscar_ordenes: "Buscar PO, SO, Cliente o Asunto…", buscar_sap: "Buscar SO, PO o Cliente…", buscar_archivos: "Buscar Archivo…",
    c_po: "PO", c_categoria: "Situación", c_hallazgos: "Hallazgos", c_dias: "Días desde Recepción", c_recibido: "Recibido",
    c_fecha_orden: "Fecha de la Orden", c_sold_id: "Sold-To", c_sold_nombre: "Cliente", c_om: "Order Manager",
    c_om_zwccust: "OM en ZWCCUST", c_wc_status: "WC Status", c_review_status: "Review Status", c_sap_status: "SAP Status",
    c_nota: "Nota", c_nota_txt: "Nota", c_so: "SO", c_so_manual: "SO Capturada a Mano", c_so_po: "PO en SAP",
    c_so_entrega: "Entrega Solicitada", c_so_bloqueos: "Bloqueo de Entrega", c_intentos: "Intentos",
    c_ultimo_archivo: "Último Reporte", c_ship_id: "Ship-To", c_ship_nombre: "Ship-To Nombre", c_asunto: "Asunto",
    c_sap_enviado: "Enviado a SAP", c_revision_hecha: "Revisión Terminada",
    c_tipo: "Tipo", c_potyp: "POtyp", c_creado: "Creada", c_creado_por: "Creada por", c_entrega: "Entrega Solicitada",
    c_lineas: "Líneas", c_cantidad: "Cantidad", c_bloqueos: "Bloqueo de Entrega", c_en_sdd167: "En SDD167",
    c_archivo: "Archivo", c_corte: "Corte", c_marcas: "Marcas", c_formato: "Formato", c_filas: "Renglones",
    c_nuevos: "Envíos Nuevos", c_dias_recibido: "Fechas de Recepción", c_recibido_min: "Recibido desde",
    c_recibido_max: "Recibido hasta", c_identico_a: "Idéntico a", c_bytes: "Bytes", c_columnas: "Columnas",
    purpose: "Propósito", sources: "Fuentes de Datos", transformations: "Transformaciones",
    measures: "Diccionario de Medidas", rules: "Reglas de Negocio", limitations: "Limitaciones Conocidas",
    contact: "Contacto", qc: "Controles de Calidad", catHallazgos: "Catálogo de Hallazgos", nivel: "Nivel",
    s_fuente: "Fuente", s_sistema: "Sistema", s_ruta: "Ruta", s_archivo: "Archivo", s_extraido: "Extraído el",
    s_actualizado: "Actualizado", s_filas: "Filas", s_catalogo: "Catálogo",
    qc_archivos: "Reportes Leídos", qc_envios: "Envíos (ID) Distintos", qc_ordenes: "Órdenes (PO)",
    qc_fu: "Renglones de WC_FOLLOWUP / SO Abiertas", qc_sdd: "Renglones de SDD167 / SO", qc_sddNoFu: "SO de SDD167 que No Están en WC_FOLLOWUP",
    qc_zwc: "Clientes en ZWCCUST",
    i_medida: "Medida", i_calculo: "Cálculo", i_filtros: "Filtros", i_gran: "Granularidad",
    degradedTitle: "Datos incompletos — el tablero está en modo degradado.",
    degradedStructure: "No llegó el catálogo de situaciones o de hallazgos. Las gráficas van en orden alfabético y sin color por severidad. La tabla de detalle SÍ es confiable.",
    errorTitle: "No se pudieron leer los datos del tablero.",
    errorDetail: "No respondió ninguna de las rutas de datos. Nada de lo que se ve es confiable hasta que carguen.",
    faltaFuente: "Falta una fuente de datos.",
    semiTitle: "Datos semi-ficticios — forma real, identidades inventadas.",
    semiDetail: "Salen de un corte real con clientes, materiales, documentos y personas cambiados, y los montos movidos ±15 %. Sirven para analizar con datos parecidos a los reales; no para decidir.",
    demoTitle: "Datos inventados — no son de Willow Creek ni de SAP.",
    demoDetail: "Sirven para probar el tablero: la forma es la del reporte, los números no son reales.",
    cortesTitle: "Las fuentes son de cortes distintos.",
    cortesDetail: "Una orden puede verse sin procesar (o procesada) solo por el desfase entre WC y SAP.",
    sddTitle: "SDD167 trae órdenes que no están en WC_FOLLOWUP.",
    sddDetail: "Los dos extractos de SAP no cuadran: revisa que WC_FOLLOWUP sea del mismo día.",
    consTitle: "Hay un reporte distinto a los demás.",
    resp_si: "Archivo Distinto: {lista}",
    resp_siDet: "Junta {dias} o más fechas de recepción distintas, mientras que los demás son cortes diarios (mediana de {mediana} renglones). Ese es el que hay que validar.",
    resp_no: "Ninguno de los {n} reportes es un consolidado mensual.",
    resp_noDet: "Del {primero} al {ultimo} todos son cortes diarios: el más grande trae {max} renglones (mediana {mediana}) y ninguno junta {dias} o más fechas de recepción. Lo que sí cambia: hasta el {cambio} llegaban 3 al día con {colViejo} columnas; desde ese día llega uno a las 11 AM con {colNuevo}. {identicos} archivos son idénticos a otro (días sin movimiento). Si debía llegar un consolidado por mes, no está en la carpeta.",
    diag: "Diagnóstico", diagTitle: "Diagnóstico del Último Redibujo",
    m_intentos: "Envíos a WC de este PO (del más viejo al más nuevo).", m_id: "ID", m_recibido: "Recibido",
    m_primer: "Primer Reporte", m_ultimo: "Último Reporte"
  },
  en: {
    backToPortal: "Back to the Portal", pageTitle: "Willow Creek Order Control",
    pageSub: "Willow Creek × SAP (WC_FOLLOWUP · SDD167 · ZWCCUST) · unprocessed orders and errors.",
    updated: "Updated", extracted: "Extracted on", filters: "Filters", clearFilters: "Clear Filters",
    documentation: "Documentation", source: "Source", rows: "rows", rowsPerPage: "Rows per Page", showing: "Showing", of: "of",
    noData: "No data for the selected filters.", loading: "Loading data…",
    copy_pn: "Copy number", copy_fail: "Could not copy",
    search: "Search…", seleccionarTodo: "Select All", seleccionados: "selected",
    sinValor: "(No Value)", seleccionadaOculta: "selected item is hidden by this search.",
    seleccionadasOcultas: "selected are hidden by this search.", si: "Yes", no: "No",
    tab_ordenes: "WC Orders", tab_sap: "SAP without WC", tab_archivos: "Received Reports",
    f_categoria: "Situation", f_hallazgos: "Finding", f_wc_status: "WC Status", f_review_status: "Review Status",
    f_sap_status: "SAP Status", f_om: "Order Manager", f_mes: "Month", f_sold_nombre: "Customer (Sold-To)",
    f_tipo: "Type", f_potyp: "PO Type (POtyp)", f_creado_por: "Created by", f_marcas: "Flag", f_formato: "Format",
    f_recibido: "Received Date", f_creado: "SAP Created Date", f_fechaArchivo: "Report Date",
    f_q: "Search", f_kpi: "Card", f_archivo: "File",
    desde: "From", hasta: "To", fueraRango: "rows without that date fall outside the range.",
    k_ofTotal: "of the filtered.", k_sapTotal: "Open SOs without WC", k_bloqueo: "With Delivery Block",
    k_dfue: "PO Type DFUE", k_archTotal: "Reports Received", k_ninguno: "None",
    info_ordenes: "Latest Report", envios: "Submissions", ordenesPO: "Orders (PO)",
    info_sap: "Customers in ZWCCUST", info_sapDesde: "SOs Created Since",
    v_categoria: "Orders by Situation", v_hallazgos: "Findings", v_hallazgos_sub: "Orders with each finding · an order can have several.",
    v_mes: "Orders Received per Month", v_mes_sub: "By WC received month, stacked by situation.",
    v_cliente: "Customers with the Most Problem Orders", v_cliente_sub: "Orders not left as Processed · top 12.",
    v_sapCliente: "SOs Outside WC by Customer", v_sapPor: "SOs Outside WC by SAP User",
    v_archivos: "Rows per Report", v_archivos_sub: "Each bar is a file, in cut order.",
    ordenes: "orders", so: "SOs", archivos: "files", renglones: "rows",
    detail_ordenes: "WC Orders by PO (Latest Update)", detail_sap: "Open SOs of WC Customers That Did Not Go Through WC",
    detail_archivos: "Willow Creek Reports Received",
    buscar_ordenes: "Search PO, SO, Customer or Subject…", buscar_sap: "Search SO, PO or Customer…", buscar_archivos: "Search File…",
    c_po: "PO", c_categoria: "Situation", c_hallazgos: "Findings", c_dias: "Days Since Received", c_recibido: "Received",
    c_fecha_orden: "Order Date", c_sold_id: "Sold-To", c_sold_nombre: "Customer", c_om: "Order Manager",
    c_om_zwccust: "OM in ZWCCUST", c_wc_status: "WC Status", c_review_status: "Review Status", c_sap_status: "SAP Status",
    c_nota: "Note", c_nota_txt: "Note", c_so: "SO", c_so_manual: "Manually Entered SO", c_so_po: "PO in SAP",
    c_so_entrega: "Requested Delivery", c_so_bloqueos: "Delivery Block", c_intentos: "Attempts",
    c_ultimo_archivo: "Latest Report", c_ship_id: "Ship-To", c_ship_nombre: "Ship-To Name", c_asunto: "Subject",
    c_sap_enviado: "Sent to SAP", c_revision_hecha: "Review Completed",
    c_tipo: "Type", c_potyp: "POtyp", c_creado: "Created", c_creado_por: "Created by", c_entrega: "Requested Delivery",
    c_lineas: "Lines", c_cantidad: "Quantity", c_bloqueos: "Delivery Block", c_en_sdd167: "In SDD167",
    c_archivo: "File", c_corte: "Cut", c_marcas: "Flags", c_formato: "Format", c_filas: "Rows",
    c_nuevos: "New Submissions", c_dias_recibido: "Received Dates", c_recibido_min: "Received from",
    c_recibido_max: "Received to", c_identico_a: "Identical to", c_bytes: "Bytes", c_columnas: "Columns",
    purpose: "Purpose", sources: "Data Sources", transformations: "Transformations",
    measures: "Measure Dictionary", rules: "Business Rules", limitations: "Known Limitations",
    contact: "Contact", qc: "Quality Checks", catHallazgos: "Findings Catalog", nivel: "Level",
    s_fuente: "Source", s_sistema: "System", s_ruta: "Path", s_archivo: "File", s_extraido: "Extracted on",
    s_actualizado: "Updated", s_filas: "Rows", s_catalogo: "Catalog",
    qc_archivos: "Reports Read", qc_envios: "Distinct Submissions (ID)", qc_ordenes: "Orders (PO)",
    qc_fu: "WC_FOLLOWUP Rows / Open SOs", qc_sdd: "SDD167 Rows / SOs", qc_sddNoFu: "SDD167 SOs Missing from WC_FOLLOWUP",
    qc_zwc: "Customers in ZWCCUST",
    i_medida: "Measure", i_calculo: "Calculation", i_filtros: "Filters", i_gran: "Granularity",
    degradedTitle: "Incomplete data — this dashboard is running degraded.",
    degradedStructure: "The situation or findings catalog did not arrive. Charts are alphabetical and without severity colors. The detail table IS reliable.",
    errorTitle: "The dashboard data could not be read.",
    errorDetail: "None of the data paths responded. Nothing on screen is reliable until the data loads.",
    faltaFuente: "A data source is missing.",
    semiTitle: "Semi-fictitious data — real shape, made-up identities.",
    semiDetail: "Built from a real cut with customers, materials, documents and people replaced, and amounts shifted ±15%. Good for analysis on realistic data; not for decisions.",
    demoTitle: "Made-up data — not from Willow Creek or SAP.",
    demoDetail: "They are for testing the dashboard: the layout is the report's, the numbers are not real.",
    cortesTitle: "The sources come from different extracts.",
    cortesDetail: "An order may look unprocessed (or processed) only because of the gap between WC and SAP.",
    sddTitle: "SDD167 has orders that are not in WC_FOLLOWUP.",
    sddDetail: "The two SAP extracts do not match: check that WC_FOLLOWUP is from the same day.",
    consTitle: "One report is different from the others.",
    resp_si: "Different File: {lista}",
    resp_siDet: "It holds {dias} or more distinct received dates, while the others are daily cuts (median {mediana} rows). That is the one to validate.",
    resp_no: "None of the {n} reports is a monthly consolidated one.",
    resp_noDet: "From {primero} to {ultimo} all are daily cuts: the largest has {max} rows (median {mediana}) and none holds {dias} or more received dates. What does change: until {cambio} three a day arrived with {colViejo} columns; since then one arrives at 11 AM with {colNuevo}. {identicos} files are identical to another (days with no activity). If a monthly consolidated file was due, it is not in the folder.",
    diag: "Diagnostics", diagTitle: "Last Redraw Diagnostics",
    m_intentos: "WC submissions of this PO (oldest to newest).", m_id: "ID", m_recibido: "Received",
    m_primer: "First Report", m_ultimo: "Latest Report"
  }
};

/* ============================================================
   ESTADO — uno por pestana; una sola puerta de redibujo
   ============================================================ */
let META = {};
const DATA = { ordenes: [], sap: [], archivos: [] };
let INTENTOS = {};
let lang = leerLS("dash_lang") || CONFIG.lang.default;
if (!CONFIG.lang.enabled.includes(lang)) lang = CONFIG.lang.default;
let vista = "ordenes";
let pageSize = (() => { const v = +leerLS("wc_page_size"); return CONFIG.detail.pageSizes.includes(v) ? v : CONFIG.detail.pageSize; })();
const S = {};
Object.keys(CONFIG.vistas).forEach(v => { S[v] = { panel: {}, desde: "", hasta: "", q: "", crossfilter: null, sort: [], page: 1 }; });
const st = () => S[vista];
const rows = () => DATA[vista];
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
const tpl = (k, o) => t(k).replace(/\{(\w+)\}/g, (_, x) => (o[x] === undefined || o[x] === null) ? "–" : String(o[x]));
function leerLS(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function guardarLS(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* sin storage: no pasa nada */ } }
const $ = id => document.getElementById(id);

/* ============================================================
   CATALOGOS: orden, rol y etiqueta salen de meta.filters
   ============================================================ */
const CATALOGO = { categoria: "categoria", hallazgos: "hallazgos", tipo: "tipo_sap", marcas: "marcas_archivo" };
const ARRAYS = new Set(["hallazgos", "marcas"]);
let degradado = false;
function catalogo(campo) {
  const nombre = CATALOGO[campo];
  return (nombre && META.filters && META.filters[nombre]) || [];
}
function itemCat(campo, valor) { return catalogo(campo).find(x => x.valor === valor) || null; }
function nombreCat(campo, valor) { const c = itemCat(campo, valor); return c ? (c[lang] || c.valor) : valor; }
function rolCat(campo, valor) { const c = itemCat(campo, valor); return c ? c.rol : null; }
function colorRol(rol, i) {
  if (rol === "critical") return cssVar("--c-critical");
  if (rol === "warn") return cssVar("--c-warn");
  if (rol === "ok") return cssVar("--c-ok");
  if (rol === "neutral") return cssVar("--c-neutral");
  if (rol === "manual") return cssVar("--c-cat-2");
  if (rol === "obs") return cssVar("--c-cat-4");
  return cssVar(`--c-cat-${Math.min((i || 0) + 1, 5)}`);
}
function initCatalogos() {
  degradado = !cargaFallo && (!catalogo("categoria").length || !catalogo("hallazgos").length);
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
function hoyISO() { const d = new Date(); return utcAISO(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())); }
function diasEntre(a, b) { return Math.round((isoAUTC(b) - isoAUTC(a)) / 864e5); }

function fmtNum(v, dec) {
  if (v === null || v === undefined || v === "" || Number.isNaN(+v)) return "–";
  const n = +v;
  const s = Math.abs(n).toLocaleString("en-US", { minimumFractionDigits: dec || 0, maximumFractionDigits: dec || 0 });
  return n < 0 ? `(${s})` : s;
}
function fmtFecha(iso) {
  if (!iso || !ISO.test(String(iso).slice(0, 10))) return "–";
  const [y, m, d] = String(iso).slice(0, 10).split("-");
  const hora = String(iso).length > 10 ? " " + String(iso).slice(11, 16) : "";
  return (lang === "es" ? `${d}/${m}/${y}` : `${m}/${d}/${y}`) + hora;
}
function fmtMes(wc) {
  if (!/^\d{4}-\d{2}$/.test(wc || "")) return "–";
  const [y, m] = wc.split("-");
  const mes = new Date(Date.UTC(+y, +m - 1, 1)).toLocaleString(lang === "es" ? "es-MX" : "en-US", { month: "short", timeZone: "UTC" });
  const corto = mes.replace(".", "");
  return `${corto.charAt(0).toUpperCase()}${corto.slice(1)} ${y}`;   // "oct 2026" -> "Oct 2026"
}
function abbr(n) {
  const a = Math.abs(n);
  if (a >= 1e9) return (n / 1e9).toFixed(1) + "B";
  if (a >= 1e6) return (n / 1e6).toFixed(1) + "M";
  if (a >= 1e3) return (n / 1e3).toFixed(1) + "K";
  return Math.round(n).toLocaleString("en-US");
}

/* ============================================================
   KPIs — la condicion va por valor de catalogo o por campo, nunca por texto visible
   ============================================================ */
function kpisDe(v) {
  if (v === "ordenes") {
    return catalogo("categoria").map(c => ({ id: c.valor, campo: "categoria", rol: c.rol,
      label: () => nombreCat("categoria", c.valor), pred: r => r.categoria === c.valor }));
  }
  if (v === "sap") {
    return [
      { id: "total", rol: "neutral", label: () => t("k_sapTotal"), pred: () => true },
      ...catalogo("tipo").map(c => ({ id: c.valor, campo: "tipo", rol: c.rol, label: () => nombreCat("tipo", c.valor), pred: r => r.tipo === c.valor })),
      { id: "bloqueo", rol: "warn", label: () => t("k_bloqueo"), pred: r => !!r.bloqueos }
    ];
  }
  return [
    { id: "total", rol: "neutral", label: () => t("k_archTotal"), pred: () => true },
    ...["CONSOLIDADO", "GRANDE", "FORMATO_ANTERIOR", "IDENTICO"].map(m => ({ id: m, rol: rolCat("marcas", m) || "neutral",
      label: () => nombreCat("marcas", m), pred: r => (r.marcas || []).includes(m) }))
  ];
}

/* ============================================================
   FILTRADO
   ============================================================ */
function tieneValor(r, campo, vals) {
  if (ARRAYS.has(campo)) return (r[campo] || []).some(x => vals.includes(x));
  return vals.includes(valorCrudo(r[campo]));
}
function matchesPanel(r) {
  const s = st(), cfg = CONFIG.vistas[vista];
  for (const [f, vals] of Object.entries(s.panel)) {
    if (vals && vals.length && !tieneValor(r, f, vals)) return false;
  }
  if (s.desde || s.hasta) {
    const d = String(r[cfg.fecha] || "").slice(0, 10);
    if (!d) return false;
    if (s.desde && d < s.desde) return false;
    if (s.hasta && d > s.hasta) return false;
  }
  if (s.q) {
    const q = s.q.toLowerCase();
    if (!cfg.buscar.some(c => String(r[c] || "").toLowerCase().includes(q))) return false;
  }
  return true;
}
function matchesCrossfilter(r, cf) {
  if (!cf) return true;
  if (cf.field === "kpi") return cf.values.some(id => { const k = kpisDe(vista).find(x => x.id === id); return k && k.pred(r); });
  return tieneValor(r, cf.field, cf.values);
}
/* exceptField: el visual que origino la seleccion se dibuja sin ella (y atenua lo no seleccionado). */
function getFilteredData(exceptField) {
  const cf = st().crossfilter;
  const usarCf = cf && cf.field !== exceptField ? cf : null;
  return rows().filter(r => matchesPanel(r) && matchesCrossfilter(r, usarCf));
}
function comparar(va, vb) {
  if (Array.isArray(va)) va = va.length; if (Array.isArray(vb)) vb = vb.length;
  const na = va === null || va === undefined || va === "", nb = vb === null || vb === undefined || vb === "";
  if (na || nb) return na === nb ? 0 : (na ? 1 : -1);          // vacios siempre al final
  if (typeof va === "number" && typeof vb === "number") return va - vb;
  return String(va).localeCompare(String(vb), "en", { numeric: true });
}
function getSortedData() {
  const d = getFilteredData(), sort = st().sort;
  if (!sort.length) return d;
  return d.sort((a, b) => {
    for (const { field, dir } of sort) {
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
  DIAG.etapas = {};
  medir("kpis", renderKPIs);
  CHARTS.filter(c => c.vista === vista).forEach(c => medir(c.id, () => c.update()));
  medir("tabla", renderTable);
  renderChips(); updateFilterBadge(); renderNotaFechas(); renderTabCounts(); syncURL();
  DIAG.etapas.total = Math.round(performance.now() - t0);
}
function setCrossfilter(field, value, multi) {
  const s = st(), cf = s.crossfilter;
  if (cf && cf.field === field) {
    const tiene = cf.values.includes(value);
    if (multi) cf.values = tiene ? cf.values.filter(v => v !== value) : cf.values.concat(value);
    else cf.values = (tiene && cf.values.length === 1) ? [] : [value];   // segundo click deselecciona
    if (!cf.values.length) s.crossfilter = null;
  } else {
    s.crossfilter = { field, values: [value] };
  }
  s.page = 1;
  applyFilters();
}
function limpiarTodo() {
  const s = st();
  s.panel = {}; s.desde = ""; s.hasta = ""; s.q = ""; s.crossfilter = null; s.page = 1;
  $("fDesde").value = ""; $("fHasta").value = ""; $("tblBuscar").value = "";
  construirFiltros(); applyFilters();
}

/* ============================================================
   PESTANAS — el manejador se engancha al ROL (data-tab), no al contenedor
   ============================================================ */
function mostrarVista() {
  if (!CONFIG.vistas[vista]) {                 // red: nunca dejar todos los paneles ocultos
    console.error(`vista "${vista}" no existe; se regresa a ordenes`);
    vista = "ordenes";
  }
  document.querySelectorAll("#tabs button[data-tab]").forEach(b => b.classList.toggle("is-active", b.dataset.tab === vista));
  document.querySelectorAll(".tab-pane[data-pane]").forEach(p => { p.hidden = p.dataset.pane !== vista; });
  const s = st();
  $("fDesde").value = s.desde; $("fHasta").value = s.hasta; $("tblBuscar").value = s.q;
  $("tblBuscar").placeholder = t("buscar_" + vista);
  $("detailTitle").textContent = t("detail_" + vista);
  $("fechasLabel").textContent = t(CONFIG.vistas[vista].fechaLabel);
  initFechas();
  construirFiltros();
}
document.querySelectorAll("#tabs button[data-tab]").forEach(b => b.addEventListener("click", () => {
  if (b.dataset.tab === vista) return;
  vista = b.dataset.tab;
  mostrarVista(); applyFilters();
  setTimeout(() => CHARTS.filter(c => c.vista === vista && c.chart).forEach(c => c.chart.resize()), 0);
}));
function renderTabCounts() {
  Object.keys(CONFIG.vistas).forEach(v => {
    const el = $("nTab_" + v); if (!el) return;
    el.textContent = cargaFallo ? "" : DATA[v].length.toLocaleString("en-US");
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
  const s = st();
  let n = Object.values(s.panel).filter(v => v && v.length).length;
  if (s.desde || s.hasta) n++;
  if (s.q) n++;
  return n + (s.crossfilter ? 1 : 0);
}
function updateFilterBadge() {
  const n = countActiveFilters(), b = $("filterBadge");
  b.textContent = n; b.hidden = n === 0;
}
function etiquetaCampoValor(f, v) {
  if (f === "kpi") { const k = kpisDe(vista).find(x => x.id === v); return k ? k.label() : v; }
  return etiquetaValor(f, v);
}
function renderChips() {
  const box = $("chips"); box.textContent = "";
  const s = st();
  const add = (label, onX) => {
    const c = document.createElement("span"); c.className = "chip";
    c.textContent = label + " ";                     // valores de datos/URL: siempre textContent
    const x = document.createElement("span"); x.className = "chip__x"; x.textContent = "✕";
    x.addEventListener("click", onX); c.appendChild(x); box.appendChild(c);
  };
  Object.entries(s.panel).forEach(([f, vals]) => {
    if (!vals || !vals.length) return;
    if (vals.length > 3) {
      add(`${t("f_" + f)}: ${vals.length} ${t("seleccionados")}`, () => {
        delete s.panel[f]; s.page = 1; construirFiltros(); applyFilters(); });
      return;
    }
    vals.forEach(v => add(`${t("f_" + f)}: ${etiquetaCampoValor(f, v)}`, () => {
      s.panel[f] = s.panel[f].filter(x => x !== v);
      if (!s.panel[f].length) delete s.panel[f];
      s.page = 1; construirFiltros(); applyFilters();
    }));
  });
  if (s.desde || s.hasta) {
    add(`${t(CONFIG.vistas[vista].fechaLabel)}: ${fmtFecha(s.desde)} → ${fmtFecha(s.hasta)}`, () => {
      s.desde = ""; s.hasta = ""; $("fDesde").value = ""; $("fHasta").value = "";
      s.page = 1; applyFilters();
    });
  }
  if (s.q) add(`${t("f_q")}: ${s.q}`, () => { s.q = ""; $("tblBuscar").value = ""; s.page = 1; applyFilters(); });
  const cf = s.crossfilter;
  if (cf) {
    const vals = cf.values.length > 3 ? `${cf.values.length} ${t("seleccionados")}`
      : cf.values.map(v => etiquetaCampoValor(cf.field, v)).join(", ");
    add(`${t("f_" + cf.field)}: ${vals}`, () => { s.crossfilter = null; s.page = 1; applyFilters(); });
  }
}
function camposFiltro(v) { const c = CONFIG.vistas[v]; return c.alcance.concat(c.resto); }
function syncURL() {
  const p = new URLSearchParams(), s = st();
  if (vista !== "ordenes") p.set("tab", vista);
  Object.entries(s.panel).forEach(([f, v]) => v && v.length && p.set(f, v.join("|")));
  if (s.desde) p.set("desde", s.desde);
  if (s.hasta) p.set("hasta", s.hasta);
  if (s.q) p.set("q", s.q);
  history.replaceState(null, "", p.toString() ? "?" + p : location.pathname);
}
/* Lista blanca de NOMBRES y de VALORES: un valor solo entra si existe en el catalogo del campo. */
function readURL() {
  const q = new URLSearchParams(location.search);
  if (CONFIG.vistas[q.get("tab")]) vista = q.get("tab");
  const s = st(), campos = new Set(camposFiltro(vista));
  q.forEach((v, k) => {
    if ((k === "desde" || k === "hasta") && ISO.test(v)) s[k] = v;
    else if (k === "q") s.q = v.slice(0, 60);
    else if (campos.has(k)) {
      const validos = new Set(opcionesDe(k).map(o => String(o.v)));
      const vals = v.split("|").filter(x => validos.has(x));
      if (vals.length) s.panel[k] = vals;
    }
  });
}

const FILTRO_SELECT_ALL = 5;
const FILTRO_PLEGABLE = 12;
const panelUI = { tocado: {}, busca: {} };

function etiquetaValor(campo, valor) {
  if (valorCrudo(valor) === "") return t("sinValor");
  if (CATALOGO[campo]) return nombreCat(campo, valor);
  if (campo === "mes") return fmtMes(valor);
  return String(valor).replace(/\s+/g, " ").trim() || String(valor);
}
function opcionesDe(campo) {
  const cuenta = new Map();
  rows().forEach(r => {
    const vals = ARRAYS.has(campo) ? (r[campo] || []) : [valorCrudo(r[campo])];
    vals.forEach(v => cuenta.set(v, (cuenta.get(v) || 0) + 1));
  });
  const cat = catalogo(campo);
  if (cat.length) {   // catalogos: SU orden, el del proceso; sin las opciones que no aparecen
    return cat.filter(c => cuenta.has(c.valor)).map(c => ({ v: c.valor, txt: etiquetaValor(campo, c.valor), n: cuenta.get(c.valor) }));
  }
  const ops = [...cuenta.keys()].map(v => ({ v, txt: etiquetaValor(campo, v), n: cuenta.get(v) }));
  if (campo === "mes") return ops.sort((a, b) => String(a.v).localeCompare(String(b.v)));
  return ops.sort((a, b) => a.v === "" ? 1 : b.v === "" ? -1 : a.txt.localeCompare(b.txt, lang, { numeric: true }));
}
function construirFiltros() {
  const cfg = CONFIG.vistas[vista];
  [["grupoAlcance", cfg.alcance], ["grupoResto", cfg.resto]].forEach(([id, campos]) => {
    const box = $(id); box.textContent = "";
    campos.forEach(c => { const g = document.createElement("div"); g.className = "filter-group"; g.dataset.field = c; box.appendChild(g); });
  });
  const s = st();
  document.querySelectorAll(".filter-group[data-field]").forEach(g => {
    const campo = g.dataset.field;
    const ops = opcionesDe(campo);
    const sel = s.panel[campo] || [];
    const plegable = ops.length > FILTRO_PLEGABLE;
    const buscable = ops.length > FILTRO_SELECT_ALL;
    const llave = vista + ":" + campo;
    const abierto = panelUI.tocado[llave] === undefined ? (!plegable || sel.length > 0) : panelUI.tocado[llave];
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
      panelUI.tocado[llave] = !g.classList.contains("filter-group--abierto");
      g.classList.toggle("filter-group--abierto", panelUI.tocado[llave]);
    });
    g.appendChild(cab);

    if (buscable) {
      const b = document.createElement("input"); b.type = "search"; b.className = "filter-buscar";
      b.placeholder = `${t("search").replace("…", "")} ${t("f_" + campo).toLowerCase()}…`;
      b.value = panelUI.busca[llave] || "";
      b.addEventListener("input", () => {
        panelUI.busca[llave] = b.value;
        if (b.value) { panelUI.tocado[llave] = true; g.classList.add("filter-group--abierto"); }
        pintar();
      });
      g.appendChild(b);
    }
    const cuerpo = document.createElement("div"); cuerpo.className = "filter-group__cuerpo"; g.appendChild(cuerpo);
    const caja = document.createElement("div"); caja.className = "filter-opts"; cuerpo.appendChild(caja);
    const pie = document.createElement("div"); cuerpo.appendChild(pie);

    function marcar(valores, prender) {
      const ahora = new Set(s.panel[campo] || []);
      valores.forEach(v => prender ? ahora.add(v) : ahora.delete(v));
      if (ahora.size) s.panel[campo] = [...ahora]; else delete s.panel[campo];
      s.page = 1; construirFiltros(); applyFilters();
    }
    function pintar() {
      const q = (panelUI.busca[llave] || "").trim().toLowerCase();
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
        const sp = document.createElement("span"); sp.textContent = o.txt;
        const n = document.createElement("span"); n.className = "filter-opt__n"; n.textContent = o.n.toLocaleString("en-US");
        l.append(i, sp, n); caja.appendChild(l);
      });
      const ocultas = sel.filter(v => !lista.some(o => o.v === v)).length;
      pie.textContent = "";
      if (ocultas) { const d = document.createElement("div"); d.className = "filter-vacio";
        d.textContent = `${ocultas} ${t(ocultas === 1 ? "seleccionadaOculta" : "seleccionadasOcultas")}`; pie.appendChild(d); }
    }
    pintar();
  });
}

/* Rango de fechas: acotado a lo que existe en los datos de la pestana */
function initFechas() {
  const campo = CONFIG.vistas[vista].fecha;
  const fechas = rows().map(r => String(r[campo] || "").slice(0, 10)).filter(f => ISO.test(f)).sort();
  ["fDesde", "fHasta"].forEach(id => {
    $(id).min = fechas.length ? fechas[0] : ""; $(id).max = fechas.length ? fechas[fechas.length - 1] : "";
  });
}
["fDesde", "fHasta"].forEach(id => $(id).addEventListener("change", () => {
  const v = $(id).value, s = st();
  s[id === "fDesde" ? "desde" : "hasta"] = ISO.test(v) ? v : "";
  s.page = 1; applyFilters();
}));
function renderNotaFechas() {
  const nota = $("fechasNota"), s = st();
  if (!s.desde && !s.hasta) { nota.textContent = ""; return; }
  const campo = CONFIG.vistas[vista].fecha;
  const d = s.desde, h = s.hasta;
  s.desde = ""; s.hasta = "";
  const sinFecha = getFilteredData().filter(r => !r[campo]).length;
  s.desde = d; s.hasta = h;
  nota.textContent = sinFecha ? `${sinFecha.toLocaleString("en-US")} ${t("fueraRango")}` : "";
}

let tBuscar;
$("tblBuscar").addEventListener("input", e => {
  clearTimeout(tBuscar);
  tBuscar = setTimeout(() => { const s = st(); s.q = e.target.value.trim().slice(0, 60); s.page = 1; applyFilters(); }, 200);
});

function renderToolbarInfo() {
  const escribir = (el, partes) => {
    el.textContent = "";
    partes.forEach(([k, v], i) => {
      if (i) el.appendChild(document.createTextNode(" · "));
      el.appendChild(document.createTextNode(k + ": "));
      const b = document.createElement("b"); b.textContent = v; el.appendChild(b);
    });
  };
  const c = META.counts || {};
  escribir($("infoOrdenes"), META.corte_wc ? [
    [t("info_ordenes"), fmtFecha(META.corte_wc)],
    [t("envios"), (c.envios || 0).toLocaleString("en-US")],
    [t("ordenesPO"), (c.ordenes || 0).toLocaleString("en-US")]] : []);
  const desde = DATA.ordenes.map(o => o.recibido).filter(Boolean).sort()[0];
  escribir($("infoSap"), META.corte_wc ? [
    [t("info_sap"), (c.zwccust || 0).toLocaleString("en-US")],
    [t("info_sapDesde"), fmtFecha(desde)]] : []);
}

/* ============================================================
   KPIs
   ============================================================ */
function renderKPIs() {
  const row = $("kpi_" + vista); row.textContent = "";
  const data = getFilteredData("kpi");
  const cf = st().crossfilter;
  kpisDe(vista).forEach(k => {
    const campoCf = k.campo || "kpi";
    // Sin datos se pinta "–", nunca 0: un cero dice "no hay errores", que no es lo que paso.
    const n = (cargaFallo || (degradado && k.campo)) ? null
      : (k.campo && cf && cf.field === k.campo ? getFilteredData(k.campo) : data).filter(k.pred).length;
    const base = k.campo && cf && cf.field === k.campo ? getFilteredData(k.campo).length : data.length;
    const card = document.createElement("div");
    card.className = `card kpi kpi--${k.rol}`;
    if (cf && cf.field === campoCf && cf.values.includes(k.id)) card.classList.add("is-active");
    const v = document.createElement("div"); v.className = "kpi__value"; v.textContent = n === null ? "–" : n.toLocaleString("en-US");
    const l = document.createElement("div"); l.className = "kpi__label"; l.textContent = k.label();
    const s = document.createElement("div"); s.className = "kpi__sub";
    s.textContent = (n !== null && base) ? `${(n / base * 100).toFixed(1)}% ${t("k_ofTotal")}` : "–";
    card.append(v, l, s);
    card.addEventListener("click", e => setCrossfilter(campoCf, k.id, e.ctrlKey || e.metaKey));
    row.appendChild(card);
  });
  // El i del bloque de tarjetas va en la primera tarjeta
  const primera = row.firstElementChild;
  if (primera) { const h = document.createElement("div"); h.className = "card__header"; h.style.margin = "0"; primera.prepend(h); attachInfo(primera, "kpi_" + vista); }
}

/* ============================================================
   GRAFICAS (Chart.js local). Cada una expone update().
   calcular() devuelve claves + etiquetas + una o varias series (apiladas).
   ============================================================ */
Chart.register(ChartDataLabels);
Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
Chart.defaults.font.size = 11;
Chart.defaults.animation.duration = 240;
Chart.defaults.plugins.legend.display = false;

function crearChart(id, vistaId, field, cfg) {
  const canvas = $(id);
  const box = canvas.parentElement;
  const vacio = box.querySelector(".empty-state");
  const obj = { id, vista: vistaId, field, chart: null, claves: [] };
  obj.update = () => {
    const data = getFilteredData(field);
    const r = cfg.calcular(data);
    obj.claves = r.claves;
    const cf = st().crossfilter;
    const sel = cf && cf.field === field ? cf.values : null;
    const series = r.series || [{ label: "", valores: r.valores, colores: r.colores }];
    const apilada = series.length > 1;
    const datasets = series.map(s => ({
      label: s.label, data: s.valores, borderRadius: 3, maxBarThickness: 46, stack: "s",
      backgroundColor: r.claves.map((k, i) => { const c = s.colores ? s.colores[i] : s.color; return (sel && !sel.includes(k)) ? conAlfa(c, 0.25) : c; })
    }));
    vacio.hidden = series.some(s => s.valores.some(v => v > 0));
    DIAG.visuales[id] = { puntos: r.claves.length, conValor: r.claves.filter((_, i) => series.some(s => s.valores[i] > 0)).length };
    const opciones = () => {
      const o = cfg.opciones();
      o.plugins = Object.assign({ legend: { display: apilada, position: "bottom", labels: { boxWidth: 12 } } }, o.plugins);
      if (apilada) {
        Object.values(o.scales).forEach(sc => { sc.stacked = true; });
        o.plugins.datalabels = { color: cssVar("--c-text-invert"), font: { weight: "600", size: 10 },
          formatter: v => v > 0 ? v.toLocaleString("en-US") : "", display: c => c.dataset.data[c.dataIndex] > 0 };
      }
      return o;
    };
    if (!obj.chart) {
      obj.chart = new Chart(canvas, {
        type: "bar",
        data: { labels: r.etiquetas, datasets },
        options: Object.assign({
          responsive: true, maintainAspectRatio: false,
          onClick: (e, els) => {
            if (!els.length) return;
            setCrossfilter(field, obj.claves[els[0].index], e.native && (e.native.ctrlKey || e.native.metaKey));
          },
          onHover: (e, els) => { e.native.target.style.cursor = els.length ? "pointer" : "default"; }
        }, opciones())
      });
      canvas.addEventListener("dblclick", e => {
        const els = obj.chart.getElementsAtEventForMode(e, "nearest", { intersect: true }, false);
        const s = st();
        if (!els.length && s.crossfilter) { s.crossfilter = null; s.page = 1; applyFilters(); }
      });
    } else {
      obj.chart.data.labels = r.etiquetas;
      obj.chart.data.datasets = datasets;
      Object.assign(obj.chart.options, opciones());
      obj.chart.update();
    }
  };
  return obj;
}
const ejeCfg = () => ({ grid: { color: conAlfa(cssVar("--c-border"), 0.6) }, ticks: { color: cssVar("--c-text-muted"), callback: function (v) { return abbr(v); } } });
const ejeCat = () => ({ grid: { display: false }, ticks: { color: cssVar("--c-text"), autoSkip: false } });
const labelsCfg = (fmt, align) => ({
  anchor: "end", align: align || "end", clamp: false, offset: 2, color: cssVar("--c-text"),
  font: { weight: "600", size: 11 }, formatter: (v) => v > 0 ? fmt(v) : ""
});
const enteros = v => v.toLocaleString("en-US");
const corto = (s, n) => { s = String(s || ""); return s.length > n ? s.slice(0, n - 1) + "…" : s; };
const cuentaPor = (data, campo) => { const c = {}; data.forEach(r => { const k = valorCrudo(r[campo]); c[k] = (c[k] || 0) + 1; }); return c; };
/* Top N por cuenta, sobre el conjunto que entra: estable mientras no cambie el filtro */
function topClaves(data, campo, n) {
  const c = cuentaPor(data, campo);
  return Object.keys(c).sort((a, b) => c[b] - c[a] || a.localeCompare(b)).slice(0, n);
}
/* Series apiladas por un catalogo (categoria, tipo) */
function seriesPor(data, campo, claves, catCampo, excluir) {
  return catalogo(catCampo).filter(c => !(excluir || []).includes(c.valor)).map((c, i) => {
    const valores = claves.map(k => data.filter(r => valorCrudo(r[campo]) === k && r[catCampo] === c.valor).length);
    return { label: c[lang] || c.valor, valores, color: colorRol(c.rol, i) };
  }).filter(s => s.valores.some(v => v > 0));
}
const tooltipEnteros = unidad => ({ callbacks: { label: c => ` ${c.dataset.label ? c.dataset.label + ": " : ""}${enteros(c.raw)} ${t(unidad)}` } });

const CHARTS = [
  crearChart("chCategoria", "ordenes", "categoria", {
    calcular: data => {
      const cuenta = cuentaPor(data, "categoria");
      const cat = catalogo("categoria");
      const claves = cat.length ? cat.map(c => c.valor) : Object.keys(cuenta).sort();
      return { claves, etiquetas: claves.map(k => nombreCat("categoria", k)), valores: claves.map(k => cuenta[k] || 0),
               colores: claves.map((k, i) => colorRol(rolCat("categoria", k), i)) };
    },
    opciones: () => ({ indexAxis: "y", layout: { padding: { right: 40 } },
      scales: { x: Object.assign(ejeCfg(), { beginAtZero: true }), y: ejeCat() },
      plugins: { datalabels: labelsCfg(enteros), tooltip: tooltipEnteros("ordenes") } })
  }),
  crearChart("chHallazgos", "ordenes", "hallazgos", {
    calcular: data => {
      const cuenta = {};
      data.forEach(r => (r.hallazgos || []).forEach(h => { cuenta[h] = (cuenta[h] || 0) + 1; }));
      const enDatos = new Set(DATA.ordenes.flatMap(r => r.hallazgos || []));   // claves estables: las que existen
      const cat = catalogo("hallazgos");
      const claves = cat.length ? cat.map(c => c.valor).filter(k => enDatos.has(k)) : [...enDatos].sort();
      return { claves, etiquetas: claves.map(k => nombreCat("hallazgos", k)), valores: claves.map(k => cuenta[k] || 0),
               colores: claves.map((k, i) => colorRol(rolCat("hallazgos", k), i)) };
    },
    opciones: () => ({ indexAxis: "y", layout: { padding: { right: 40 } },
      scales: { x: Object.assign(ejeCfg(), { beginAtZero: true }), y: Object.assign(ejeCat(), { ticks: { color: cssVar("--c-text"), autoSkip: false, font: { size: 10 } } }) },
      plugins: { datalabels: labelsCfg(enteros), tooltip: tooltipEnteros("ordenes") } })
  }),
  crearChart("chMes", "ordenes", "mes", {
    calcular: data => {
      const claves = [...new Set(DATA.ordenes.map(r => r.mes).filter(Boolean))].sort();
      const series = seriesPor(data, "mes", claves, "categoria");
      return { claves, etiquetas: claves.map(fmtMes),
               series: series.length ? series : [{ label: "", valores: claves.map(k => data.filter(r => r.mes === k).length), color: cssVar("--c-cat-1") }] };
    },
    opciones: () => ({ scales: { y: Object.assign(ejeCfg(), { beginAtZero: true }), x: Object.assign(ejeCat(), { ticks: { color: cssVar("--c-text"), maxRotation: 0 } }) },
      plugins: { tooltip: tooltipEnteros("ordenes") } })
  }),
  crearChart("chCliente", "ordenes", "sold_nombre", {
    calcular: data => {
      const problema = data.filter(r => r.categoria !== "PROCESADA");
      const claves = topClaves(problema, "sold_nombre", CONFIG.topN);
      const series = seriesPor(problema, "sold_nombre", claves, "categoria", ["PROCESADA"]);
      return { claves, etiquetas: claves.map(k => corto(etiquetaValor("sold_nombre", k), 28)),
               series: series.length ? series : [{ label: "", valores: claves.map(() => 0), color: cssVar("--c-cat-1") }] };
    },
    opciones: () => ({ indexAxis: "y",
      scales: { x: Object.assign(ejeCfg(), { beginAtZero: true }), y: Object.assign(ejeCat(), { ticks: { color: cssVar("--c-text"), autoSkip: false, font: { size: 10 } } }) },
      plugins: { tooltip: Object.assign(tooltipEnteros("ordenes"), { callbacks: Object.assign({}, tooltipEnteros("ordenes").callbacks,
        { title: c => etiquetaValor("sold_nombre", CHARTS[3].claves[c[0].dataIndex]) }) }) } })
  }),
  crearChart("chSapCliente", "sap", "sold_nombre", {
    calcular: data => {
      const claves = topClaves(data, "sold_nombre", CONFIG.topN);
      const series = seriesPor(data, "sold_nombre", claves, "tipo");
      return { claves, etiquetas: claves.map(k => corto(etiquetaValor("sold_nombre", k), 28)),
               series: series.length ? series : [{ label: "", valores: claves.map(k => data.filter(r => r.sold_nombre === k).length), color: cssVar("--c-cat-1") }] };
    },
    opciones: () => ({ indexAxis: "y",
      scales: { x: Object.assign(ejeCfg(), { beginAtZero: true }), y: Object.assign(ejeCat(), { ticks: { color: cssVar("--c-text"), autoSkip: false, font: { size: 10 } } }) },
      plugins: { tooltip: tooltipEnteros("so") } })
  }),
  crearChart("chSapPor", "sap", "creado_por", {
    calcular: data => {
      const claves = topClaves(data, "creado_por", CONFIG.topN);
      const series = seriesPor(data, "creado_por", claves, "tipo");
      return { claves, etiquetas: claves.map(k => etiquetaValor("creado_por", k)),
               series: series.length ? series : [{ label: "", valores: claves.map(k => data.filter(r => r.creado_por === k).length), color: cssVar("--c-cat-1") }] };
    },
    opciones: () => ({ indexAxis: "y",
      scales: { x: Object.assign(ejeCfg(), { beginAtZero: true }), y: Object.assign(ejeCat(), { ticks: { color: cssVar("--c-text"), autoSkip: false, font: { family: cssVar("--font-mono"), size: 10 } } }) },
      plugins: { tooltip: tooltipEnteros("so") } })
  }),
  crearChart("chArchivos", "archivos", "archivo", {
    calcular: data => {
      const orden = data.slice().sort((a, b) => String(a.corte).localeCompare(String(b.corte)));
      const color = r => {
        const m = r.marcas || [];
        if (m.includes("CONSOLIDADO")) return colorRol("critical");
        if (m.includes("GRANDE")) return colorRol("warn");
        if (m.includes("IDENTICO")) return colorRol("neutral");
        if (m.includes("FORMATO_ANTERIOR")) return cssVar("--c-cat-3");
        return cssVar("--c-cat-1");
      };
      CH_ARCH = orden;
      return { claves: orden.map(r => r.archivo), etiquetas: orden.map(r => fmtFecha(r.corte)),
               valores: orden.map(r => r.filas), colores: orden.map(color) };
    },
    opciones: () => {
      const max = Math.max(0, ...CH_ARCH.map(r => r.filas));
      return { layout: { padding: { top: 18 } },
        scales: { y: Object.assign(ejeCfg(), { beginAtZero: true }),
                  x: { grid: { display: false }, ticks: { color: cssVar("--c-text-muted"), maxRotation: 0, autoSkip: true, autoSkipPadding: 14, font: { size: 10 } } } },
        plugins: {
          // Labels solo donde importan: el maximo y los marcados como distintos (los 100 juntos se encimarian)
          datalabels: Object.assign(labelsCfg(enteros), { display: c => { const r = CH_ARCH[c.dataIndex]; return !!r && (r.filas === max || (r.marcas || []).some(m => m === "CONSOLIDADO" || m === "GRANDE")); } }),
          tooltip: { callbacks: {
            title: c => CH_ARCH[c[0].dataIndex] ? CH_ARCH[c[0].dataIndex].archivo : "",
            label: c => { const r = CH_ARCH[c.dataIndex]; return [` ${enteros(c.raw)} ${t("renglones")} · ${r.formato}`, ...(r.marcas || []).map(m => ` · ${nombreCat("marcas", m)}`)]; } } } } };
    }
  })
];
let CH_ARCH = [];
function redibujarCharts() { setTimeout(() => CHARTS.forEach(c => c.chart && c.chart.resize()), 260); }

/* ============================================================
   TABLA DE DETALLE — una por pestana, mismas reglas
   ============================================================ */
const COLUMNAS = {
  ordenes: [
    { field: "po", type: "text", pn: true }, { field: "categoria", type: "cat" }, { field: "hallazgos", type: "pills" },
    { field: "dias", type: "int" }, { field: "recibido", type: "date" }, { field: "sold_id", type: "text" },
    { field: "sold_nombre", type: "desc" }, { field: "om", type: "text" }, { field: "wc_status", type: "text" },
    { field: "review_status", type: "text" }, { field: "sap_status", type: "text" }, { field: "nota", type: "desc" },
    { field: "so", type: "text", pn: true }, { field: "so_manual", type: "text", pn: true }, { field: "so_po", type: "text" },
    { field: "so_entrega", type: "date" }, { field: "so_bloqueos", type: "text" }, { field: "om_zwccust", type: "text" },
    { field: "intentos", type: "int" }, { field: "ultimo_archivo", type: "date" }
  ],
  sap: [
    { field: "so", type: "text", pn: true }, { field: "tipo", type: "cat" }, { field: "po", type: "text", pn: true }, { field: "potyp", type: "text" },
    { field: "sold_id", type: "text" }, { field: "sold_nombre", type: "desc" }, { field: "creado", type: "date" },
    { field: "creado_por", type: "text" }, { field: "om_zwccust", type: "text" }, { field: "entrega", type: "date" },
    { field: "lineas", type: "int", total: true }, { field: "cantidad", type: "num", total: true, barra: true },
    { field: "bloqueos", type: "text" }, { field: "en_sdd167", type: "bool" }
  ],
  archivos: [
    { field: "archivo", type: "text" }, { field: "corte", type: "date" }, { field: "marcas", type: "pills" },
    { field: "formato", type: "text" }, { field: "filas", type: "int", total: true, barra: true },
    { field: "nuevos", type: "int", total: true }, { field: "dias_recibido", type: "int" },
    { field: "recibido_min", type: "date" }, { field: "recibido_max", type: "date" },
    { field: "identico_a", type: "text" }, { field: "bytes", type: "int", total: true }
  ]
};
const PILL_CAMPO = { hallazgos: "hallazgos", marcas: "marcas" };
const etiquetaCol = c => t("c_" + c.field);
function celda(r, c) {
  const v = r[c.field];
  switch (c.type) {
    case "num": return fmtNum(v, Number.isInteger(+v) ? 0 : 1);
    case "int": return fmtNum(v);
    case "date": return fmtFecha(v);
    case "cat": return valorCrudo(v) === "" ? "–" : nombreCat(c.field, v);
    case "bool": return v === true ? t("si") : v === false ? t("no") : "–";
    case "pills": return (v || []).map(x => nombreCat(PILL_CAMPO[c.field], x)).join(", ") || "–";
    default: return v === null || v === undefined || v === "" ? "–" : String(v);
  }
}
function pill(rol, txt) { const p = document.createElement("span"); p.className = `pill pill--${rol || "neutral"}`; p.textContent = txt; return p; }
function renderTable() {
  const cols = COLUMNAS[vista], s = st();
  const data = getSortedData();
  const pages = Math.max(1, Math.ceil(data.length / pageSize));
  s.page = Math.min(s.page, pages);
  const slice = data.slice((s.page - 1) * pageSize, s.page * pageSize);
  const barras = {};
  cols.filter(c => c.barra).forEach(c => { barras[c.field] = Math.max(1, ...data.map(r => +r[c.field] || 0)); });

  const head = $("detailHead"); head.textContent = "";
  cols.forEach(c => {
    const th = document.createElement("th");
    const so = s.sort.find(x => x.field === c.field);
    th.textContent = etiquetaCol(c);
    const ind = document.createElement("span"); ind.className = "sort-ind";
    ind.textContent = so ? (so.dir === "asc" ? "▲" : "▼") : "▲"; th.appendChild(ind);
    if (so) th.classList.add("is-sorted");
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
    if (vista === "ordenes") tr.addEventListener("click", () => abrirModal(r));
    cols.forEach(c => {
      const td = document.createElement("td");
      if (["num", "int"].includes(c.type)) td.className = "num";
      if (c.type === "date") td.className = "date";
      if (c.type === "desc") { td.className = "desc"; td.title = r[c.field] || ""; }
      if (["num", "int"].includes(c.type) && r[c.field] < 0) td.classList.add("neg");
      if (c.type === "cat" && valorCrudo(r[c.field]) !== "") td.appendChild(pill(rolCat(c.field, r[c.field]), celda(r, c)));
      else if (c.type === "pills") {
        const box = document.createElement("span"); box.className = "pills";
        (r[c.field] || []).forEach(x => box.appendChild(pill(rolCat(PILL_CAMPO[c.field], x), nombreCat(PILL_CAMPO[c.field], x))));
        if (!(r[c.field] || []).length) box.textContent = "–";
        td.appendChild(box);
      } else if (c.barra) {
        const w = document.createElement("span"); w.className = "bar-cell";
        const b = document.createElement("span"); b.className = "bar-cell__bar";
        b.style.width = `${Math.round((+r[c.field] || 0) / barras[c.field] * 60)}px`;
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
      if (c.total) { td.className = "num"; td.textContent = fmtNum(data.reduce((a, r) => a + (+r[c.field] || 0), 0)); }
      tr.appendChild(td);
    });
    foot.appendChild(tr);
  }
  renderPager(data.length, pages);
  $("rowCount").textContent = `${data.length.toLocaleString("en-US")} ${t("rows")}`;
  DIAG.visuales.tabla = { filas: slice.length, total: data.length };
}
function toggleSort(field, shift) {
  const sort = st().sort;
  const i = sort.findIndex(x => x.field === field);
  if (!shift) { const keep = i >= 0 ? sort[i] : null; sort.length = 0; if (keep) sort.push(keep); }
  const j = sort.findIndex(x => x.field === field);
  if (j < 0) sort.push({ field, dir: "asc" });
  else if (sort[j].dir === "asc") sort[j].dir = "desc";
  else sort.splice(j, 1);
}
function renderPager(total, pages) {
  const s = st();
  const from = total ? (s.page - 1) * pageSize + 1 : 0;
  const to = Math.min(s.page * pageSize, total);
  $("pagerRange").textContent = `${t("showing")} ${from.toLocaleString("en-US")}–${to.toLocaleString("en-US")} ${t("of")} ${total.toLocaleString("en-US")}`;
  const box = $("pagerPages"); box.textContent = "";
  const btn = (label, page, disabled, active) => {
    const b = document.createElement("button"); b.textContent = label; b.disabled = !!disabled;
    if (active) b.classList.add("is-active");
    b.addEventListener("click", () => { s.page = page; renderTable(); });
    box.appendChild(b);
  };
  btn("‹", s.page - 1, s.page === 1);
  const win = [];
  for (let p = 1; p <= pages; p++) if (p === 1 || p === pages || Math.abs(p - s.page) <= 1) win.push(p);
  win.forEach((p, i) => {
    if (i && p - win[i - 1] > 1) { const sp = document.createElement("span"); sp.textContent = "…"; box.appendChild(sp); }
    btn(p, p, false, p === s.page);
  });
  btn("›", s.page + 1, s.page === pages);
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
  const s = st();
  const primera = (s.page - 1) * pageSize;   // conserva la primera fila visible
  pageSize = v; s.page = Math.floor(primera / pageSize) + 1;
  guardarLS("wc_page_size", v); renderTable();
});
initPageSize();

/* ============================================================
   EXPORTACION — columnas de la tabla (y las de apoyo) sobre el conjunto
   filtrado y ordenado. Cada valor pasa por un formateador que cubre
   todos los tipos: nada de arrays ni objetos en una celda.
   ============================================================ */
const EXTRA_EXPORT = {
  ordenes: [{ field: "nota_txt", type: "text" }, { field: "fecha_orden", type: "date" }, { field: "ship_id", type: "text" },
            { field: "ship_nombre", type: "text" }, { field: "sap_enviado", type: "text" }, { field: "revision_hecha", type: "text" },
            { field: "asunto", type: "text" }],
  sap: [], archivos: [{ field: "columnas", type: "int" }]
};
function valorExport(c, v) {
  if (v === null || v === undefined || v === "") return "";
  switch (c.type) {
    case "date": return String(v).slice(0, 10);
    case "cat": return nombreCat(c.field, v);
    case "pills": return (v || []).map(x => nombreCat(PILL_CAMPO[c.field], x)).join("; ");
    case "bool": return v === true ? t("si") : v === false ? t("no") : "";
    case "num": case "int": return typeof v === "number" ? v : (Number.isNaN(+v) ? String(v) : +v);
    default: return Array.isArray(v) ? v.join("; ") : String(v);
  }
}
function exportRows() {
  const cols = COLUMNAS[vista].filter(c => c.field !== "nota").concat(EXTRA_EXPORT[vista]);
  return getSortedData().map(r => {
    const o = {};
    cols.forEach(c => { o[etiquetaCol(c)] = valorExport(c, r[c.field]); });
    return o;
  });
}
function nombreArchivo(ext) {
  const d = new Date(), p = n => String(n).padStart(2, "0");
  const stamp = `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}`;
  return `${CONFIG.dashboardName}_${CONFIG.vistas[vista].archivo}_${stamp}.${ext}`;
}
$("btnCsv").addEventListener("click", () => {
  const filas = exportRows(); if (!filas.length) return;
  const headers = Object.keys(filas[0]);
  const csv = [headers.map(csvCelda).join(","), ...filas.map(r => headers.map(h => csvCelda(r[h])).join(","))].join("\r\n");
  descargar(new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" }), nombreArchivo("csv"));
});
$("btnXlsx").addEventListener("click", () => {
  const filas = exportRows(); if (!filas.length) return;
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.json_to_sheet(filas);
  ws["!autofilter"] = { ref: ws["!ref"] };
  ws["!cols"] = Object.keys(filas[0]).map(h => ({ wch: Math.min(40, Math.max(h.length + 2, ...filas.slice(0, 200).map(r => String(r[h]).length + 2))) }));
  XLSX.utils.book_append_sheet(wb, ws, t("tab_" + vista).slice(0, 31));
  const fuentes = META.fuentes || [];
  const meta = [
    ["Dashboard", CONFIG.dashboardName],
    [t("detail_" + vista), ""],
    [t("updated"), META.generated_at || ""],
    [t("info_ordenes"), META.corte_wc || ""],
    [t("rows"), filas.length],
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
   FRESCURA — "Extraido el" de la fuente mas vieja manda el semaforo.
   Un catalogo (ZWCCUST) no habla por las demas: se topa en ambar.
   ============================================================ */
function renderFreshness() {
  const fuentes = META.fuentes || [];
  const nom = f => lang === "en" ? f.nombre_en : f.nombre;
  $("metaUpdated").textContent = META.generated_at || "–";
  $("ftrUpdated").textContent = META.generated_at || "–";
  $("ftrSources").textContent = fuentes.map(nom).join(", ") || "–";
  const el = $("metaFreshness");
  const conFecha = fuentes.filter(f => f.extraido_el && ISO.test(f.extraido_el));
  const trans = conFecha.filter(f => !f.catalogo);
  const base = trans.length ? trans : conFecha;
  if (!base.length) { el.className = "freshness freshness--critical"; el.textContent = `⚠ ${t("extracted")}: –`; return; }
  const vieja = base.reduce((a, b) => a.extraido_el < b.extraido_el ? a : b);
  const dias = diasEntre(vieja.extraido_el, hoyISO());
  let lvl = fuentes.some(f => f.falta) || dias > CONFIG.freshness.criticalDays ? "critical"
    : dias > CONFIG.freshness.warnDays ? "warn" : "ok";
  const catVieja = conFecha.filter(f => f.catalogo).some(f => diasEntre(f.extraido_el, hoyISO()) > CONFIG.freshness.warnDays);
  if (lvl === "ok" && catVieja) lvl = "warn";
  el.className = `freshness freshness--${lvl}`;
  el.textContent = `${lvl === "critical" ? "⚠ " : ""}${t("extracted")}: `;
  const b = document.createElement("b"); b.textContent = fmtFecha(vieja.extraido_el); el.appendChild(b);
  el.title = fuentes.map(f => `${nom(f)}${f.catalogo ? " (" + t("s_catalogo") + ")" : ""}: ${f.extraido_el ? fmtFecha(f.extraido_el) + " (" + diasEntre(f.extraido_el, hoyISO()) + "d)" : "–"}`).join("\n");
}

/* ============================================================
   BANDA DE AVISOS
   ============================================================ */
function renderBanner() {
  const el = $("banner");
  const avisos = [];
  const nom = f => lang === "en" ? f.nombre_en : f.nombre;
  if (cargaFallo) avisos.push(["critical", t("errorTitle"), t("errorDetail")]);
  else {
    if (META.semi) avisos.push(["warn", t("semiTitle"), t("semiDetail")]);
    else if (META.demo) avisos.push(["warn", t("demoTitle"), t("demoDetail")]);
    if (degradado) avisos.push(["critical", t("degradedTitle"), t("degradedStructure")]);
    (META.fuentes || []).filter(f => f.falta).forEach(f => avisos.push(["critical", t("faltaFuente"), nom(f)]));
    const trans = (META.fuentes || []).filter(f => !f.catalogo && f.extraido_el && ISO.test(f.extraido_el));
    const fechas = trans.map(f => f.extraido_el).sort();
    if (fechas.length > 1 && diasEntre(fechas[0], fechas[fechas.length - 1]) > CONFIG.maxDiasEntreFuentes) {
      avisos.push(["warn", t("cortesTitle"), `${trans.map(f => `${nom(f)}: ${fmtFecha(f.extraido_el)}`).join(" · ")}. ${t("cortesDetail")}`]);
    }
    if ((META.avisos || {}).sdd167_no_en_wc_followup > 0) avisos.push(["warn", t("sddTitle"), `${META.avisos.sdd167_no_en_wc_followup} SO. ${t("sddDetail")}`]);
    const cons = (META.archivos_resumen || {}).consolidados || [];
    if (cons.length) avisos.push(["warn", t("consTitle"), cons.join(", ")]);
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

/* La respuesta a "cual archivo es distinto", escrita, arriba de la pestana de reportes */
function renderRespuesta() {
  const box = $("respuestaArchivo"), a = META.archivos_resumen;
  if (!a) { box.hidden = true; return; }
  box.hidden = false;
  const viejo = Object.keys(a.formatos || {}).map(Number).filter(n => n !== a.formato_actual);
  const datos = { n: a.total, primero: fmtFecha(a.primero), ultimo: fmtFecha(a.ultimo), max: a.max_filas,
    mediana: a.mediana_filas, dias: a.consolidado_min_dias, cambio: fmtFecha(a.cambio_formato),
    colViejo: viejo.length ? viejo.join("/") : a.formato_actual, colNuevo: a.formato_actual,
    identicos: a.identicos, lista: (a.consolidados || []).join(", ") };
  const hay = (a.consolidados || []).length > 0;
  box.className = `card respuesta respuesta--${hay ? "critical" : "ok"}`;
  $("respTitulo").textContent = tpl(hay ? "resp_si" : "resp_no", datos);
  $("respDetalle").textContent = tpl(hay ? "resp_siDet" : "resp_noDet", datos);
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
function attachInfos() { CHARTS.forEach(c => attachInfo($("card_" + c.id), c.id)); }

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
  filas.forEach(f => { const r = document.createElement("tr"); f.forEach(v => { const td = document.createElement("td"); td.textContent = v === null || v === undefined || v === "" ? "–" : String(v); r.appendChild(td); }); bd.appendChild(r); });
  tb.appendChild(bd); return tb;
}
function renderDoc() {
  const d = CONFIG.documentation[lang] || {};
  const body = $("docBody"); body.textContent = "";
  $("docTitle").textContent = t("documentation");
  const p = document.createElement("p"); p.textContent = d.purpose;
  body.append(h3(t("purpose")), p, h3(t("sources")));
  body.appendChild(tablaDoc([t("s_fuente"), t("s_sistema"), t("s_ruta"), t("s_extraido"), t("s_actualizado"), t("s_filas")],
    (META.fuentes || []).map(f => [(lang === "en" ? f.nombre_en : f.nombre) + (f.catalogo ? ` (${t("s_catalogo")})` : ""),
      f.sistema, f.tabla, fmtFecha(f.extraido_el), f.actualizado, (f.filas || 0).toLocaleString("en-US")])));
  body.append(h3(t("transformations")), lista(d.transformations), h3(t("measures")), lista(d.measures),
              h3(t("rules")), lista(d.rules), h3(t("catHallazgos")));
  body.appendChild(tablaDoc([t("f_hallazgos"), t("nivel"), ""], catalogo("hallazgos").map(h => [h[lang], h.rol, h["desc_" + lang]])));
  body.append(h3(t("limitations")), lista(d.limitations), h3(t("qc")));
  const c = META.counts || {}, a = META.avisos || {};
  body.appendChild(tablaDoc(["", ""], [
    [t("qc_archivos"), c.archivos], [t("qc_envios"), c.envios], [t("qc_ordenes"), c.ordenes],
    [t("qc_fu"), `${(c.wc_followup_filas || 0).toLocaleString("en-US")} / ${(c.wc_followup_so || 0).toLocaleString("en-US")}`],
    [t("qc_sdd"), `${c.sdd167_filas} / ${c.sdd167_so}`], [t("qc_sddNoFu"), a.sdd167_no_en_wc_followup],
    [t("qc_zwc"), c.zwccust]
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
    lineas.push(`  ${c.id} [${c.vista}]: ${dv.puntos} barras, ${dv.conValor} con valor · ${getComputedStyle(box).display} ${Math.round(rc.width)}x${Math.round(rc.height)}px`);
  });
  document.querySelectorAll(".tab-pane[data-pane]").forEach(p => {
    lineas.push(`  pane ${p.dataset.pane}: ${getComputedStyle(p).display}, ${Math.round(p.getBoundingClientRect().height)}px`);
  });
  const tb = $("detailTable").getBoundingClientRect(), dt = DIAG.visuales.tabla || {};
  lineas.push(`  tabla: ${dt.filas} filas pintadas de ${dt.total} · ${Math.round(tb.width)}x${Math.round(tb.height)}px`);
  lineas.push("", `vista: ${vista} · filas: ${Object.entries(DATA).map(([k, v]) => k + " " + v.length).join(", ")} · lang: ${lang}`,
              `filtros: ${JSON.stringify(st())}`);
  const body = $("docBody"); body.textContent = "";
  $("docTitle").textContent = t("diag");
  const pre = document.createElement("div"); pre.className = "diag-box"; pre.textContent = lineas.join("\n");
  body.appendChild(pre);
  docPanel.classList.add("is-open"); docOv.hidden = false;
});

/* ============================================================
   MODAL DE LA ORDEN — hallazgos explicados y la historia de envios
   ============================================================ */
function abrirModal(r) {
  $("modalTitle").textContent = `PO ${r.po} · ${r.sold_nombre || ""}`;
  if (r.po) $("modalTitle").appendChild(pnBoton(r.po));
  const grid = $("modalGrid"); grid.textContent = "";
  [[t("c_categoria"), nombreCat("categoria", r.categoria)], [t("c_dias"), fmtNum(r.dias)],
   [t("c_wc_status"), r.wc_status || "–"], [t("c_sap_status"), r.sap_status || "–"],
   [t("c_review_status"), r.review_status || "–"], [t("c_nota"), r.nota_txt || "–"],
   [t("c_so"), r.so || r.so_manual || "–"], [t("c_so_po"), r.so_po || "–"],
   [t("c_sold_id"), r.sold_id || "–"], [t("c_ship_id"), r.ship_id || "–"],
   [t("c_om"), r.om || "–"], [t("c_om_zwccust"), r.om_zwccust || "–"]
  ].forEach(([k, v]) => {
    const d = document.createElement("div"); d.className = "modal__dato";
    const s = document.createElement("span"); s.textContent = k; const b = document.createElement("b"); b.textContent = v;
    d.append(s, b); grid.appendChild(d);
  });
  const hz = $("modalHallazgos"); hz.textContent = "";
  if ((r.hallazgos || []).length) {
    hz.appendChild(tablaDoc([t("c_hallazgos"), ""], r.hallazgos.map(h => { const c = itemCat("hallazgos", h); return [c ? c[lang] : h, c ? c["desc_" + lang] : ""]; })));
  }
  const tabla = $("modalTabla"); tabla.textContent = "";
  const filas = (INTENTOS[r.po] || []).map(x => [x[0], fmtFecha(x[1]), fmtFecha(x[2]), fmtFecha(x[3]), x[4], x[5], x[6], x[7], x[8] || "–"]);
  const tb = tablaDoc([t("m_id"), t("m_recibido"), t("m_primer"), t("m_ultimo"), t("c_wc_status"), t("c_review_status"), t("c_sap_status"), t("c_nota"), t("c_so")], filas);
  [...tb.childNodes].forEach(n => tabla.appendChild(n));
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
  document.querySelectorAll("#langToggle button").forEach(b => b.classList.toggle("is-active", b.dataset.lang === lang));
  attachInfos();
  renderFreshness(); renderBanner(); renderToolbarInfo(); renderRespuesta();
  mostrarVista();
  if (!$("loading").hidden) return;
  applyFilters();
  if (docPanel.classList.contains("is-open")) renderDoc();
}
$("langToggle").addEventListener("click", e => {
  const b = e.target.closest("button[data-lang]"); if (!b) return;
  lang = b.dataset.lang; guardarLS("dash_lang", lang); applyLang();
});
if (CONFIG.lang.enabled.length < 2) $("langToggle").hidden = true;

/* ============================================================
   CARGA — portal primero, ./data_real/ y ./data/ en local. Sin datos de
   respaldo: si no llega nada, se dice.
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
  applyLang();
  const t0 = performance.now();
  try {
    const [meta, dash] = await Promise.all([leerJSON("meta.json"), leerJSON("dashboard.json")]);
    META = meta || {};
    DATA.ordenes = dash.ordenes || [];
    DATA.sap = dash.sap_sin_wc || [];
    DATA.archivos = (dash.archivos || []).map(a => Object.assign({}, a, { mes: String(a.fecha || "").slice(0, 7), formato: `${a.columnas} col` }));
    INTENTOS = dash.intentos || {};
  } catch (e) {
    cargaFallo = true;
  }
  DIAG.etapas.carga = Math.round(performance.now() - t0);
  $("loading").hidden = true;
  initCatalogos();
  readURL();
  applyLang();
}
init();

let rt;
addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => CHARTS.forEach(c => c.chart && c.chart.resize()), 150); });
