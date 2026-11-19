// Made by: Hazzard
// FreeCodeCamp Certification Project - Palindrome Checker
// Return true if the given string is a palindrome. Otherwise, return false.
// Must ignore all non-alphanumeric characters (punctuation, spaces and symbols) and case.

function palindrome(str) {
  // Strip non-alphanumeric characters and lowercase
  const cleanStr = str.toLowerCase().replace(/[^a-z0-9]/g, "");
  const reversedStr = cleanStr.split("").reverse().join("");
  return cleanStr === reversedStr;
}

// Test cases from freeCodeCamp
const testCases = [
  "eye",
  "_eye",
  "race car",
  "not a palindrome",
  "A man, a plan, a canal. Panama",
  "never odd or even",
  "nope",
  "almostomla",
  "My age is 0, 0 si ega ym.",
  "1 eye for of 1 eye.",
  "0_0 (: /-\\ :) 0-0",
  "five|\\_/|four"
];

console.log("=== Palindrome Checker Tests ===");
testCases.forEach((t) => {
  console.log(`"${t}" -> ${palindrome(t)}`);
});
