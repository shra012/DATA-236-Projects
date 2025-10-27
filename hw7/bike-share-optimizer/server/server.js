import express from 'express';
import cors from 'cors';
import multer from 'multer';
import Papa from 'papaparse';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import dotenv from 'dotenv';
import { loadCSVData } from './tools/csv_sql.js';
import runReActAgent from './agent/reactAgent.js';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

const upload = multer({ dest: 'uploads/' });

if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads');
}

const DEFAULT_CSV_PATH = join(__dirname, '..', 'data', 'baywheels-tripdata.csv');

function loadDefaultCSV() {
  try {
    console.log('Loading default CSV data from:', DEFAULT_CSV_PATH);
    const fileContent = fs.readFileSync(DEFAULT_CSV_PATH, 'utf8');
    
    Papa.parse(fileContent, {
      header: true,
      dynamicTyping: false,
      skipEmptyLines: true,
      complete: (results) => {
        const subset = results.data.slice(0, 500);
        
        const converted = subset.map((row, index) => ({
          ride_id: `R${String(index + 1).padStart(6, '0')}`,
          rideable_type: 'classic_bike',
          started_at: row.start_time,
          ended_at: row.end_time,
          start_station_name: row.start_station_name || '',
          start_station_id: row.start_station_id || '',
          end_station_name: row.end_station_name || '',
          end_station_id: row.end_station_id || '',
          start_lat: row.start_station_latitude || '',
          start_lng: row.start_station_longitude || '',
          end_lat: row.end_station_latitude || '',
          end_lng: row.end_station_longitude || '',
          member_casual: row.user_type === 'Subscriber' ? 'member' : 'casual',
          duration_sec: row.duration_sec
        }));
        
        const columns = Object.keys(converted[0]);
        const loadResult = loadCSVData(converted, columns);
        
        if (loadResult.success) {
          console.log(`Loaded ${converted.length} rows from default CSV`);
        } else {
          console.error('Error loading default CSV:', loadResult.error);
        }
      },
      error: (error) => {
        console.error('Error parsing default CSV:', error);
      }
    });
  } catch (error) {
    console.error('Error reading default CSV file:', error.message);
  }
}

loadDefaultCSV();

app.post('/api/upload', upload.single('csv'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ success: false, error: 'No file uploaded' });
    }
    
    const filePath = req.file.path;
    const fileContent = fs.readFileSync(filePath, 'utf8');
    
    Papa.parse(fileContent, {
      header: true,
      dynamicTyping: false,
      skipEmptyLines: true,
      complete: (results) => {
        const columns = results.meta.fields;
        const loadResult = loadCSVData(results.data, columns);
        
        fs.unlinkSync(filePath);
        
        if (loadResult.success) {
          res.json({
            success: true,
            message: loadResult.message,
            columns: loadResult.columns,
            rowCount: results.data.length,
            preview: results.data.slice(0, 5)
          });
        } else {
          res.status(500).json({
            success: false,
            error: loadResult.error
          });
        }
      },
      error: (error) => {
        fs.unlinkSync(filePath);
        res.status(400).json({
          success: false,
          error: `CSV parse error: ${error.message}`
        });
      }
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.post('/api/analyze', async (req, res) => {
  req.setTimeout(300000);
  res.setTimeout(300000);
  
  try {
    const { pricingUrl } = req.body;
    
    if (!pricingUrl) {
      return res.status(400).json({
        success: false,
        error: 'Pricing URL is required'
      });
    }
    
    const result = await runReActAgent(pricingUrl);
    
    res.json(result);
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok',
    timestamp: new Date().toISOString(),
    openaiConfigured: !!process.env.OPENAI_API_KEY,
    dataLoaded: true
  });
});

const server = app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/api/health`);
  
  if (!process.env.OPENAI_API_KEY) {
    console.warn('OPENAI_API_KEY not set in environment variables');
  }
});

server.timeout = 300000;
server.keepAliveTimeout = 300000;
server.headersTimeout = 305000;

export default app;
