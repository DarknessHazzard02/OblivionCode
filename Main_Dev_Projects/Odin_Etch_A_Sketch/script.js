// Made by: Hazzard
// Odin Etch-a-Sketch - builds an N x N grid of divs; hovering paints a cell.
// Rainbow mode picks a new random color on every pass and adds 10% opacity per pass
// (fully opaque after 10).

const MAX_SIZE = 100;
const grid = document.getElementById("grid");
const sizeLabel = document.getElementById("size-label");
const modeButton = document.getElementById("mode");
let size = 16;
let rainbow = false;

const randomColor = () => `hsl(${Math.floor(Math.random() * 360)}, 80%, 55%)`;

function paint(cell) {
  if (!rainbow) {
    cell.style.backgroundColor = "#d7263d";
    cell.style.opacity = "1";
    delete cell.dataset.passes;
    return;
  }
  const passes = Math.min(10, Number(cell.dataset.passes || 0) + 1);
  cell.dataset.passes = passes;
  cell.style.backgroundColor = randomColor();
  cell.style.opacity = String(passes / 10);
}

function buildGrid(n) {
  grid.replaceChildren();
  for (let r = 0; r < n; r++) {
    const row = document.createElement("div");
    row.className = "row";
    for (let c = 0; c < n; c++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      row.appendChild(cell);
    }
    grid.appendChild(row);
  }
  sizeLabel.textContent = `${n} x ${n}`;
}

// One listener on the grid instead of one per cell.
grid.addEventListener("mouseover", (event) => {
  if (event.target.classList.contains("cell")) paint(event.target);
});

document.getElementById("resize").addEventListener("click", () => {
  const answer = prompt(`Squares per side (1-${MAX_SIZE}):`, String(size));
  if (answer === null) return;
  const n = Number(answer);
  if (!Number.isInteger(n) || n < 1 || n > MAX_SIZE) {
    alert(`Please enter a whole number from 1 to ${MAX_SIZE}.`);
    return;
  }
  size = n;
  buildGrid(size);
});

modeButton.addEventListener("click", () => {
  rainbow = !rainbow;
  modeButton.textContent = rainbow ? "Mode: rainbow" : "Mode: red";
  modeButton.setAttribute("aria-pressed", String(rainbow));
});

document.getElementById("clear").addEventListener("click", () => buildGrid(size));

buildGrid(size);
