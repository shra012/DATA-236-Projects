import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';

const DeleteBook = ({ deleteBook }) => {
  const [book, setBook] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const selected = location.state?.book;
    if (selected) {
      setBook(selected);
    } else {
      navigate('/');
    }
  }, [location, navigate]);

  const handleDelete = async () => {
    if (!book) {
      return;
    }
    await deleteBook(book.id);
    navigate('/');
  };

  if (!book) {
    return null;
  }

  return (
    <div>
      <div className='navigation-header'>
        <h2 className='section-title'>Delete Book</h2>
        <Link to='/' className='back-button'>
          Back to Home
        </Link>
      </div>
      <div className='form-container'>
        <div className='confirm-card'>
          <h3 className='book-title'>{book.title}</h3>
          <p className='book-author'>By {book.author}</p>
          <p className='book-id'>ID: {book.id}</p>
        </div>
        <div className='form-actions'>
          <button className='btn btn-danger' onClick={handleDelete}>
            Delete
          </button>
          <Link to='/' className='btn btn-secondary'>
            Cancel
          </Link>
        </div>
      </div>
    </div>
  );
};

export default DeleteBook;
