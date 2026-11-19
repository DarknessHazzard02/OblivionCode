// Made by: Hazzard
// Odin Restaurant Page - Home tab.
import { el, withAccent } from "./dom.js";

const HOURS = [["Mon - Thu", "1 pm - 10 pm"], ["Fri - Sat", "1 pm - 12 am"], ["Sunday", "12 pm - 8 pm"]];

export default function renderHome() {
  return el("section", {},
    el("div", { class: "hero" },
      el("h1", {}, ...withAccent("Ember ", "&", " Ash")),
      el("p", {}, "Wood-fired grill, slow-smoked meats and seasonal sides."),
      el("p", {}, "A fictional restaurant for a practice project.")),
    el("div", { class: "hours" },
      ...HOURS.map(([days, time]) => el("div", {}, el("strong", {}, days), time))));
}
