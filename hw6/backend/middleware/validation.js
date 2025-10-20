const validateRequest = (schema, source = 'body') => {
  return (req, res, next) => {
    const payload = req[source] || req.body;
    const result = schema.safeParse(payload);

    if (!result.success) {
      const errorMessages = result.error.issues.map(issue => ({
        field: issue.path.join('.') || source,
        message: issue.message
      }));

      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errorMessages
      });
    }

    if (source === 'body') req.body = result.data;
    if (source === 'query') req.query = result.data;
    if (source === 'params') req.params = result.data;

    next();
  };
};

module.exports = { validateRequest };
