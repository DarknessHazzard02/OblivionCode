// FreeCodeCamp - Gradebook App
// Teaches: Functions, Arrays, Conditionals, Template Literals

function getAverage(scores) {
  let sum = 0;
  for (const score of scores) {
    sum += score;
  }
  return sum / scores.length;
}

function getGrade(score) {
  if (score === 100) return "A++";
  if (score >= 90) return "A";
  if (score >= 80) return "B";
  if (score >= 70) return "C";
  if (score >= 60) return "D";
  return "F";
}

function hasPassingGrade(score) {
  return getGrade(score) !== "F";
}

function studentMsg(totalScores, studentScore) {
  const average = getAverage(totalScores);
  const grade = getGrade(studentScore);
  const passed = hasPassingGrade(studentScore);

  if (passed) {
    return `Class average: ${average.toFixed(1)}. Your grade: ${grade}. You passed the course.`;
  } else {
    return `Class average: ${average.toFixed(1)}. Your grade: ${grade}. You failed the course.`;
  }
}

// Tests
const classScores = [92, 88, 12, 77, 57, 100, 67, 38, 97, 89];
console.log(studentMsg(classScores, 85));
console.log(studentMsg(classScores, 52));
