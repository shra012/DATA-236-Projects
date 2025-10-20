const express = require('express');
const router = express.Router();
const Task = require('../models/Task');
const { validateRequest } = require('../middleware/validation');
const { 
  createTaskSchema, 
  updateTaskSchema, 
  queryFiltersSchema,
  paramsWithIdSchema 
} = require('../validation/taskValidation');

router.post('/', validateRequest(createTaskSchema), async (req, res) => {
  try {
    const task = new Task(req.body);
    const savedTask = await task.save();
    res.status(201).json({
      success: true,
      message: 'Task created successfully',
      data: savedTask
    });
  } catch (error) {
    console.error('Error creating task:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

router.get('/', validateRequest(queryFiltersSchema, 'query'), async (req, res) => {
  try {
    const { status, priority, category, page, limit } = req.query;
    
    const filter = {};
    if (status) filter.status = status;
    if (priority) filter.priority = priority;
    if (category) filter.category = category;

    const skip = (page - 1) * limit;
    const tasks = await Task.find(filter)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);
    
    const total = await Task.countDocuments(filter);
    
    res.status(200).json({
      success: true,
      count: tasks.length,
      total,
      page,
      totalPages: Math.ceil(total / limit),
      data: tasks
    });
  } catch (error) {
    console.error('Error fetching tasks:', error);
    res.status(500).json({
      success: false,
      message: 'Server error while fetching tasks'
    });
  }
});

router.get('/:id', validateRequest(paramsWithIdSchema, 'params'), async (req, res) => {
  try {
    const task = await Task.findById(req.params.id);
    
    if (!task) {
      return res.status(404).json({
        success: false,
        message: 'Task not found'
      });
    }

    res.status(200).json({
      success: true,
      data: task
    });
  } catch (error) {
    console.error('Error fetching task by ID:', error);
    res.status(500).json({
      success: false,
      message: 'Server error while fetching task'
    });
  }
});

router.put('/:id', 
  validateRequest(paramsWithIdSchema, 'params'),
  validateRequest(updateTaskSchema, 'body'),
  async (req, res) => {
    try {
      const task = await Task.findByIdAndUpdate(
        req.params.id,
        req.body,
        {
          new: true,
          runValidators: true
        }
      );

      if (!task) {
        return res.status(404).json({
          success: false,
          message: 'Task not found'
        });
      }

      res.status(200).json({
        success: true,
        message: 'Task updated successfully',
        data: task
      });
    } catch (error) {
      console.error('Error updating task:', error);
      res.status(500).json({
        success: false,
        message: 'Server error while updating task'
      });
    }
  }
);

router.delete('/:id', validateRequest(paramsWithIdSchema, 'params'), async (req, res) => {
  try {
    const task = await Task.findByIdAndDelete(req.params.id);

    if (!task) {
      return res.status(404).json({
        success: false,
        message: 'Task not found'
      });
    }

    res.status(200).json({
      success: true,
      message: 'Task deleted successfully',
      data: task
    });
  } catch (error) {
    console.error('Error deleting task:', error);
    res.status(500).json({
      success: false,
      message: 'Server error while deleting task'
    });
  }
});

module.exports = router;

