// Made by: Hazzard
// The Odin Project - Full Stack JavaScript (Computer Science): Binary Search Tree.
// Balanced build from a sorted, de-duplicated array; traversals; rebalance. Run: node Binary_Search_Tree.js

const assert = require("node:assert/strict");

class Node {
  constructor(data) {
    this.data = data;
    this.left = null;
    this.right = null;
  }
}

class Tree {
  constructor(array) {
    this.root = Tree.buildTree(array);
  }

  static buildTree(array) {
    const sorted = [...new Set(array)].sort((a, b) => a - b);
    const build = (start, end) => {
      if (start > end) return null;
      const mid = Math.floor((start + end) / 2);
      const node = new Node(sorted[mid]);
      node.left = build(start, mid - 1);
      node.right = build(mid + 1, end);
      return node;
    };
    return build(0, sorted.length - 1);
  }

  insert(value, node = this.root) {
    if (!this.root) {
      this.root = new Node(value);
      return;
    }
    if (value === node.data) return;
    const side = value < node.data ? "left" : "right";
    if (node[side]) this.insert(value, node[side]);
    else node[side] = new Node(value);
  }

  deleteItem(value) {
    const remove = (node, v) => {
      if (!node) return null;
      if (v < node.data) node.left = remove(node.left, v);
      else if (v > node.data) node.right = remove(node.right, v);
      else {
        if (!node.left) return node.right;
        if (!node.right) return node.left;
        let successor = node.right;
        while (successor.left) successor = successor.left;
        node.data = successor.data;
        node.right = remove(node.right, successor.data);
      }
      return node;
    };
    this.root = remove(this.root, value);
  }

  find(value) {
    let node = this.root;
    while (node && node.data !== value) node = value < node.data ? node.left : node.right;
    return node;
  }

  levelOrder(callback) {
    if (typeof callback !== "function") throw new TypeError("A callback is required.");
    const queue = this.root ? [this.root] : [];
    while (queue.length) {
      const node = queue.shift();
      callback(node);
      if (node.left) queue.push(node.left);
      if (node.right) queue.push(node.right);
    }
  }

  depthFirst(order, callback) {
    if (typeof callback !== "function") throw new TypeError("A callback is required.");
    const walk = (node) => {
      if (!node) return;
      if (order === "pre") callback(node);
      walk(node.left);
      if (order === "in") callback(node);
      walk(node.right);
      if (order === "post") callback(node);
    };
    walk(this.root);
  }

  inOrder(callback) { this.depthFirst("in", callback); }

  preOrder(callback) { this.depthFirst("pre", callback); }

  postOrder(callback) { this.depthFirst("post", callback); }

  // Edges on the longest path from the node down to a leaf; null when the value is missing.
  height(value) {
    const node = this.find(value);
    if (!node) return null;
    const h = (n) => (n ? 1 + Math.max(h(n.left), h(n.right)) : -1);
    return h(node);
  }

  // Edges from the root to the node; null when the value is missing.
  depth(value) {
    let node = this.root;
    let edges = 0;
    while (node) {
      if (value === node.data) return edges;
      node = value < node.data ? node.left : node.right;
      edges += 1;
    }
    return null;
  }

  isBalanced() {
    const check = (node) => {
      if (!node) return -1;
      const left = check(node.left);
      const right = check(node.right);
      if (left === null || right === null || Math.abs(left - right) > 1) return null;
      return 1 + Math.max(left, right);
    };
    return check(this.root) !== null;
  }

  rebalance() {
    const values = [];
    this.inOrder((node) => values.push(node.data));
    this.root = Tree.buildTree(values);
  }

  values(order = "in") {
    const out = [];
    if (order === "level") this.levelOrder((n) => out.push(n.data));
    else this.depthFirst(order, (n) => out.push(n.data));
    return out;
  }
}

if (require.main === module) {
  const random = Array.from({ length: 15 }, () => Math.floor(Math.random() * 100));
  const tree = new Tree(random);
  assert.equal(tree.isBalanced(), true);
  assert.deepEqual(tree.values("in"), [...new Set(random)].sort((a, b) => a - b));
  [101, 150, 175, 200, 250].forEach((v) => tree.insert(v));
  assert.equal(tree.isBalanced(), false, "inserting a run of large numbers must unbalance it");
  tree.rebalance();
  assert.equal(tree.isBalanced(), true);

  const fixed = new Tree([1, 7, 4, 23, 8, 9, 4, 3, 5, 7, 9, 67, 6345, 324]);
  assert.deepEqual(fixed.values("in"), [1, 3, 4, 5, 7, 8, 9, 23, 67, 324, 6345]);
  assert.equal(fixed.root.data, 8);
  assert.equal(fixed.depth(8), 0);
  assert.equal(fixed.height(8), 3);
  assert.equal(fixed.find(999), null);
  fixed.deleteItem(8);
  assert.equal(fixed.find(8), null);
  assert.deepEqual(fixed.values("in"), [1, 3, 4, 5, 7, 9, 23, 67, 324, 6345]);
  assert.throws(() => fixed.levelOrder(), TypeError);

  console.log("level:", tree.values("level").join(" "));
  console.log("pre:  ", tree.values("pre").join(" "));
  console.log("post: ", tree.values("post").join(" "));
  console.log("Binary Search Tree: all checks passed.");
}

module.exports = { Tree, Node };
