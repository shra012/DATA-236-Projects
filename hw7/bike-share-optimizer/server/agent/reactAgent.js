/**
 * ReAct Agent Orchestrator
 */

import OpenAI from 'openai';
import csv_sql from '../tools/csv_sql.js';
import policy_retriever from '../tools/policy_retriever.js';
import calculator from '../tools/calculator.js';

let openai = null;

function getOpenAIClient() {
  if (!openai) {
    openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
  }
  return openai;
}

const TOOLS = {
  csv_sql,
  policy_retriever,
  calculator
};

const SYSTEM_PROMPT = `You are a bike-share optimization agent using the ReAct (Reasoning + Acting) framework.

Your task: Analyze uploaded trip data and pricing policy to recommend whether a rider should buy a monthly membership or pay per ride/minute.

Available Tools (MRKL):

1. csv_sql - Execute SQL queries on trip data
   Input: { "sql": "SELECT ..." }
   Output: { "rows": [...], "row_count": N, "source": "uploaded.csv" }

2. policy_retriever - Fetch pricing page snippets
   Input: { "url": "https://...", "query": "membership pricing", "k": 5 }
   Output: { "passages": [{ "text": "...", "source": "...", "score": N }] }

3. calculator - Safe arithmetic
   Input: { "expression": "150 * 0.30", "units": "USD" }
   Output: { "value": 45, "units": "USD" }

ReAct Format:
Thought: [your reasoning about what to do next]
Action: tool_name
Action Input: {"param": "value"}
Observation: [tool output will be provided]

Continue this loop until you have enough information, then provide:
Final Answer: [your recommendation]

Required Analysis:
1. Query trip data (count, durations, bike types)
2. Fetch pricing policy (membership cost, per-ride fees, included minutes, ebike surcharges)
3. Calculate costs for both options
4. Compare and recommend

Be concise in thoughts. Cite sources in your final answer.`;

function parseAgentResponse(text) {
  const thoughtMatch = text.match(/Thought:\s*(.+?)(?=\nAction:|$)/s);
  const actionMatch = text.match(/Action:\s*(\w+)/);
  const actionInputMatch = text.match(/Action Input:\s*(\{.+?\})/s);
  const finalAnswerMatch = text.match(/Final Answer:\s*(.+)/s);
  
  return {
    thought: thoughtMatch ? thoughtMatch[1].trim() : null,
    action: actionMatch ? actionMatch[1].trim() : null,
    actionInput: actionInputMatch ? actionInputMatch[1].trim() : null,
    finalAnswer: finalAnswerMatch ? finalAnswerMatch[1].trim() : null
  };
}


export async function runReActAgent(pricingUrl) {
  const steps = [];
  const maxIterations = 15;
  let iteration = 0;
  let conversationHistory = [
    { role: 'system', content: SYSTEM_PROMPT },
    { 
      role: 'user', 
      content: `Analyze the uploaded trip data and pricing policy at ${pricingUrl}. Recommend whether to buy a monthly membership or pay per ride/minute. Provide cost breakdown and citations.` 
    }
  ];
  
  const startTime = Date.now();
  let stopReason = 'max_iterations';
  
  try {
    while (iteration < maxIterations) {
      iteration++;
      
      const client = getOpenAIClient();
      const completion = await client.chat.completions.create({
        model: 'gpt-4-turbo-preview',
        messages: conversationHistory,
        temperature: 0.7,
        max_tokens: 1000
      });
      
      const response = completion.choices[0].message.content;
      const parsed = parseAgentResponse(response);
      
      if (parsed.thought) {
        steps.push({
          type: 'thought',
          content: parsed.thought,
          timestamp: new Date().toISOString()
        });
      }
      
      if (parsed.finalAnswer) {
        steps.push({
          type: 'answer',
          content: parsed.finalAnswer,
          timestamp: new Date().toISOString()
        });
        stopReason = 'complete';
        break;
      }
      
      if (parsed.action && parsed.actionInput) {
        const toolName = parsed.action;
        
        steps.push({
          type: 'action',
          tool: toolName,
          input: parsed.actionInput,
          timestamp: new Date().toISOString()
        });
        
        let observation;
        try {
          const tool = TOOLS[toolName];
          if (!tool) {
            observation = { success: false, error: `Unknown tool: ${toolName}` };
          } else {
            const input = JSON.parse(parsed.actionInput);
            observation = await tool(input);
          }
        } catch (error) {
          observation = { success: false, error: error.message };
        }
        
        steps.push({
          type: 'observation',
          content: observation,
          timestamp: new Date().toISOString()
        });
        
        conversationHistory.push({
          role: 'assistant',
          content: response
        });
        
        conversationHistory.push({
          role: 'user',
          content: `Observation: ${JSON.stringify(observation, null, 2)}`
        });
      } else {
        conversationHistory.push({
          role: 'assistant',
          content: response
        });
        conversationHistory.push({
          role: 'user',
          content: 'Continue with your analysis. Use the tools to gather information.'
        });
      }
    }
    
    const totalTime = Date.now() - startTime;
    
    return {
      success: true,
      steps,
      metrics: {
        totalSteps: steps.length,
        iterations: iteration,
        totalTime: `${(totalTime / 1000).toFixed(2)}s`,
        stopReason
      }
    };
    
  } catch (error) {
    return {
      success: false,
      error: error.message,
      steps,
      metrics: {
        totalSteps: steps.length,
        iterations: iteration,
        totalTime: `${((Date.now() - startTime) / 1000).toFixed(2)}s`,
        stopReason: 'error'
      }
    };
  }
}

export default runReActAgent;
