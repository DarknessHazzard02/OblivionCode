/**
 * Node.js / npm Boilerplate Concepts - freeCodeCamp Back End APIs
 *
 * Concepts: package.json anatomy, npm scripts, semantic versioning,
 *           require/module.exports, CommonJS vs ES Modules,
 *           environment variables, .npmrc, .nvmrc
 *
 * This file documents and demonstrates core npm/Node.js concepts
 * that form the foundation of all Back End projects.
 */

// ─── Environment Variables ────────────────────────────────────────────────────
// In a real project: require('dotenv').config();
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || "development";

console.log("=== Node.js / npm Boilerplate Concepts ===\n");

// ─── 1. package.json anatomy ─────────────────────────────────────────────────
const packageJsonExample = {
  name: "my-fcc-project",
  version: "1.0.0",
  description: "A freeCodeCamp Back End project",
  main: "server.js",
  scripts: {
    start:   "node server.js",
    dev:     "nodemon server.js",
    test:    "mocha ./tests",
    lint:    "eslint .",
  },
  dependencies: {
    express:  "^4.18.2",
    dotenv:   "^16.0.3",
    mongoose: "^7.0.0",
    cors:     "^2.8.5",
  },
  devDependencies: {
    nodemon: "^3.0.0",
    mocha:   "^10.0.0",
    chai:    "^4.3.7",
  },
  engines: { node: ">=18.0.0" },
  license: "MIT",
};

console.log("1) package.json structure:");
console.log("  ", JSON.stringify(packageJsonExample, null, 2));

// ─── 2. Semantic Versioning ───────────────────────────────────────────────────
console.log("\n2) Semantic Versioning (SemVer):");
const semverExamples = [
  { version: "^4.18.2", meaning: "Compatible with 4.x.x — MINOR & PATCH updates OK" },
  { version: "~4.18.2", meaning: "Approximately 4.18.x — PATCH updates only" },
  { version: "4.18.2",  meaning: "Exact version — no updates" },
  { version: "*",       meaning: "Any version (dangerous in production!)" },
];
semverExamples.forEach(({ version, meaning }) => {
  console.log(`   ${version.padEnd(10)} → ${meaning}`);
});

// ─── 3. CommonJS module system ────────────────────────────────────────────────
console.log("\n3) CommonJS module patterns:");
const modulePatterns = `
  // Export a single function
  module.exports = function greet(name) { return 'Hello, ' + name; };

  // Export an object with multiple methods
  module.exports = { add, subtract, multiply };

  // Named exports (destructured import)
  const { add, subtract } = require('./math');

  // Default import
  const greet = require('./greet');
`;
console.log(modulePatterns);

// ─── 4. Environment variable patterns ────────────────────────────────────────
console.log("4) Environment variable best practices:");
console.log(`   Current PORT    : ${PORT}`);
console.log(`   Current NODE_ENV: ${NODE_ENV}`);
console.log("   .env file (never commit to git!):");
console.log("     PORT=3000");
console.log("     MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/db");
console.log("     SESSION_SECRET=your_long_random_secret_here");

// ─── 5. Minimal Express server template ───────────────────────────────────────
console.log("\n5) Minimal Express server template:");
const serverTemplate = `
const express = require('express');
const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/', (req, res) => res.json({ message: 'API is running' }));

// 404 handler
app.use((req, res) => res.status(404).json({ error: 'Not found' }));

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal server error' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(\`Server running on port \${PORT}\`));
module.exports = app; // for testing
`;
console.log(serverTemplate);

// ─── 6. npm scripts cheat-sheet ───────────────────────────────────────────────
console.log("6) Common npm commands:");
const commands = [
  ["npm init -y",          "Create package.json with defaults"],
  ["npm install <pkg>",    "Install & save to dependencies"],
  ["npm install -D <pkg>", "Install & save to devDependencies"],
  ["npm run dev",          "Run the 'dev' script"],
  ["npm test",             "Run the 'test' script"],
  ["npm audit",            "Check for security vulnerabilities"],
  ["npm outdated",         "List outdated packages"],
  ["npm update",           "Update packages within SemVer ranges"],
  ["npx <pkg>",            "Run a package without installing globally"],
];
commands.forEach(([cmd, desc]) => {
  console.log(`   ${cmd.padEnd(28)} → ${desc}`);
});
