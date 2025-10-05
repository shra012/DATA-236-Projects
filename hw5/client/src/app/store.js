import { configureStore } from '@reduxjs/toolkit';
import booksReducer from '../features/books/booksSlice';
import authorsReducer from '../features/authors/authorsSlice';

const store = configureStore({
  reducer: {
    books: booksReducer,
    authors: authorsReducer,
  },
});

export default store;
