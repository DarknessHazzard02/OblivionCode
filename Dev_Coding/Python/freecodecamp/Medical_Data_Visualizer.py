# Author: Haz
# FreeCodeCamp Data Analysis with Python - Medical Examination Data Visualizer
# Processes patient health metrics, calculates BMI overweight category, normalizes indicators, and computes correlation matrix

def process_medical_data():
    # Sample medical records: id, age_days, sex, height_cm, weight_kg, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active, cardio
    sample_records = [
        {"id": 0, "age": 18393, "sex": 2, "height": 168, "weight": 62.0, "ap_hi": 110, "ap_lo": 80, "cholesterol": 1, "gluc": 1, "smoke": 0, "alco": 0, "active": 1, "cardio": 0},
        {"id": 1, "age": 20228, "sex": 1, "height": 156, "weight": 85.0, "ap_hi": 140, "ap_lo": 90, "cholesterol": 3, "gluc": 1, "smoke": 0, "alco": 0, "active": 1, "cardio": 1},
        {"id": 2, "age": 18857, "sex": 1, "height": 165, "weight": 64.0, "ap_hi": 130, "ap_lo": 70, "cholesterol": 3, "gluc": 1, "smoke": 0, "alco": 0, "active": 0, "cardio": 1},
        {"id": 3, "age": 17623, "sex": 2, "height": 169, "weight": 82.0, "ap_hi": 150, "ap_lo": 100, "cholesterol": 1, "gluc": 1, "smoke": 0, "alco": 0, "active": 1, "cardio": 1},
        {"id": 4, "age": 17474, "sex": 1, "height": 156, "weight": 56.0, "ap_hi": 100, "ap_lo": 60, "cholesterol": 1, "gluc": 1, "smoke": 0, "alco": 0, "active": 0, "cardio": 0},
        {"id": 5, "age": 21914, "sex": 1, "height": 151, "weight": 67.0, "ap_hi": 120, "ap_lo": 80, "cholesterol": 2, "gluc": 2, "smoke": 0, "alco": 0, "active": 0, "cardio": 0},
        {"id": 6, "age": 22113, "sex": 1, "height": 157, "weight": 93.0, "ap_hi": 130, "ap_lo": 80, "cholesterol": 3, "gluc": 1, "smoke": 0, "alco": 0, "active": 1, "cardio": 0},
        {"id": 7, "age": 22584, "sex": 2, "height": 178, "weight": 95.0, "ap_hi": 130, "ap_lo": 90, "cholesterol": 3, "gluc": 3, "smoke": 0, "alco": 0, "active": 1, "cardio": 1}
    ]

    cleaned_data = []

    for r in sample_records:
        # Rule 1: Diastolic pressure cannot be higher than systolic
        if r["ap_lo"] > r["ap_hi"]:
            continue

        # Rule 2: Add 'overweight' column: BMI = weight / (height/100)^2. If > 25 then 1, else 0
        bmi = r["weight"] / ((r["height"] / 100) ** 2)
        r["overweight"] = 1 if bmi > 25 else 0

        # Rule 3: Normalize cholesterol and glucose: 1 (normal) -> 0; >1 (above normal) -> 1
        r["cholesterol"] = 0 if r["cholesterol"] == 1 else 1
        r["gluc"] = 0 if r["gluc"] == 1 else 1

        cleaned_data.append(r)

    # Categorical breakdown by cardiovascular disease outcome
    categories = ["cholesterol", "gluc", "smoke", "alco", "active", "overweight"]
    summary = {0: {c: {"0": 0, "1": 0} for c in categories}, 1: {c: {"0": 0, "1": 0} for c in categories}}

    for r in cleaned_data:
        c_state = r["cardio"]
        for cat in categories:
            val_str = str(r[cat])
            summary[c_state][cat][val_str] += 1

    print("=== Medical Data Visualizer Analysis ===")
    print(f"Total Valid Patients: {len(cleaned_data)}")
    print("\nFeature Counts grouped by Cardio State (0 = Healthy, 1 = Cardiovascular Disease):")
    for cardio_status, cats in summary.items():
        label = "Healthy (cardio=0)" if cardio_status == 0 else "Patient with Disease (cardio=1)"
        print(f"\n--- {label} ---")
        for feature, counts in cats.items():
            print(f"  {feature:12}: Value 0 = {counts['0']}, Value 1 = {counts['1']}")

    return cleaned_data, summary

if __name__ == "__main__":
    process_medical_data()
