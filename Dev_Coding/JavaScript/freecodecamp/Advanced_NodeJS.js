// Made by: Hazzard
/**
 * Advanced Node.js Concepts - freeCodeCamp Back End APIs
 *
 * Concepts: Session management, Passport.js auth strategies,
 *           Socket.io real-time events, streams, clustering,
 *           worker threads, event emitters, rate limiting
 */

const { EventEmitter } = require("events");
const crypto = require("crypto");
const os = require("os");

console.log("=== Advanced Node.js Concepts Demo ===\n");

// ─── 1. Event Emitter ─────────────────────────────────────────────────────────
console.log("1) Event Emitter (foundation of Node.js I/O):\n");

class NotificationService extends EventEmitter {
  sendWelcome(user) {
    this.emit("notification", { type: "welcome", user, message: `Welcome, ${user.name}!` });
  }

  sendAlert(message, level = "info") {
    this.emit("notification", { type: "alert", level, message });
    if (level === "critical") this.emit("critical", message);
  }
}

const notifications = new NotificationService();

notifications.on("notification", (data) => {
  console.log(`   [NOTIFY] [${data.type.toUpperCase()}] ${data.message}`);
});

notifications.once("critical", (msg) => {
  // 'once' fires only the first time
  console.log(`   [CRITICAL ALERT - once handler] ${msg}`);
});

notifications.sendWelcome({ name: "Alice" });
notifications.sendAlert("Server CPU high", "critical");
notifications.sendAlert("Server CPU high again", "critical"); // 'once' won't fire again

// ─── 2. Session Management ────────────────────────────────────────────────────
console.log("\n2) Session management pattern (express-session):\n");

class SessionStore {
  constructor() {
    this.sessions = new Map();
  }

  create(userId, data = {}) {
    const sessionId = crypto.randomBytes(32).toString("hex");
    this.sessions.set(sessionId, {
      userId,
      data,
      createdAt: Date.now(),
      lastAccessed: Date.now(),
      maxAge: 24 * 60 * 60 * 1000, // 24 hours
    });
    return sessionId;
  }

  get(sessionId) {
    const session = this.sessions.get(sessionId);
    if (!session) return null;
    if (Date.now() - session.createdAt > session.maxAge) {
      this.sessions.delete(sessionId);
      return null; // expired
    }
    session.lastAccessed = Date.now();
    return session;
  }

  destroy(sessionId) {
    return this.sessions.delete(sessionId);
  }
}

const store = new SessionStore();
const sid = store.create("user_123", { cart: ["item1", "item2"], theme: "dark" });
console.log(`   Created session: ${sid.slice(0, 16)}...`);
console.log("   Session data:", store.get(sid)?.data);
store.destroy(sid);
console.log("   After destroy:", store.get(sid));

// ─── 3. Passport.js auth strategies ──────────────────────────────────────────
console.log("\n3) Passport.js auth strategy patterns:\n");
const passportCode = `
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const GitHubStrategy = require('passport-github2').Strategy;

// Local strategy (username + password)
passport.use(new LocalStrategy(async (username, password, done) => {
  try {
    const user = await User.findOne({ username });
    if (!user) return done(null, false, { message: 'User not found' });
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return done(null, false, { message: 'Incorrect password' });
    return done(null, user);
  } catch (err) {
    return done(err);
  }
}));

// GitHub OAuth2 strategy
passport.use(new GitHubStrategy({
  clientID: process.env.GITHUB_CLIENT_ID,
  clientSecret: process.env.GITHUB_CLIENT_SECRET,
  callbackURL: '/auth/github/callback',
}, async (accessToken, refreshToken, profile, done) => {
  const user = await User.findOrCreate({ githubId: profile.id });
  return done(null, user);
}));

// Serialize/deserialize (for session support)
passport.serializeUser((user, done) => done(null, user.id));
passport.deserializeUser(async (id, done) => {
  const user = await User.findById(id);
  done(null, user);
});
`;
console.log(passportCode);

// ─── 4. Socket.io real-time events ───────────────────────────────────────────
console.log("4) Socket.io event patterns:\n");
const socketCode = `
// Server side
const io = require('socket.io')(server);

io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  // Join a room
  socket.on('join-room', (room) => {
    socket.join(room);
    socket.to(room).emit('user-joined', { id: socket.id });
  });

  // Handle chat message
  socket.on('message', ({ room, text }) => {
    io.to(room).emit('message', { from: socket.id, text, time: Date.now() });
  });

  // Private message
  socket.on('private-msg', ({ to, text }) => {
    socket.to(to).emit('private-msg', { from: socket.id, text });
  });

  socket.on('disconnect', () => {
    io.emit('user-left', socket.id);
  });
});

// Client side (browser)
const socket = io();
socket.emit('join-room', 'general');
socket.on('message', ({ from, text }) => console.log(from + ': ' + text));
socket.emit('message', { room: 'general', text: 'Hello!' });
`;
console.log(socketCode);

// ─── 5. Node.js clustering ───────────────────────────────────────────────────
console.log("5) Clustering to use all CPU cores:\n");
const clusterCode = `
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

if (cluster.isPrimary) {
  console.log('Primary PID:', process.pid, '— forking', numCPUs, 'workers');
  for (let i = 0; i < numCPUs; i++) cluster.fork();
  cluster.on('exit', (worker) => {
    console.log('Worker', worker.process.pid, 'died — restarting');
    cluster.fork();
  });
} else {
  require('./server'); // each worker runs the Express server
  console.log('Worker', process.pid, 'started');
}
`;
console.log(clusterCode);
console.log(`   This machine has ${os.cpus().length} CPU core(s)\n`);

// ─── 6. Rate limiting ─────────────────────────────────────────────────────────
console.log("6) Simple rate limiter:\n");

class RateLimiter {
  constructor(maxRequests = 100, windowMs = 60000) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
    this.clients = new Map();
  }

  isAllowed(ip) {
    const now = Date.now();
    const client = this.clients.get(ip) || { count: 0, windowStart: now };

    if (now - client.windowStart > this.windowMs) {
      client.count = 0;
      client.windowStart = now;
    }

    client.count++;
    this.clients.set(ip, client);
    return client.count <= this.maxRequests;
  }
}

const limiter = new RateLimiter(3, 60000); // 3 requests per minute for demo
const testIP = "192.168.1.1";
for (let i = 1; i <= 5; i++) {
  const allowed = limiter.isAllowed(testIP);
  console.log(`   Request ${i}: ${allowed ? "✅ Allowed" : "❌ Rate limited (429 Too Many Requests)"}`);
}
