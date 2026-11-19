// Made by: Hazzard
// Odin Todo List - DOM layer: renders projects and todos, wires the forms. Uses only textContent.
import { PRIORITIES } from "./model.js";

const el = (tag, props = {}, ...children) => {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
};

function formatDue(dueDate) {
  if (!dueDate) return "No due date";
  const [y, m, d] = dueDate.split("-").map(Number);
  const due = new Date(y, m - 1, d);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const days = Math.round((due - today) / 86400000);
  const label = due.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  if (days < 0) return `${label} (overdue)`;
  if (days === 0) return `${label} (today)`;
  return `${label} (in ${days} day${days === 1 ? "" : "s"})`;
}

export function createUI(store, persist) {
  let activeId = store.getProjects()[0].id;
  let expandedId = null;
  const projectList = document.getElementById("project-list");
  const todoList = document.getElementById("todo-list");
  const title = document.getElementById("project-title");
  const dialog = document.getElementById("todo-dialog");
  const todoForm = document.getElementById("todo-form");
  const formError = document.getElementById("todo-error");

  const commit = () => { persist(store.getProjects()); render(); };

  function renderProjects() {
    projectList.replaceChildren(...store.getProjects().map((project) => {
      const open = project.todos.filter((todo) => !todo.done).length;
      const button = el("button", { className: `project${project.id === activeId ? " active" : ""}` },
        el("span", { textContent: project.name }), el("span", { className: "count", textContent: String(open) }));
      button.addEventListener("click", () => { activeId = project.id; expandedId = null; render(); });
      return el("li", {}, button);
    }));
  }

  function renderTodos() {
    const project = store.getProject(activeId);
    title.textContent = project.name;
    const todos = [...project.todos].sort((a, b) => Number(a.done) - Number(b.done) || (a.dueDate || "9").localeCompare(b.dueDate || "9"));
    if (!todos.length) {
      todoList.replaceChildren(el("li", { className: "empty", textContent: "Nothing here yet. Add a todo." }));
      return;
    }
    todoList.replaceChildren(...todos.map((todo) => {
      const check = el("input", { type: "checkbox", checked: todo.done, title: "Mark done" });
      check.addEventListener("change", () => { store.updateTodo(activeId, todo.id, { done: check.checked }); commit(); });
      const summary = el("button", { className: "todo__summary" },
        el("span", { className: "todo__title", textContent: todo.title }),
        el("span", { className: "todo__due", textContent: formatDue(todo.dueDate) }));
      summary.addEventListener("click", () => { expandedId = expandedId === todo.id ? null : todo.id; render(); });
      const item = el("li", { className: `todo prio-${todo.priority}${todo.done ? " done" : ""}` }, el("div", { className: "todo__row" }, check, summary));
      if (expandedId === todo.id) {
        const edit = el("button", { className: "btn btn--small btn--ghost", textContent: "Edit" });
        edit.addEventListener("click", () => openForm(todo));
        const remove = el("button", { className: "btn btn--small", textContent: "Delete" });
        remove.addEventListener("click", () => { store.removeTodo(activeId, todo.id); commit(); });
        item.append(el("div", { className: "todo__details" },
          el("p", { textContent: todo.description || "No description." }),
          el("p", { className: "muted", textContent: `Priority: ${todo.priority}` }),
          todo.notes ? el("p", { className: "muted", textContent: `Notes: ${todo.notes}` }) : "",
          el("div", { className: "row" }, edit, remove)));
      }
      return item;
    }));
  }

  function render() {
    renderProjects();
    renderTodos();
  }

  function openForm(todo = null) {
    todoForm.reset();
    formError.textContent = "";
    todoForm.elements.id.value = todo?.id ?? "";
    todoForm.elements.title.value = todo?.title ?? "";
    todoForm.elements.description.value = todo?.description ?? "";
    todoForm.elements.dueDate.value = todo?.dueDate ?? "";
    todoForm.elements.priority.value = todo?.priority ?? "medium";
    todoForm.elements.notes.value = todo?.notes ?? "";
    document.getElementById("todo-dialog-title").textContent = todo ? "Edit todo" : "New todo";
    dialog.showModal();
  }

  todoForm.elements.priority.replaceChildren(...PRIORITIES.map((p) => el("option", { value: p, textContent: p })));

  todoForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(todoForm));
    const { id, ...fields } = data;
    try {
      if (id) store.updateTodo(activeId, id, fields);
      else store.addTodo(activeId, fields);
    } catch (error) {
      formError.textContent = error.message;
      return;
    }
    dialog.close();
    commit();
  });
  document.getElementById("cancel-todo").addEventListener("click", () => dialog.close());
  document.getElementById("new-todo").addEventListener("click", () => openForm());

  document.getElementById("project-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const input = event.target.elements.name;
    if (!input.value.trim()) return;
    activeId = store.addProject(input.value).id;
    input.value = "";
    commit();
  });

  document.getElementById("delete-project").addEventListener("click", () => {
    const project = store.getProject(activeId);
    if (!confirm(`Delete "${project.name}" and its ${project.todos.length} todos?`)) return;
    if (!store.removeProject(activeId)) {
      alert("You need at least one project.");
      return;
    }
    activeId = store.getProjects()[0].id;
    commit();
  });

  return { render };
}
