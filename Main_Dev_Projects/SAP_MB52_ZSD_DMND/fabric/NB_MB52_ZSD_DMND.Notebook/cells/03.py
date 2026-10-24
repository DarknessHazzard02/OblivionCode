
# ===============================================
# Helpers
# ===============================================
def canonical(value):
    return re.sub(r'[^a-z0-9]', '', str(value).lower())

def resolve_column(df, candidates, required=True):
    available = {canonical(c): c for c in df.columns}
    for candidate in candidates:
        key = canonical(candidate)
        if key in available:
            return available[key]
    if required:
        raise KeyError(f'Missing expected column. Candidates: {candidates}. Available: {list(df.columns)}')
    # Optional column: it becomes 0 / empty downstream, so say it out loud
    log.warning('Optional column not found, filled as empty: %s', candidates[0])
    return None

def normalize_material(series):
    text = series.astype('string').str.strip()
    return text.str.replace(r'\.0$', '', regex=True)

def numeric(series):
    if series is None:
        return 0.0
    return pd.to_numeric(series, errors='coerce').fillna(0.0)

def parse_dates(series):
    return pd.to_datetime(series, errors='coerce').dt.normalize()

def sunday_only_workdays(start, end, inclusive_end=True):
    if pd.isna(start) or pd.isna(end) or end < start:
        return 0
    end_value = end if inclusive_end else end - pd.Timedelta(days=1)
    days = pd.date_range(start, end_value, freq='D')
    return int((days.dayofweek != 6).sum())

def choose_analysis_date(mb52):
    if ANALYSIS_DATE_OVERRIDE:
        return pd.Timestamp(ANALYSIS_DATE_OVERRIDE).normalize()
    for name in ['FILE_DATE','LOAD_DATE']:
        if name in mb52.columns:
            values = parse_dates(mb52[name]).dropna()
            if not values.empty:
                return values.max()
    raise ValueError('Analysis date could not be derived. Set ANALYSIS_DATE_OVERRIDE.')

def stockout_date(group, inventory, analysis_date, horizon_end):
    if group.empty or inventory <= 0:
        return analysis_date
    past_due = group.loc[group['Date'] < analysis_date, 'Abs'].sum()
    if past_due >= inventory:
        return analysis_date
    future = group[(group['Date'] >= analysis_date) & (group['Date'] < horizon_end)].copy()
    if future.empty:
        return pd.NaT
    future['Running'] = past_due + future['Abs'].cumsum()
    hits = future.loc[future['Running'] >= inventory, 'Date']
    return hits.iloc[0] if not hits.empty else pd.NaT

def validate_source_files():
    missing = [str(path) for path in [MB52_PATH, SD48_PATH] if not path.exists()]
    if missing:
        raise FileNotFoundError('Missing OneLake input file(s): ' + ', '.join(missing))
    log.info('MB52 source: %s', MB52_PATH)
    log.info('ZSD_DMND source: %s', SD48_PATH)
    log.info('Output workbook: %s', OUTPUT_PATH)


