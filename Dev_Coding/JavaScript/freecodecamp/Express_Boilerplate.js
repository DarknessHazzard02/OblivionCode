/**
 * Express.js Boilerplate Concepts - freeCodeCamp Back End APIs
 *
 * Concepts: Express middleware chain, routing, req/res objects,
 *           static files, query/route params, body parsing,
 *           error handling, CORS, response methods
 */

const http = require("http");

// ─── Simulated Express-like mini framework ────────────────────────────────────
// (Real project: const express = require('express'))
class MiniExpress {
  constructor() {
    this.middlewares = [];
    this.routes = { GET: {}, POST: {}, PUT: {}, DELETE: {} };
  }

  use(fn) { this.middlewares.push(fn); }

  get(path, handler)    { this.routes.GET[path] = handler; }
  post(path, handler)   { this.routes.POST[path] = handler; }
  put(path, handler)    { this.routes.PUT[path] = handler; }
  delete(path, handler) { this.routes.DELETE[path] = handler; }

  handle(method, path, body = {}) {
    const req = {
      method, path, body,
      query: Object.fromEntries(
        path.includes("?")
          ? new URLSearchParams(path.split("?")[1]).entries()
          : []
      ),
      params: {},
    };
    const cleanPath = path.split("?")[0];
    const res = {
      _status: 200,
      status(code) { this._status = code; return this; },
      json(data) { return { status: this._status, data }; },
      send(text) { return { status: this._status, data: text }; },
    };

    // Run middleware
    for (const mw of this.middlewares) mw(req, res, () => {});

    // Find route
    const handler = this.routes[method]?.[cleanPath];
    if (!handler) return res.status(404).json({ error: "Not found" });
    return handler(req, res);
  }
}

const app = new MiniExpress();

// ─── Middleware examples ───────────────────────────────────────────────────────
// Logger middleware
app.use((req, res, next) => {
  console.log(`   [LOG] ${req.method} ${req.path}`);
  next();
});

// CORS middleware (in real Express: app.use(cors()))
app.use((req, res, next) => {
  // res.setHeader('Access-Control-Allow-Origin', '*');
  next();
});

// ─── Routes ───────────────────────────────────────────────────────────────────
app.get("/", (req, res) => res.json({ message: "Welcome to Express boilerplate!" }));

app.get("/api/users", (req, res) => {
  const users = [
    { id: 1, name: "Alice" },
    { id: 2, name: "Bob" },
  ];
  // ?limit query param
  const limit = parseInt(req.query.limit) || users.length;
  return res.json(users.slice(0, limit));
});

app.get("/api/users/:id", (req, res) => {
  const users = { "1": { id: 1, name: "Alice" }, "2": { id: 2, name: "Bob" } };
  // Route params from path (simulated)
  const id = req.path.split("/").pop();
  const user = users[id];
  if (!user) return res.status(404).json({ error: "User not found" });
  return res.json(user);
});

app.post("/api/users", (req, res) => {
  const { name } = req.body;
  if (!name) return res.status(400).json({ error: "Name required" });
  return res.status(201).json({ id: 3, name });
});

app.put("/api/users/:id", (req, res) => {
  const { name } = req.body;
  return res.json({ id: req.path.split("/").pop(), name, updated: true });
});

app.delete("/api/users/:id", (req, res) => {
  return res.json({ deleted: true, id: req.path.split("/").pop() });
});

// ─── Demo ─────────────────────────────────────────────────────────────────────
console.log("=== Express.js Boilerplate Concepts Demo ===\n");

console.log("1) GET /");
console.log("  ", app.handle("GET", "/"));

console.log("\n2) GET /api/users");
console.log("  ", app.handle("GET", "/api/users"));

console.log("\n3) GET /api/users?limit=1");
console.log("  ", app.handle("GET", "/api/users?limit=1"));

console.log("\n4) GET /api/users/2");
console.log("  ", app.handle("GET", "/api/users/2"));

console.log("\n5) POST /api/users");
console.log("  ", app.handle("POST", "/api/users", { name: "Charlie" }));

console.log("\n6) POST with missing body:");
console.log("  ", app.handle("POST", "/api/users", {}));

console.log("\n7) Unknown route:");
console.log("  ", app.handle("GET", "/unknown"));

// ─── Express concept cheat sheet ─────────────────────────────────────────────
console.log("\n8) Key Express concepts:");
const concepts = [
  ["app.use(fn)",             "Mount middleware for all routes"],
  ["app.use('/path', fn)",    "Mount middleware for specific path prefix"],
  ["req.params.id",           "Route parameter from /users/:id"],
  ["req.query.limit",         "Query string ?limit=10"],
  ["req.body",                "Request body (needs express.json() middleware)"],
  ["res.json(data)",          "Send JSON response (sets Content-Type)"],
  ["res.status(404).json(e)", "Chain status code with response"],
  ["res.send('text')",        "Send plain text response"],
  ["res.redirect('/new')",    "Redirect to another URL"],
  ["next()",                  "Pass control to the next middleware"],
  ["next(err)",               "Pass error to the error handler"],
];
concepts.forEach(([method, desc]) => {
  console.log(`   ${method.padEnd(28)} → ${desc}`);
});
