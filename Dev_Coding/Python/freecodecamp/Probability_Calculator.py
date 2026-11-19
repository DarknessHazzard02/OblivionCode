# Author: Haz
# FreeCodeCamp Scientific Computing with Python - Probability Calculator
# Simulates drawing balls at random from a hat to estimate probability of specific outcomes using Monte Carlo experiment

import copy
import random

class Hat:
    def __init__(self, **balls):
        self.contents = []
        for color, count in balls.items():
            self.contents.extend([color] * count)

    def draw(self, count):
        if count >= len(self.contents):
            drawn = self.contents.copy()
            self.contents.clear()
            return drawn

        drawn = []
        for _ in range(count):
            idx = random.randrange(len(self.contents))
            drawn.append(self.contents.pop(idx))
        return drawn


def experiment(hat, expected_balls, num_balls_drawn, num_experiments):
    success_count = 0

    for _ in range(num_experiments):
        hat_copy = copy.deepcopy(hat)
        drawn = hat_copy.draw(num_balls_drawn)

        # Count drawn balls
        drawn_counts = {}
        for ball in drawn:
            drawn_counts[ball] = drawn_counts.get(ball, 0) + 1

        # Check if expected balls condition is met
        success = True
        for color, req_count in expected_balls.items():
            if drawn_counts.get(color, 0) < req_count:
                success = False
                break

        if success:
            success_count += 1

    return success_count / num_experiments


# Demo
random.seed(42)
test_hat = Hat(blue=4, red=2, green=6)
prob = experiment(
    hat=test_hat,
    expected_balls={"blue": 2, "red": 1},
    num_balls_drawn=4,
    num_experiments=3000
)

print("=== Probability Calculator Experiment ===")
print("Hat Contents: 4 blue, 2 red, 6 green")
print("Expected: At least 2 blue and 1 red when drawing 4 balls")
print(f"Calculated Probability (over 3000 trials): {prob:.4f}")
