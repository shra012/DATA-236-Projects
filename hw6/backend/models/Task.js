const mongoose = require('mongoose');
const {
  TASK_STATUS,
  TASK_PRIORITY,
  TASK_CATEGORY,
  VALIDATION_LIMITS
} = require('../constants');

const taskSchema = new mongoose.Schema(
  {
    title: {
      type: String,
      required: [true, 'Title is required'],
      trim: true,
      maxlength: [
        VALIDATION_LIMITS.TITLE_MAX_LENGTH,
        `Title cannot exceed ${VALIDATION_LIMITS.TITLE_MAX_LENGTH} characters`
      ]
    },
    description: {
      type: String,
      trim: true,
      maxlength: [
        VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH,
        `Description cannot exceed ${VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH} characters`
      ],
      default: ''
    },
    status: {
      type: String,
      enum: {
        values: Object.values(TASK_STATUS),
        message: `Status must be one of: ${Object.values(TASK_STATUS).join(', ')}`
      },
      default: TASK_STATUS.PENDING
    },
    priority: {
      type: String,
      enum: {
        values: Object.values(TASK_PRIORITY),
        message: `Priority must be one of: ${Object.values(TASK_PRIORITY).join(', ')}`
      },
      default: TASK_PRIORITY.MEDIUM
    },
    dueDate: {
      type: Date,
      required: [true, 'Due date is required'],
      validate: {
        validator: (value) => value instanceof Date && !isNaN(value),
        message: 'Please provide a valid date'
      }
    },
    category: {
      type: String,
      required: [true, 'Category is required'],
      enum: {
        values: Object.values(TASK_CATEGORY),
        message: `Category must be one of: ${Object.values(TASK_CATEGORY).join(', ')}`
      },
      default: TASK_CATEGORY.WORK
    }
  },
  { timestamps: true }
);

module.exports = mongoose.model('Task', taskSchema);
