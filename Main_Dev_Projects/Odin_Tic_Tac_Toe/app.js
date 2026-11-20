// Made by: Hazzard
// Odin Tic Tac Toe - Gameboard and DisplayController are single instances (IIFE module
// pattern); players come from a factory. The game logic never touches the DOM.

// ==============================================================================
// Game logic
// ==============================================================================
const Gameboard = (() => {
  const board = Array(9).fill("");
  const getBoard = () => [...board];
  const place = (index, mark) => {
    if (index < 0 || index > 8 || board[index] !== "") return false;
    board[index] = mark;
    return true;
  };
  const reset = () => board.fill("");
  return { getBoard, place, reset };
})();

const createPlayer = (name, mark) => ({ name, mark });

const LINES = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]];

const GameController = (() => {
  let players = [createPlayer("Player 1", "X"), createPlayer("Player 2", "O")];
  let current = 0;
  let result = null; // null while playing, then { winner, line } or { tie: true }

  const start = (nameX, nameO) => {
    players = [createPlayer(nameX, "X"), createPlayer(nameO, "O")];
    current = 0;
    result = null;
    Gameboard.reset();
  };

  const checkResult = () => {
    const board = Gameboard.getBoard();
    const line = LINES.find(([a, b, c]) => board[a] && board[a] === board[b] && board[a] === board[c]);
    if (line) return { winner: players[current], line };
    if (board.every((cell) => cell !== "")) return { tie: true };
    return null;
  };

  const playRound = (index) => {
    if (result || !Gameboard.place(index, players[current].mark)) return false;
    result = checkResult();
    if (!result) current = 1 - current;
    return true;
  };

  return { start, playRound, getCurrent: () => players[current], getResult: () => result };
})();

// ==============================================================================
// Display
// ==============================================================================
const DisplayController = (() => {
  const boardEl = document.getElementById("board");
  const statusEl = document.getElementById("status");

  const render = () => {
    const board = Gameboard.getBoard();
    const result = GameController.getResult();
    boardEl.replaceChildren(...board.map((mark, index) => {
      const cell = document.createElement("button");
      cell.className = `cell${mark === "O" ? " o" : ""}${result?.line?.includes(index) ? " win" : ""}`;
      cell.textContent = mark;
      cell.dataset.index = index;
      cell.disabled = Boolean(mark || result);
      cell.setAttribute("aria-label", mark ? `Square ${index + 1}: ${mark}` : `Square ${index + 1}: empty`);
      return cell;
    }));
    if (result?.winner) statusEl.textContent = `${result.winner.name} (${result.winner.mark}) wins!`;
    else if (result?.tie) statusEl.textContent = "It's a tie.";
    else statusEl.textContent = `${GameController.getCurrent().name}'s turn (${GameController.getCurrent().mark})`;
  };

  boardEl.addEventListener("click", (event) => {
    const cell = event.target.closest(".cell");
    if (cell && GameController.playRound(Number(cell.dataset.index))) render();
  });

  document.getElementById("players").addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(event.target);
    GameController.start(data.get("x").trim() || "Player 1", data.get("o").trim() || "Player 2");
    render();
  });

  return { render };
})();

DisplayController.render();
window.ticTacToe = { Gameboard, GameController };
