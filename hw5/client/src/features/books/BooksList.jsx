import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { deleteBook, fetchBooks, setCurrentPage } from './booksSlice';
import usePagination from '../../app/usePagination';

const BooksList = () => {
  const dispatch = useDispatch();
  const { items, status, error, total, currentPage, itemsPerPage } = useSelector((state) => state.books);

  useEffect(() => {
    const skip = (currentPage - 1) * itemsPerPage;
    dispatch(fetchBooks({ skip, limit: itemsPerPage }));
  }, [dispatch, currentPage, itemsPerPage]);

  const handleDelete = (id) => {
    dispatch(deleteBook(id));
  };

  const { totalPages } = usePagination(total, currentPage, itemsPerPage);

  const handlePrevPage = () => currentPage > 1 && dispatch(setCurrentPage(currentPage - 1));
  const handleNextPage = () => currentPage < totalPages && dispatch(setCurrentPage(currentPage + 1));

  return (
    <div className="home">
      <div className="navigation-header">
        <h2 className="section-title">Books Catalogue</h2>
        <Link to="/books/create" className="btn btn-primary">
          Add Book
        </Link>
      </div>

      {status === 'loading' && (
        <div className="status-text">Loading books...</div>
      )}

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button type="button" className="btn btn-outline btn-sm" onClick={() => dispatch(fetchBooks())}>
            Retry
          </button>
        </div>
      )}

      {items.length === 0 && status === 'succeeded' && (
        <div className="empty-state">
          No books found. Add your first title to get started.
        </div>
      )}

      {items.length > 0 && (
        <>
          <div className="card-grid">
            {items.map((book) => (
              <div className="card" key={book.id}>
                <div className="card-title">{book.title}</div>
                <div className="card-subtitle">
                  {book.author ? `${book.author.first_name} ${book.author.last_name}` : 'Unknown author'}
                </div>
                <div className="card-meta">ISBN: {book.isbn}</div>
                <div className="card-meta">Published: {book.publication_year}</div>
                <div className="card-meta">Copies: {book.available_copies}</div>

                <div className="card-actions">
                  <Link to={`/books/edit/${book.id}`} className="btn btn-secondary btn-sm">
                    Edit
                  </Link>
                  <button
                    type="button"
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(book.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handlePrevPage}
                disabled={currentPage === 1}
              >
                Previous
              </button>
              <span className="pagination-info">
                Page {currentPage} of {totalPages} ({total} total books)
              </span>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleNextPage}
                disabled={currentPage === totalPages}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default BooksList;
