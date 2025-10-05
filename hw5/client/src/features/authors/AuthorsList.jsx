import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { deleteAuthor, fetchAuthors, setCurrentPage } from './authorsSlice';
import usePagination from '../../app/usePagination';

const AuthorsList = () => {
  const dispatch = useDispatch();
  const { items, status, error, total, currentPage, itemsPerPage } = useSelector((state) => state.authors);

  useEffect(() => {
    const skip = (currentPage - 1) * itemsPerPage;
    dispatch(fetchAuthors({ skip, limit: itemsPerPage }));
  }, [dispatch, currentPage, itemsPerPage]);

  const handleDelete = (id) => {
    dispatch(deleteAuthor(id));
  };

  const { totalPages } = usePagination(total, currentPage, itemsPerPage);

  const handlePrevPage = () => currentPage > 1 && dispatch(setCurrentPage(currentPage - 1));
  const handleNextPage = () => currentPage < totalPages && dispatch(setCurrentPage(currentPage + 1));

  const formatDate = (isoString) => {
    if (!isoString) {
      return null;
    }
    const date = new Date(isoString);
    return Number.isNaN(date.getTime()) ? null : date.toLocaleDateString();
  };

  return (
    <div className="home">
      <div className="navigation-header">
        <h2 className="section-title">Authors Directory</h2>
        <Link to="/authors/create" className="btn btn-primary">
          Add Author
        </Link>
      </div>

      {status === 'loading' && (
        <div className="status-text">Loading authors...</div>
      )}

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button type="button" className="btn btn-outline btn-sm" onClick={() => dispatch(fetchAuthors())}>
            Retry
          </button>
        </div>
      )}

      {items.length === 0 && status === 'succeeded' && (
        <div className="empty-state">
          No authors found. Add your first author to get started.
        </div>
      )}

      {items.length > 0 && (
        <>
          <div className="card-grid">
            {items.map((author) => (
              <div className="card" key={author.id}>
                <div className="card-title">
                  {author.first_name} {author.last_name}
                </div>
                <div className="card-subtitle">{author.email}</div>
                <div className="card-meta">ID: {author.id}</div>
                {formatDate(author.created_at) && (
                  <div className="card-meta">Joined: {formatDate(author.created_at)}</div>
                )}

                <div className="card-actions">
                  <Link to={`/authors/edit/${author.id}`} className="btn btn-secondary btn-sm">
                    Edit
                  </Link>
                  <button
                    type="button"
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(author.id)}
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
                Page {currentPage} of {totalPages} ({total} total authors)
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

export default AuthorsList;
