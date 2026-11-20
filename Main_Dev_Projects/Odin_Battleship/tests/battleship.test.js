// Made by: Hazzard
// Odin Battleship - tests for the game logic with node's built-in runner (no Jest, no install).
// Run from the project folder: node --test (or npm test)
import { test } from "node:test";
import assert from "node:assert/strict";
import createShip from "../js/ship.js";
import createGameboard, { FLEET, SIZE } from "../js/gameboard.js";
import { createComputerBrain } from "../js/player.js";

test("ship sinks after as many hits as its length", () => {
  const ship = createShip(3);
  ship.hit();
  ship.hit();
  assert.equal(ship.isSunk(), false);
  ship.hit();
  assert.equal(ship.isSunk(), true);
  ship.hit();
  assert.equal(ship.getHits(), 3, "extra hits are not counted");
  assert.throws(() => createShip(0), RangeError);
});

test("ships cannot overlap or leave the board", () => {
  const board = createGameboard();
  assert.equal(board.placeShip(0, 0, 3, true), true);
  assert.equal(board.placeShip(1, 0, 2, false), false, "overlap");
  assert.equal(board.placeShip(8, 5, 3, true), false, "off the right edge");
  assert.equal(board.placeShip(5, 9, 2, false), false, "off the bottom edge");
});

test("attacks report miss, hit and sunk, and never count twice", () => {
  const board = createGameboard();
  board.placeShip(2, 2, 2, false);
  assert.equal(board.receiveAttack(0, 0), "miss");
  assert.equal(board.receiveAttack(0, 0), null);
  assert.equal(board.receiveAttack(2, 2), "hit");
  assert.equal(board.allSunk(), false);
  assert.equal(board.receiveAttack(2, 3), "sunk");
  assert.equal(board.allSunk(), true);
  assert.deepEqual(board.getMisses(), [[0, 0]]);
  assert.equal(board.receiveAttack(-1, 4), null);
});

test("random fleet places every ship", () => {
  const board = createGameboard();
  board.placeFleetRandomly();
  assert.equal(board.shipCount(), FLEET.length);
  let shipCells = 0;
  for (let x = 0; x < SIZE; x++) for (let y = 0; y < SIZE; y++) if (board.hasShipAt(x, y)) shipCells += 1;
  assert.equal(shipCells, FLEET.reduce((a, b) => a + b, 0));
});

test("computer never repeats a square and can clear a whole board", () => {
  const board = createGameboard();
  board.placeFleetRandomly();
  const brain = createComputerBrain();
  const seen = new Set();
  for (let turn = 0; turn < SIZE * SIZE; turn++) {
    const move = brain.chooseMove(board);
    assert.ok(!seen.has(move.join(",")), `repeated ${move}`);
    seen.add(move.join(","));
    brain.report(move, board.receiveAttack(...move));
  }
  assert.equal(brain.chooseMove(board), null);
  assert.equal(board.allSunk(), true);
});
