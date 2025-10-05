import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useParams, Link } from 'react-router-dom';
import AuthorForm from './AuthorForm';
import { clearSelectedAuthor, fetchAuthorById, updateAuthor } from './authorsSlice';

const EditAuthor = () => {
  const { id } = useParams();
  const numericId = Number(id);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { selectedAuthor, status, error } = useSelector((state) => state.authors);
  const [formError, setFormError] = useState(null);

  useEffect(() => {
    if (!Number.isNaN(numericId)) {
      dispatch(fetchAuthorById(numericId));
    }
    return () => {
      dispatch(clearSelectedAuthor());
    };
  }, [dispatch, numericId]);

  const handleSubmit = async (values) => {
    setFormError(null);
    if (!Number.isNaN(numericId)) {
      try {
        await dispatch(updateAuthor({ id: numericId, data: values })).unwrap();
        navigate('/authors');
      } catch (updateError) {
        setFormError(updateError);
      }
    }
  };

  return (
    <div className="home">
      <div className="navigation-header">
        <h2 className="section-title">Edit Author</h2>
        <Link to="/authors" className="btn btn-secondary">
          Back to list
        </Link>
      </div>

      {status === 'loading' && <div className="status-text">Loading author...</div>}
      {error && <div className="error-banner">{error}</div>}
      {formError && <div className="error-banner">{formError}</div>}

      {selectedAuthor && (
        <AuthorForm
          initialValues={selectedAuthor}
          submitLabel="Update Author"
          onSubmit={handleSubmit}
        />
      )}
    </div>
  );
};

export default EditAuthor;
