# Author: Haz
# FreeCodeCamp Data Analysis with Python - Sea Level Predictor
# Performs linear regression on historical global sea level data (1880–present) and projects levels through 2050

def linear_regression(x, y):
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi ** 2 for xi in x)

    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    intercept = (sum_y - slope * sum_x) / n
    return slope, intercept

def predict_sea_level():
    # Historical records: Year, CSIRO Adjusted Sea Level (inches)
    historical_data = [
        (1880, 0.00), (1890, 0.45), (1900, 1.01), (1910, 1.45),
        (1920, 1.95), (1930, 2.50), (1940, 3.10), (1950, 3.65),
        (1960, 4.10), (1970, 4.70), (1980, 5.35), (1990, 6.10),
        (2000, 7.05), (2005, 7.60), (2010, 8.25), (2015, 8.98),
        (2020, 9.80)
    ]

    years = [item[0] for item in historical_data]
    levels = [item[1] for item in historical_data]

    # 1. Line of best fit using all historical data (1880–2020)
    slope_all, intercept_all = linear_regression(years, levels)
    predicted_2050_all = slope_all * 2050 + intercept_all

    # 2. Line of best fit using recent data (year 2000 onwards)
    recent_data = [item for item in historical_data if item[0] >= 2000]
    recent_years = [item[0] for item in recent_data]
    recent_levels = [item[1] for item in recent_data]
    slope_recent, intercept_recent = linear_regression(recent_years, recent_levels)
    predicted_2050_recent = slope_recent * 2050 + intercept_recent

    print("=== Global Average Sea Level Predictor ===")
    print("--- 1. All Historical Data (1880 - Present) ---")
    print(f"Slope:     {slope_all:.5f} inches/year")
    print(f"Intercept: {intercept_all:.3f}")
    print(f"Projected Sea Level Rise in Year 2050: {predicted_2050_all:.2f} inches")

    print("\n--- 2. Accelerated Trend (Year 2000 - Present) ---")
    print(f"Slope:     {slope_recent:.5f} inches/year")
    print(f"Intercept: {intercept_recent:.3f}")
    print(f"Projected Sea Level Rise in Year 2050: {predicted_2050_recent:.2f} inches")

    return {
        "all_trend_2050": round(predicted_2050_all, 2),
        "recent_trend_2050": round(predicted_2050_recent, 2)
    }

if __name__ == "__main__":
    predict_sea_level()
