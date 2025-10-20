const createServer = require('./config/server');

const startServer = async () => {
  try {
    const app = await createServer();
    
    const PORT = process.env.PORT || 5000;
    
    const server = app.listen(PORT, () => {
      console.log('Task Management API Server Started');
      console.log(`Port: ${PORT}`);
      console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
      console.log(`API Base URL: http://localhost:${PORT}/api`);
      console.log(`Health Check: http://localhost:${PORT}/health`);
      console.log('Documentation: See README.md for API details');
      console.log('─'.repeat(50));
    });

    process.on('SIGTERM', () => {
      console.log('SIGTERM received, shutting down gracefully...');
      server.close(() => {
        console.log('Server closed');
        process.exit(0);
      });
    });

    process.on('SIGINT', () => {
      console.log('SIGINT received, shutting down gracefully...');
      server.close(() => {
        console.log('Server closed');
        process.exit(0);
      });
    });

  } catch (error) {
    console.error('Failed to start server:', error.message);
    process.exit(1);
  }
};

startServer();

module.exports = startServer;
