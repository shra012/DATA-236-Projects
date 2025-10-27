import { Paper, Box, Typography, TextField, Button, Chip } from '@mui/material';
import { CheckCircle, PlayArrow, CloudUpload } from '@mui/icons-material';

function UploadSection({ csvUploaded, pricingUrl, setPricingUrl, onCSVUpload, onAnalyze, analyzing }) {
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onCSVUpload(file);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3, borderRadius: 3 }}>
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 3 }}>
        
        <Box>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            1. Trip Data (CSV)
          </Typography>
          {csvUploaded ? (
            <Chip
              icon={<CheckCircle />}
              label="Data Loaded (500 rows)"
              color="success"
              sx={{ width: '100%', height: 'auto', py: 1.5, '& .MuiChip-label': { whiteSpace: 'normal' } }}
            />
          ) : (
            <Button
              fullWidth
              variant="outlined"
              component="label"
              startIcon={<CloudUpload />}
              sx={{ py: 1.5 }}
            >
              Upload CSV
              <input
                type="file"
                accept=".csv"
                hidden
                onChange={handleFileChange}
              />
            </Button>
          )}
        </Box>

        <Box>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            2. Pricing Policy URL
          </Typography>
          <TextField
            fullWidth
            type="url"
            value={pricingUrl}
            onChange={(e) => setPricingUrl(e.target.value)}
            placeholder="https://www.lyft.com/bikes/bay-wheels/pricing"
            variant="outlined"
            size="medium"
          />
        </Box>

        <Box>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            3. Run Analysis
          </Typography>
          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={onAnalyze}
            disabled={!csvUploaded || analyzing}
            startIcon={<PlayArrow />}
            sx={{ py: 1.5 }}
          >
            {analyzing ? 'Analyzing...' : 'Run Agent'}
          </Button>
        </Box>

      </Box>
    </Paper>
  );
}

export default UploadSection;
