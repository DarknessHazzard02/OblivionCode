// Made by: Hazzard
/**
 * Secure Real-Time Multiplayer Game - freeCodeCamp Information Security Project
 *
 * Concepts: Canvas/game loop, socket.io real-time communication,
 *           Helmet.js security headers, collision detection,
 *           player synchronization, anti-cheat (server-authoritative)
 *
 * Game: "Collect the coins" — players move on a 2D grid, collect items,
 *       avoid collisions. Server is authoritative (validates all moves).
 *
 * This file is a standalone Node.js simulation of the core game logic.
 * In production: Express + Socket.io + Helmet serve an HTML canvas client.
 */

// ─── Game Constants ───────────────────────────────────────────────────────────
const GRID_WIDTH = 640;
const GRID_HEIGHT = 480;
const PLAYER_SIZE = 20;
const COIN_SIZE = 15;
const MOVE_SPEED = 5;
const MAX_COINS = 5;

// ─── Utilities ────────────────────────────────────────────────────────────────
function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function rectOverlap(ax, ay, aw, ah, bx, by, bw, bh) {
  return ax < bx + bw && ax + aw > bx && ay < by + bh && ay + ah > by;
}

// ─── Game State ───────────────────────────────────────────────────────────────
class GameState {
  constructor() {
    this.players = {}; // { [socketId]: Player }
    this.coins = [];
    this.scores = {};
    this._spawnCoins();
  }

  _spawnCoins() {
    while (this.coins.length < MAX_COINS) {
      this.coins.push({
        x: randomInt(0, GRID_WIDTH - COIN_SIZE),
        y: randomInt(0, GRID_HEIGHT - COIN_SIZE),
        value: randomInt(1, 5),
      });
    }
  }

  addPlayer(socketId, username) {
    this.players[socketId] = {
      id: socketId,
      username,
      x: randomInt(0, GRID_WIDTH - PLAYER_SIZE),
      y: randomInt(0, GRID_HEIGHT - PLAYER_SIZE),
      score: 0,
      color: `hsl(${randomInt(0, 360)}, 70%, 55%)`,
    };
    this.scores[socketId] = 0;
    return this.players[socketId];
  }

  removePlayer(socketId) {
    delete this.players[socketId];
    delete this.scores[socketId];
  }

  movePlayer(socketId, dir) {
    const player = this.players[socketId];
    if (!player) return { error: "Player not found" };

    const prev = { x: player.x, y: player.y };

    switch (dir) {
      case "up":    player.y = Math.max(0, player.y - MOVE_SPEED); break;
      case "down":  player.y = Math.min(GRID_HEIGHT - PLAYER_SIZE, player.y + MOVE_SPEED); break;
      case "left":  player.x = Math.max(0, player.x - MOVE_SPEED); break;
      case "right": player.x = Math.min(GRID_WIDTH - PLAYER_SIZE, player.x + MOVE_SPEED); break;
      default:      return { error: `Unknown direction: ${dir}` };
    }

    // Server-side collision check with coins
    const collected = [];
    this.coins = this.coins.filter((coin) => {
      if (rectOverlap(player.x, player.y, PLAYER_SIZE, PLAYER_SIZE,
                      coin.x, coin.y, COIN_SIZE, COIN_SIZE)) {
        player.score += coin.value;
        this.scores[socketId] = player.score;
        collected.push(coin);
        return false; // remove coin
      }
      return true;
    });

    // Respawn coins to maintain MAX_COINS
    this._spawnCoins();

    return {
      player: { id: player.id, x: player.x, y: player.y, score: player.score },
      collected,
      moved: prev.x !== player.x || prev.y !== player.y,
    };
  }

  getLeaderboard() {
    return Object.values(this.players)
      .sort((a, b) => b.score - a.score)
      .map(({ id, username, score }) => ({ id, username, score }));
  }

  getState() {
    return {
      players: Object.values(this.players).map(({ id, username, x, y, score, color }) => ({
        id, username, x, y, score, color,
      })),
      coins: this.coins,
      leaderboard: this.getLeaderboard(),
    };
  }
}

// ─── Demo ─────────────────────────────────────────────────────────────────────
console.log("=== Secure Real-Time Multiplayer Game Demo ===\n");

const game = new GameState();

console.log("1) Players join:");
const p1 = game.addPlayer("socket_alice", "Alice");
const p2 = game.addPlayer("socket_bob",   "Bob");
console.log(`   Alice spawned at (${p1.x}, ${p1.y})`);
console.log(`   Bob   spawned at (${p2.x}, ${p2.y})`);

console.log(`\n2) Initial coins: ${game.coins.length} coins on map`);

console.log("\n3) Alice moves right 5 times:");
for (let i = 0; i < 5; i++) {
  const res = game.movePlayer("socket_alice", "right");
  if (res.collected.length) {
    console.log(`   Step ${i + 1}: Collected ${res.collected.length} coin(s)! Score: ${res.player.score}`);
  }
}
console.log(`   Alice final position: (${game.players["socket_alice"].x}, ${game.players["socket_alice"].y})`);

console.log("\n4) Invalid move direction:");
console.log("  ", game.movePlayer("socket_alice", "diagonal"));

console.log("\n5) Invalid player:");
console.log("  ", game.movePlayer("unknown_socket", "up"));

console.log("\n6) Current game state:");
const state = game.getState();
console.log(`   Players: ${state.players.length}, Coins: ${state.coins.length}`);
console.log("   Leaderboard:", state.leaderboard);

console.log("\n7) Bob disconnects:");
game.removePlayer("socket_bob");
console.log(`   Players remaining: ${Object.keys(game.players).length}`);

console.log("\n8) Security headers (Helmet.js) in production:");
const helmetHeaders = {
  "X-DNS-Prefetch-Control": "off",
  "X-Frame-Options": "SAMEORIGIN",
  "X-XSS-Protection": "0",
  "X-Content-Type-Options": "nosniff",
  "Strict-Transport-Security": "max-age=15552000; includeSubDomains",
  "Content-Security-Policy": "default-src 'self'",
};
Object.entries(helmetHeaders).forEach(([h, v]) => console.log(`   ${h}: ${v}`));
