const express = require('express');
const cors = require('cors');
require('dotenv').config();
const {
  sequelize,
  testConnection,
  createDatabaseIfNotExists,
} = require('./config/database');
const bookRoutes = require('./routes/bookRoutes');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.use('/api/books', bookRoutes);

app.get('/api/health', (req, res) => {
  res.status(200).json({ success: true, message: 'Books API ready' });
});

app.get('/', (req, res) => {
  res.status(200).json({ success: true, message: 'Welcome to the Books API' });
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ success: false, message: 'Unexpected error' });
});

const startServer = async () => {
  try {
    await createDatabaseIfNotExists();
    await testConnection();
    await sequelize.sync();
    app.listen(PORT, () => {
      console.log(`Server ready at http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error('Failed to start server', error);
  }
};

startServer();

module.exports = app;
