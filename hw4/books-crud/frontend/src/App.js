import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Home from './components/Home/Home.jsx';
import CreateBook from './components/Create/CreateBook.jsx';
import UpdateBook from './components/Update/UpdateBook.jsx';
import DeleteBook from './components/Delete/DeleteBook.jsx';
import { bookService } from './services/bookService';

const App = () => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await bookService.getAllBooks();
        setBooks(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const addBook = async (title, author) => {
    try {
      const book = await bookService.createBook({ title, author });
      setBooks((prev) => [...prev, book]);
      return { success: true };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  const updateBook = async (id, title, author) => {
    try {
      const book = await bookService.updateBook(id, { title, author });
      setBooks((prev) => prev.map((item) => (item.id === id ? book : item)));
      return { success: true };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  const deleteBook = async (id) => {
    try {
      await bookService.deleteBook(id);
      setBooks((prev) => prev.filter((item) => item.id !== id));
      return { success: true };
    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    }
  };

  return (
    <Router>
      <div className='app-container'>
        <header className='header'>
          <h1 className='main-title'>Book Manager</h1>
          <p className='subtitle'>Simple CRUD for your library.</p>
        </header>
        <main className='main-content'>
          {error && (
            <div className='error-banner'>
              <span>{error}</span>
              <button onClick={() => setError(null)}>Dismiss</button>
            </div>
          )}
          <Routes>
            <Route
              path='/'
              element={<Home books={books} loading={loading} />}
            />
            <Route path='/create' element={<CreateBook addBook={addBook} />} />
            <Route
              path='/update'
              element={<UpdateBook updateBook={updateBook} />}
            />
            <Route
              path='/delete'
              element={<DeleteBook books={books} deleteBook={deleteBook} />}
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
