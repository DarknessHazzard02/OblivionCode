// Made by: Hazzard
// Odin Todo List - entry module: loads saved projects, shows any load warning on the page,
// and seeds sample todos only on a true first run (never over existing, unreadable data).
import { createStore } from "./model.js";
import { load, save } from "./storage.js";
import { createUI } from "./ui.js";

const { projects, hadData, warning } = load();
const store = createStore(projects);

if (warning) {
  const notice = document.getElementById("notice");
  notice.textContent = warning;
  notice.hidden = false;
}

if (!hadData) {
  const inbox = store.getProjects()[0];
  const inDays = (n) => {
    const d = new Date();
    d.setDate(d.getDate() + n);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  };
  store.addTodo(inbox.id, { title: "Finish the Odin Todo List", description: "Projects, todos, localStorage.", dueDate: inDays(2), priority: "high" });
  store.addTodo(inbox.id, { title: "Review merge sort", dueDate: inDays(7), priority: "low" });
  save(store.getProjects());
}

createUI(store, save).render();
