// Made by: Hazzard
// Odin Rock Paper Scissors - game logic kept in pure functions, DOM wiring at the bottom.

const MOVES = ["rock", "paper", "scissors"];
const BEATS = { rock: "scissors", paper: "rock", scissors: "paper" };
const WINNING_SCORE = 5;

// ==============================================================================
// Game logic
// ==============================================================================
function getComputerChoice() {
  return MOVES[Math.floor(Math.random() * MOVES.length)];
}

// Returns "human", "computer" or "tie".
function playRound(human, computer) {
  if (human === computer) return "tie";
  return BEATS[human] === computer ? "human" : "computer";
}

const capitalize = (word) => word[0].toUpperCase() + word.slice(1);

// ==============================================================================
// UI
// ==============================================================================
const score = { human: 0, computer: 0 };
const humanScore = document.getElementById("human-score");
const computerScore = document.getElementById("computer-score");
const roundText = document.getElementById("round");
const winnerText = document.getElementById("winner");
const resetButton = document.getElementById("reset");
const choiceButtons = document.querySelectorAll(".choice");

function render() {
  humanScore.textContent = score.human;
  computerScore.textContent = score.computer;
}

function onChoice(human) {
  const computer = getComputerChoice();
  const result = playRound(human, computer);
  if (result !== "tie") score[result] += 1;

  roundText.textContent =
    result === "tie" ? `Tie: both chose ${human}.`
    : result === "human" ? `You win the round: ${capitalize(human)} beats ${computer}.`
    : `You lose the round: ${capitalize(computer)} beats ${human}.`;
  render();

  if (score.human === WINNING_SCORE || score.computer === WINNING_SCORE) {
    winnerText.textContent = score.human === WINNING_SCORE ? "You won the game!" : "The computer won the game.";
    choiceButtons.forEach((button) => { button.disabled = true; });
    resetButton.hidden = false;
  }
}

choiceButtons.forEach((button) => {
  button.addEventListener("click", () => onChoice(button.dataset.choice));
});

resetButton.addEventListener("click", () => {
  score.human = 0;
  score.computer = 0;
  roundText.textContent = "Pick a move to start.";
  winnerText.textContent = "";
  choiceButtons.forEach((button) => { button.disabled = false; });
  resetButton.hidden = true;
  render();
});
