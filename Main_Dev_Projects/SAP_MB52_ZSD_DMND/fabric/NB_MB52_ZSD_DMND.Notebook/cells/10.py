
# ===============================================
# Quality Checks
# ===============================================
log.info('Rows - MB52: %s | ZSD_DMND: %s | MB52_P: %s | ZSD_DMND_P: %s | Final: %s',
         f'{len(mb52):,}', f'{len(sd48):,}', f'{len(mb52_p):,}', f'{len(sd48_p):,}', f'{len(final):,}')
log.info('Unrestricted status counts: %s', final['Unrestricted_Status'].value_counts(dropna=False).to_dict())
unmapped = mb52.loc[mb52['Resume_Location'].eq('Blank'), ['Plant','Storage_Location','Storage_Location_Description']].drop_duplicates()
if not unmapped.empty:
    log.warning('Storage locations not in BASE_ROWS (reported as Blank): %s',
                unmapped[['Plant','Storage_Location']].astype(str).agg('/'.join, axis=1).tolist())
if final['Material'].isna().any():
    raise ValueError('Final output contains null materials.')
if (final['Total_Inventory'] < final['Unrestricted']).any():
    log.warning('Some materials have Total_Inventory lower than Unrestricted. Review negative inspection or blocked quantities.')


