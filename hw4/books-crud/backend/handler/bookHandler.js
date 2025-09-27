const Book = require('../models/Book');

const getAllBooks = async (req, res) => {
  try {
    const books = await Book.findAll({ order: [['createdAt', 'DESC']] });
    res.status(200).json({ success: true, data: books });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Unable to load books' });
  }
};

const getBookById = async (req, res) => {
  try {
    const book = await Book.findByPk(req.params.id);
    if (!book) {
      return res
        .status(404)
        .json({ success: false, message: 'Book not found' });
    }
    res.status(200).json({ success: true, data: book });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Unable to load book' });
  }
};

const createBook = async (req, res) => {
  try {
    const { title, author } = req.body;
    if (!title || !author) {
      return res
        .status(400)
        .json({ success: false, message: 'Title and author are required' });
    }
    const book = await Book.create({
      title: title.trim(),
      author: author.trim(),
    });
    res.status(201).json({ success: true, data: book });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Unable to create book' });
  }
};

const updateBook = async (req, res) => {
  try {
    const { title, author } = req.body;
    if (!title || !author) {
      return res
        .status(400)
        .json({ success: false, message: 'Title and author are required' });
    }
    const book = await Book.findByPk(req.params.id);
    if (!book) {
      return res
        .status(404)
        .json({ success: false, message: 'Book not found' });
    }
    await book.update({ title: title.trim(), author: author.trim() });
    res.status(200).json({ success: true, data: book });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Unable to update book' });
  }
};

const deleteBook = async (req, res) => {
  try {
    const book = await Book.findByPk(req.params.id);
    if (!book) {
      return res
        .status(404)
        .json({ success: false, message: 'Book not found' });
    }
    await book.destroy();
    res.status(200).json({ success: true, data: book });
  } catch (error) {
    res.status(500).json({ success: false, message: 'Unable to delete book' });
  }
};

module.exports = {
  getAllBooks,
  getBookById,
  createBook,
  updateBook,
  deleteBook,
};
