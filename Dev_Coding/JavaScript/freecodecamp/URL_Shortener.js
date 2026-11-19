// FreeCodeCamp Back End Development and APIs - URL Shortener Microservice
// Validates target URLs, assigns sequential/hashed short IDs, and performs redirect lookup

class URLShortener {
  constructor() {
    this.urlDatabase = new Map();
    this.idCounter = 1;
  }

  isValidUrl(urlString) {
    try {
      const parsed = new URL(urlString);
      return parsed.protocol === "http:" || parsed.protocol === "https:";
    } catch {
      return false;
    }
  }

  createShortUrl(originalUrl) {
    if (!this.isValidUrl(originalUrl)) {
      return { error: "invalid url" };
    }

    // Check if URL was previously shortened
    for (const [id, url] of this.urlDatabase.entries()) {
      if (url === originalUrl) {
        return { original_url: originalUrl, short_url: id };
      }
    }

    const shortId = this.idCounter++;
    this.urlDatabase.set(shortId, originalUrl);

    return {
      original_url: originalUrl,
      short_url: shortId
    };
  }

  resolveShortUrl(shortId) {
    const id = parseInt(shortId, 10);
    if (!this.urlDatabase.has(id)) {
      return { error: "No short URL found for the given input" };
    }
    return { redirect_to: this.urlDatabase.get(id) };
  }
}

// Tests
console.log("=== URL Shortener Demo ===");
const shortener = new URLShortener();

const entry1 = shortener.createShortUrl("https://freecodecamp.org");
console.log("Created:", entry1);

const entry2 = shortener.createShortUrl("https://github.com/DarknessHazzard02/OblivionCode");
console.log("Created:", entry2);

console.log("Invalid Attempt:", shortener.createShortUrl("ftp://invalid-protocol.com"));

console.log("\nLookup ID 1:", shortener.resolveShortUrl(entry1.short_url));
console.log("Lookup ID 2:", shortener.resolveShortUrl(entry2.short_url));
console.log("Lookup Non-existent:", shortener.resolveShortUrl(999));
