// FreeCodeCamp Quality Assurance - Issue Tracker
// In-memory CRUD system for tracking project issues with filtering, updating, and deletion

class IssueTracker {
  constructor() {
    this.projects = {}; // { projectName: [ issue, ... ] }
    this.idCounter = 1;
  }

  createIssue(project, fields) {
    const { issue_title, issue_text, created_by, assigned_to = "", status_text = "" } = fields;

    if (!issue_title || !issue_text || !created_by) {
      return { error: "Required field(s) missing" };
    }

    const now = new Date().toISOString();
    const issue = {
      _id: String(this.idCounter++),
      issue_title,
      issue_text,
      created_by,
      assigned_to,
      status_text,
      created_on: now,
      updated_on: now,
      open: true
    };

    if (!this.projects[project]) this.projects[project] = [];
    this.projects[project].push(issue);
    return issue;
  }

  getIssues(project, filters = {}) {
    const issues = this.projects[project] || [];
    return issues.filter((issue) =>
      Object.entries(filters).every(([key, val]) => String(issue[key]) === String(val))
    );
  }

  updateIssue(project, _id, updates) {
    if (!_id) return { error: "missing _id" };

    const fields = Object.entries(updates).filter(([k, v]) => v !== "" && k !== "_id");
    if (fields.length === 0) return { error: "no update field(s) sent", _id };

    const issues = this.projects[project] || [];
    const issue = issues.find((i) => i._id === _id);
    if (!issue) return { error: "could not update", _id };

    fields.forEach(([k, v]) => { issue[k] = v; });
    issue.updated_on = new Date().toISOString();
    return { result: "successfully updated", _id };
  }

  deleteIssue(project, _id) {
    if (!_id) return { error: "missing _id" };

    const issues = this.projects[project] || [];
    const idx = issues.findIndex((i) => i._id === _id);
    if (idx === -1) return { error: "could not delete", _id };

    issues.splice(idx, 1);
    return { result: "successfully deleted", _id };
  }
}

// Tests
const tracker = new IssueTracker();

console.log("=== Issue Tracker Demo ===");

const i1 = tracker.createIssue("apitest", { issue_title: "Fix authentication bug", issue_text: "JWT tokens expire prematurely", created_by: "Hazzard", assigned_to: "Dev Team" });
const i2 = tracker.createIssue("apitest", { issue_title: "Update README", issue_text: "Missing setup instructions", created_by: "Hazzard" });
const i3 = tracker.createIssue("apitest", { issue_title: "Missing field test", issue_text: "", created_by: "" });

console.log("\nCreated Issue 1:", i1);
console.log("Created Issue 2:", i2);
console.log("Created with missing fields:", i3);

console.log("\nAll Open Issues:", tracker.getIssues("apitest", { open: true }));

console.log("\nUpdate Issue 1:", tracker.updateIssue("apitest", i1._id, { status_text: "In progress", open: false }));
console.log("\nDelete Issue 2:", tracker.deleteIssue("apitest", i2._id));

console.log("\nFinal Issue List:", tracker.getIssues("apitest"));
