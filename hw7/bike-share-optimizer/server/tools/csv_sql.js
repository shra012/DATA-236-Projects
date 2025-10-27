import alasql from 'alasql';

let currentDataset = null;
let tableName = 'trips';

export function loadCSVData(csvData, columns) {
  try {
    alasql(`DROP TABLE IF EXISTS ${tableName}`);
    
    const columnDefs = columns.map(col => `${col} STRING`).join(', ');
    alasql(`CREATE TABLE ${tableName} (${columnDefs})`);
    
    alasql.tables[tableName].data = csvData;
    currentDataset = csvData;
    
    return {
      success: true,
      message: `Loaded ${csvData.length} rows`,
      columns: columns
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

export async function csv_sql(input) {
  const startTime = Date.now();
  
  try {
    const { sql } = input;
    
    if (!sql || typeof sql !== 'string') {
      throw new Error('SQL query string is required');
    }
    
    const lowerSQL = sql.toLowerCase().trim();
    if (lowerSQL.startsWith('insert') || 
        lowerSQL.startsWith('update') || 
        lowerSQL.startsWith('delete') || 
        lowerSQL.startsWith('drop') ||
        lowerSQL.startsWith('create') ||
        lowerSQL.startsWith('alter')) {
      throw new Error('Only SELECT queries are allowed');
    }
    
    if (!currentDataset || currentDataset.length === 0) {
      throw new Error('No CSV data loaded. Please upload a CSV file first.');
    }
    
    const rows = alasql(sql);
    
    const latency = Date.now() - startTime;
    
    return {
      success: true,
      data: {
        rows: rows || [],
        row_count: rows ? rows.length : 0,
        source: 'uploaded.csv'
      },
      source: 'csv_sql',
      ts: new Date().toISOString(),
      latency: `${latency}ms`
    };
    
  } catch (error) {
    const latency = Date.now() - startTime;
    
    return {
      success: false,
      error: error.message,
      source: 'csv_sql',
      ts: new Date().toISOString(),
      latency: `${latency}ms`
    };
  }
}

export default csv_sql;
