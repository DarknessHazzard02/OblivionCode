// Made by: Hazzard
// The Odin Project - Full Stack JavaScript (Computer Science): Knights Travails.
// Breadth-first search over an 8x8 board for the shortest knight path. Run: node Knights_Travails.js

const assert = require("node:assert/strict");

const MOVES = [[1, 2], [2, 1], [2, -1], [1, -2], [-1, -2], [-2, -1], [-2, 1], [-1, 2]];
const onBoard = ([x, y]) => x >= 0 && x < 8 && y >= 0 && y < 8;
const key = ([x, y]) => `${x},${y}`;

function knightMoves(start, end) {
  if (!onBoard(start) || !onBoard(end)) throw new RangeError("Squares must be [x, y] with 0 <= x, y <= 7.");
  const previous = new Map([[key(start), null]]);
  const queue = [start];
  while (queue.length) {
    const square = queue.shift();
    if (key(square) === key(end)) break;
    for (const [dx, dy] of MOVES) {
      const next = [square[0] + dx, square[1] + dy];
      if (onBoard(next) && !previous.has(key(next))) {
        previous.set(key(next), square);
        queue.push(next);
      }
    }
  }
  const path = [];
  for (let square = end; square; square = previous.get(key(square))) path.unshift(square);
  return path;
}

function describe(path) {
  const lines = [`You made it in ${path.length - 1} moves! Here's your path:`];
  path.forEach((square) => lines.push(`  [${square.join(",")}]`));
  return lines.join("\n");
}

if (require.main === module) {
  assert.equal(knightMoves([0, 0], [1, 2]).length - 1, 1);
  assert.equal(knightMoves([0, 0], [3, 3]).length - 1, 2);
  assert.equal(knightMoves([3, 3], [0, 0]).length - 1, 2);
  assert.equal(knightMoves([0, 0], [7, 7]).length - 1, 6);
  assert.deepEqual(knightMoves([4, 4], [4, 4]), [[4, 4]]);
  const path = knightMoves([3, 3], [4, 3]);
  for (let i = 1; i < path.length; i++) {
    const dx = Math.abs(path[i][0] - path[i - 1][0]);
    const dy = Math.abs(path[i][1] - path[i - 1][1]);
    assert.ok((dx === 1 && dy === 2) || (dx === 2 && dy === 1), "every step must be a legal knight move");
  }
  assert.throws(() => knightMoves([0, 0], [8, 8]), RangeError);
  console.log(describe(knightMoves([0, 0], [7, 7])));
  console.log("Knights Travails: all checks passed.");
}

module.exports = { knightMoves };
