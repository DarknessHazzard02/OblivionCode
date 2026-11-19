// Made by: Hazzard
// Odin Calculator - evaluates a single pair of numbers at a time, left to right
// (12 + 7 - 1 = 18, as the Odin spec asks), with decimals, backspace and keyboard.

// ==============================================================================
// Math
// ==============================================================================
const add = (a, b) => a + b;
const subtract = (a, b) => a - b;
const multiply = (a, b) => a * b;
const divide = (a, b) => (b === 0 ? null : a / b);
const OPS = { "+": add, "-": subtract, "*": multiply, "/": divide };
const SYMBOLS = { "+": "+", "-": "−", "*": "×", "/": "÷" };

// Returns null when the result is undefined or not representable (division by zero, overflow).
function operate(operator, a, b) {
  const result = OPS[operator](a, b);
  if (result === null || !Number.isFinite(result)) return null;
  const rounded = Math.round(result * 1e10) / 1e10;
  return Number.isFinite(rounded) ? rounded : result;
}

// ==============================================================================
// State
// ==============================================================================
const state = { first: null, operator: null, current: "0", fresh: true };
const display = document.getElementById("display");
const history = document.getElementById("history");

function render() {
  display.textContent = state.current;
  history.textContent = state.operator ? `${state.first} ${SYMBOLS[state.operator]}` : "";
  document.querySelectorAll(".key--op").forEach((key) => {
    key.classList.toggle("active", state.fresh && key.dataset.op === state.operator);
  });
}

function clearAll() {
  Object.assign(state, { first: null, operator: null, current: "0", fresh: true });
}

function inputDigit(digit) {
  if (state.current === "Nope" || state.fresh) {
    state.current = digit;
    state.fresh = false;
  } else if (state.current.replace(/[-.]/g, "").length < 14) {
    state.current = state.current === "0" ? digit : state.current + digit;
  }
}

function inputDot() {
  if (state.fresh || state.current === "Nope") {
    state.current = "0.";
    state.fresh = false;
  } else if (!state.current.includes(".")) {
    state.current += ".";
  }
}

function backspace() {
  if (state.fresh) return;
  state.current = state.current.length > 1 ? state.current.slice(0, -1) : "0";
  if (state.current === "-") state.current = "0";
}

// Runs the pending operation; returns false when it was a division by zero.
function evaluatePending() {
  if (state.operator === null || state.fresh) return true;
  const result = operate(state.operator, Number(state.first), Number(state.current));
  if (result === null) {
    clearAll();
    state.current = "Nope";
    return false;
  }
  state.current = String(result);
  return true;
}

function chooseOperator(op) {
  if (state.current === "Nope") return;
  if (!evaluatePending()) return;
  state.first = state.current;
  state.operator = op;
  state.fresh = true;
}

function equals() {
  if (state.operator === null || state.fresh) return;
  if (!evaluatePending()) return;
  state.first = null;
  state.operator = null;
  state.fresh = true;
}

// ==============================================================================
// Input
// ==============================================================================
function handle(action) {
  if (/^\d$/.test(action)) inputDigit(action);
  else if (action in OPS) chooseOperator(action);
  else if (action === ".") inputDot();
  else if (action === "=") equals();
  else if (action === "back") backspace();
  else if (action === "clear") clearAll();
  render();
}

document.querySelector(".keys").addEventListener("click", (event) => {
  const key = event.target.closest("button");
  if (!key) return;
  const { digit, op, action } = key.dataset;
  handle(digit ?? op ?? { dot: ".", equals: "=" }[action] ?? action);
});

document.addEventListener("keydown", (event) => {
  const map = { Enter: "=", "=": "=", Backspace: "back", Escape: "clear", ",": "." };
  const action = map[event.key] ?? event.key;
  if (/^\d$/.test(action) || action in OPS || ["=", ".", "back", "clear"].includes(action)) {
    event.preventDefault();
    handle(action);
  }
});

render();

// Exposed for quick checks in the browser console.
window.calculator = { operate, handle, state };
