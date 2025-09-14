const express = require("express");
const bodyParser = require("body-parser");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

let books = [
  { id: 1, title: "To Kill a Mockingbird", author: "Harper Lee" },
  { id: 2, title: "1984", author: "George Orwell" },
  { id: 3, title: "Pride and Prejudice", author: "Jane Austen" },
  { id: 4, title: "The Great Gatsby", author: "F. Scott Fitzgerald" },
  {
    id: 5,
    title: "Harry Potter and the Philosopher's Stone",
    author: "J.K. Rowling",
  },
  { id: 6, title: "The Catcher in the Rye", author: "J.D. Salinger" },
  { id: 7, title: "Lord of the Flies", author: "William Golding" },
  { id: 8, title: "The Chronicles of Narnia", author: "C.S. Lewis" },
  { id: 9, title: "Animal Farm", author: "George Orwell" },
  { id: 10, title: "The Hobbit", author: "J.R.R. Tolkien" },
];

let nextId = 11;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, "public")));

app.set("views", path.join(__dirname, "views"));

function getHighestId() {
  if (books.length === 0) return 0;
  return Math.max(...books.map((book) => book.id));
}

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "views", "index.html"));
});

app.get("/api/books", (req, res) => {
  res.json({
    books: books,
    totalBooks: books.length,
    highestId: getHighestId(),
  });
});

app.post("/books", (req, res) => {
  const { title, author } = req.body;

  if (!title || !author) {
    return res.status(400).json({ error: "Title and Author are required" });
  }

  const newBook = {
    id: nextId++,
    title: title.trim(),
    author: author.trim(),
  };

  books.push(newBook);

  console.log(
    `Added new book: ${newBook.title} by ${newBook.author} (ID: ${newBook.id})`
  );

  res.json(newBook);
});

app.put("/api/books/:id", (req, res) => {
  const bookId = parseInt(req.params.id);
  const { title, author } = req.body;

  if (!title || !author) {
    return res.status(400).json({ error: "Title and Author are required" });
  }

  const bookIndex = books.findIndex((book) => book.id === bookId);

  if (bookIndex === -1) {
    return res.status(404).json({ error: "Book not found" });
  }

  books[bookIndex] = {
    id: bookId,
    title: title.trim(),
    author: author.trim(),
  };

  console.log(`Updated book with ID ${bookId}: ${title} by ${author}`);
  res.json(books[bookIndex]);
});

app.delete("/api/books/:id", (req, res) => {
  const bookId = parseInt(req.params.id);
  const bookIndex = books.findIndex((book) => book.id === bookId);

  if (bookIndex === -1) {
    return res.status(404).json({ error: "Book not found" });
  }

  const deletedBook = books.splice(bookIndex, 1)[0];
  console.log(
    `Deleted book with ID ${bookId}: ${deletedBook.title} by ${deletedBook.author}`
  );

  res.json({ message: "Book deleted successfully", book: deletedBook });
});

app.post("/books/delete-highest", (req, res) => {
  if (books.length === 0) {
    console.log("No books to delete");
    return res.redirect("/");
  }

  const highestId = getHighestId();
  const bookIndex = books.findIndex((book) => book.id === highestId);

  if (bookIndex !== -1) {
    const deletedBook = books.splice(bookIndex, 1)[0];
    console.log(
      `Deleted book with highest ID (${highestId}): ${deletedBook.title} by ${deletedBook.author}`
    );
  }

  res.redirect("/");
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send("Something went wrong!");
});

app.use((req, res) => {
  res.status(404).send("Page not found");
});

app.listen(PORT, () => {
  console.log(`Book Management Server is running on http://localhost:${PORT}`);
  console.log(`Current books in library: ${books.length}`);
  books.forEach((book) => {
    console.log(`  - ID ${book.id}: "${book.title}" by ${book.author}`);
  });
});

module.exports = app;
