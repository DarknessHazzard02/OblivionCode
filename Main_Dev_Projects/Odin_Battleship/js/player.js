// Made by: Hazzard
// Odin Battleship - Players. The computer never repeats a square and, after a hit,
// tries the four neighbours before going back to random shots.
import createGameboard, { SIZE } from "./gameboard.js";

export function createPlayer(name, isComputer = false) {
  return { name, isComputer, board: createGameboard() };
}

export function createComputerBrain(random = Math.random) {
  const targets = [];

  function chooseMove(enemyBoard) {
    while (targets.length) {
      const [x, y] = targets.shift();
      if (x >= 0 && x < SIZE && y >= 0 && y < SIZE && !enemyBoard.wasAttacked(x, y)) return [x, y];
    }
    const open = [];
    for (let x = 0; x < SIZE; x++) for (let y = 0; y < SIZE; y++) if (!enemyBoard.wasAttacked(x, y)) open.push([x, y]);
    if (!open.length) return null;
    return open[Math.floor(random() * open.length)];
  }

  function report([x, y], result) {
    if (result === "hit") targets.push([x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]);
    if (result === "sunk") targets.length = 0;
  }

  return { chooseMove, report };
}
