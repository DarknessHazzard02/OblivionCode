
# ===============================================
# Normalize MB52
# ===============================================
mb52_map = {
    'Material': resolve_column(mb52_raw, ['Material']),
    'Material_Description': resolve_column(mb52_raw, ['Material_Description','Material Description','Description']),
    'Base_Unit': resolve_column(mb52_raw, ['Base_Unit','Base Unit','Base Unit of Measure'], False),
    'Plant': resolve_column(mb52_raw, ['Plant']),
    'Storage_Location': resolve_column(mb52_raw, ['Storage_Location','Storage Location','SLoc']),
    'Storage_Location_Description': resolve_column(mb52_raw, ['Storage_Location_Description','Storage Location Description'], False),
    'Unrestricted': resolve_column(mb52_raw, ['Unrestricted','Unrestricted Stock']),
    'Value_Unrestricted': resolve_column(mb52_raw, ['Value_Unrestricted','Value Unrestricted'], False),
    'Quality_Inspection': resolve_column(mb52_raw, ['Quality_Inspection','Quality Inspection'], False),
    'Value_Quality_Inspection': resolve_column(mb52_raw, ['Value_Quality_Inspection','Value Quality Inspection'], False),
    'Blocked': resolve_column(mb52_raw, ['Blocked'], False),
    'Value_Blocked': resolve_column(mb52_raw, ['Value_Blocked','Value Blocked'], False),
    'Stock_In_Transfer': resolve_column(mb52_raw, ['Stock_In_Transfer','Stock in Transfer'], False),
    'Value_In_Transfer': resolve_column(mb52_raw, ['Value_In_Transfer','Value in Transfer'], False),
    'Returns': resolve_column(mb52_raw, ['Returns'], False),
    'Material_Type': resolve_column(mb52_raw, ['Material_Type','Material Type'], False),
    'Material_Group': resolve_column(mb52_raw, ['Material_Group','Material Group'], False),
    'FILE_DATE': resolve_column(mb52_raw, ['FILE_DATE','File Date'], False),
    'LOAD_DATE': resolve_column(mb52_raw, ['LOAD_DATE','Load Date'], False),
    'SOURCE_FILE': resolve_column(mb52_raw, ['SOURCE_FILE','Source File'], False)
}
mb52 = pd.DataFrame(index=mb52_raw.index)
for target, source in mb52_map.items():
    mb52[target] = mb52_raw[source] if source else pd.NA
mb52['Material'] = normalize_material(mb52['Material'])
for column in ['Material_Description','Base_Unit','Plant','Storage_Location','Storage_Location_Description','Material_Type','Material_Group','SOURCE_FILE']:
    mb52[column] = mb52[column].astype('string').str.strip()
for column in ['Unrestricted','Value_Unrestricted','Quality_Inspection','Value_Quality_Inspection','Blocked','Value_Blocked','Stock_In_Transfer','Value_In_Transfer','Returns']:
    mb52[column] = numeric(mb52[column])
mb52['FILE_DATE'] = parse_dates(mb52['FILE_DATE'])
mb52['LOAD_DATE'] = pd.to_datetime(mb52['LOAD_DATE'], errors='coerce')
base = pd.DataFrame(BASE_ROWS, columns=BASE_COLUMNS)
base_key = base[['Plant','Storage_Location','Resume']].drop_duplicates(['Plant','Storage_Location'], keep='first')
mb52 = mb52.merge(base_key, how='left', on=['Plant','Storage_Location'])
mb52 = mb52.rename(columns={'Resume':'Resume_Location'})
mb52['Resume_Location'] = mb52['Resume_Location'].fillna('Blank')
mb52['Available'] = mb52['Unrestricted']
mb52['Total Inv'] = mb52['Unrestricted'] + mb52['Quality_Inspection'] + mb52['Blocked']
mb52 = mb52[[
    'Material','Material_Description','Base_Unit','Plant','Storage_Location','Storage_Location_Description',
    'Resume_Location','Unrestricted','Value_Unrestricted','Quality_Inspection','Value_Quality_Inspection',
    'Blocked','Value_Blocked','Stock_In_Transfer','Value_In_Transfer','Returns','Material_Type',
    'Material_Group','FILE_DATE','LOAD_DATE','SOURCE_FILE','Available','Total Inv'
]]
analysis_date = choose_analysis_date(mb52)
period_1_end = analysis_date + relativedelta(months=1)
period_2_end = analysis_date + relativedelta(months=2)
period_3_end = analysis_date + relativedelta(months=3)
workable_days = sunday_only_workdays(analysis_date, period_3_end, inclusive_end=False)
log.info('Analysis date: %s | 3M workable days: %s', analysis_date.date(), workable_days)


