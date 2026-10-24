// Made by: Hazzard
// Loads the latest SAP ZMM_MD04 pipe-delimited file and adds Aging, Status, Reschedule and Exception
shared ZMM_MD04 = let
    SourceFolder = "\\files.contoso-motors.example\shared\Logistics\BI Reports\ZMM_MD04",
    AgingPoVendors = {"VND01", "VND02", "VND03", "VND04", "VND05", "VND06", "VND07", "VND08", "VND09"},
    ExcludedVendors = {"9900003", "9900002", "9900004", "9900001", "9900005"},
    ExcludedMaterials = {"77233554", "77269668", "77049219", "77637835", "77437336", "77887719", "77275405", "77814976", "77228750", "77331855", "77823545", "77701214", "77108081", "77738965", "77442621", "77987351", "77709422", "77554563", "77593134", "77550324", "77182229", "77997791", "77251084", "77457208", "77502829", "77005437", "77607215", "77514340", "77539056", "77621857", "77209450", "77845590", "77057585", "77942143", "77471087", "77228448", "77497796", "77226731", "77348591", "77428953", "77005602", "77973895", "77601715", "77841771", "77044574", "77246059", "77628520", "77605306", "77606756", "77624794", "77770007", "77012737", "77099193", "77769111", "77068196", "77895272", "77254157", "77534957", "77090243"},
    SapColumns = {"Centro", "Planif. Nec", "Proveedor", "Nombre del Proveedor", "Material", "Material Description", "Material Proveedor", "Ind. ABC", "Pedido", "Posición", "Unidad Med", "Tipo Conf.", "Referencia", "Fecha Reprog", "Excepcion", "Estrategia Lib", "Fecha Entrada Necesidad", "Status Msg", "Fecha Pedido", "Fecha Entrega Pedido", "Fecha Embarque", "Fecha Planta TC", "Cantidad", "Precio Neto", "Por", "Mon", "Stock Centro Disp", "Ubicación", "Family", "ROP", "Plazo Entrega Previo", "Tiempo Tratamiento EM"},
    OutputColumns = {"Centro", "Proveedor", "Nombre del Proveedor", "Planif. Nec", "Material", "Material Description", "Material Proveedor", "Ind. ABC", "Pedido", "Posición", "Unidad Med", "Tipo Conf.", "Referencia", "Fecha Reprog", "Estrategia Lib", "Fecha Entrada Necesidad", "Status Msg", "Fecha creación OC", "Fecha entrega PO", "Fecha Embarque AB", "Fecha Embarque LA", "Cantidad", "Precio Neto", "Por", "Mon", "Stock Centro Disp", "Ubicación", "Family", "ROP", "Plazo Entrega Previo", "Tiempo Tratamiento EM", "Aging", "Status", "Reschedule Days", "Reschedule", "Excepción", "Data created"},
    DateColumns = {"Fecha creación OC", "Fecha entrega PO", "Fecha Embarque AB", "Fecha Embarque LA", "Fecha Reprog"},
    Today = Date.From(DateTime.LocalNow()),
    Source = Folder.Files(SourceFolder),
    VisibleFiles = Table.SelectRows(Source, each [Attributes]?[Hidden]? <> true),
    LatestFile = Table.FirstN(Table.Sort(VisibleFiles, {{"Date created", Order.Descending}}), 1),
    ParsedFile = Table.AddColumn(LatestFile, "Transform File", each #"Transform file"([Content])),
    KeptFileColumns = Table.SelectColumns(ParsedFile, {"Transform File", "Date created"}),
    ExpandedRows = Table.ExpandTableColumn(KeptFileColumns, "Transform File", Table.ColumnNames(#"Transform file"(#"Sample file"))),
    RemovedPipeEdges = Table.RemoveColumns(ExpandedRows, {"Column1", "Column34"}),
    SkippedFirstLine = Table.Skip(RemovedPipeEdges, 1),
    RemovedDashLines = Table.SelectRows(SkippedFirstLine, each not Text.Contains([Column2], "-------")),
    PromotedHeaders = Table.PromoteHeaders(RemovedDashLines),
    RenamedFileDate = Table.RenameColumns(PromotedHeaders, {{"Column33", "Data created"}}),
    TrimmedHeaders = Table.TransformColumnNames(RenamedFileDate, Text.Trim),
    TrimmedValues = Table.TransformColumns(TrimmedHeaders, List.Transform(SapColumns, each {_, (value) => Text.Trim(Text.From(value)), type nullable text})),
    RemovedPageHeaders = Table.SelectRows(TrimmedValues, each [Centro] <> "" and [Centro] <> "Centro"),
    TypedDates = Table.TransformColumnTypes(RemovedPageHeaders, {{"Fecha Reprog", type date}, {"Fecha Pedido", type date}, {"Fecha Entrega Pedido", type date}, {"Fecha Embarque", type date}, {"Fecha Planta TC", type date}}, "en-US"),
    TypedNumbers = Table.TransformColumnTypes(TypedDates, {{"Cantidad", type number}, {"Precio Neto", type number}, {"Por", type number}, {"Stock Centro Disp", type number}, {"ROP", type number}, {"Plazo Entrega Previo", type number}, {"Tiempo Tratamiento EM", type number}}),
    CleanedMaterial = Table.TransformColumns(TypedNumbers, {{"Material", each Text.Replace(Text.Trim(_), " ", ""), type text}}),
    RemovedExcludedMaterials = Table.SelectRows(CleanedMaterial, each not List.Contains(ExcludedMaterials, [Material])),
    RemovedExcludedVendors = Table.SelectRows(RemovedExcludedMaterials, each not List.AnyTrue(List.Transform(ExcludedVendors, (vendor) => Text.Contains([Proveedor], vendor)))),
    CompactedConfirmation = Table.ReplaceValue(RemovedExcludedVendors, " ", "", Replacer.ReplaceText, {"Tipo Conf."}),
    DefaultedConfirmation = Table.ReplaceValue(CompactedConfirmation, "", "SC", Replacer.ReplaceValue, {"Tipo Conf."}),
    RenamedDates = Table.RenameColumns(DefaultedConfirmation, {{"Fecha Pedido", "Fecha creación OC"}, {"Fecha Entrega Pedido", "Fecha entrega PO"}, {"Fecha Embarque", "Fecha Embarque AB"}, {"Fecha Planta TC", "Fecha Embarque LA"}}),
    AddedAging = Table.AddColumn(RenamedDates, "Aging", each
        if [#"Tipo Conf."] = "AB" then Duration.Days(Today - [Fecha Embarque AB])
        else if [#"Tipo Conf."] = "LA" or [#"Tipo Conf."] = "LA+" then Duration.Days(Today - [Fecha Embarque LA])
        else if [#"Tipo Conf."] = "SC" and List.Contains(AgingPoVendors, [Proveedor]) then Duration.Days(Today - [Fecha entrega PO])
        else if [#"Tipo Conf."] = "SC" then Duration.Days(Today - [Fecha creación OC])
        else null, Int64.Type),
    AddedStatus = Table.AddColumn(AddedAging, "Status", each
        if [Aging] = null then "Sin Clasificar"
        else if [#"Tipo Conf."] = "SC" and [Aging] > 10 then "Delay"
        else if List.Contains({"AB", "LA", "LA+"}, [#"Tipo Conf."]) and [Aging] > 0 then "Delay"
        else "On time", type text),
    AddedRescheduleDays = Table.AddColumn(AddedStatus, "Reschedule Days", each
        if [Fecha Reprog] = null or [Fecha Embarque LA] = null then null
        else Number.Abs(Duration.Days([Fecha Reprog] - [Fecha Embarque LA])), Int64.Type),
    AddedReschedule = Table.AddColumn(AddedRescheduleDays, "Reschedule", each Aging([Reschedule Days]), type text),
    ClearedRescheduleErrors = Table.ReplaceErrorValues(AddedReschedule, {{"Reschedule", null}}),
    AddedException = Table.AddColumn(ClearedRescheduleErrors, "Excepción", each
        if Text.Contains([Excepcion], "Reschedule in") then "Reschedule in"
        else if Text.Contains([Excepcion], "Reschedule out") then "Reschedule out"
        else if Text.Contains([Excepcion], "Finish date in the past") then "Finish date in the past"
        else if Text.Contains([Excepcion], "Cancel process") then "Cancel process"
        else "No Exception", type text),
    TypedPosition = Table.TransformColumnTypes(AddedException, {{"Posición", Int64.Type}}),
    ClearedDateErrors = Table.ReplaceErrorValues(TypedPosition, List.Transform(DateColumns, each {_, null})),
    DatesAsText = Table.TransformColumnTypes(ClearedDateErrors, List.Transform(DateColumns, each {_, type text}) & {{"Aging", type text}}),
    SelectedOutput = Table.SelectColumns(DatesAsText, OutputColumns),
    RemovedErrorRows = Table.RemoveRowsWithErrors(SelectedOutput),
    BlanksAsNull = Table.ReplaceValue(RemovedErrorRows, "", null, Replacer.ReplaceValue, List.RemoveItems(OutputColumns, {"Data created"})),
    AddedExecutionTime = Table.AddColumn(BlanksAsNull, "EXECUTION_TIME", each Text.AfterDelimiter(Text.From([Data created]), " ", 0), type text),
    AddedExecutionDate = Table.AddColumn(AddedExecutionTime, "EXECUTION_DATE", each Text.BeforeDelimiter(Text.From([Data created]), " ", 0), type text),
    AddedDataBase = Table.AddColumn(AddedExecutionDate, "DATA_BASE", each "SAP", type text),
    RemovedFileDate = Table.RemoveColumns(AddedDataBase, {"Data created"}),
    TypedExecutionDate = Table.TransformColumnTypes(RemovedFileDate, {{"EXECUTION_DATE", type date}}),
    RenamedConfirmation = Table.RenameColumns(TypedExecutionDate, {{"Tipo Conf.", "Tipo Confirmacion"}})
in
    RenamedConfirmation;
