import { evaluate } from 'mathjs';

function validateExpression(expression) {
  const whitelist = /^[0-9+\-*/().\s]+$/;
  return whitelist.test(expression);
}

export async function calculator(input) {
  const startTime = Date.now();
  
  try {
    const { expression, units } = input;
    
    if (!expression || typeof expression !== 'string') {
      throw new Error('Expression string is required');
    }
    
    if (!validateExpression(expression)) {
      throw new Error('Invalid expression. Only numbers and operators (+, -, *, /, (), .) are allowed');
    }
    
    const result = evaluate(expression);
    
    const latency = Date.now() - startTime;
    
    return {
      success: true,
      data: {
        value: result,
        units: units || null
      },
      source: 'calculator',
      ts: new Date().toISOString(),
      latency: `${latency}ms`
    };
    
  } catch (error) {
    const latency = Date.now() - startTime;
    
    return {
      success: false,
      error: error.message,
      source: 'calculator',
      ts: new Date().toISOString(),
      latency: `${latency}ms`
    };
  }
}

export default calculator;
