const express = require('express');
const router = express.Router();

const taskRoutes = require('./taskRoutes');

router.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'Task Management API',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    endpoints: {
      tasks: {
        'GET /api/tasks': 'Get all tasks (supports filtering by status, priority, category)',
        'GET /api/tasks/:id': 'Get task by ID',
        'POST /api/tasks': 'Create a new task',
        'PUT /api/tasks/:id': 'Update task by ID',
        'DELETE /api/tasks/:id': 'Delete task by ID'
      }
    },
    documentation: 'See README.md for detailed API documentation'
  });
});

router.use('/tasks', taskRoutes);

module.exports = router;