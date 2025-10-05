import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import BookForm from './BookForm';
import { createBook } from './booksSlice';

const CreateBook = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [formError, setFormError] = useState(null);

  const handleSubmit = async (values) => {
    try {
      await dispatch(createBook(values)).unwrap();
      navigate('/books');
    } catch (error) {
      setFormError(error);
    }
  };

  return (
    <div className="home">
      <div className="navigation-header">
        <h2 className="section-title">Add New Book</h2>
        <Link to="/books" className="btn btn-secondary">
          Back to list
        </Link>
      </div>

      {formError && <div className="error-banner">{formError}</div>}

      <BookForm submitLabel="Create Book" onSubmit={handleSubmit} />
    </div>
  );
};

export default CreateBook;
