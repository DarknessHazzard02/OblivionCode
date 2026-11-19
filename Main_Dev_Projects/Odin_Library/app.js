// Made by: Hazzard
// Odin Library - books live in an array of Book objects built with a constructor;
// toggleRead lives on the prototype. Each card is linked to its book by a stable id.

// ==============================================================================
// Model
// ==============================================================================
function Book(title, author, pages, read) {
  if (!new.target) throw new Error("Use the 'new' operator to create a Book.");
  this.id = crypto.randomUUID();
  this.title = title;
  this.author = author;
  this.pages = pages;
  this.read = read;
}

Book.prototype.toggleRead = function toggleRead() {
  this.read = !this.read;
};

const myLibrary = [];

function addBookToLibrary(title, author, pages, read) {
  const book = new Book(title, author, pages, read);
  myLibrary.push(book);
  return book;
}

function removeBook(id) {
  const index = myLibrary.findIndex((book) => book.id === id);
  if (index !== -1) myLibrary.splice(index, 1);
}

// ==============================================================================
// View
// ==============================================================================
const shelf = document.getElementById("shelf");
const summary = document.getElementById("summary");

function el(tag, props = {}, ...children) {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
}

function render() {
  shelf.replaceChildren();
  if (myLibrary.length === 0) shelf.append(el("p", { className: "empty", textContent: "No books yet. Add one with + New book." }));
  myLibrary.forEach((book) => {
    const toggle = el("button", { className: "btn btn--small btn--ghost", textContent: book.read ? "Mark unread" : "Mark read" });
    toggle.dataset.action = "toggle";
    const remove = el("button", { className: "btn btn--small", textContent: "Remove" });
    remove.dataset.action = "remove";
    const card = el("article", { className: `card${book.read ? " is-read" : ""}` },
      el("h3", { textContent: book.title }),
      el("p", { textContent: `by ${book.author}` }),
      el("p", { textContent: `${book.pages} pages - ${book.read ? "read" : "not read yet"}` }),
      el("div", { className: "row" }, toggle, remove));
    card.dataset.id = book.id;
    shelf.append(card);
  });
  const read = myLibrary.filter((book) => book.read).length;
  summary.textContent = `${myLibrary.length} books, ${read} read.`;
}

shelf.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const { id } = button.closest(".card").dataset;
  if (button.dataset.action === "remove") removeBook(id);
  else myLibrary.find((book) => book.id === id)?.toggleRead();
  render();
});

// ==============================================================================
// Form
// ==============================================================================
const dialog = document.getElementById("book-dialog");
const form = document.getElementById("book-form");

document.getElementById("new-book").addEventListener("click", () => dialog.showModal());
document.getElementById("cancel").addEventListener("click", () => { form.reset(); dialog.close(); });

form.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const data = new FormData(form);
  addBookToLibrary(data.get("title").trim(), data.get("author").trim(), Number(data.get("pages")), data.get("read") === "on");
  form.reset();
  dialog.close();
  render();
});

addBookToLibrary("The Hobbit", "J.R.R. Tolkien", 295, true);
addBookToLibrary("Storytelling with Data", "Cole Nussbaumer Knaflic", 288, false);
render();

window.library = { myLibrary, addBookToLibrary };
