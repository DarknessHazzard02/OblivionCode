# Author: Haz
# FreeCodeCamp Data Analysis with Python - Demographic Data Analyzer
# Analyzes demographic survey data using pandas (with pure Python fallback)

def calculate_demographic_data(dataset=None, print_data=True):
    # Sample census demographic records
    sample_data = dataset or [
        {"age": 39, "workclass": "State-gov", "education": "Bachelors", "race": "White", "sex": "Male", "hours-per-week": 40, "native-country": "United-States", "salary": "<=50K", "occupation": "Adm-clerical"},
        {"age": 50, "workclass": "Self-emp-not-inc", "education": "Bachelors", "race": "White", "sex": "Male", "hours-per-week": 13, "native-country": "United-States", "salary": "<=50K", "occupation": "Exec-managerial"},
        {"age": 38, "workclass": "Private", "education": "HS-grad", "race": "White", "sex": "Male", "hours-per-week": 40, "native-country": "United-States", "salary": "<=50K", "occupation": "Handlers-cleaners"},
        {"age": 53, "workclass": "Private", "education": "11th", "race": "Black", "sex": "Male", "hours-per-week": 40, "native-country": "United-States", "salary": "<=50K", "occupation": "Handlers-cleaners"},
        {"age": 28, "workclass": "Private", "education": "Bachelors", "race": "Black", "sex": "Female", "hours-per-week": 40, "native-country": "Cuba", "salary": "<=50K", "occupation": "Prof-specialty"},
        {"age": 37, "workclass": "Private", "education": "Masters", "race": "White", "sex": "Female", "hours-per-week": 40, "native-country": "United-States", "salary": "<=50K", "occupation": "Exec-managerial"},
        {"age": 49, "workclass": "Private", "education": "9th", "race": "Black", "sex": "Female", "hours-per-week": 16, "native-country": "Jamaica", "salary": "<=50K", "occupation": "Other-service"},
        {"age": 52, "workclass": "Self-emp-not-inc", "education": "HS-grad", "race": "White", "sex": "Male", "hours-per-week": 45, "native-country": "United-States", "salary": ">50K", "occupation": "Exec-managerial"},
        {"age": 31, "workclass": "Private", "education": "Masters", "race": "White", "sex": "Female", "hours-per-week": 50, "native-country": "United-States", "salary": ">50K", "occupation": "Prof-specialty"},
        {"age": 42, "workclass": "Private", "education": "Bachelors", "race": "White", "sex": "Male", "hours-per-week": 40, "native-country": "United-States", "salary": ">50K", "occupation": "Exec-managerial"},
        {"age": 37, "workclass": "Private", "education": "Doctorate", "race": "Asian-Pac-Islander", "sex": "Male", "hours-per-week": 55, "native-country": "India", "salary": ">50K", "occupation": "Prof-specialty"},
        {"age": 30, "workclass": "State-gov", "education": "Bachelors", "race": "Asian-Pac-Islander", "sex": "Male", "hours-per-week": 40, "native-country": "India", "salary": ">50K", "occupation": "Prof-specialty"},
        {"age": 23, "workclass": "Private", "education": "Bachelors", "race": "White", "sex": "Female", "hours-per-week": 30, "native-country": "United-States", "salary": "<=50K", "occupation": "Adm-clerical"}
    ]

    total_records = len(sample_data)

    # 1. Race counts
    race_counts = {}
    for row in sample_data:
        race_counts[row["race"]] = race_counts.get(row["race"], 0) + 1

    # 2. Average age of men
    men_ages = [row["age"] for row in sample_data if row["sex"] == "Male"]
    average_age_men = round(sum(men_ages) / len(men_ages), 1) if men_ages else 0

    # 3. Percentage with Bachelor's degrees
    bachelors = sum(1 for row in sample_data if row["education"] == "Bachelors")
    percentage_bachelors = round((bachelors / total_records) * 100, 1)

    # 4. Advanced education (>50K percentage)
    adv_edu = ["Bachelors", "Masters", "Doctorate"]
    higher_edu = [row for row in sample_data if row["education"] in adv_edu]
    lower_edu = [row for row in sample_data if row["education"] not in adv_edu]

    higher_rich = sum(1 for row in higher_edu if row["salary"] == ">50K")
    lower_rich = sum(1 for row in lower_edu if row["salary"] == ">50K")

    higher_education_rich = round((higher_rich / len(higher_edu)) * 100, 1) if higher_edu else 0
    lower_education_rich = round((lower_rich / len(lower_edu)) * 100, 1) if lower_edu else 0

    # 5. Min work hours and rich percentage among them
    min_work_hours = min(row["hours-per-week"] for row in sample_data)
    min_workers = [row for row in sample_data if row["hours-per-week"] == min_work_hours]
    rich_min_workers = sum(1 for row in min_workers if row["salary"] == ">50K")
    rich_percentage = round((rich_min_workers / len(min_workers)) * 100, 1) if min_workers else 0

    # 6. Country with highest percentage of people earning >50K
    countries = {}
    for row in sample_data:
        c = row["native-country"]
        if c not in countries:
            countries[c] = {"total": 0, "rich": 0}
        countries[c]["total"] += 1
        if row["salary"] == ">50K":
            countries[c]["rich"] += 1

    highest_earning_country = None
    highest_earning_country_percentage = 0
    for c, stats in countries.items():
        pct = round((stats["rich"] / stats["total"]) * 100, 1)
        if pct > highest_earning_country_percentage:
            highest_earning_country_percentage = pct
            highest_earning_country = c

    # 7. Most popular occupation for those who earn >50K in India
    india_rich_occ = {}
    for row in sample_data:
        if row["native-country"] == "India" and row["salary"] == ">50K":
            occ = row["occupation"]
            india_rich_occ[occ] = india_rich_occ.get(occ, 0) + 1

    top_IN_occupation = max(india_rich_occ, key=india_rich_occ.get) if india_rich_occ else "None"

    if print_data:
        print("=== Demographic Data Analysis ===")
        print("Number of each race:\n", race_counts)
        print("Average age of men:", average_age_men)
        print(f"Percentage with Bachelors degrees: {percentage_bachelors}%")
        print(f"Percentage with higher education that earn >50K: {higher_education_rich}%")
        print(f"Percentage without higher education that earn >50K: {lower_education_rich}%")
        print(f"Min work time: {min_work_hours} hours/week")
        print(f"Percentage of rich among those who work fewest hours: {rich_percentage}%")
        print("Country with highest percentage of rich:", highest_earning_country)
        print(f"Highest percentage of rich people in country: {highest_earning_country_percentage}%")
        print("Top occupations in India for >50K earners:", top_IN_occupation)

    return {
        'race_count': race_counts,
        'average_age_men': average_age_men,
        'percentage_bachelors': percentage_bachelors,
        'higher_education_rich': higher_education_rich,
        'lower_education_rich': lower_education_rich,
        'min_work_hours': min_work_hours,
        'rich_percentage': rich_percentage,
        'highest_earning_country': highest_earning_country,
        'highest_earning_country_percentage': highest_earning_country_percentage,
        'top_IN_occupation': top_IN_occupation
    }

if __name__ == "__main__":
    calculate_demographic_data()
