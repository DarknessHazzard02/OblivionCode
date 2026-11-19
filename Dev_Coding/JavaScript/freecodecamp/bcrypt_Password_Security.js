// Made by: Hazzard
/**
 * bcrypt Password Security Boilerplate - freeCodeCamp Information Security
 *
 * Concepts: Password hashing vs encryption, salting, work factor (cost),
 *           bcrypt algorithm, timing-safe comparison, common attacks
 *
 * In production: npm install bcrypt  (or bcryptjs for pure-JS)
 * This file simulates bcrypt patterns using Node.js crypto module.
 */

const crypto = require("crypto");

console.log("=== bcrypt Password Security Boilerplate Demo ===\n");

// ─── Why bcrypt? ─────────────────────────────────────────────────────────────
console.log("1) Why bcrypt over MD5/SHA256?\n");
const reasons = [
  "MD5/SHA256 are fast — attackers can test billions of guesses/second",
  "bcrypt is intentionally slow (cost factor controls iterations)",
  "bcrypt automatically generates a random salt (prevents rainbow tables)",
  "bcrypt hashes include the salt, algorithm, and cost in the output",
  "Cost factor can be increased as hardware gets faster",
];
reasons.forEach((r, i) => console.log(`   ${i + 1}. ${r}`));

// ─── Simulated bcrypt (using PBKDF2 as an analogy) ────────────────────────────
// Real bcrypt: bcrypt.hash(password, saltRounds)  → returns hash string
// Real verify: bcrypt.compare(plaintext, hash)    → returns boolean

const COST = 12; // saltRounds — 2^12 iterations; real production default is 10-12

function simulateHash(password, saltRounds = COST) {
  const salt = crypto.randomBytes(16).toString("hex");
  const iterations = Math.pow(2, saltRounds);
  // PBKDF2 approximation (real bcrypt uses Blowfish cipher internally)
  const hash = crypto.pbkdf2Sync(password, salt, iterations, 32, "sha256").toString("hex");
  // Real bcrypt output format: $2b$12$<22-char salt><31-char hash>
  return `$sim$${saltRounds}$${salt}$${hash}`;
}

function simulateCompare(password, storedHash) {
  const parts = storedHash.split("$");
  if (parts.length < 5 || parts[1] !== "sim") return false;
  const saltRounds = parseInt(parts[2]);
  const salt = parts[3];
  const originalHash = parts[4];
  const iterations = Math.pow(2, saltRounds);
  const candidateHash = crypto.pbkdf2Sync(password, salt, iterations, 32, "sha256").toString("hex");
  // Timing-safe comparison (prevents timing attacks)
  return crypto.timingSafeEqual(Buffer.from(originalHash), Buffer.from(candidateHash));
}

// ─── Demo: hashing & verifying ───────────────────────────────────────────────
console.log("\n2) Hashing a password:\n");
const password = "MySecureP@ssword123";
console.log(`   Password:   "${password}"`);

console.time("   Hash time");
const hash1 = simulateHash(password, 10); // lower cost for demo speed
console.timeEnd("   Hash time");
console.log(`   Hash:       ${hash1}`);
console.log(`   Hash length: ${hash1.length} chars\n`);

console.log("3) Same password → different hashes (different salts):");
const hash2 = simulateHash(password, 10);
console.log(`   Hash A: ${hash1.slice(0, 60)}...`);
console.log(`   Hash B: ${hash2.slice(0, 60)}...`);
console.log(`   Are they the same? ${hash1 === hash2}\n`);

console.log("4) Verification:");
console.log(`   Correct password: ${simulateCompare(password, hash1)}`);
console.log(`   Wrong password:   ${simulateCompare("wrongpassword", hash1)}`);
console.log(`   Empty password:   ${simulateCompare("", hash1)}\n`);

// ─── Real bcrypt patterns ─────────────────────────────────────────────────────
console.log("5) Real bcrypt code patterns:\n");
const bcryptPatterns = `
const bcrypt = require('bcrypt');

// HASH (async — preferred)
const saltRounds = 12;
const hashedPassword = await bcrypt.hash(plainTextPassword, saltRounds);

// HASH (sync — only for scripts, blocks event loop)
const hashedPassword = bcrypt.hashSync(plainTextPassword, saltRounds);

// VERIFY (async)
const isMatch = await bcrypt.compare(plainTextPassword, hashedPassword);

// VERIFY (sync)
const isMatch = bcrypt.compareSync(plainTextPassword, hashedPassword);

// Cost factor benchmark (run once to pick your saltRounds):
// 10 rounds  → ~65ms  (minimum for production)
// 12 rounds  → ~250ms (recommended)
// 14 rounds  → ~1000ms (high security)
`;
console.log(bcryptPatterns);

// ─── Common attacks bcrypt prevents ──────────────────────────────────────────
console.log("6) Security protections:\n");
const protections = [
  { attack: "Rainbow Table",   protection: "Unique salt per hash — tables are useless" },
  { attack: "Brute Force",     protection: "High cost factor slows attackers drastically" },
  { attack: "Timing Attack",   protection: "timingSafeEqual / bcrypt.compare always takes same time" },
  { attack: "Database Breach", protection: "Hashed passwords useless without cracking each one" },
  { attack: "Credential Reuse", protection: "Each site's hash is unique — not reusable elsewhere" },
];
protections.forEach(({ attack, protection }) => {
  console.log(`   ${attack.padEnd(20)} → ${protection}`);
});

console.log("\n7) ⚠️  Anti-patterns to NEVER do:");
const antiPatterns = [
  'store plaintext passwords',
  'use MD5 or SHA256 without salt',
  'use a static/shared salt',
  'return password hash in API responses',
  'log passwords in console/files',
  'use bcryptjs in a sync loop for many users',
];
antiPatterns.forEach((ap) => console.log(`   ❌ ${ap}`));
