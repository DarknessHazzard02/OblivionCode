// FreeCodeCamp - Calorie Counter
// Teaches: Regular Expressions, String Parsing, Arithmetic Validation

function cleanInputString(str) {
  const regex = /[+-\s]/g;
  return str.replace(regex, "");
}

function isInvalidInput(str) {
  const regex = /\d+e\d+/i;
  return str.match(regex);
}

function calculateCalories(budget, meals) {
  // meals is an object with breakfast, lunch, dinner, snacks, exercise arrays of calorie values
  let totalMealCalories = 0;

  for (const mealCategory of ["breakfast", "lunch", "dinner", "snacks"]) {
    if (meals[mealCategory]) {
      for (const item of meals[mealCategory]) {
        const cleaned = cleanInputString(String(item));
        if (isInvalidInput(cleaned)) {
          return { error: `Invalid number format detected in ${mealCategory}: ${item}` };
        }
        totalMealCalories += Number(cleaned);
      }
    }
  }

  let totalExerciseCalories = 0;
  if (meals.exercise) {
    for (const item of meals.exercise) {
      const cleaned = cleanInputString(String(item));
      totalExerciseCalories += Number(cleaned);
    }
  }

  const remainingCalories = budget - totalMealCalories + totalExerciseCalories;
  const surplusOrDeficit = remainingCalories < 0 ? "Surplus" : "Deficit";

  return {
    budget,
    consumed: totalMealCalories,
    burned: totalExerciseCalories,
    remaining: Math.abs(remainingCalories),
    status: surplusOrDeficit
  };
}

// Test Run
const dayLog = {
  breakfast: [" 350 ", "120"],
  lunch: ["650"],
  dinner: ["800", "150"],
  snacks: ["200"],
  exercise: ["400"]
};

const result = calculateCalories(2000, dayLog);
console.log("=== Daily Calorie Summary ===");
console.log(`Budget:    ${result.budget} kcal`);
console.log(`Consumed:  ${result.consumed} kcal`);
console.log(`Burned:    ${result.burned} kcal`);
console.log(`Result:    ${result.remaining} kcal ${result.status}`);
