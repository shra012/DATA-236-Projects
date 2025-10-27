import { useState, useEffect } from 'react';
import axios from 'axios';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Container, Box, Typography, Alert, CssBaseline, Paper } from '@mui/material';
import UploadSection from './components/UploadSection';
import Timeline from './components/Timeline';
import Results from './components/Results';
import MetricsStrip from './components/MetricsStrip';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2196f3',
      light: '#64b5f6',
      dark: '#1976d2',
    },
    secondary: {
      main: '#ff5722',
      light: '#ff8a65',
      dark: '#e64a19',
    },
    success: {
      main: '#4caf50',
      light: '#81c784',
      dark: '#388e3c',
    },
    warning: {
      main: '#ff9800',
      light: '#ffb74d',
      dark: '#f57c00',
    },
    info: {
      main: '#00bcd4',
      light: '#4dd0e1',
      dark: '#0097a7',
    },
    background: {
      default: '#f0f2f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h3: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 16,
  },
  shadows: [
    'none',
    '0px 2px 4px rgba(0,0,0,0.05)',
    '0px 4px 8px rgba(0,0,0,0.08)',
    '0px 8px 16px rgba(0,0,0,0.1)',
    '0px 12px 24px rgba(0,0,0,0.12)',
    '0px 16px 32px rgba(0,0,0,0.14)',
  ],
});

function App() {
  const [csvUploaded, setCsvUploaded] = useState(false);
  const [pricingUrl, setPricingUrl] = useState('https://www.lyft.com/bikes/bay-wheels/pricing');
  const [analyzing, setAnalyzing] = useState(false);
  const [steps, setSteps] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);

  const handleCSVUpload = async (file) => {
    const formData = new FormData();
    formData.append('csv', file);

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (response.data.success) {
        setCsvUploaded(true);
        setError(null);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  const handleAnalyze = async () => {
    if (!pricingUrl) {
      alert('Please enter a pricing URL');
      return;
    }

    setAnalyzing(true);
    setSteps([]);
    setMetrics(null);
    setError(null);

    try {
      const response = await axios.post('/api/analyze', { pricingUrl });

      if (response.data.success) {
        setSteps(response.data.steps);
        setMetrics(response.data.metrics);
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
        <Container maxWidth="xl">
          <Paper
            elevation={0}
            sx={{
              background: 'linear-gradient(135deg, #2196f3 0%, #1976d2 50%, #0d47a1 100%)',
              color: 'white',
              textAlign: 'center',
              py: 6,
              px: 3,
              mb: 4,
              borderRadius: 4,
              boxShadow: '0 8px 32px rgba(33, 150, 243, 0.3)',
            }}
          >
            <Typography variant="h3" component="h1" gutterBottom fontWeight={600}>
              Bike-Share Pass Optimizer
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.95 }}>
              Bay Wheels Agent Analysis
            </Typography>
          </Paper>

          <UploadSection
            csvUploaded={csvUploaded}
            pricingUrl={pricingUrl}
            setPricingUrl={setPricingUrl}
            onCSVUpload={handleCSVUpload}
            onAnalyze={handleAnalyze}
            analyzing={analyzing}
          />

          {error && (
            <Alert severity="error" sx={{ my: 3 }}>
              <strong>Error:</strong> {error}
            </Alert>
          )}

          {metrics && <MetricsStrip metrics={metrics} />}

          {steps.length > 0 && (
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 3, mt: 4 }}>
              <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                <Timeline steps={steps} />
              </Paper>
              <Paper elevation={3} sx={{ p: 3, borderRadius: 3 }}>
                <Results steps={steps} />
              </Paper>
            </Box>
          )}
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
