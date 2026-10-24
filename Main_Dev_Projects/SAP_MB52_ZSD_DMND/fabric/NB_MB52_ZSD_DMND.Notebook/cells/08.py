
# ===============================================
# Build MB52_P (Inventory by Material)
# ===============================================
mb52_p = (mb52.groupby('Material', as_index=False, dropna=False)
    .agg(**{
        'Sum of Available': ('Available','sum'),
        'Sum of Total Inv': ('Total Inv','sum'),
        'Material_Description': ('Material_Description','first')
    }))
warehouse = (mb52.loc[mb52['Resume_Location'].eq(WAREHOUSE_RESUME)]
    .groupby('Material', as_index=False)['Available'].sum()
    .rename(columns={'Available':'Resume Available'}))
mb52_p = mb52_p.merge(warehouse, how='left', on='Material')
mb52_p['Resume Available'] = mb52_p['Resume Available'].fillna(0.0)


