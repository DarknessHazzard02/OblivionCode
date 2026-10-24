
# ===============================================
# Build Final Coverage Model
# ===============================================
p1 = (sd48_p.loc[sd48_p['Date'] < period_1_end]
    .groupby('Material')['Abs'].sum().rename('Past_Due_+_Period_1_Demand'))
p2 = (sd48_p.loc[(sd48_p['Date'] >= period_1_end) & (sd48_p['Date'] < period_2_end)]
    .groupby('Material')['Abs'].sum().rename('Period_2_Demand'))
p3 = (sd48_p.loc[(sd48_p['Date'] >= period_2_end) & (sd48_p['Date'] < period_3_end)]
    .groupby('Material')['Abs'].sum().rename('Period_3_Demand'))
materials = pd.DataFrame({'Material': pd.unique(pd.concat([mb52_p['Material'], sd48_p['Material']], ignore_index=True).dropna())})
final = materials.merge(mb52_p, how='left', on='Material')
final = final.merge(p1, how='left', left_on='Material', right_index=True)
final = final.merge(p2, how='left', left_on='Material', right_index=True)
final = final.merge(p3, how='left', left_on='Material', right_index=True)
for column in ['Sum of Available','Sum of Total Inv','Resume Available','Past_Due_+_Period_1_Demand','Period_2_Demand','Period_3_Demand']:
    final[column] = numeric(final[column])
final = final.rename(columns={
    'Resume Available':'Warehouse Available Inventory',
    'Sum of Available':'Unrestricted',
    'Sum of Total Inv':'Total_Inventory'
})
final['Warehouse Share of Available Inventory'] = np.where(final['Unrestricted'].ne(0), final['Warehouse Available Inventory'] / final['Unrestricted'], 0.0)
final['Non-Warehouse Available Inventory'] = final['Unrestricted'] - final['Warehouse Available Inventory']
final['Total_Demand_Exposure'] = final[['Past_Due_+_Period_1_Demand','Period_2_Demand','Period_3_Demand']].sum(axis=1)
final['Average_Daily_Demand'] = np.where(final['Total_Demand_Exposure'].ne(0), final['Total_Demand_Exposure'] / workable_days, 0.0)
for inv, coverage, percentage in [
    ('Warehouse Available Inventory','Warehouse Average Coverage Days','Warehouse Demand Coverage %'),
    ('Unrestricted','Available_Average_Days_Coverage','Available_Demand_Coverage_%'),
    ('Total_Inventory','Total_Average_Days_Coverage','Total_Demand_Coverage_%')
]:
    final[coverage] = np.where(final['Average_Daily_Demand'].gt(0), np.floor(final[inv] / final['Average_Daily_Demand']).clip(0, workable_days), 0).astype(int)
    final[percentage] = np.where(final['Total_Demand_Exposure'].gt(0), (final[inv] / final['Total_Demand_Exposure']).clip(upper=1.01), 1.0)

demand_groups = {material: group.sort_values('Date') for material, group in sd48_p.groupby('Material')}
final['Unrestricted_Stockout_Date'] = final.apply(lambda row: pd.NaT if row['Total_Demand_Exposure'] == 0 else stockout_date(demand_groups.get(row['Material'], pd.DataFrame()), row['Unrestricted'], analysis_date, period_3_end), axis=1)
final['Total_Inventory_Stockout_Date'] = final.apply(lambda row: pd.NaT if row['Total_Demand_Exposure'] == 0 else stockout_date(demand_groups.get(row['Material'], pd.DataFrame()), row['Total_Inventory'], analysis_date, period_3_end), axis=1)
final['Available_SAP_Days_Coverage'] = final['Unrestricted_Stockout_Date'].apply(lambda value: max(0, sunday_only_workdays(analysis_date, value) - 1) if pd.notna(value) else 0)
final['Total_SAP_Days_Coverage'] = final['Total_Inventory_Stockout_Date'].apply(lambda value: max(0, sunday_only_workdays(analysis_date, value) - 1) if pd.notna(value) else 0)

def status(row, inventory_column, stockout_column):
    if row['Total_Demand_Exposure'] == 0:
        return 'No Demand'
    if row[inventory_column] <= 0 or row[stockout_column] == analysis_date:
        return 'Immediate Shortage'
    if row[inventory_column] < row['Total_Demand_Exposure']:
        return 'Below Rolling 3M Coverage'
    return 'Covered Rolling 3M'

final['Unrestricted_Status'] = final.apply(status, axis=1, args=('Unrestricted','Unrestricted_Stockout_Date'))
final['Total_Inventory_Status'] = final.apply(status, axis=1, args=('Total_Inventory','Total_Inventory_Stockout_Date'))
final_columns = [
    'Material','Material_Description','Warehouse Available Inventory','Unrestricted','Total_Inventory',
    'Warehouse Share of Available Inventory','Non-Warehouse Available Inventory','Past_Due_+_Period_1_Demand',
    'Period_2_Demand','Period_3_Demand','Total_Demand_Exposure','Average_Daily_Demand',
    'Warehouse Average Coverage Days','Available_Average_Days_Coverage','Total_Average_Days_Coverage',
    'Warehouse Demand Coverage %','Available_Demand_Coverage_%','Total_Demand_Coverage_%',
    'Unrestricted_Stockout_Date','Total_Inventory_Stockout_Date','Available_SAP_Days_Coverage',
    'Total_SAP_Days_Coverage','Unrestricted_Status','Total_Inventory_Status'
]
final = final[final_columns].sort_values(['Warehouse Share of Available Inventory','Material'], kind='stable').reset_index(drop=True)


