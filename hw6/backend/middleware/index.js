const cors = require('cors');
const express = require('express');

const corsMiddleware = cors({
  origin: [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://localhost:5173'
  ],
  credentials: true,
  optionsSuccessStatus: 200
});

const jsonMiddleware = express.json({ limit: '10mb' });

const urlEncodedMiddleware = express.urlencoded({ 
  extended: true,
  limit: '10mb'
});

const requestLoggingMiddleware = (req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next();
};

const errorHandlerMiddleware = (err, req, res, next) => {
  console.error('Error Stack:', err.stack);
  
  if (err.type === 'entity.parse.failed') {
    return res.status(400).json({
      success: false,
      message: 'Invalid JSON syntax'
    });
  }
  
  res.status(err.status || 500).json({
    success: false,
    message: err.message || 'Internal Server Error',
    error: process.env.NODE_ENV === 'development' ? err.stack : undefined
  });
};

const notFoundMiddleware = (req, res) => {
  res.status(404).json({
    success: false,
    message: `Route ${req.method} ${req.url} not found`
  });
};

module.exports = {
  corsMiddleware,
  jsonMiddleware,
  urlEncodedMiddleware,
  requestLoggingMiddleware,
  errorHandlerMiddleware,
  notFoundMiddleware
};
