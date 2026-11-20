// Made by: Hazzard
// Odin Weather App - search a place, show current weather and a 5-day forecast.
// Shows a loading state while fetching and a visible message when anything fails.
import { findPlace, getForecast, describe, NetworkError, PlaceNotFoundError } from "./api.js";

const form = document.getElementById("search");
const statusEl = document.getElementById("status");
const result = document.getElementById("result");
const unitButton = document.getElementById("unit");
let unit = "C";
let lastPlace = null;

const el = (tag, props = {}, ...children) => {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
};
const round = (n) => Math.round(n);

function setStatus(text, kind = "") {
  statusEl.textContent = text;
  statusEl.className = `status ${kind}`;
}

function render(place, forecast) {
  const { current, daily, units } = forecast;
  const now = describe(current.code);
  document.body.dataset.look = current.isDay ? now.look : "night";
  const where = [place.name, place.region, place.country].filter(Boolean).join(", ");
  result.replaceChildren(
    el("section", { className: "now" },
      el("h2", { textContent: where }),
      el("p", { className: "temp", textContent: `${round(current.temperature)}${units.temp}` }),
      el("p", { className: "desc", textContent: now.text }),
      el("ul", { className: "facts" },
        el("li", { textContent: `Feels like ${round(current.feelsLike)}${units.temp}` }),
        el("li", { textContent: `Humidity ${current.humidity}%` }),
        el("li", { textContent: `Wind ${round(current.wind)} ${units.wind}` })),
      el("p", { className: "muted", textContent: `Local time of reading: ${current.time.replace("T", " ")}` })),
    el("section", { className: "days" },
      ...daily.map((day) => {
        const label = new Date(`${day.date}T12:00:00`).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
        return el("article", { className: "day" },
          el("h3", { textContent: label }),
          el("p", { textContent: describe(day.code).text }),
          el("p", { className: "range", textContent: `${round(day.max)}° / ${round(day.min)}°` }),
          el("p", { className: "muted", textContent: day.rain === null ? "Rain chance: n/a" : `Rain chance ${day.rain}%` }));
      })));
}

let loading = false;

async function load(query) {
  loading = true;
  const requestedUnit = unit;
  form.querySelector("button").disabled = true;
  setStatus("Loading...", "loading");
  try {
    // The place only becomes "current" once its forecast has rendered, so a failed search
    // keeps the city that is on screen.
    const place = query ? await findPlace(query) : lastPlace;
    const forecast = await getForecast(place, requestedUnit);
    render(place, forecast);
    lastPlace = place;
    setStatus("");
  } catch (error) {
    if (!(error instanceof NetworkError || error instanceof PlaceNotFoundError)) console.error(error);
    setStatus(error.message, "error");
  } finally {
    loading = false;
    form.querySelector("button").disabled = false;
  }
  // The unit was switched while this request was in flight: fetch again in the new unit.
  if (requestedUnit !== unit && lastPlace) load(null);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const query = form.elements.city.value.trim();
  if (query.length < 2) {
    setStatus("Type at least two letters.", "error");
    return;
  }
  load(query);
});

unitButton.addEventListener("click", () => {
  unit = unit === "C" ? "F" : "C";
  unitButton.textContent = `°${unit === "C" ? "F" : "C"}`;
  unitButton.setAttribute("aria-label", `Switch to ${unit === "C" ? "Fahrenheit" : "Celsius"}`);
  if (lastPlace && !loading) load(null);
});

load("London");
