// Made by: Hazzard
// Odin Battleship - Ship factory: length, hits, sunk state.

export default function createShip(length) {
  if (!Number.isInteger(length) || length < 1) throw new RangeError("Ship length must be a positive integer.");
  let hits = 0;
  return {
    length,
    hit() {
      if (hits < length) hits += 1;
    },
    getHits: () => hits,
    isSunk: () => hits >= length,
  };
}
