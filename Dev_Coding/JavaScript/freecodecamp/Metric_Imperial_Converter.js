// Made by: Hazzard
// FreeCodeCamp Quality Assurance - Metric-Imperial Converter
// Converts units between Gallons <-> Liters, Miles <-> Kilometers, Pounds <-> Kilograms

const validUnits = ["gal", "l", "mi", "km", "lbs", "kg"];

const unitMap = {
  gal: { target: "L", spell: "gallons", targetSpell: "liters", factor: 3.78541 },
  l:   { target: "gal", spell: "liters", targetSpell: "gallons", factor: 1 / 3.78541 },
  lbs: { target: "kg", spell: "pounds", targetSpell: "kilograms", factor: 0.453592 },
  kg:  { target: "lbs", spell: "kilograms", targetSpell: "pounds", factor: 1 / 0.453592 },
  mi:  { target: "km", spell: "miles", targetSpell: "kilometers", factor: 1.60934 },
  km:  { target: "mi", spell: "kilometers", targetSpell: "miles", factor: 1 / 1.60934 }
};

function parseNum(input) {
  const match = input.match(/[a-zA-Z]/);
  if (!match) return null;
  const numStr = input.slice(0, match.index).trim();
  if (numStr === "") return 1;

  if (numStr.includes("/")) {
    const parts = numStr.split("/");
    if (parts.length > 2) return "invalid number";
    return parseFloat(parts[0]) / parseFloat(parts[1]);
  }

  const val = parseFloat(numStr);
  return isNaN(val) ? "invalid number" : val;
}

function parseUnit(input) {
  const match = input.match(/[a-zA-Z]+$/);
  if (!match) return "invalid unit";
  const unit = match[0].toLowerCase();
  return validUnits.includes(unit) ? (unit === "l" ? "L" : unit) : "invalid unit";
}

function convert(input) {
  const initNum = parseNum(input);
  const rawUnit = parseUnit(input);

  const isNumInvalid = initNum === "invalid number" || initNum === null;
  const isUnitInvalid = rawUnit === "invalid unit";

  if (isNumInvalid && isUnitInvalid) return { error: "invalid number and unit" };
  if (isNumInvalid) return { error: "invalid number" };
  if (isUnitInvalid) return { error: "invalid unit" };

  const unitKey = rawUnit.toLowerCase();
  const info = unitMap[unitKey];
  const returnNum = Math.round(initNum * info.factor * 100000) / 100000;
  const returnUnit = info.target;

  return {
    initNum,
    initUnit: rawUnit,
    returnNum,
    returnUnit,
    string: `${initNum} ${info.spell} converts to ${returnNum} ${info.targetSpell}`
  };
}

// Tests
console.log("=== Metric-Imperial Converter Tests ===");
["3.1mi", "4gal", "1/2km", "5.4/3lbs", "1L", "32g", "3/7.2/4kg"].forEach((test) => {
  console.log(`\nInput: "${test}"`);
  console.log(convert(test));
});
