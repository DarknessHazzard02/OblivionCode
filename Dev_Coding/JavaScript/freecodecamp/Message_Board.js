/**
 * Anonymous Message Board - freeCodeCamp Information Security Project
 *
 * Concepts: REST API design, bcrypt password hashing, security headers,
 *           CRUD operations, thread/reply data model, reporting content
 *
 * Endpoints:
 *   POST   /api/threads/:board                       → create thread
 *   GET    /api/threads/:board                       → list threads (top 10, top 3 replies)
 *   DELETE /api/threads/:board                       → delete thread (requires password)
 *   PUT    /api/threads/:board                       → report thread
 *   POST   /api/replies/:board                       → add reply to thread
 *   GET    /api/replies/:board?thread_id=...         → get thread with all replies
 *   DELETE /api/replies/:board                       → delete reply
 *   PUT    /api/replies/:board                       → report reply
 *
 * This file is a standalone Node.js simulation with an in-memory store.
 */

// ─── Simple hash simulation (bcrypt would be used in production) ───────────
function simpleHash(password) {
  // Real implementation would use: bcrypt.hashSync(password, 12)
  return `hashed_${Buffer.from(password).toString("base64")}`;
}

function simpleCompare(password, hash) {
  // Real implementation would use: bcrypt.compareSync(password, hash)
  return hash === `hashed_${Buffer.from(password).toString("base64")}`;
}

// ─── In-Memory Store ──────────────────────────────────────────────────────────
const boards = {}; // { [boardName]: Thread[] }
let nextThreadId = 1;
let nextReplyId = 1;

// ─── Thread Operations ────────────────────────────────────────────────────────
function createThread(board, text, deletePassword) {
  if (!boards[board]) boards[board] = [];
  const thread = {
    _id: `thread_${nextThreadId++}`,
    text,
    created_on: new Date().toISOString(),
    bumped_on: new Date().toISOString(),
    reported: false,
    delete_password: simpleHash(deletePassword),
    replies: [],
    replycount: 0,
  };
  boards[board].push(thread);
  return { _id: thread._id, text: thread.text, created_on: thread.created_on };
}

function getThreads(board) {
  if (!boards[board]) return [];
  return boards[board]
    .sort((a, b) => new Date(b.bumped_on) - new Date(a.bumped_on))
    .slice(0, 10)
    .map((t) => ({
      _id: t._id,
      text: t.text,
      created_on: t.created_on,
      bumped_on: t.bumped_on,
      replycount: t.replycount,
      // Last 3 replies, without delete_password and reported fields
      replies: t.replies.slice(-3).map((r) => ({
        _id: r._id,
        text: r.text,
        created_on: r.created_on,
      })),
    }));
}

function deleteThread(board, thread_id, delete_password) {
  if (!boards[board]) return "incorrect password";
  const idx = boards[board].findIndex((t) => t._id === thread_id);
  if (idx === -1) return "thread not found";
  if (!simpleCompare(delete_password, boards[board][idx].delete_password)) {
    return "incorrect password";
  }
  boards[board].splice(idx, 1);
  return "success";
}

function reportThread(board, thread_id) {
  const thread = boards[board]?.find((t) => t._id === thread_id);
  if (!thread) return "thread not found";
  thread.reported = true;
  return "reported";
}

// ─── Reply Operations ─────────────────────────────────────────────────────────
function addReply(board, thread_id, text, deletePassword) {
  const thread = boards[board]?.find((t) => t._id === thread_id);
  if (!thread) return { error: "thread not found" };

  const reply = {
    _id: `reply_${nextReplyId++}`,
    text,
    created_on: new Date().toISOString(),
    reported: false,
    delete_password: simpleHash(deletePassword),
  };
  thread.replies.push(reply);
  thread.replycount++;
  thread.bumped_on = reply.created_on;
  return { _id: reply._id, text: reply.text, created_on: reply.created_on };
}

function getThread(board, thread_id) {
  const thread = boards[board]?.find((t) => t._id === thread_id);
  if (!thread) return { error: "thread not found" };
  return {
    _id: thread._id,
    text: thread.text,
    created_on: thread.created_on,
    bumped_on: thread.bumped_on,
    replycount: thread.replycount,
    replies: thread.replies.map((r) => ({
      _id: r._id,
      text: r.text,
      created_on: r.created_on,
    })),
  };
}

// ─── Demo ─────────────────────────────────────────────────────────────────────
console.log("=== Anonymous Message Board Demo ===\n");

console.log("1) Create threads on 'general' board:");
const t1 = createThread("general", "Hello World! First thread here.", "pass123");
const t2 = createThread("general", "Anyone else learning freeCodeCamp?", "mypassword");
console.log("   Thread 1:", t1);
console.log("   Thread 2:", t2);

console.log("\n2) Add replies to thread 1:");
const r1 = addReply("general", t1._id, "Welcome! This is a reply.", "replypass");
const r2 = addReply("general", t1._id, "Great thread!", "anotherpass");
console.log("   Reply 1:", r1);
console.log("   Reply 2:", r2);

console.log("\n3) Get thread listing (top 10, 3 replies each):");
console.log("  ", JSON.stringify(getThreads("general"), null, 2));

console.log("\n4) Get single thread with all replies:");
console.log("  ", JSON.stringify(getThread("general", t1._id), null, 2));

console.log("\n5) Report a thread:");
console.log("  ", reportThread("general", t2._id));

console.log("\n6) Delete with wrong password:");
console.log("  ", deleteThread("general", t1._id, "wrongpass"));

console.log("\n7) Delete with correct password:");
console.log("  ", deleteThread("general", t1._id, "pass123"));

console.log("\n8) Threads after delete:");
console.log("   Count:", getThreads("general").length);
