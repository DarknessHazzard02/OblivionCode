// Made by: Hazzard
// FreeCodeCamp Certification Project - Roman Numeral Converter
// Convert the given number into a roman numeral.

function convertToRoman(num) {
  const romanLookup = [
    { value: 1000, symbol: "M" },
    { value: 900,  symbol: "CM" },
    { value: 500,  symbol: "D" },
    { value: 400,  symbol: "CD" },
    { value: 100,  symbol: "C" },
    { value: 90,   symbol: "XC" },
    { value: 50,   symbol: "L" },
    { value: 40,   symbol: "XL" },
    { value: 10,   symbol: "X" },
    { value: 9,    symbol: "IX" },
    { value: 5,    symbol: "V" },
    { value: 4,    symbol: "IV" },
    { value: 1,    symbol: "I" }
  ];

  let romanNumeral = "";
  let remaining = num;

  for (const entry of romanLookup) {
    while (remaining >= entry.value) {
      romanNumeral += entry.symbol;
      remaining -= entry.value;
    }
  }

  return romanNumeral;
}

// Test cases from freeCodeCamp
const testNumbers = [2, 3, 4, 5, 9, 12, 16, 29, 44, 68, 83, 97, 99, 400, 500, 501, 649, 798, 891, 1000, 1004, 1006, 1023, 2014, 3999];

console.log("=== Roman Numeral Converter Tests ===");
testNumbers.forEach((n) => {
  console.log(`${n} => ${convertToRoman(n)}`);
});
