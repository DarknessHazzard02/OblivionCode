/**
 * Stock Price Checker - freeCodeCamp Information Security Project
 *
 * Concepts: Security headers (Helmet.js), IP-based anonymous likes,
 *           external API calls, rate limiting, privacy-preserving storage
 *
 * Endpoint:
 *   GET /api/stock-prices?stock=GOOG[&like=true]
 *   GET /api/stock-prices?stock=GOOG&stock=AAPL[&like=true]  → compare two stocks
 *
 * Security requirement: Only ONE like per IP per stock (privacy: store hashed IPs)
 *
 * This file is a standalone Node.js simulation with mock stock data.
 */

const crypto = require("crypto");

// ─── Mock Stock Data ──────────────────────────────────────────────────────────
const MOCK_PRICES = {
  GOOG: 175.43,
  AAPL: 189.3,
  MSFT: 420.15,
  AMZN: 185.6,
  TSLA: 250.78,
  META: 540.12,
  NVDA: 875.5,
};

// ─── In-Memory Like Store ─────────────────────────────────────────────────────
// { [stock]: Set<hashedIP> }
const stockLikes = {};

function hashIP(ip) {
  // Privacy-preserving: store a one-way hash, never the raw IP
  return crypto.createHash("sha256").update(ip + "salt_secret").digest("hex");
}

function getStockPrice(ticker) {
  const price = MOCK_PRICES[ticker.toUpperCase()];
  return price ?? null;
}

function getLikes(stock) {
  return stockLikes[stock]?.size ?? 0;
}

function addLike(stock, ip) {
  if (!stockLikes[stock]) stockLikes[stock] = new Set();
  stockLikes[stock].add(hashIP(ip));
}

// ─── Core API Logic ───────────────────────────────────────────────────────────
function checkStock(stocks, like, userIP) {
  const tickers = Array.isArray(stocks) ? stocks : [stocks];

  if (tickers.length === 0 || tickers.length > 2) {
    return { error: "Provide 1 or 2 stock tickers" };
  }

  const results = tickers.map((ticker) => {
    const symbol = ticker.toUpperCase();
    const price = getStockPrice(symbol);
    if (price === null) return { error: `Unknown ticker: ${symbol}` };

    if (like) addLike(symbol, userIP);

    return { stock: symbol, price, likes: getLikes(symbol) };
  });

  if (results.some((r) => r.error)) {
    return results.find((r) => r.error);
  }

  if (results.length === 2) {
    // Compare mode: return rel_likes (difference)
    const [a, b] = results;
    return {
      stockData: [
        { stock: a.stock, price: a.price, rel_likes: a.likes - b.likes },
        { stock: b.stock, price: b.price, rel_likes: b.likes - a.likes },
      ],
    };
  }

  return { stockData: results[0] };
}

// ─── Demo ─────────────────────────────────────────────────────────────────────
console.log("=== Stock Price Checker Demo ===\n");

// Single stock, no like
console.log("1) GET /api/stock-prices?stock=GOOG");
console.log("  ", checkStock("GOOG", false, "192.168.1.1"));

// Single stock, with like
console.log("\n2) GET /api/stock-prices?stock=GOOG&like=true (IP: 192.168.1.1)");
console.log("  ", checkStock("GOOG", true, "192.168.1.1"));

// Same IP liking again — should NOT increment
console.log("\n3) Same IP likes GOOG again (should still be 1 like):");
console.log("  ", checkStock("GOOG", true, "192.168.1.1"));

// Different IP likes GOOG
console.log("\n4) Different IP (10.0.0.5) likes GOOG:");
console.log("  ", checkStock("GOOG", true, "10.0.0.5"));
console.log("   GOOG likes:", getLikes("GOOG"));

// Compare two stocks
console.log("\n5) GET /api/stock-prices?stock=GOOG&stock=AAPL&like=true");
checkStock("AAPL", true, "192.168.1.1"); // give AAPL 1 like from same IP
console.log("  ", checkStock(["GOOG", "AAPL"], false, "192.168.1.99"));

// Unknown ticker
console.log("\n6) Unknown ticker:");
console.log("  ", checkStock("FAKE", false, "1.2.3.4"));
