// Made by: Hazzard
// Utility - Array Deduplicator
// Demonstrates unique values extraction using Set and Array filtering

function removeDuplicates(arr) {
  return [...new Set(arr)];
}

function removeDuplicatesByKey(arr, key) {
  const seen = new Set();
  return arr.filter((item) => {
    const val = item[key];
    if (seen.has(val)) {
      return false;
    }
    seen.add(val);
    return true;
  });
}

// Tests
const numbers = [1, 2, 2, 3, 4, 4, 4, 5, 1, 6];
console.log("Original numbers:", numbers);
console.log("Deduplicated:    ", removeDuplicates(numbers));

const users = [
  { id: 1, name: "Alice" },
  { id: 2, name: "Bob" },
  { id: 1, name: "Alice (Duplicate)" },
  { id: 3, name: "Charlie" }
];
console.log("\nOriginal users:", users);
console.log("Deduplicated by id:", removeDuplicatesByKey(users, "id"));
