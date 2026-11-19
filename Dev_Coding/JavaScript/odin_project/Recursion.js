// Made by: Hazzard
// The Odin Project - Full Stack JavaScript (Computer Science): Recursion.
// fibs (iterative), fibsRec (recursive) and mergeSort. Run: node Recursion.js

const assert = require("node:assert/strict");

// ==============================================================================
// Fibonacci
// ==============================================================================
function fibs(n) {
  const out = [];
  for (let i = 0; i < n; i++) out.push(i < 2 ? i : out[i - 1] + out[i - 2]);
  return out;
}

function fibsRec(n) {
  if (n <= 0) return [];
  if (n === 1) return [0];
  if (n === 2) return [0, 1];
  const prev = fibsRec(n - 1);
  return [...prev, prev[prev.length - 1] + prev[prev.length - 2]];
}

// ==============================================================================
// Merge sort
// ==============================================================================
function merge(left, right) {
  const out = [];
  let i = 0;
  let j = 0;
  while (i < left.length && j < right.length) out.push(left[i] <= right[j] ? left[i++] : right[j++]);
  return out.concat(left.slice(i), right.slice(j));
}

function mergeSort(arr) {
  if (arr.length <= 1) return arr.slice();
  const mid = Math.floor(arr.length / 2);
  return merge(mergeSort(arr.slice(0, mid)), mergeSort(arr.slice(mid)));
}

// ==============================================================================
// Checks
// ==============================================================================
if (require.main === module) {
  assert.deepEqual(fibs(8), [0, 1, 1, 2, 3, 5, 8, 13]);
  assert.deepEqual(fibsRec(8), fibs(8));
  assert.deepEqual(fibsRec(0), []);
  assert.deepEqual(mergeSort([3, 2, 1, 13, 8, 5, 0, 1]), [0, 1, 1, 2, 3, 5, 8, 13]);
  assert.deepEqual(mergeSort([105, 79, 100, 110]), [79, 100, 105, 110]);
  assert.deepEqual(mergeSort([]), []);
  console.log("fibs(8)     ", fibs(8).join(", "));
  console.log("mergeSort   ", mergeSort([3, 2, 1, 13, 8, 5, 0, 1]).join(", "));
  console.log("Recursion: all checks passed.");
}

module.exports = { fibs, fibsRec, mergeSort };
