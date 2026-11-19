# Author: Haz
# FreeCodeCamp Data Analysis with Python - Mean-Variance-Standard Deviation Calculator
# Calculates mean, variance, standard deviation, max, min, and sum of a 3x3 matrix along both axes and flattened

try:
    import numpy as np
except ImportError:
    np = None

def calculate(list_of_nine):
    if len(list_of_nine) != 9:
        raise ValueError("List must contain nine numbers.")

    if np is not None:
        matrix = np.array(list_of_nine).reshape((3, 3))
        calculations = {
            'mean': [matrix.mean(axis=0).tolist(), matrix.mean(axis=1).tolist(), float(matrix.mean())],
            'variance': [matrix.var(axis=0).tolist(), matrix.var(axis=1).tolist(), float(matrix.var())],
            'standard deviation': [matrix.std(axis=0).tolist(), matrix.std(axis=1).tolist(), float(matrix.std())],
            'max': [matrix.max(axis=0).tolist(), matrix.max(axis=1).tolist(), int(matrix.max())],
            'min': [matrix.min(axis=0).tolist(), matrix.min(axis=1).tolist(), int(matrix.min())],
            'sum': [matrix.sum(axis=0).tolist(), matrix.sum(axis=1).tolist(), int(matrix.sum())]
        }
    else:
        # Pure Python fallback for environments without numpy
        rows = [list_of_nine[0:3], list_of_nine[3:6], list_of_nine[6:9]]
        cols = [[rows[r][c] for r in range(3)] for c in range(3)]
        
        def calc_stats(series):
            m = sum(series) / len(series)
            var = sum((x - m) ** 2 for x in series) / len(series)
            std = var ** 0.5
            return m, var, std, max(series), min(series), sum(series)
        
        col_stats = [calc_stats(c) for c in cols]
        row_stats = [calc_stats(r) for r in rows]
        flat_stats = calc_stats(list_of_nine)

        calculations = {
            'mean': [[s[0] for s in col_stats], [s[0] for s in row_stats], flat_stats[0]],
            'variance': [[s[1] for s in col_stats], [s[1] for s in row_stats], flat_stats[1]],
            'standard deviation': [[s[2] for s in col_stats], [s[2] for s in row_stats], flat_stats[2]],
            'max': [[s[3] for s in col_stats], [s[3] for s in row_stats], flat_stats[3]],
            'min': [[s[4] for s in col_stats], [s[4] for s in row_stats], flat_stats[4]],
            'sum': [[s[5] for s in col_stats], [s[5] for s in row_stats], flat_stats[5]]
        }

    return calculations

# Test Run
sample_input = [0, 1, 2, 3, 4, 5, 6, 7, 8]
print("=== Mean-Variance-Standard Deviation Calculator ===")
print("Input:", sample_input)
result = calculate(sample_input)
for key, val in result.items():
    print(f"{key:20}: {val}")
