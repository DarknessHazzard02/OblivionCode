// Made by: Hazzard
// Odin Todo List - localStorage persistence. Bad saved data never crashes the app and is never
// silently thrown away: invalid items are skipped one by one, the original text is backed up
// under a second key, and a warning is returned for the UI to show.
import { createProject, createTodo } from "./model.js";

const KEY = "odin-todo-list";
const BACKUP_KEY = `${KEY}-backup`;

function backup(raw) {
  try {
    localStorage.setItem(BACKUP_KEY, raw);
    return ` The original data was copied to localStorage key "${BACKUP_KEY}".`;
  } catch {
    return "";
  }
}

// Returns { projects, hadData, warning }. hadData is true when something was saved before,
// even if none of it could be read, so the caller knows not to seed sample todos over it.
export function load() {
  let raw = null;
  try {
    raw = localStorage.getItem(KEY);
  } catch (error) {
    return { projects: [], hadData: false, warning: `Storage is unavailable, so nothing will be saved (${error.message}).` };
  }
  if (!raw) return { projects: [], hadData: false, warning: "" };

  let parsed;
  try {
    parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) throw new Error("expected a list of projects");
  } catch (error) {
    return { projects: [], hadData: true, warning: `Saved data could not be read (${error.message}).${backup(raw)}` };
  }

  let skipped = 0;
  const projects = [];
  parsed.forEach((p) => {
    try {
      const todos = [];
      (Array.isArray(p.todos) ? p.todos : []).forEach((t) => {
        try {
          todos.push(createTodo(t));
        } catch {
          skipped += 1;
        }
      });
      projects.push(createProject(p.name, todos, p.id));
    } catch {
      skipped += 1;
    }
  });
  const warning = skipped ? `${skipped} saved item(s) were invalid and were skipped.${backup(raw)}` : "";
  return { projects, hadData: true, warning };
}

export function save(projects) {
  try {
    localStorage.setItem(KEY, JSON.stringify(projects));
    return true;
  } catch (error) {
    console.warn(`Could not save: ${error.message}`);
    return false;
  }
}
