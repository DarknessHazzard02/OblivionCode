// FreeCodeCamp Certification Project - Telephone Number Validator
// Return true if the passed string looks like a valid US phone number.

function telephoneCheck(str) {
  // Regex explanation:
  // ^(1\s?)?               -> Optional country code 1, optionally followed by space
  // (\(\d{3}\)|\d{3})      -> Area code: either (555) or 555
  // [\s\-]?                -> Optional separator space or hyphen
  // \d{3}                  -> 3 digits
  // [\s\-]?                -> Optional separator space or hyphen
  // \d{4}$                 -> 4 digits at the end
  const regex = /^(1\s?)?(\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{4}$/;
  return regex.test(str);
}

// Test cases from freeCodeCamp
const testPhones = [
  { phone: "555-555-5555", expected: true },
  { phone: "1 555-555-5555", expected: true },
  { phone: "1 (555) 555-5555", expected: true },
  { phone: "5555555555", expected: true },
  { phone: "555-555-5556", expected: true },
  { phone: "(555)555-5555", expected: true },
  { phone: "1(555)555-5555", expected: true },
  { phone: "555-5555", expected: false },
  { phone: "5555555", expected: false },
  { phone: "1 555)555-5555", expected: false },
  { phone: "123**&!!asdf#", expected: false },
  { phone: "55555555", expected: false },
  { phone: "(6054756961)", expected: false },
  { phone: "2 (757) 622-7382", expected: false },
  { phone: "0 (757) 622-7382", expected: false },
  { phone: "-1 (757) 622-7382", expected: false },
  { phone: "2 757 622-7382", expected: false }
];

console.log("=== Telephone Number Validator Tests ===");
testPhones.forEach(({ phone, expected }) => {
  const result = telephoneCheck(phone);
  const status = result === expected ? "PASS" : "FAIL";
  console.log(`[${status}] "${phone}" -> ${result} (expected: ${expected})`);
});
