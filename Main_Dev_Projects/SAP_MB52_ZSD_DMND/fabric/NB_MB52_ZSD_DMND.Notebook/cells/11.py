
# ===============================================
# Export Workbook
# ===============================================
ROOT.mkdir(parents=True, exist_ok=True)
if OUTPUT_PATH.exists():
    OUTPUT_PATH.unlink()
with pd.ExcelWriter(OUTPUT_PATH, engine='openpyxl', datetime_format='yyyy-mm-dd') as writer:
    final.to_excel(writer, sheet_name='Final', index=False, startrow=3)
    sd48_p.to_excel(writer, sheet_name='ZSD_DMND_P', index=False, startrow=2)
    sd48.to_excel(writer, sheet_name='ZSD_DMND', index=False)
    mb52_p[['Material','Sum of Available','Sum of Total Inv','Resume Available']].to_excel(writer, sheet_name='MB52_P', index=False, startrow=2)
    mb52.to_excel(writer, sheet_name='MB52', index=False)
    base.to_excel(writer, sheet_name='Base', index=False)
    workbook = writer.book
    ws_final = writer.sheets['Final']
    ws_final['A1'] = 'Analysis Date:'
    ws_final['A2'] = analysis_date.to_pydatetime()
    ws_final['B1'] = '3M Workable Days:'
    ws_final['B2'] = workable_days
    ws_final['H3'] = 'Past_Due_+_Period_1_Demand'
    ws_final['I3'] = 'Period_2_Demand'
    ws_final['J3'] = 'Period_3_Demand'
    writer.sheets['ZSD_DMND_P']['A1'] = 'Type'
    writer.sheets['ZSD_DMND_P']['B1'] = 'Demand'
    header_rows = {'Final':4,'ZSD_DMND_P':3,'ZSD_DMND':1,'MB52_P':3,'MB52':1,'Base':1}
    freeze_cells = {'Final':'A5','ZSD_DMND_P':'A4','ZSD_DMND':'A2','MB52_P':'A4','MB52':'A2','Base':'A2'}
    header_fill = PatternFill('solid', fgColor='1F4E78')
    header_font = Font(color='FFFFFF', bold=True)
    for sheet_name, worksheet in writer.sheets.items():
        header_row = header_rows[sheet_name]
        worksheet.freeze_panes = freeze_cells[sheet_name]
        worksheet.auto_filter.ref = f'A{header_row}:{get_column_letter(worksheet.max_column)}{worksheet.max_row}'
        for cell in worksheet[header_row]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        worksheet.row_dimensions[header_row].height = 30
        for column_index in range(1, worksheet.max_column + 1):
            values = [worksheet.cell(row, column_index).value for row in range(1, min(worksheet.max_row, 250) + 1)]
            width = min(max([len(str(v)) for v in values if v is not None] or [10]) + 2, 42)
            worksheet.column_dimensions[get_column_letter(column_index)].width = width
    for column in ['F','P','Q','R']:
        for cell in ws_final[column][4:]:
            cell.number_format = '0.0%'
    for column in ['S','T']:
        for cell in ws_final[column][4:]:
            cell.number_format = 'yyyy-mm-dd'

log.info('Workbook created: %s (%s bytes)', OUTPUT_PATH, f'{OUTPUT_PATH.stat().st_size:,}')
log.info('MB52 x ZSD_DMND coverage completed: %s materials', f'{len(final):,}')


