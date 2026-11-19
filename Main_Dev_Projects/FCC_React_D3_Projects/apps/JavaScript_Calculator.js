// Made by: Hazzard
// FreeCodeCamp Front End Development Libraries - JavaScript Calculator (React)
// Uses formula logic (3 + 5 * 6 = 33). Expressions are evaluated with a
// shunting-yard parser instead of eval().
// Run it: open ../FCC_JS_Runner.html?app=JavaScript_Calculator

const h = React.createElement;

// ==============================================================================
// Evaluator
// ==============================================================================
const PRECEDENCE = { "+": 1, "-": 1, "*": 2, "/": 2 };

function tokenize(expr) {
  // A "-" is a unary sign when it starts the expression or follows an operator.
  // Numbers may carry an exponent (1e-7) because String() of a tiny or huge result uses one.
  return expr.match(/(?<=^|[+\-*/])-?\d*\.?\d+(?:e[+-]?\d+)?|[+\-*/]/g) || [];
}

function evaluate(expr) {
  const output = [];
  const ops = [];
  for (const tok of tokenize(expr)) {
    if (tok in PRECEDENCE) {
      while (ops.length && PRECEDENCE[ops[ops.length - 1]] >= PRECEDENCE[tok]) {
        output.push(ops.pop());
      }
      ops.push(tok);
    } else {
      output.push(parseFloat(tok));
    }
  }
  while (ops.length) output.push(ops.pop());

  const stack = [];
  for (const tok of output) {
    if (typeof tok === "number") { stack.push(tok); continue; }
    const b = stack.pop();
    const a = stack.pop();
    stack.push(tok === "+" ? a + b : tok === "-" ? a - b : tok === "*" ? a * b : a / b);
  }
  const result = stack[0];
  return Number.isFinite(result) ? parseFloat(result.toPrecision(12)) : NaN;
}

// ==============================================================================
// Input rules (from the challenge user stories)
// ==============================================================================
function applyKey(state, key) {
  const { formula, done } = state;
  const isOp = /[+\-*/]/.test(key);

  if (key === "AC") return { formula: "", display: "0", done: false };

  if (key === "=") {
    if (!formula || /[+\-*/]$/.test(formula)) return state;
    const result = evaluate(formula);
    return { formula: Number.isNaN(result) ? "" : String(result), display: Number.isNaN(result) ? "Error" : String(result), done: true };
  }

  if (isOp) {
    let base = formula || "0";
    if (key === "-" && /[+*/]$/.test(base)) {
      base += "-";                                    // allow 5 * -2
    } else {
      base = base.replace(/[+\-*/]+$/, "") + key;      // last operator wins
    }
    return { formula: base, display: key, done: false };
  }

  // Digits and decimal point
  let start = done ? "" : formula;
  const current = (start.match(/-?\d*\.?\d*$/) || [""])[0].replace(/^-/, "");
  if (key === "." && current.includes(".")) return state;
  if (key === "0" && current === "0") return state;
  if (current === "0" && key !== ".") start = start.slice(0, -1);
  const next = start + (key === "." && current === "" ? "0." : key);
  return { formula: next, display: (next.match(/-?\d*\.?\d*$/) || [next])[0] || "0", done: false };
}

// ==============================================================================
// Component
// ==============================================================================
const KEYS = [
  ["clear", "AC"], ["divide", "/"], ["multiply", "*"], ["seven", "7"],
  ["eight", "8"], ["nine", "9"], ["subtract", "-"], ["four", "4"],
  ["five", "5"], ["six", "6"], ["add", "+"], ["one", "1"],
  ["two", "2"], ["three", "3"], ["equals", "="], ["zero", "0"], ["decimal", "."],
];

function Calculator() {
  const [state, setState] = React.useState({ formula: "", display: "0", done: false });

  return h("div", { className: "card calc" },
    h("div", { className: "formula muted" }, state.formula || " "),
    h("div", { id: "display", className: "display" }, state.display),
    h("div", { className: "calc-grid" },
      KEYS.map(([id, label]) =>
        h("button", {
          key: id, id,
          className: "btn" + (/[+\-*/=]|AC/.test(label) ? "" : " ghost"),
          onClick: () => setState((s) => applyKey(s, label)),
        }, label)
      )
    )
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(h(Calculator));
