// Utility - Task / Chore Manager
// Simple in-memory task tracker with priority and status

class TaskManager {
  constructor() {
    this.tasks = [];
    this.nextId = 1;
  }

  addTask(title, priority = "medium") {
    const task = {
      id: this.nextId++,
      title,
      priority,
      completed: false,
      createdAt: new Date().toISOString()
    };
    this.tasks.push(task);
    return task;
  }

  completeTask(id) {
    const task = this.tasks.find((t) => t.id === id);
    if (!task) return null;
    task.completed = true;
    return task;
  }

  getPendingTasks() {
    return this.tasks.filter((t) => !t.completed);
  }

  listSummary() {
    return this.tasks.map(
      (t) => `[${t.completed ? "X" : " "}] #${t.id} (${t.priority.toUpperCase()}) ${t.title}`
    ).join("\n");
  }
}

// Demo
const manager = new TaskManager();
manager.addTask("Refactor API service", "high");
manager.addTask("Update documentation", "low");
manager.addTask("Write unit tests", "medium");
manager.completeTask(1);

console.log("=== Task Summary ===");
console.log(manager.listSummary());
