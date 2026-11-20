// Made by: Hazzard
// S&OP KPI Dashboard - loads data/meta.json and data/dashboard.json, validates them, and draws
// KPI cards, two SVG charts, a paginated detail table with CSV export and an inventory table.
// Clicking a bar (or a chip) filters every visual by line. Missing data shows as degraded, never as 0.

const CONFIG = {
  dataUrls: { meta: "data/meta.json", data: "data/dashboard.json" },
  pageSize: 10,
  adherenceTarget: 0.95,
};
const PRODUCTION_FIELDS = ["date", "line", "item", "planned_qty", "actual_qty", "good_qty", "planned_min", "run_min", "ideal_cycle_sec"];
const INVENTORY_FIELDS = ["item", "family", "on_hand", "forecast_daily", "safety_stock"];
const state = { production: [], inventory: [], line: null, page: 0 };

// ==============================================================================
// Helpers
// ==============================================================================
const $ = (id) => document.getElementById(id);
const pct = (v) => (v === null ? "—" : `${(v * 100).toFixed(1)}%`);
const sum = (rows, f) => rows.reduce((total, r) => total + f(r), 0);
const divide = (a, b) => (b ? a / b : null);
const SVG_NS = "http://www.w3.org/2000/svg";

function el(tag, props = {}, ...children) {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
}

function svg(tag, attrs = {}, text) {
  const node = document.createElementNS(SVG_NS, tag);
  Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, v));
  if (text !== undefined) node.textContent = text;
  return node;
}

// ==============================================================================
// KPIs
// ==============================================================================
function oee(rows) {
  const planned = sum(rows, (r) => r.planned_min);
  const run = sum(rows, (r) => r.run_min);
  const ideal = sum(rows, (r) => (r.ideal_cycle_sec * r.actual_qty) / 60);
  const actual = sum(rows, (r) => r.actual_qty);
  const good = sum(rows, (r) => r.good_qty);
  const a = divide(run, planned);
  const p = divide(ideal, run);
  const q = divide(good, actual);
  return a === null || p === null || q === null ? null : a * p * q;
}

function adherence(rows) {
  return divide(sum(rows, (r) => Math.min(r.actual_qty, r.planned_qty)), sum(rows, (r) => r.planned_qty));
}

function coverageStatus(item) {
  if (item.forecast_daily === 0) return "NO_DEMAND";
  return item.on_hand < item.safety_stock ? "BELOW_SAFETY" : "OK";
}

// ==============================================================================
// Render
// ==============================================================================
const filtered = () => state.production.filter((r) => !state.line || r.line === state.line);
const lines = () => [...new Set(state.production.map((r) => r.line))].sort();

function renderFilters() {
  const chips = [null, ...lines()].map((line) => {
    const chip = el("button", { className: "chip", textContent: line ?? "All Lines" });
    chip.setAttribute("aria-pressed", String(state.line === line));
    chip.addEventListener("click", () => setLine(line));
    return chip;
  });
  $("line-filter").replaceChildren(...chips);
}

function kpiCard(label, value, note, missingNote = "No data for this filter.") {
  const missing = value === "—";
  return el("article", { className: `kpi${missing ? " kpi--missing" : ""}` },
    el("div", { className: "kpi__label", textContent: label }),
    el("div", { className: "kpi__value", textContent: value }),
    el("div", { className: "kpi__note", textContent: missing ? missingNote : note }));
}

function renderKpis() {
  const rows = filtered();
  const covered = state.inventory.filter((i) => i.forecast_daily > 0);
  const avgCoverage = covered.length ? sum(covered, (i) => i.on_hand / i.forecast_daily) / covered.length : null;
  const below = state.inventory.filter((i) => coverageStatus(i) === "BELOW_SAFETY").length;
  $("kpis").replaceChildren(
    kpiCard("OEE", pct(oee(rows)), `${rows.length} line-days`),
    kpiCard("Schedule Adherence", pct(adherence(rows)), `Target ${pct(CONFIG.adherenceTarget)}`),
    kpiCard("Avg Days of Coverage", avgCoverage === null ? "—" : avgCoverage.toFixed(1), `${covered.length} items with demand (all lines)`),
    kpiCard("Items Below Safety", String(below), `of ${state.inventory.length} items (all lines)`));
}

function renderOeeChart() {
  const data = lines().map((line) => ({ line, value: oee(state.production.filter((r) => r.line === line)) }));
  const width = 480;
  const height = 220;
  const pad = { top: 24, bottom: 28, left: 8 };
  const barWidth = (width - pad.left * 2) / data.length;
  const root = svg("svg", { viewBox: `0 0 ${width} ${height}`, role: "img", "aria-label": "OEE by line" });
  root.append(svg("line", { class: "axis", x1: 0, x2: width, y1: height - pad.bottom, y2: height - pad.bottom }));
  data.forEach((d, i) => {
    const h = d.value === null ? 0 : d.value * (height - pad.top - pad.bottom);
    const x = pad.left + i * barWidth + barWidth * 0.15;
    const y = height - pad.bottom - h;
    const bar = svg("rect", { class: `bar${state.line === d.line ? " active" : ""}`, x, y, width: barWidth * 0.7, height: h, rx: 4 });
    bar.append(svg("title", {}, `${d.line}: ${pct(d.value)}`));
    bar.addEventListener("click", () => setLine(state.line === d.line ? null : d.line));
    root.append(bar,
      svg("text", { class: "value", x: x + barWidth * 0.35, y: y - 6, "text-anchor": "middle" }, pct(d.value)),
      svg("text", { x: x + barWidth * 0.35, y: height - 10, "text-anchor": "middle" }, d.line));
  });
  $("oee-chart").replaceChildren(root);
}

function renderAdherenceChart() {
  const byDay = new Map();
  filtered().forEach((r) => byDay.set(r.date, [...(byDay.get(r.date) ?? []), r]));
  // A day with nothing planned has no adherence: it is left out of the line, never drawn as 0%.
  const points = [...byDay.keys()].sort()
    .map((d) => [d, adherence(byDay.get(d))])
    .filter(([, value]) => value !== null);
  const days = points.map(([d]) => d);
  const values = points.map(([, value]) => value);
  const width = 480;
  const height = 220;
  const pad = { top: 16, bottom: 28, left: 36, right: 8 };
  // The axis starts at 70% unless a day is lower, so no point is ever clipped.
  const min = Math.min(0.7, Math.floor(Math.min(...values) * 10) / 10);
  const x = (i) => pad.left + (days.length < 2 ? 0 : (i * (width - pad.left - pad.right)) / (days.length - 1));
  const y = (v) => height - pad.bottom - ((v - min) / (1 - min)) * (height - pad.top - pad.bottom);
  const root = svg("svg", { viewBox: `0 0 ${width} ${height}`, role: "img", "aria-label": "Schedule adherence by day" });
  if (!days.length) {
    root.append(svg("text", { x: width / 2, y: height / 2, "text-anchor": "middle" }, "No data for this filter."));
    $("adherence-chart").replaceChildren(root);
    return;
  }
  const ticks = [];
  for (let t = Math.round(min * 10); t <= 10; t += 1) ticks.push(t / 10);
  ticks.forEach((tick) => root.append(
    svg("line", { class: "axis", x1: pad.left, x2: width - pad.right, y1: y(tick), y2: y(tick) }),
    svg("text", { x: 2, y: y(tick) + 4 }, `${Math.round(tick * 100)}%`)));
  root.append(svg("line", { class: "target", x1: pad.left, x2: width - pad.right, y1: y(CONFIG.adherenceTarget), y2: y(CONFIG.adherenceTarget) }));
  root.append(svg("path", { class: "path", d: values.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ") }));
  values.forEach((v, i) => {
    const dot = svg("circle", { cx: x(i), cy: y(v), r: 3.5, fill: v < CONFIG.adherenceTarget ? "#d7263d" : "#3fb950" });
    dot.append(svg("title", {}, `${days[i]}: ${pct(v)}`));
    root.append(dot);
  });
  [0, days.length - 1].forEach((i) => root.append(svg("text", { x: x(i), y: height - 8, "text-anchor": i ? "end" : "start" }, days[i])));
  $("adherence-chart").replaceChildren(root);
}

function renderDetail() {
  const rows = filtered();
  const pages = Math.max(1, Math.ceil(rows.length / CONFIG.pageSize));
  state.page = Math.min(state.page, pages - 1);
  const slice = rows.slice(state.page * CONFIG.pageSize, (state.page + 1) * CONFIG.pageSize);
  $("detail").tBodies[0].replaceChildren(...slice.map((r) => el("tr", {},
    el("td", { textContent: r.date }), el("td", { textContent: r.line }), el("td", { textContent: r.item }),
    el("td", { className: "num", textContent: r.planned_qty }), el("td", { className: "num", textContent: r.actual_qty }),
    el("td", { className: "num", textContent: r.good_qty }), el("td", { className: "num", textContent: pct(oee([r])) }))));
  $("page-info").textContent = `Page ${state.page + 1} of ${pages} (${rows.length} rows)`;
  $("prev").disabled = state.page === 0;
  $("next").disabled = state.page >= pages - 1;
}

function renderCoverage() {
  const items = [...state.inventory].sort((a, b) => {
    const ca = a.forecast_daily ? a.on_hand / a.forecast_daily : Infinity;
    const cb = b.forecast_daily ? b.on_hand / b.forecast_daily : Infinity;
    return ca - cb;
  });
  $("coverage").tBodies[0].replaceChildren(...items.map((i) => {
    const status = coverageStatus(i);
    return el("tr", {},
      el("td", { textContent: i.item }), el("td", { textContent: i.family }),
      el("td", { className: "num", textContent: i.on_hand }), el("td", { className: "num", textContent: i.forecast_daily }),
      el("td", { className: "num", textContent: i.forecast_daily ? (i.on_hand / i.forecast_daily).toFixed(1) : "—" }),
      el("td", {}, el("span", { className: `status status--${status}`, textContent: status.replace("_", " ") })));
  }));
}

function render() {
  renderFilters();
  renderKpis();
  renderOeeChart();
  renderAdherenceChart();
  renderDetail();
  renderCoverage();
}

function setLine(line) {
  state.line = line;
  state.page = 0;
  render();
}

// ==============================================================================
// Export (cells starting with = + - @ are prefixed so spreadsheets don't run them as formulas)
// ==============================================================================
function toCsv(rows) {
  const safe = (v) => {
    let text = String(v ?? "");
    if (/^[=+\-@\t\r]/.test(text)) text = `'${text}`;
    return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
  };
  return [PRODUCTION_FIELDS.join(","), ...rows.map((r) => PRODUCTION_FIELDS.map((f) => safe(r[f])).join(","))].join("\r\n");
}

$("export").addEventListener("click", () => {
  const blob = new Blob(["﻿" + toCsv(filtered())], { type: "text/csv;charset=utf-8" });
  const link = el("a", { href: URL.createObjectURL(blob), download: `production_${state.line ?? "all_lines"}.csv` });
  link.click();
  URL.revokeObjectURL(link.href);
});
$("prev").addEventListener("click", () => { state.page -= 1; renderDetail(); });
$("next").addEventListener("click", () => { state.page += 1; renderDetail(); });

// ==============================================================================
// Load
// ==============================================================================
// Text fields must be non-empty strings and every other field a finite number, so a "450" sent
// as text can never be concatenated into a wrong total.
const TEXT_FIELDS = new Set(["date", "line", "item", "family"]);

function validate(rows, fields, name) {
  if (!Array.isArray(rows)) throw new Error(`${name} is missing from dashboard.json`);
  const bad = rows.filter((r) => fields.some((f) => (TEXT_FIELDS.has(f)
    ? typeof r[f] !== "string" || r[f] === ""
    : !Number.isFinite(r[f]))));
  if (bad.length) throw new Error(`${bad.length} ${name} rows have missing or non-numeric fields`);
}

function validateMeta(meta) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(meta?.data_as_of ?? "")) throw new Error("meta.json has no valid data_as_of date");
  if (typeof meta.source !== "string" || !meta.source) throw new Error("meta.json has no source");
}

async function load() {
  const band = $("band");
  try {
    const [meta, data] = await Promise.all(Object.values(CONFIG.dataUrls).map(async (url) => {
      const response = await fetch(url, { cache: "no-store" });
      if (!response.ok) throw new Error(`${url} answered ${response.status}`);
      return response.json();
    }));
    validateMeta(meta);
    validate(data.production, PRODUCTION_FIELDS, "production");
    validate(data.inventory, INVENTORY_FIELDS, "inventory");
    state.production = data.production;
    state.inventory = data.inventory;
    $("freshness").textContent = `Data as of ${meta.data_as_of} · Source: ${meta.source}`;
    if (meta.demo) {
      band.textContent = "Demo: every number on this page is invented.";
      band.hidden = false;
    }
    render();
  } catch (error) {
    $("freshness").textContent = "Data unavailable.";
    band.textContent = `Could not load the data: ${error.message}. Nothing below is current.`;
    band.className = "band error";
    band.hidden = false;
    const failed = "Data could not be loaded.";
    $("kpis").replaceChildren(...["OEE", "Schedule Adherence", "Avg Days of Coverage", "Items Below Safety"]
      .map((label) => kpiCard(label, "—", "", failed)));
  }
}

load();
window.dashboard = { state, oee, adherence, toCsv };
