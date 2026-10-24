
# ===============================================
# Build ZSD_DMND_P (Demand by Material and Date)
# ===============================================
sd48_p = (sd48.groupby(['Material','Date'], as_index=False, dropna=False)['Qty_Valor']
    .sum().rename(columns={'Qty_Valor':'Sum of Qty_Valor'}))
sd48_p['Abs'] = sd48_p['Sum of Qty_Valor'].abs()
sd48_p = sd48_p.sort_values(['Material','Date'], kind='stable').reset_index(drop=True)
sd48_p['Cumulative Demand from Analysis Date'] = sd48_p.groupby('Material', sort=False)['Abs'].cumsum()


