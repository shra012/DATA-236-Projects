import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useParams, Link } from 'react-router-dom';
import BookForm from './BookForm';
import { clearSelectedBook, fetchBookById, updateBook } from './booksSlice';

const EditBook = () => {
  const { id } = useParams();
  const numericId = Number(id);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { selectedBook, status, error } = useSelector((state) => state.books);
  const [formError, setFormError] = useState(null);

  useEffect(() => {
    if (!Number.isNaN(numericId)) {
      dispatch(fetchBookById(numericId));
    }
    return () => {
      dispatch(clearSelectedBook());
    };
  }, [dispatch, numericId]);

  const handleSubmit = async (values) => {
    setFormError(null);
    if (!Number.isNaN(numericId)) {
      try {
        await dispatch(updateBook({ id: numericId, data: values })).unwrap();
        navigate('/books');
      } catch (updateError) {
        setFormError(updateError);
      }
    }
  };

  return (
    <div className="home">
      <div className="navigation-header">
        <h2 className="section-title">Edit Book</h2>
        <Link to="/books" className="btn btn-secondary">
          Back to list
        </Link>
      </div>

      {status === 'loading' && <div className="status-text">Loading book...</div>}
      {error && <div className="error-banner">{error}</div>}
      {formError && <div className="error-banner">{formError}</div>}

      {selectedBook && (
        <BookForm
          initialValues={selectedBook}
          submitLabel="Update Book"
          onSubmit={handleSubmit}
        />
      )}
    </div>
  );
};

export default EditBook;
