import axios from 'axios';
import * as cheerio from 'cheerio';

function extractRelevantSnippets(text, query, k = 5) {
  const chunks = text
    .split(/[.!?]\s+/)
    .filter(chunk => chunk.trim().length > 20);
  
  const queryTerms = query.toLowerCase().split(/\s+/);
  
  const scoredChunks = chunks.map(chunk => {
    const lowerChunk = chunk.toLowerCase();
    let score = 0;
    
    queryTerms.forEach(term => {
      const matches = (lowerChunk.match(new RegExp(term, 'g')) || []).length;
      score += matches;
    });
    
    const pricingKeywords = ['$', 'price', 'cost', 'fee', 'membership', 'minute', 'ride', 'ebike', 'unlock', 'month', 'annual'];
    pricingKeywords.forEach(keyword => {
      if (lowerChunk.includes(keyword)) score += 2;
    });
    
    return {
      text: chunk.trim(),
      score: score
    };
  });
  
  return scoredChunks
    .filter(item => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, k);
}

export async function policy_retriever(input) {
  const startTime = Date.now();
  
  try {
    const { url, query, k = 5 } = input;
    
    if (!url || typeof url !== 'string') {
      throw new Error('URL is required');
    }
    
    if (!query || typeof query !== 'string') {
      throw new Error('Query string is required');
    }
    
    const response = await axios.get(url, {
      timeout: 10000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; BikeShareOptimizer/1.0)'
      }
    });
    
    const $ = cheerio.load(response.data);
    
    $('script, style, nav, footer, header').remove();
    
    let text = $('body').text();
    
    text = text.replace(/\s+/g, ' ').trim();
    
    const passages = extractRelevantSnippets(text, query, k);
    
    const latency = Date.now() - startTime;
    
    return {
      success: true,
      data: {
        passages: passages.map(p => ({
          text: p.text,
          source: url,
          score: p.score
        }))
      },
      source: 'policy_retriever',
      ts: new Date().toISOString(),
      latency: `${latency}ms`
    };
    
  } catch (error) {
    const latency = Date.now() - startTime;
    
    return {
      success: false,
      error: error.message,
      source: 'policy_retriever',
      ts: new Date().toISOString(),
      latency: `${latency}ms`
    };
  }
}

export default policy_retriever;
