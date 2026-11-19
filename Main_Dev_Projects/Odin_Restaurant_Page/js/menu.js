// Made by: Hazzard
// Odin Restaurant Page - Menu tab, rendered from a plain data object.
import { el } from "./dom.js";

const MENU = {
  Starters: [
    ["Charred Corn", "Lime, chili salt and aged cheese.", 6.5],
    ["Smoked Wings", "Six wings, guajillo glaze.", 9],
  ],
  "From the Grill": [
    ["Ember Ribeye", "300 g, rosemary butter, fire-roasted peppers.", 24],
    ["Brisket Plate", "12-hour smoked brisket, pickles, house bread.", 18],
    ["Grilled Cauliflower", "Tahini, pomegranate, toasted seeds.", 13],
  ],
  Desserts: [
    ["Ash Brownie", "Dark chocolate, smoked sea salt.", 7],
  ],
};

const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

export default function renderMenu() {
  return el("section", {},
    ...Object.entries(MENU).map(([section, dishes]) =>
      el("div", { class: "menu-section" },
        el("h2", {}, section),
        el("div", { class: "dishes" },
          ...dishes.map(([name, description, price]) =>
            el("article", { class: "dish" },
              el("div", {}, el("h3", {}, name), el("p", {}, description)),
              el("span", { class: "price" }, money.format(price))))))));
}
