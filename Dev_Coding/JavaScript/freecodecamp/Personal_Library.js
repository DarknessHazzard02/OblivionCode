// FreeCodeCamp Quality Assurance - Personal Library
// In-memory book management system with comment threads and deletion controls

class PersonalLibrary {
  constructor() {
    this.books = {};
    this.idCounter = 1;
  }

  addBook(title) {
    if (!title) return { error: "title is required" };

    const book = {
      _id: String(this.idCounter++),
      title,
      comments: [],
      commentcount: 0
    };

    this.books[book._id] = book;
    return { _id: book._id, title: book.title };
  }

  getAllBooks() {
    return Object.values(this.books).map(({ _id, title, commentcount }) => ({
      _id, title, commentcount
    }));
  }

  getBook(_id) {
    if (!_id) return { error: "missing _id" };
    const book = this.books[_id];
    if (!book) return { error: "no book exists" };
    return book;
  }

  addComment(_id, comment) {
    if (!_id) return { error: "missing _id" };
    if (!comment) return { error: "missing required field comment" };

    const book = this.books[_id];
    if (!book) return { error: "no book exists" };

    book.comments.push(comment);
    book.commentcount = book.comments.length;
    return book;
  }

  deleteBook(_id) {
    if (!_id) return { error: "missing _id" };
    if (!this.books[_id]) return { error: "no book exists" };

    delete this.books[_id];
    return { result: "delete successful", _id };
  }

  deleteAllBooks() {
    this.books = {};
    return { result: "complete delete successful" };
  }
}

// Tests
const library = new PersonalLibrary();

console.log("=== Personal Library Demo ===");

const b1 = library.addBook("Clean Code");
const b2 = library.addBook("The Pragmatic Programmer");
const b3 = library.addBook("Design Patterns");

console.log("\nAdded books:", b1, b2, b3);
console.log("\nAdd comment to 'Clean Code':", library.addComment(b1._id, "Must-read for every developer"));
console.log("Add comment to 'Clean Code':", library.addComment(b1._id, "Chapter 3 on functions is gold"));
console.log("\nAll books:", library.getAllBooks());
console.log("\nGet single book:", library.getBook(b1._id));
console.log("\nDelete 'Design Patterns':", library.deleteBook(b3._id));
console.log("Library after delete:", library.getAllBooks());
