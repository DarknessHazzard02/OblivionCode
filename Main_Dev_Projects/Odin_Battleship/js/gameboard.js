// Made by: Hazzard
// Odin Battleship - Gameboard: places ships, receives attacks, tracks misses and whether all ships sank.
import createShip from "./ship.js";

export const SIZE = 10;
export const FLEET = [5, 4, 3, 3, 2];

const key = (x, y) => `${x},${y}`;
const inBounds = (x, y) => x >= 0 && x < SIZE && y >= 0 && y < SIZE;

export default function createGameboard() {
  const cells = new Map(); // "x,y" -> ship
  const ships = [];
  const attacked = new Set();
  const misses = [];
  const hits = [];

  function cellsFor(x, y, length, horizontal) {
    return Array.from({ length }, (_, i) => (horizontal ? [x + i, y] : [x, y + i]));
  }

  function canPlace(x, y, length, horizontal) {
    return cellsFor(x, y, length, horizontal).every(([cx, cy]) => inBounds(cx, cy) && !cells.has(key(cx, cy)));
  }

  function placeShip(x, y, length, horizontal = true) {
    if (!canPlace(x, y, length, horizontal)) return false;
    const ship = createShip(length);
    cellsFor(x, y, length, horizontal).forEach(([cx, cy]) => cells.set(key(cx, cy), ship));
    ships.push(ship);
    return true;
  }

  // Returns "miss", "hit", "sunk", or null when the square is invalid or already attacked.
  function receiveAttack(x, y) {
    if (!inBounds(x, y) || attacked.has(key(x, y))) return null;
    attacked.add(key(x, y));
    const ship = cells.get(key(x, y));
    if (!ship) {
      misses.push([x, y]);
      return "miss";
    }
    ship.hit();
    hits.push([x, y]);
    return ship.isSunk() ? "sunk" : "hit";
  }

  function placeFleetRandomly(fleet = FLEET, random = Math.random) {
    fleet.forEach((length) => {
      for (let tries = 0; tries < 1000; tries++) {
        const horizontal = random() < 0.5;
        const x = Math.floor(random() * SIZE);
        const y = Math.floor(random() * SIZE);
        if (placeShip(x, y, length, horizontal)) return;
      }
      throw new Error(`Could not place a ship of length ${length}.`);
    });
  }

  return {
    placeShip,
    canPlace,
    receiveAttack,
    placeFleetRandomly,
    allSunk: () => ships.length > 0 && ships.every((ship) => ship.isSunk()),
    hasShipAt: (x, y) => cells.has(key(x, y)),
    wasAttacked: (x, y) => attacked.has(key(x, y)),
    getMisses: () => misses.map((m) => [...m]),
    getHits: () => hits.map((h) => [...h]),
    shipCount: () => ships.length,
  };
}
