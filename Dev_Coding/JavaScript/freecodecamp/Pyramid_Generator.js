// Made by: Hazzard
// FreeCodeCamp - Pyramid Generator
// Teaches: Arrays, Loops (for, for...of), Functions, String manipulation

function padRow(rowNumber, rowCount, character) {
  return " ".repeat(rowCount - rowNumber) + character.repeat(2 * rowNumber - 1) + " ".repeat(rowCount - rowNumber);
}

function generatePyramid(character = "#", count = 8, inverted = false) {
  const rows = [];

  for (let i = 1; i <= count; i++) {
    if (inverted) {
      rows.unshift(padRow(i, count, character));
    } else {
      rows.push(padRow(i, count, character));
    }
  }

  let result = "";
  for (const row of rows) {
    result = result + row + "\n";
  }

  return result;
}

console.log("=== Standard Pyramid ===");
console.log(generatePyramid("o", 8, false));

console.log("=== Inverted Pyramid ===");
console.log(generatePyramid("*", 6, true));
