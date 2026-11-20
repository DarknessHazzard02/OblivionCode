// Made by: Hazzard
// The Odin Project - Full Stack JavaScript (Computer Science): Linked List.
// Singly linked list with the methods from the Odin spec. Run: node Linked_List.js

const assert = require("node:assert/strict");

class Node {
  constructor(value = null, nextNode = null) {
    this.value = value;
    this.nextNode = nextNode;
  }
}

class LinkedList {
  constructor() {
    this.headNode = null;
    this.length = 0;
  }

  append(value) {
    const node = new Node(value);
    if (!this.headNode) this.headNode = node;
    else this.tail().nextNode = node;
    this.length += 1;
  }

  prepend(value) {
    this.headNode = new Node(value, this.headNode);
    this.length += 1;
  }

  size() { return this.length; }

  head() { return this.headNode; }

  tail() {
    let node = this.headNode;
    while (node && node.nextNode) node = node.nextNode;
    return node;
  }

  at(index) {
    if (index < 0 || index >= this.length) return null;
    let node = this.headNode;
    for (let i = 0; i < index; i++) node = node.nextNode;
    return node;
  }

  pop() {
    if (!this.headNode) return null;
    if (!this.headNode.nextNode) {
      const only = this.headNode;
      this.headNode = null;
      this.length = 0;
      return only;
    }
    const beforeTail = this.at(this.length - 2);
    const last = beforeTail.nextNode;
    beforeTail.nextNode = null;
    this.length -= 1;
    return last;
  }

  contains(value) { return this.find(value) !== null; }

  find(value) {
    let node = this.headNode;
    for (let i = 0; node; i++, node = node.nextNode) if (node.value === value) return i;
    return null;
  }

  toString() {
    let out = "";
    for (let node = this.headNode; node; node = node.nextNode) out += `( ${node.value} ) -> `;
    return out + "null";
  }

  // Extra credit
  insertAt(value, index) {
    if (index < 0 || index > this.length) throw new RangeError(`Index ${index} out of range 0..${this.length}`);
    if (index === 0) return this.prepend(value);
    const before = this.at(index - 1);
    before.nextNode = new Node(value, before.nextNode);
    this.length += 1;
  }

  removeAt(index) {
    if (index < 0 || index >= this.length) throw new RangeError(`Index ${index} out of range 0..${this.length - 1}`);
    if (index === 0) {
      const removed = this.headNode;
      this.headNode = removed.nextNode;
      this.length -= 1;
      return removed;
    }
    const before = this.at(index - 1);
    const removed = before.nextNode;
    before.nextNode = removed.nextNode;
    this.length -= 1;
    return removed;
  }
}

if (require.main === module) {
  const list = new LinkedList();
  ["dog", "cat", "parrot", "hamster", "snake", "turtle"].forEach((pet) => list.append(pet));
  assert.equal(list.toString(), "( dog ) -> ( cat ) -> ( parrot ) -> ( hamster ) -> ( snake ) -> ( turtle ) -> null");
  list.prepend("fish");
  assert.equal(list.size(), 7);
  assert.equal(list.head().value, "fish");
  assert.equal(list.tail().value, "turtle");
  assert.equal(list.at(3).value, "parrot");
  assert.equal(list.at(99), null);
  assert.equal(list.pop().value, "turtle");
  assert.equal(list.contains("snake"), true);
  assert.equal(list.find("hamster"), 4);
  assert.equal(list.find("lion"), null);
  list.insertAt("lion", 2);
  assert.equal(list.at(2).value, "lion");
  assert.equal(list.removeAt(2).value, "lion");
  assert.throws(() => list.insertAt("x", 99), RangeError);
  console.log(list.toString());
  console.log("Linked List: all checks passed.");
}

module.exports = { LinkedList, Node };
