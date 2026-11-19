# Author: Haz
# FreeCodeCamp Scientific Computing with Python - Arithmetic Formatter
# Arranges arithmetic problems vertically and side-by-side with optional answer display

def arithmetic_arranger(problems, show_answers=False):
    if len(problems) > 5:
        return "Error: Too many problems."

    first_line = []
    second_line = []
    dashes = []
    answers = []

    for problem in problems:
        parts = problem.split()
        if len(parts) != 3:
            return "Error: Invalid problem format."

        num1, operator, num2 = parts

        if operator not in ["+", "-"]:
            return "Error: Operator must be '+' or '-'."

        if not (num1.isdigit() and num2.isdigit()):
            return "Error: Numbers must only contain digits."

        if len(num1) > 4 or len(num2) > 4:
            return "Error: Numbers cannot be more than four digits."

        width = max(len(num1), len(num2)) + 2

        first_line.append(num1.rjust(width))
        second_line.append(operator + " " + num2.rjust(width - 2))
        dashes.append("-" * width)

        if show_answers:
            ans = str(int(num1) + int(num2)) if operator == "+" else str(int(num1) - int(num2))
            answers.append(ans.rjust(width))

    arranged_problems = (
        "    ".join(first_line) + "\n" +
        "    ".join(second_line) + "\n" +
        "    ".join(dashes)
    )

    if show_answers:
        arranged_problems += "\n" + "    ".join(answers)

    return arranged_problems

# Test Run
sample_problems = ["32 + 698", "3801 - 2", "45 + 43", "123 + 49"]
print("=== Without Answers ===")
print(arithmetic_arranger(sample_problems))
print("\n=== With Answers ===")
print(arithmetic_arranger(sample_problems, True))
