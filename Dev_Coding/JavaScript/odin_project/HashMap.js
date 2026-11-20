// Made by: Hazzard
// The Odin Project - Full Stack JavaScript (Computer Science): HashMap.
// Separate chaining, string keys, grows x2 when load factor is passed. Run: node HashMap.js

const assert = require("node:assert/strict");

class HashMap {
  constructor(loadFactor = 0.75, capacity = 16) {
    this.loadFactor = loadFactor;
    this.capacity = capacity;
    this.buckets = Array.from({ length: capacity }, () => []);
    this.count = 0;
  }

  hash(key) {
    if (typeof key !== "string") throw new TypeError("HashMap keys must be strings.");
    let hashCode = 0;
    const prime = 31;
    for (let i = 0; i < key.length; i++) hashCode = (prime * hashCode + key.charCodeAt(i)) % this.capacity;
    return hashCode;
  }

  bucket(key) {
    const index = this.hash(key);
    if (index < 0 || index >= this.buckets.length) throw new Error("Trying to access index out of bounds");
    return this.buckets[index];
  }

  set(key, value) {
    const bucket = this.bucket(key);
    const entry = bucket.find(([k]) => k === key);
    if (entry) {
      entry[1] = value;
      return;
    }
    bucket.push([key, value]);
    this.count += 1;
    if (this.count > this.capacity * this.loadFactor) this.grow();
  }

  grow() {
    const old = this.entries();
    this.capacity *= 2;
    this.buckets = Array.from({ length: this.capacity }, () => []);
    this.count = 0;
    old.forEach(([k, v]) => this.set(k, v));
  }

  get(key) {
    const entry = this.bucket(key).find(([k]) => k === key);
    return entry ? entry[1] : null;
  }

  has(key) { return this.bucket(key).some(([k]) => k === key); }

  remove(key) {
    const bucket = this.bucket(key);
    const index = bucket.findIndex(([k]) => k === key);
    if (index === -1) return false;
    bucket.splice(index, 1);
    this.count -= 1;
    return true;
  }

  length() { return this.count; }

  clear() {
    this.buckets = Array.from({ length: this.capacity }, () => []);
    this.count = 0;
  }

  keys() { return this.entries().map(([k]) => k); }

  values() { return this.entries().map(([, v]) => v); }

  entries() { return this.buckets.flatMap((bucket) => bucket.map(([k, v]) => [k, v])); }
}

if (require.main === module) {
  const test = new HashMap();
  const fruits = { apple: "red", banana: "yellow", carrot: "orange", dog: "brown", elephant: "gray",
    frog: "green", grape: "purple", hat: "black", "ice cream": "white", jacket: "blue", kite: "pink", lion: "golden" };
  Object.entries(fruits).forEach(([k, v]) => test.set(k, v));
  assert.equal(test.length(), 12);
  assert.equal(test.capacity, 16);
  test.set("apple", "green");
  assert.equal(test.length(), 12, "overwriting must not add an entry");
  assert.equal(test.get("apple"), "green");
  test.set("moon", "silver");
  assert.equal(test.capacity, 32, "13 entries > 16 * 0.75 must grow the table");
  assert.equal(test.length(), 13);
  assert.equal(test.get("lion"), "golden");
  assert.equal(test.has("kite"), true);
  assert.equal(test.remove("kite"), true);
  assert.equal(test.remove("kite"), false);
  assert.equal(test.get("kite"), null);
  assert.equal(test.keys().length, 12);
  assert.throws(() => test.set(42, "x"), TypeError);
  test.clear();
  assert.equal(test.length(), 0);
  console.log("HashMap: capacity grew to 32 after 13 entries; all checks passed.");
}

module.exports = { HashMap };
