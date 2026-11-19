// Made by: Hazzard
// FreeCodeCamp - Rock, Paper, Scissors Game
// Teaches: Randomization, Conditional Branching, Game Evaluation

const choices = ["Rock", "Paper", "Scissors"];

function getRandomComputerResult() {
  const randomIndex = Math.floor(Math.random() * choices.length);
  return choices[randomIndex];
}

function hasPlayerWonRound(player, computer) {
  return (
    (player === "Rock" && computer === "Scissors") ||
    (player === "Scissors" && computer === "Paper") ||
    (player === "Paper" && computer === "Rock")
  );
}

function playRound(playerChoice) {
  const computerChoice = getRandomComputerResult();

  if (playerChoice === computerChoice) {
    return {
      playerChoice,
      computerChoice,
      result: `It's a tie! Both chose ${playerChoice}.`,
      outcome: "tie"
    };
  }

  if (hasPlayerWonRound(playerChoice, computerChoice)) {
    return {
      playerChoice,
      computerChoice,
      result: `Player wins! ${playerChoice} beats ${computerChoice}.`,
      outcome: "win"
    };
  }

  return {
    playerChoice,
    computerChoice,
    result: `Computer wins! ${computerChoice} beats ${playerChoice}.`,
    outcome: "lose"
  };
}

// Play 5 simulated rounds
console.log("=== Rock Paper Scissors Match ===");
let playerScore = 0;
let computerScore = 0;

for (let round = 1; round <= 5; round++) {
  const playerPick = choices[Math.floor(Math.random() * choices.length)];
  const outcome = playRound(playerPick);
  if (outcome.outcome === "win") playerScore++;
  if (outcome.outcome === "lose") computerScore++;
  console.log(`Round ${round}: ${outcome.result}`);
}

console.log("\nFinal Score -> Player:", playerScore, "| Computer:", computerScore);
