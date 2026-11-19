// Made by: Hazzard
// FreeCodeCamp Front End Development Libraries - 25 + 5 Clock (React)
// Pomodoro timer: session/break lengths 1-60 min, start/stop, reset, beep.
// Run it: open ../../HTML/freecodecamp/FCC_JS_Runner.html?app=Pomodoro_25_5_Clock

const h = React.createElement;

// ==============================================================================
// Helpers
// ==============================================================================
const fmt = (secs) =>
  String(Math.floor(secs / 60)).padStart(2, "0") + ":" + String(secs % 60).padStart(2, "0");

// 1.2 s, 880 Hz tone encoded as an in-memory WAV for the <audio id="beep"> element.
function makeBeepUrl(rate = 22050, seconds = 1.2) {
  const n = Math.floor(rate * seconds);
  const view = new DataView(new ArrayBuffer(44 + n * 2));
  const writeText = (offset, text) => [...text].forEach((c, i) => view.setUint8(offset + i, c.charCodeAt(0)));
  writeText(0, "RIFF");
  view.setUint32(4, 36 + n * 2, true);
  writeText(8, "WAVE");
  writeText(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, rate, true);
  view.setUint32(28, rate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeText(36, "data");
  view.setUint32(40, n * 2, true);
  for (let i = 0; i < n; i++) {
    const t = i / rate;
    const sample = Math.sin(2 * Math.PI * 880 * t) * Math.pow(0.001, t / seconds) * 0.5;
    view.setInt16(44 + i * 2, sample * 0x7fff, true);
  }
  return URL.createObjectURL(new Blob([view], { type: "audio/wav" }));
}
const BEEP_URL = makeBeepUrl();

// ==============================================================================
// Components
// ==============================================================================
function LengthControl({ label, prefix, value, onChange, disabled }) {
  return h("div", { className: "length" },
    h("p", { id: `${prefix}-label` }, label),
    h("div", { className: "row" },
      h("button", { id: `${prefix}-decrement`, className: "btn ghost", disabled, onClick: () => onChange(Math.max(1, value - 1)) }, "-"),
      h("span", { id: `${prefix}-length`, className: "display" }, value),
      h("button", { id: `${prefix}-increment`, className: "btn ghost", disabled, onClick: () => onChange(Math.min(60, value + 1)) }, "+")
    )
  );
}

function Clock() {
  const [breakLen, setBreakLen] = React.useState(5);
  const [sessionLen, setSessionLen] = React.useState(25);
  const [mode, setMode] = React.useState("Session");
  const [left, setLeft] = React.useState(25 * 60);
  const [running, setRunning] = React.useState(false);
  const beepRef = React.useRef(null);

  React.useEffect(() => {
    if (!running) return undefined;
    const id = setInterval(() => setLeft((secs) => secs - 1), 1000);
    return () => clearInterval(id);
  }, [running]);

  // Beep on 00:00; one tick later switch Session <-> Break. Layout effect so -1 never paints.
  React.useLayoutEffect(() => {
    if (left === 0 && beepRef.current) {
      beepRef.current.currentTime = 0;
      beepRef.current.play().catch((err) => console.warn(`Could not play beep: ${err.message}`));
    }
    if (left >= 0) return;
    const next = mode === "Session" ? "Break" : "Session";
    setMode(next);
    setLeft((next === "Session" ? sessionLen : breakLen) * 60);
  }, [left]);

  const changeSession = (v) => { setSessionLen(v); if (mode === "Session") setLeft(v * 60); };
  const changeBreak = (v) => { setBreakLen(v); if (mode === "Break") setLeft(v * 60); };

  const reset = () => {
    if (beepRef.current) {
      beepRef.current.pause();
      beepRef.current.currentTime = 0;
    }
    setRunning(false);
    setBreakLen(5);
    setSessionLen(25);
    setMode("Session");
    setLeft(25 * 60);
  };

  return h("div", { className: "card clock" },
    h("div", { className: "row" },
      h(LengthControl, { label: "Break Length", prefix: "break", value: breakLen, onChange: changeBreak, disabled: running }),
      h(LengthControl, { label: "Session Length", prefix: "session", value: sessionLen, onChange: changeSession, disabled: running })
    ),
    h("p", { id: "timer-label", className: "muted" }, mode),
    h("p", { id: "time-left", className: "display big" + (left < 60 ? " warn" : "") }, fmt(left)),
    h("div", { className: "row" },
      h("button", { id: "start_stop", className: "btn", onClick: () => setRunning((r) => !r) }, running ? "Pause" : "Start"),
      h("button", { id: "reset", className: "btn ghost", onClick: reset }, "Reset")
    ),
    h("audio", { id: "beep", src: BEEP_URL, preload: "auto", ref: beepRef })
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(h(Clock));
