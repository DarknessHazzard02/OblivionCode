# ==============================================================================
# Author: Haz
# FreeCodeCamp Machine Learning with Python - Linear Regression Health Costs
# Predicts insurance `expenses` from age, sex, bmi, children, smoker and
# region. The original uses TensorFlow/Keras; this version solves the same
# multiple linear regression with gradient descent in pure Python so it runs
# anywhere. Goal from the challenge: Mean Absolute Error under 3,500.
# Data below is synthetic (generated with a fixed seed), not the course CSV.
# ==============================================================================

import random

# ==============================================================================
# Synthetic dataset
# ==============================================================================
REGIONS = ["northeast", "northwest", "southeast", "southwest"]


def make_dataset(n=1338, seed=7):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        age = rng.randint(18, 64)
        sex = rng.choice(["male", "female"])
        bmi = round(rng.gauss(30.6, 6.0), 1)
        children = rng.choice([0, 0, 1, 1, 2, 3, 4])
        smoker = "yes" if rng.random() < 0.2 else "no"
        region = rng.choice(REGIONS)
        expenses = (250 * age + 330 * bmi + 475 * children
                    + (23800 if smoker == "yes" else 0) - 12000
                    + rng.gauss(0, 1500))
        rows.append({"age": age, "sex": sex, "bmi": bmi, "children": children,
                     "smoker": smoker, "region": region,
                     "expenses": max(1100.0, round(expenses, 2))})
    return rows


# ==============================================================================
# Feature engineering: categorical -> numeric, then standardise
# ==============================================================================
def encode(row):
    features = [row["age"], row["bmi"], row["children"],
                1.0 if row["sex"] == "male" else 0.0,
                1.0 if row["smoker"] == "yes" else 0.0]
    features += [1.0 if row["region"] == r else 0.0 for r in REGIONS[1:]]
    return features


def standardise(matrix):
    cols = list(zip(*matrix))
    means = [sum(c) / len(c) for c in cols]
    stds = [(sum((x - m) ** 2 for x in c) / len(c)) ** 0.5 or 1.0
            for c, m in zip(cols, means)]
    scaled = [[(x - m) / s for x, m, s in zip(r, means, stds)] for r in matrix]
    return scaled, means, stds


# ==============================================================================
# Model: y = w.x + b, trained with batch gradient descent on MSE
# ==============================================================================
def train(X, y, epochs=600, lr=0.05):
    w = [0.0] * len(X[0])
    b = 0.0
    n = len(X)
    for _ in range(epochs):
        grad_w = [0.0] * len(w)
        grad_b = 0.0
        for xi, yi in zip(X, y):
            err = sum(wj * xj for wj, xj in zip(w, xi)) + b - yi
            for j, xj in enumerate(xi):
                grad_w[j] += err * xj
            grad_b += err
        w = [wj - lr * g / n for wj, g in zip(w, grad_w)]
        b -= lr * grad_b / n
    return w, b


def predict(w, b, X):
    return [sum(wj * xj for wj, xj in zip(w, xi)) + b for xi in X]


if __name__ == "__main__":
    data = make_dataset()
    random.Random(1).shuffle(data)
    split = int(len(data) * 0.8)
    train_rows, test_rows = data[:split], data[split:]

    X_train, means, stds = standardise([encode(r) for r in train_rows])
    X_test = [[(x - m) / s for x, m, s in zip(encode(r), means, stds)]
              for r in test_rows]
    y_train = [r["expenses"] for r in train_rows]
    y_test = [r["expenses"] for r in test_rows]

    w, b = train(X_train, y_train)
    preds = predict(w, b, X_test)
    mae = sum(abs(p - t) for p, t in zip(preds, y_test)) / len(y_test)

    print(f"Testing set Mean Abs Error: {mae:,.2f} expenses")
    print("PASS: MAE < 3500" if mae < 3500 else "FAIL: MAE >= 3500")
