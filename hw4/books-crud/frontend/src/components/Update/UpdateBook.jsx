import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';

const UpdateBook = ({ updateBook }) => {
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [bookId, setBookId] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const book = location.state?.book;
    if (book) {
      setBookId(book.id);
      setTitle(book.title);
      setAuthor(book.author);
    } else {
      navigate('/');
    }
  }, [location, navigate]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!bookId || !title.trim() || !author.trim()) {
      return;
    }
    await updateBook(bookId, title.trim(), author.trim());
    navigate('/');
  };

  if (!bookId) {
    return null;
  }

  return (
    <div>
      <div className='navigation-header'>
        <h2 className='section-title'>Update Book</h2>
        <Link to='/' className='back-button'>
          Back to Home
        </Link>
      </div>
      <div className='form-container'>
        <form onSubmit={handleSubmit}>
          <div className='form-group'>
            <label htmlFor='bookTitle' className='form-label'>
              Book Title
            </label>
            <input
              id='bookTitle'
              type='text'
              className='form-input'
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder='Enter a title'
              required
            />
          </div>
          <div className='form-group'>
            <label htmlFor='authorName' className='form-label'>
              Author
            </label>
            <input
              id='authorName'
              type='text'
              className='form-input'
              value={author}
              onChange={(event) => setAuthor(event.target.value)}
              placeholder='Enter an author'
              required
            />
          </div>
          <div className='form-actions'>
            <button type='submit' className='btn btn-primary'>
              Update
            </button>
            <Link to='/' className='btn btn-secondary'>
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UpdateBook;
