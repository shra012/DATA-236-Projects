const { z } = require('zod');
const { 
  TASK_STATUS, 
  TASK_PRIORITY, 
  TASK_CATEGORY, 
  VALIDATION_LIMITS 
} = require('../constants');

const TaskStatus = z.enum([TASK_STATUS.PENDING, TASK_STATUS.IN_PROGRESS, TASK_STATUS.COMPLETED], {
  errorMap: () => ({ message: `Status must be one of: ${Object.values(TASK_STATUS).join(', ')}` })
});

const TaskPriority = z.enum([TASK_PRIORITY.LOW, TASK_PRIORITY.MEDIUM, TASK_PRIORITY.HIGH], {
  errorMap: () => ({ message: `Priority must be one of: ${Object.values(TASK_PRIORITY).join(', ')}` })
});

const TaskCategory = z.enum([
  TASK_CATEGORY.WORK, 
  TASK_CATEGORY.PERSONAL, 
  TASK_CATEGORY.SHOPPING, 
  TASK_CATEGORY.HEALTH, 
  TASK_CATEGORY.OTHER
], {
  errorMap: () => ({ message: `Category must be one of: ${Object.values(TASK_CATEGORY).join(', ')}` })
});

const createTaskSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(VALIDATION_LIMITS.TITLE_MAX_LENGTH, `Title must be ${VALIDATION_LIMITS.TITLE_MAX_LENGTH} characters or less`)
    .trim(),
  
  description: z.string()
    .max(VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH, `Description must be ${VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH} characters or less`)
    .trim()
    .optional(),
  
  status: TaskStatus.default(TASK_STATUS.PENDING),
  
  priority: TaskPriority.default(TASK_PRIORITY.MEDIUM),
  
  dueDate: z.string()
    .refine((date) => {
      const parsedDate = new Date(date);
      return !isNaN(parsedDate.getTime());
    }, 'Invalid date format')
    .refine((date) => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const dueDate = new Date(date);
      return dueDate >= today;
    }, 'Due date cannot be in the past'),
  
  category: TaskCategory.default(TASK_CATEGORY.WORK)
});

const updateTaskSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(VALIDATION_LIMITS.TITLE_MAX_LENGTH, `Title must be ${VALIDATION_LIMITS.TITLE_MAX_LENGTH} characters or less`)
    .trim()
    .optional(),
  
  description: z.string()
    .max(VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH, `Description must be ${VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH} characters or less`)
    .trim()
    .optional(),
  
  status: TaskStatus.optional(),
  
  priority: TaskPriority.optional(),
  
  dueDate: z.string()
    .refine((date) => {
      const parsedDate = new Date(date);
      return !isNaN(parsedDate.getTime());
    }, 'Invalid date format')
    .optional(),
  
  category: TaskCategory.optional()
});

const queryFiltersSchema = z.object({
  status: TaskStatus.optional(),
  priority: TaskPriority.optional(),
  category: TaskCategory.optional(),
  page: z.string()
    .transform((val) => parseInt(val))
    .refine((val) => val > 0, 'Page must be a positive number')
    .default(VALIDATION_LIMITS.PAGINATION_DEFAULT_PAGE.toString()),
  limit: z.string()
    .transform((val) => parseInt(val))
    .refine((val) => val > 0 && val <= VALIDATION_LIMITS.PAGINATION_MAX_LIMIT, `Limit must be between 1 and ${VALIDATION_LIMITS.PAGINATION_MAX_LIMIT}`)
    .default(VALIDATION_LIMITS.PAGINATION_DEFAULT_LIMIT.toString())
});

const mongoIdSchema = z.string()
  .regex(/^[0-9a-fA-F]{24}$/, 'Invalid MongoDB ObjectId format');

const paramsWithIdSchema = z.object({
  id: mongoIdSchema
});

module.exports = {
  createTaskSchema,
  updateTaskSchema,
  queryFiltersSchema,
  mongoIdSchema,
  paramsWithIdSchema
};
