// Made by: Hazzard
// Odin Restaurant Page - entry module: swaps the content area when a tab is clicked.
import renderHome from "./home.js";
import renderMenu from "./menu.js";
import renderContact from "./contact.js";

const TABS = { home: renderHome, menu: renderMenu, contact: renderContact };
const content = document.getElementById("content");
const buttons = document.querySelectorAll(".tabs button");

function show(tab) {
  content.replaceChildren(TABS[tab]());
  buttons.forEach((button) => button.classList.toggle("active", button.dataset.tab === tab));
}

buttons.forEach((button) => button.addEventListener("click", () => show(button.dataset.tab)));
show("home");
