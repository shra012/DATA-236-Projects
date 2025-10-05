import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchAuthors } from '../authors/authorsSlice';

const BookForm = ({ initialValues, onSubmit, submitLabel }) => {
  const dispatch = useDispatch();
  const { items: authors, status: authorStatus } = useSelector((state) => state.authors);

  const [formValues, setFormValues] = useState({
    title: '',
    isbn: '',
    publication_year: '',
    available_copies: 1,
    author_id: '',
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (authorStatus === 'idle') {
      dispatch(fetchAuthors());
    }
  }, [authorStatus, dispatch]);

  useEffect(() => {
    if (initialValues) {
      setFormValues({
        title: initialValues.title || '',
        isbn: initialValues.isbn || '',
        publication_year: initialValues.publication_year || '',
        available_copies: initialValues.available_copies ?? 1,
        author_id: initialValues.author_id || initialValues.author?.id || '',
      });
    }
  }, [initialValues]);

  const validate = () => {
    const validationErrors = {};
    if (!formValues.title) {
      validationErrors.title = 'Title is required';
    }
    if (!formValues.isbn) {
      validationErrors.isbn = 'ISBN is required';
    }
    if (!formValues.publication_year) {
      validationErrors.publication_year = 'Publication year is required';
    }
    if (!formValues.author_id) {
      validationErrors.author_id = 'Author is required';
    }
    setErrors(validationErrors);
    return Object.keys(validationErrors).length === 0;
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormValues((prev) => ({
      ...prev,
      [name]: name === 'available_copies' || name === 'publication_year' ? Number(value) : value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!validate()) {
      return;
    }
    onSubmit({
      ...formValues,
      publication_year: Number(formValues.publication_year),
      available_copies: Number(formValues.available_copies),
      author_id: Number(formValues.author_id),
    });
  };

  return (
    <form className="form-container" onSubmit={handleSubmit}>
      <div className="form-group">
        <label className="form-label" htmlFor="title">Title</label>
        <input
          id="title"
          name="title"
          type="text"
          value={formValues.title}
          onChange={handleChange}
          className="form-input"
          placeholder="Book title"
        />
        {errors.title && <span className="field-error">{errors.title}</span>}
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="isbn">ISBN</label>
        <input
          id="isbn"
          name="isbn"
          type="text"
          value={formValues.isbn}
          onChange={handleChange}
          className="form-input"
          placeholder="ISBN"
        />
        {errors.isbn && <span className="field-error">{errors.isbn}</span>}
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="publication_year">Publication Year</label>
        <input
          id="publication_year"
          name="publication_year"
          type="number"
          value={formValues.publication_year}
          onChange={handleChange}
          className="form-input"
          placeholder="2024"
        />
        {errors.publication_year && <span className="field-error">{errors.publication_year}</span>}
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="available_copies">Available Copies</label>
        <input
          id="available_copies"
          name="available_copies"
          type="number"
          min="0"
          value={formValues.available_copies}
          onChange={handleChange}
          className="form-input"
        />
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="author_id">Author</label>
        <select
          id="author_id"
          name="author_id"
          value={formValues.author_id}
          onChange={handleChange}
          className="form-select"
        >
          <option value="">Select an author</option>
          {authorStatus === 'loading' && <option disabled>Loading authors...</option>}
          {authorStatus === 'succeeded' &&
            authors.map((author) => (
              <option key={author.id} value={author.id}>
                {author.first_name} {author.last_name}
              </option>
            ))}
        </select>
        {errors.author_id && <span className="field-error">{errors.author_id}</span>}
      </div>

      <button type="submit" className="btn btn-primary">
        {submitLabel}
      </button>
    </form>
  );
};

export default BookForm;
