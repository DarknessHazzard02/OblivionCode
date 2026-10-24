
# ===============================================
# Normalize ZSD_DMND
# ===============================================
sd48_map = {
    'Plant': resolve_column(sd48_raw, ['Plant'], False),
    'Material': resolve_column(sd48_raw, ['Material','Material Number']),
    'Parent_Material': resolve_column(sd48_raw, ['Parent_Material','Parent Material'], False),
    'Necessity_Type': resolve_column(sd48_raw, ['Necessity_Type','Necessity Type'], False),
    'Qty': resolve_column(sd48_raw, ['Qty','Quantity'], False),
    'Remain_Qty': resolve_column(sd48_raw, ['Remain_Qty','Remain Qty'], False),
    'CN': resolve_column(sd48_raw, ['CN'], False),
    'Object_Number': resolve_column(sd48_raw, ['Object_Number','Object Number'], False),
    'Object_Flag': resolve_column(sd48_raw, ['Object_Flag','Object Flag'], False),
    'Item': resolve_column(sd48_raw, ['Item'], False),
    'Obj_Type': resolve_column(sd48_raw, ['Obj_Type','Obj Type'], False),
    'Date': resolve_column(sd48_raw, ['Date','Requirement Date','Basic Date']),
    'Inventory': resolve_column(sd48_raw, ['Inventory'], False),
    'Coverage': resolve_column(sd48_raw, ['Coverage'], False),
    'Goods_Issue_Date': resolve_column(sd48_raw, ['Goods_Issue_Date','Goods Issue Date'], False),
    'Shipping_Date': resolve_column(sd48_raw, ['Shipping_Date','Shipping Date'], False),
    'Customer_Name': resolve_column(sd48_raw, ['Customer_Name','Customer Name'], False),
    'MRP': resolve_column(sd48_raw, ['MRP'], False),
    'Material_Group': resolve_column(sd48_raw, ['Material_Group','Material Group'], False),
    'Section': resolve_column(sd48_raw, ['Section'], False),
    'Qty_Truncada': resolve_column(sd48_raw, ['Qty_Truncada','Qty Truncada'], False),
    'Qty_Valor': resolve_column(sd48_raw, ['Qty_Valor','Qty Valor','Quantity Value','Quantity']),
    'Type': resolve_column(sd48_raw, ['Type'], False),
    'DateRange': resolve_column(sd48_raw, ['DateRange','Date Range'], False),
    'Qty_Reconstruida': resolve_column(sd48_raw, ['Qty_Reconstruida','Qty Reconstruida'], False),
    'FILE_DATE': resolve_column(sd48_raw, ['FILE_DATE','File Date'], False),
    'LOAD_DATE': resolve_column(sd48_raw, ['LOAD_DATE','Load Date'], False),
    'SOURCE_FILE': resolve_column(sd48_raw, ['SOURCE_FILE','Source File'], False)
}
sd48 = pd.DataFrame(index=sd48_raw.index)
for target, source in sd48_map.items():
    sd48[target] = sd48_raw[source] if source else pd.NA
sd48['Material'] = normalize_material(sd48['Material'])
sd48['Parent_Material'] = normalize_material(sd48['Parent_Material'])
for column in ['Qty','Remain_Qty','Inventory','Coverage','Qty_Truncada','Qty_Valor','Qty_Reconstruida']:
    sd48[column] = numeric(sd48[column])
for column in ['Date','Goods_Issue_Date','Shipping_Date','FILE_DATE']:
    sd48[column] = parse_dates(sd48[column])
sd48['LOAD_DATE'] = pd.to_datetime(sd48['LOAD_DATE'], errors='coerce')
valid_rows = sd48['Material'].notna() & sd48['Date'].notna()
if (~valid_rows).any():
    log.warning('ZSD_DMND rows dropped (no material or date): %s', f'{(~valid_rows).sum():,}')
sd48 = sd48[valid_rows].copy()


