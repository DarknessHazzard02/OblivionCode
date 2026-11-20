// Made by: Hazzard
// Odin Todo List - application logic only (no DOM): projects that hold todos.

export const PRIORITIES = ["low", "medium", "high"];

export function createTodo({ title, description = "", dueDate = "", priority = "medium", notes = "", done = false, id }) {
  if (!title || !title.trim()) throw new Error("A todo needs a title.");
  if (!PRIORITIES.includes(priority)) throw new Error(`Unknown priority: ${priority}`);
  return { id: id ?? crypto.randomUUID(), title: title.trim(), description, dueDate, priority, notes, done };
}

export function createProject(name, todos = [], id) {
  if (!name || !name.trim()) throw new Error("A project needs a name.");
  return { id: id ?? crypto.randomUUID(), name: name.trim(), todos };
}

export function createStore(initialProjects) {
  const projects = initialProjects.length ? initialProjects : [createProject("Inbox")];

  const getProjects = () => projects;
  const getProject = (id) => projects.find((project) => project.id === id) ?? null;
  const addProject = (name) => {
    const project = createProject(name);
    projects.push(project);
    return project;
  };
  const removeProject = (id) => {
    if (projects.length === 1) return false; // keep at least one project
    const index = projects.findIndex((project) => project.id === id);
    if (index === -1) return false;
    projects.splice(index, 1);
    return true;
  };
  const addTodo = (projectId, fields) => {
    const project = getProject(projectId);
    if (!project) throw new Error(`Project ${projectId} not found.`);
    const todo = createTodo(fields);
    project.todos.push(todo);
    return todo;
  };
  const updateTodo = (projectId, todoId, fields) => {
    const project = getProject(projectId);
    const index = project?.todos.findIndex((todo) => todo.id === todoId) ?? -1;
    if (index === -1) return null;
    project.todos[index] = createTodo({ ...project.todos[index], ...fields, id: todoId });
    return project.todos[index];
  };
  const removeTodo = (projectId, todoId) => {
    const project = getProject(projectId);
    if (!project) return false;
    const before = project.todos.length;
    project.todos = project.todos.filter((todo) => todo.id !== todoId);
    return project.todos.length < before;
  };

  return { getProjects, getProject, addProject, removeProject, addTodo, updateTodo, removeTodo };
}
