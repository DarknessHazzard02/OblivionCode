// Made by: Hazzard
/**
 * Mocha + Chai Testing Boilerplate - freeCodeCamp Quality Assurance
 *
 * Concepts: Unit testing, test suites (describe), test cases (it),
 *           assertions (assert/expect/should), TDD workflow,
 *           async testing, before/after hooks, spies/stubs (Sinon)
 *
 * In production: npm install mocha chai sinon --save-dev
 * Run: npm test  (which runs: mocha ./tests)
 *
 * This file is a standalone simulation demonstrating the patterns.
 */

console.log("=== Mocha + Chai Testing Boilerplate Demo ===\n");

// ─── Chai assertion styles ────────────────────────────────────────────────────
// Style 1: assert (TDD style)
// Style 2: expect (BDD style — most common)
// Style 3: should (BDD style — extends prototype)

// ─── Mini test runner simulation ─────────────────────────────────────────────
let passed = 0, failed = 0, total = 0;

function describe(suiteName, fn) {
  console.log(`\n  📦 ${suiteName}`);
  fn();
}

function it(testName, fn) {
  total++;
  try {
    fn();
    console.log(`    ✅ ${testName}`);
    passed++;
  } catch (err) {
    console.log(`    ❌ ${testName}`);
    console.log(`       → ${err.message}`);
    failed++;
  }
}

function assert(condition, message = "Assertion failed") {
  if (!condition) throw new Error(message);
}

const expect = (actual) => ({
  to: {
    equal: (expected) => {
      if (actual !== expected)
        throw new Error(`Expected ${JSON.stringify(actual)} to equal ${JSON.stringify(expected)}`);
    },
    deepEqual: (expected) => {
      if (JSON.stringify(actual) !== JSON.stringify(expected))
        throw new Error(`Expected ${JSON.stringify(actual)} to deep equal ${JSON.stringify(expected)}`);
    },
    be: {
      true:  () => { if (actual !== true)  throw new Error(`Expected true, got ${actual}`); },
      false: () => { if (actual !== false) throw new Error(`Expected false, got ${actual}`); },
      a: (type) => {
        if (typeof actual !== type)
          throw new Error(`Expected type ${type}, got ${typeof actual}`);
      },
      null:      () => { if (actual !== null) throw new Error(`Expected null, got ${actual}`); },
      undefined: () => { if (actual !== undefined) throw new Error(`Expected undefined`); },
    },
    include: (val) => {
      if (!actual.includes(val))
        throw new Error(`Expected ${JSON.stringify(actual)} to include ${JSON.stringify(val)}`);
    },
    throw: (fn_or_msg) => {
      try { actual(); throw new Error("Function did not throw"); }
      catch (e) {
        if (e.message === "Function did not throw") throw e;
      }
    },
    have: {
      lengthOf: (n) => {
        if (actual.length !== n)
          throw new Error(`Expected length ${n}, got ${actual.length}`);
      },
      property: (prop) => {
        if (!(prop in actual))
          throw new Error(`Expected object to have property '${prop}'`);
      },
    },
    be_above: (n) => { if (actual <= n) throw new Error(`Expected ${actual} > ${n}`); },
    be_below: (n) => { if (actual >= n) throw new Error(`Expected ${actual} < ${n}`); },
  },
  not: {
    to: {
      equal: (expected) => {
        if (actual === expected)
          throw new Error(`Expected NOT to equal ${JSON.stringify(expected)}`);
      },
    },
  },
});

// ─── Functions to test ────────────────────────────────────────────────────────
function add(a, b) {
  if (typeof a !== "number" || typeof b !== "number") throw new TypeError("Both args must be numbers");
  return a + b;
}

function isPalindrome(str) {
  const clean = str.toLowerCase().replace(/[^a-z0-9]/g, "");
  return clean === clean.split("").reverse().join("");
}

function chunk(arr, size) {
  if (size <= 0) throw new RangeError("Chunk size must be > 0");
  const result = [];
  for (let i = 0; i < arr.length; i += size) result.push(arr.slice(i, i + size));
  return result;
}

async function fetchUser(id) {
  const users = { 1: { id: 1, name: "Alice" }, 2: { id: 2, name: "Bob" } };
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const user = users[id];
      user ? resolve(user) : reject(new Error("User not found"));
    }, 10);
  });
}

// ─── Test Suites ──────────────────────────────────────────────────────────────
describe("add()", () => {
  it("adds two positive numbers", () => {
    expect(add(2, 3)).to.equal(5);
  });
  it("adds negative numbers", () => {
    expect(add(-1, -2)).to.equal(-3);
  });
  it("returns 0 for 0 + 0", () => {
    expect(add(0, 0)).to.equal(0);
  });
  it("throws TypeError for non-numbers", () => {
    expect(() => add("a", 1)).to.throw();
  });
});

describe("isPalindrome()", () => {
  it("detects 'racecar'", () => { expect(isPalindrome("racecar")).to.be.true(); });
  it("detects 'A man, a plan, a canal: Panama'", () => {
    expect(isPalindrome("A man, a plan, a canal: Panama")).to.be.true();
  });
  it("rejects 'hello'", () => { expect(isPalindrome("hello")).to.be.false(); });
  it("handles single char", () => { expect(isPalindrome("x")).to.be.true(); });
});

describe("chunk()", () => {
  it("chunks [1,2,3,4,5] by 2 → [[1,2],[3,4],[5]]", () => {
    expect(chunk([1,2,3,4,5], 2)).to.deepEqual([[1,2],[3,4],[5]]);
  });
  it("returns single chunk when size >= length", () => {
    expect(chunk([1,2,3], 10)).to.deepEqual([[1,2,3]]);
  });
  it("throws for size 0", () => { expect(() => chunk([], 0)).to.throw(); });
  it("returns [] for empty input", () => { expect(chunk([], 2)).to.have.lengthOf(0); });
});

// ─── Summary ──────────────────────────────────────────────────────────────────
console.log(`\n  ${"─".repeat(40)}`);
console.log(`  Results: ${passed}/${total} passed, ${failed} failed`);
if (failed === 0) console.log("  🎉 All tests passed!\n");

// ─── Async test pattern (Mocha supports async/await natively) ─────────────────
console.log("Async test example (would run in real Mocha):");
console.log(`
  it('fetches user by ID', async () => {
    const user = await fetchUser(1);
    expect(user).to.deep.equal({ id: 1, name: 'Alice' });
  });

  it('rejects unknown user', async () => {
    try {
      await fetchUser(99);
      throw new Error('Should have thrown');
    } catch (err) {
      expect(err.message).to.equal('User not found');
    }
  });
`);
