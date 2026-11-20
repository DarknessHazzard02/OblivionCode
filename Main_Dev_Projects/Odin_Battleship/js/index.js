// Made by: Hazzard
// Odin Battleship - DOM layer: draws both boards, takes the human's clicks, plays the computer's turn.
import { SIZE } from "./gameboard.js";
import { createPlayer, createComputerBrain } from "./player.js";

const humanEl = document.getElementById("human-board");
const enemyEl = document.getElementById("enemy-board");
const statusEl = document.getElementById("status");
const newGameButton = document.getElementById("new-game");

let human;
let computer;
let brain;
let over;
let busy;

function newGame() {
  human = createPlayer("You");
  computer = createPlayer("Computer", true);
  brain = createComputerBrain();
  human.board.placeFleetRandomly();
  computer.board.placeFleetRandomly();
  over = false;
  busy = false;
  statusEl.textContent = "Your turn: fire at the enemy waters.";
  render();
}

function drawBoard(container, board, revealShips) {
  const cells = [];
  for (let y = 0; y < SIZE; y++) {
    for (let x = 0; x < SIZE; x++) {
      const cell = document.createElement("button");
      cell.className = "cell";
      cell.dataset.x = x;
      cell.dataset.y = y;
      const attacked = board.wasAttacked(x, y);
      const ship = board.hasShipAt(x, y);
      if (revealShips && ship) cell.classList.add("ship");
      if (attacked) cell.classList.add(ship ? "hit" : "miss");
      cell.disabled = revealShips || attacked || over;
      cell.setAttribute("aria-label", `${String.fromCharCode(65 + x)}${y + 1}${attacked ? (ship ? " hit" : " miss") : ""}`);
      cells.push(cell);
    }
  }
  container.replaceChildren(...cells);
}

function render() {
  drawBoard(humanEl, human.board, true);
  drawBoard(enemyEl, computer.board, false);
}

function finish(text) {
  over = true;
  statusEl.textContent = text;
  render();
}

function computerTurn() {
  const move = brain.chooseMove(human.board);
  const result = human.board.receiveAttack(...move);
  brain.report(move, result);
  busy = false;
  if (human.board.allSunk()) return finish("The computer sank your fleet. Press New game to try again.");
  statusEl.textContent = `Computer fired at ${String.fromCharCode(65 + move[0])}${move[1] + 1}: ${result}. Your turn.`;
  render();
}

enemyEl.addEventListener("click", (event) => {
  const cell = event.target.closest(".cell");
  if (!cell || over || busy) return;
  const result = computer.board.receiveAttack(Number(cell.dataset.x), Number(cell.dataset.y));
  if (result === null) return;
  if (computer.board.allSunk()) return finish("You sank the whole enemy fleet!");
  statusEl.textContent = `You: ${result}. Computer is aiming...`;
  busy = true;
  render();
  setTimeout(computerTurn, 350);
});

newGameButton.addEventListener("click", newGame);
newGame();
