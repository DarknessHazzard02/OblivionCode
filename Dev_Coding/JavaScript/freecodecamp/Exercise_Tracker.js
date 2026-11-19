// Made by: Hazzard
/**
 * Exercise Tracker Microservice - freeCodeCamp Back End APIs Project
 *
 * Concepts: REST API design, MongoDB-style data modeling, date handling,
 *           query parameters, POST/GET endpoints, user management
 *
 * Endpoints:
 *   POST /api/users                          → create user
 *   GET  /api/users                          → list all users
 *   POST /api/users/:_id/exercises           → add exercise log
 *   GET  /api/users/:_id/logs[?from&to&limit]→ get exercise log
 *
 * In a real freeCodeCamp solution this uses Express + MongoDB/Mongoose.
 * This file is a standalone Node.js simulation with an in-memory store.
 */

// ─── In-Memory Data Store ────────────────────────────────────────────────────
const users = {}; // { [_id]: { _id, username, log: [] } }
let nextId = 1;

// ─── Helpers ─────────────────────────────────────────────────────────────────
function createUser(username) {
  const _id = String(nextId++);
  users[_id] = { _id, username, log: [] };
  return { username, _id };
}

function getAllUsers() {
  return Object.values(users).map(({ _id, username }) => ({ _id, username }));
}

function addExercise(_id, description, duration, dateStr) {
  const user = users[_id];
  if (!user) return { error: "Unknown user ID" };

  const date = dateStr ? new Date(dateStr) : new Date();
  if (isNaN(date.getTime())) return { error: "Invalid date" };
  if (!description) return { error: "Description required" };

  const dur = parseInt(duration, 10);
  if (isNaN(dur) || dur <= 0) return { error: "Duration must be a positive number" };

  const entry = { description, duration: dur, date: date.toDateString() };
  user.log.push(entry);

  return {
    _id: user._id,
    username: user.username,
    date: entry.date,
    duration: entry.duration,
    description: entry.description,
  };
}

function getLog(_id, from, to, limit) {
  const user = users[_id];
  if (!user) return { error: "Unknown user ID" };

  let log = [...user.log];

  if (from) {
    const fromDate = new Date(from);
    log = log.filter((e) => new Date(e.date) >= fromDate);
  }
  if (to) {
    const toDate = new Date(to);
    log = log.filter((e) => new Date(e.date) <= toDate);
  }
  if (limit) {
    log = log.slice(0, parseInt(limit, 10));
  }

  return {
    _id: user._id,
    username: user.username,
    count: log.length,
    log,
  };
}

// ─── Demo ─────────────────────────────────────────────────────────────────────
console.log("=== Exercise Tracker Microservice Demo ===\n");

// Create users
console.log("1) Create users:");
const alice = createUser("alice");
const bob = createUser("bob");
console.log("   Created:", alice);
console.log("   Created:", bob);

// List all users
console.log("\n2) All users:");
console.log("  ", getAllUsers());

// Add exercises for alice
console.log("\n3) Add exercises for alice:");
console.log("  ", addExercise(alice._id, "Running", 30, "2024-01-10"));
console.log("  ", addExercise(alice._id, "Cycling", 45, "2024-01-15"));
console.log("  ", addExercise(alice._id, "Swimming", 60, "2024-02-01"));

// Add exercise for bob
console.log("\n4) Add exercise for bob:");
console.log("  ", addExercise(bob._id, "Yoga", 20, "2024-01-20"));

// Get full log for alice
console.log("\n5) Alice full log:");
console.log("  ", JSON.stringify(getLog(alice._id), null, 2));

// Get filtered log — from 2024-01-01 to 2024-01-31, limit 1
console.log("\n6) Alice log (Jan 2024, limit 1):");
console.log("  ", JSON.stringify(getLog(alice._id, "2024-01-01", "2024-01-31", 1), null, 2));

// Error cases
console.log("\n7) Error cases:");
console.log("  ", addExercise("999", "Hiking", 90));
console.log("  ", addExercise(alice._id, "", 30, "2024-03-01"));
console.log("  ", addExercise(alice._id, "Weights", -5, "2024-03-01"));
