// Made by: Hazzard
// Odin Restaurant Page - Contact tab (placeholder details for a fictional place).
import { el } from "./dom.js";

export default function renderContact() {
  return el("section", {},
    el("h2", {}, "Contact"),
    el("div", { class: "contact-card" },
      el("p", {}, "123 Placeholder Street, Example City"),
      el("p", {}, "Phone: 555-0100"),
      el("p", {}, "Email: hello@example.com")),
    el("p", { class: "note" }, "All details are placeholders: Ember & Ash is not a real restaurant."));
}
