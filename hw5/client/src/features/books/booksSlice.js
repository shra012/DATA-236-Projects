import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import api from '../../app/api';
import { handleApiError } from '../../app/apiUtils';

const initialState = {
  items: [],
  total: 0,
  status: 'idle',
  error: null,
  selectedBook: null,
  currentPage: 1,
  itemsPerPage: 9,
};

export const fetchBooks = createAsyncThunk(
  'books/fetchBooks',
  async ({ skip = 0, limit = 10 } = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/books', { params: { skip, limit } });
      return response.data;
    } catch (error) {
      return rejectWithValue(handleApiError(error));
    }
  }
);

export const fetchBookById = createAsyncThunk(
  'books/fetchBookById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await api.get(`/books/${id}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(handleApiError(error));
    }
  }
);

export const createBook = createAsyncThunk(
  'books/createBook',
  async (payload, { rejectWithValue }) => {
    try {
      const response = await api.post('/books', payload);
      return response.data;
    } catch (error) {
      return rejectWithValue(handleApiError(error));
    }
  }
);

export const updateBook = createAsyncThunk(
  'books/updateBook',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/books/${id}`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(handleApiError(error));
    }
  }
);

export const deleteBook = createAsyncThunk(
  'books/deleteBook',
  async (id, { rejectWithValue }) => {
    try {
      await api.delete(`/books/${id}`);
      return id;
    } catch (error) {
      return rejectWithValue(handleApiError(error));
    }
  }
);

const booksSlice = createSlice({
  name: 'books',
  initialState,
  reducers: {
    clearSelectedBook: (state) => {
      state.selectedBook = null;
    },
    setCurrentPage: (state, action) => {
      state.currentPage = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchBooks.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchBooks.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.total = action.payload.total;
        state.items = action.payload.items;
      })
      .addCase(fetchBooks.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Unable to load books.';
      })
      .addCase(fetchBookById.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchBookById.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.selectedBook = action.payload;
        const exists = state.items.find((book) => book.id === action.payload.id);
        if (!exists) {
          state.items.push(action.payload);
        }
      })
      .addCase(fetchBookById.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Unable to load book.';
      })
      .addCase(createBook.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(createBook.fulfilled, (state, action) => {
        state.items.push(action.payload);
        state.total += 1;
        state.status = 'succeeded';
      })
      .addCase(createBook.rejected, (state, action) => {
        state.error = action.payload || 'Unable to create book.';
        state.status = 'failed';
      })
      .addCase(updateBook.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(updateBook.fulfilled, (state, action) => {
        state.items = state.items.map((book) =>
          book.id === action.payload.id ? action.payload : book
        );
        state.selectedBook = action.payload;
        state.status = 'succeeded';
      })
      .addCase(updateBook.rejected, (state, action) => {
        state.error = action.payload || 'Unable to update book.';
        state.status = 'failed';
      })
      .addCase(deleteBook.pending, (state) => {
        state.error = null;
      })
      .addCase(deleteBook.fulfilled, (state, action) => {
        state.items = state.items.filter((book) => book.id !== action.payload);
        state.total = Math.max(0, state.total - 1);
      })
      .addCase(deleteBook.rejected, (state, action) => {
        state.error = action.payload || 'Unable to delete book.';
      });
  },
});

export const { clearSelectedBook, setCurrentPage } = booksSlice.actions;

export default booksSlice.reducer;
