// Made by: Hazzard
// FreeCodeCamp Front End Development Libraries - Drum Machine (React)
// Sounds are synthesized in code and encoded as in-memory WAV files, so no audio
// files are needed. Each pad plays its own <audio class="clip"> element, as the
// challenge tests expect.
// Run it: open ../FCC_JS_Runner.html?app=Drum_Machine

const h = React.createElement;

// ==============================================================================
// Pads: key -> sound recipe
// ==============================================================================
const PADS = [
  { key: "Q", name: "Kick",      type: "sine",     freq: 120, end: 40,  dur: 0.35 },
  { key: "W", name: "Snare",     type: "noise",    freq: 0,   end: 0,   dur: 0.2 },
  { key: "E", name: "Hi-Hat",    type: "noise",    freq: 0,   end: 0,   dur: 0.06 },
  { key: "A", name: "Low Tom",   type: "sine",     freq: 180, end: 90,  dur: 0.3 },
  { key: "S", name: "Mid Tom",   type: "sine",     freq: 260, end: 130, dur: 0.25 },
  { key: "D", name: "High Tom",  type: "sine",     freq: 360, end: 180, dur: 0.2 },
  { key: "Z", name: "Clap",      type: "noise",    freq: 0,   end: 0,   dur: 0.12 },
  { key: "X", name: "Bass",      type: "sawtooth", freq: 55,  end: 50,  dur: 0.4 },
  { key: "C", name: "Blip",      type: "square",   freq: 880, end: 440, dur: 0.1 },
];

// ==============================================================================
// Synthesis: pad recipe -> samples -> WAV blob URL for the <audio> element
// ==============================================================================
const SAMPLE_RATE = 22050;

function synthesize(pad) {
  const samples = new Float32Array(Math.floor(SAMPLE_RATE * pad.dur));
  let phase = 0;
  for (let i = 0; i < samples.length; i++) {
    const t = i / SAMPLE_RATE;
    const envelope = Math.pow(0.001, t / pad.dur);
    if (pad.type === "noise") {
      samples[i] = (Math.random() * 2 - 1) * envelope;
      continue;
    }
    phase += (pad.freq * Math.pow(pad.end / pad.freq, t / pad.dur)) / SAMPLE_RATE;
    const p = phase % 1;
    const wave = pad.type === "sine" ? Math.sin(2 * Math.PI * p)
      : pad.type === "square" ? (p < 0.5 ? 1 : -1)
      : 2 * p - 1;
    samples[i] = wave * envelope * 0.8;
  }
  return samples;
}

function toWavUrl(samples) {
  const view = new DataView(new ArrayBuffer(44 + samples.length * 2));
  const writeText = (offset, text) => [...text].forEach((c, i) => view.setUint8(offset + i, c.charCodeAt(0)));
  writeText(0, "RIFF");
  view.setUint32(4, 36 + samples.length * 2, true);
  writeText(8, "WAVE");
  writeText(12, "fmt ");
  view.setUint32(16, 16, true);              // fmt chunk size
  view.setUint16(20, 1, true);               // PCM
  view.setUint16(22, 1, true);               // mono
  view.setUint32(24, SAMPLE_RATE, true);
  view.setUint32(28, SAMPLE_RATE * 2, true); // byte rate
  view.setUint16(32, 2, true);               // block align
  view.setUint16(34, 16, true);              // bits per sample
  writeText(36, "data");
  view.setUint32(40, samples.length * 2, true);
  samples.forEach((s, i) => view.setInt16(44 + i * 2, Math.max(-1, Math.min(1, s)) * 0x7fff, true));
  return URL.createObjectURL(new Blob([view], { type: "audio/wav" }));
}

const CLIP_URLS = Object.fromEntries(PADS.map((pad) => [pad.key, toWavUrl(synthesize(pad))]));

function playClip(pad, volume) {
  const clip = document.getElementById(pad.key);
  clip.volume = volume;
  clip.currentTime = 0;
  clip.play().catch((err) => console.warn(`Could not play ${pad.name}: ${err.message}`));
}

// ==============================================================================
// Components
// ==============================================================================
function DrumPad({ pad, onPlay, active }) {
  return h("button", {
      id: pad.name.replace(/\s+/g, "-"),
      className: "drum-pad" + (active ? " active" : ""),
      onClick: () => onPlay(pad),
    },
    pad.key,
    h("audio", { className: "clip", id: pad.key, src: CLIP_URLS[pad.key], preload: "auto" })
  );
}

function DrumMachine() {
  const [display, setDisplay] = React.useState("Press a key");
  const [volume, setVolume] = React.useState(0.6);
  const [active, setActive] = React.useState(null);

  const play = React.useCallback((pad) => {
    playClip(pad, volume);
    setDisplay(pad.name);
    setActive(pad.key);
    setTimeout(() => setActive(null), 120);
  }, [volume]);

  React.useEffect(() => {
    const onKey = (e) => {
      const pad = PADS.find((p) => p.key === e.key.toUpperCase());
      if (pad) play(pad);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [play]);

  return h("div", { id: "drum-machine", className: "card" },
    h("div", { className: "pad-grid" },
      PADS.map((pad) => h(DrumPad, { key: pad.key, pad, onPlay: play, active: active === pad.key }))
    ),
    h("div", { className: "controls" },
      h("p", { id: "display", className: "display" }, display),
      h("label", null, "Volume ",
        h("input", {
          type: "range", min: 0.05, max: 1, step: 0.05, value: volume,
          onChange: (e) => setVolume(Number(e.target.value)),
        })
      )
    )
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(h(DrumMachine));
