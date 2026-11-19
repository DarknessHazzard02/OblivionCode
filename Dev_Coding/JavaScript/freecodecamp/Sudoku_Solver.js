// FreeCodeCamp Quality Assurance - Sudoku Solver
// Validates 81-character puzzle strings and solves using recursive backtracking algorithm

class SudokuSolver {
  validate(puzzleString) {
    if (!puzzleString) {
      return { error: "Required field missing" };
    }
    if (puzzleString.length !== 81) {
      return { error: "Expected puzzle to be 81 characters long" };
    }
    if (/[^1-9.]/.test(puzzleString)) {
      return { error: "Invalid characters in puzzle" };
    }
    return { valid: true };
  }

  checkRowPlacement(grid, row, col, value) {
    for (let c = 0; c < 9; c++) {
      if (grid[row][c] === value && c !== col) return false;
    }
    return true;
  }

  checkColPlacement(grid, row, col, value) {
    for (let r = 0; r < 9; r++) {
      if (grid[r][col] === value && r !== row) return false;
    }
    return true;
  }

  checkRegionPlacement(grid, row, col, value) {
    const startRow = Math.floor(row / 3) * 3;
    const startCol = Math.floor(col / 3) * 3;

    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        const currR = startRow + r;
        const currC = startCol + c;
        if (grid[currR][currC] === value && (currR !== row || currC !== col)) {
          return false;
        }
      }
    }
    return true;
  }

  isValid(grid, row, col, value) {
    return (
      this.checkRowPlacement(grid, row, col, value) &&
      this.checkColPlacement(grid, row, col, value) &&
      this.checkRegionPlacement(grid, row, col, value)
    );
  }

  solve(puzzleString) {
    const validation = this.validate(puzzleString);
    if (!validation.valid) return validation;

    const grid = [];
    for (let r = 0; r < 9; r++) {
      grid.push(puzzleString.slice(r * 9, (r + 1) * 9).split(""));
    }

    const backtrack = (r, c) => {
      if (r === 9) return true;
      const nextR = c === 8 ? r + 1 : r;
      const nextC = c === 8 ? 0 : c + 1;

      if (grid[r][c] !== ".") {
        return backtrack(nextR, nextC);
      }

      for (let num = 1; num <= 9; num++) {
        const val = String(num);
        if (this.isValid(grid, r, c, val)) {
          grid[r][c] = val;
          if (backtrack(nextR, nextC)) return true;
          grid[r][c] = ".";
        }
      }

      return false;
    };

    if (backtrack(0, 0)) {
      return { solution: grid.flat().join("") };
    } else {
      return { error: "Puzzle cannot be solved" };
    }
  }

  prettyPrint(puzzleString) {
    let result = "";
    for (let r = 0; r < 9; r++) {
      const row = puzzleString.slice(r * 9, (r + 1) * 9).split("");
      result += row.slice(0, 3).join(" ") + " | " + row.slice(3, 6).join(" ") + " | " + row.slice(6, 9).join(" ") + "\n";
      if (r === 2 || r === 5) result += "------+-------+------\n";
    }
    return result;
  }
}

// Tests
const solver = new SudokuSolver();
const samplePuzzle = "..9..5.1.85.4....2432......1...69.83.9.....6.62.71...9......1945....4.37.4.3..6..";

console.log("=== Original Sudoku Puzzle ===");
console.log(solver.prettyPrint(samplePuzzle));

const solved = solver.solve(samplePuzzle);
if (solved.solution) {
  console.log("=== Solved Sudoku Puzzle ===");
  console.log(solver.prettyPrint(solved.solution));
} else {
  console.log("Error:", solved.error);
}
