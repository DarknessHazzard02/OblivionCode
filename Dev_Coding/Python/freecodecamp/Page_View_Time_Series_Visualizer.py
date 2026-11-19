# Author: Haz
# FreeCodeCamp Data Analysis with Python - Page View Time Series Visualizer
# Cleans daily website traffic by filtering 2.5% percentiles and computes monthly/yearly trend distributions

import datetime

def analyze_time_series():
    # Sample daily forum page views: date string, raw page views
    raw_data = [
        ("2016-05-09", 1201), ("2016-05-10", 2329), ("2016-06-15", 3500),
        ("2016-07-20", 4120), ("2016-08-11", 5200), ("2016-09-01", 6400),
        ("2017-01-10", 7200), ("2017-04-12", 8100), ("2017-07-15", 9400),
        ("2017-10-22", 11200), ("2018-01-05", 14500), ("2018-06-18", 18200),
        ("2018-11-20", 22100), ("2019-02-14", 25600), ("2019-07-04", 29800),
        ("2019-12-01", 34500), ("2019-12-31", 120000) # Outlier spike
    ]

    # 1. Clean data: filter top 2.5% and bottom 2.5%
    views = sorted([item[1] for item in raw_data])
    n = len(views)
    lower_cutoff = views[int(n * 0.025)]
    upper_cutoff = views[int(n * 0.975)]

    cleaned = [(d, v) for d, v in raw_data if lower_cutoff <= v <= upper_cutoff]

    # 2. Group by Year
    yearly_stats = {}
    for date_str, v in cleaned:
        year = date_str.split("-")[0]
        if year not in yearly_stats:
            yearly_stats[year] = []
        yearly_stats[year].append(v)

    # 3. Group by Month
    monthly_stats = {}
    for date_str, v in cleaned:
        month = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%B")
        if month not in monthly_stats:
            monthly_stats[month] = []
        monthly_stats[month].append(v)

    print("=== Forum Page Views Time Series Analysis ===")
    print(f"Raw records: {len(raw_data)} | Cleaned records (outliers filtered): {len(cleaned)}")
    
    print("\n--- Year-wise Average Daily Page Views ---")
    for year, vals in yearly_stats.items():
        avg = sum(vals) / len(vals)
        print(f"Year {year}: Average = {avg:,.0f} views (Samples: {len(vals)})")

    print("\n--- Month-wise Trend Summary ---")
    for month, vals in monthly_stats.items():
        avg = sum(vals) / len(vals)
        print(f"{month:10}: Average = {avg:,.0f} views")

    return yearly_stats, monthly_stats

if __name__ == "__main__":
    analyze_time_series()
