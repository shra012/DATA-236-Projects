require('dotenv').config();

const express = require('express');
const connectDB = require('./database');
const apiRoutes = require('../routes');
const {
  corsMiddleware,
  jsonMiddleware,
  urlEncodedMiddleware,
  requestLoggingMiddleware,
  errorHandlerMiddleware,
  notFoundMiddleware
} = require('../middleware');

const createServer = async () => {
  const app = express();

  await connectDB();

  app.use(corsMiddleware);
  app.use(jsonMiddleware);
  app.use(urlEncodedMiddleware);
  
  if (process.env.NODE_ENV === 'development') {
    app.use(requestLoggingMiddleware);
  }

  app.use('/api', apiRoutes);

  app.get('/health', (req, res) => {
    res.status(200).json({
      success: true,
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      environment: process.env.NODE_ENV || 'development'
    });
  });

  app.use('*', notFoundMiddleware);

  app.use(errorHandlerMiddleware);

  return app;
};

module.exports = createServer;