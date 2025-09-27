import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Home = ({ books, loading }) => {
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className='home'>
        <div className='navigation-header'>
          <h2 className='section-title'>Your Books</h2>
          <Link to='/create' className='btn btn-primary'>
            Add Book
          </Link>
        </div>
        <p className='status-text'>Loading books...</p>
      </div>
    );
  }

  const handleUpdate = (book) => navigate('/update', { state: { book } });
  const handleDelete = (book) => navigate('/delete', { state: { book } });

  return (
    <div className='home'>
      <div className='navigation-header'>
        <h2 className='section-title'>Your Books</h2>
        <Link to='/create' className='btn btn-primary'>
          Add Book
        </Link>
      </div>
      {books.length === 0 ? (
        <div className='empty-state'>
          <p>No books yet. Start by adding one.</p>
        </div>
      ) : (
        <div className='books-grid'>
          {books.map((book) => (
            <div key={book.id} className='book-card'>
              <h3 className='book-title'>{book.title}</h3>
              <p className='book-author'>By {book.author}</p>
              <p className='book-id'>ID: {book.id}</p>
              <div className='book-actions'>
                <button
                  className='btn btn-warning btn-sm'
                  onClick={() => handleUpdate(book)}
                >
                  Update
                </button>
                <button
                  className='btn btn-danger btn-sm'
                  onClick={() => handleDelete(book)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      {books.length > 0 && (
        <div className='stats-card'>
          <h3>Total Books</h3>
          <p className='stats-number'>{books.length}</p>
        </div>
      )}
    </div>
  );
};

export default Home;
