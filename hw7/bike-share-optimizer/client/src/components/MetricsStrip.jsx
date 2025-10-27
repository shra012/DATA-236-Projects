import { Paper, Box, Typography, Chip } from '@mui/material';
import { Timeline, Loop, Timer, CheckCircle } from '@mui/icons-material';

function MetricsStrip({ metrics }) {
  if (!metrics) return null;

  const metricItems = [
    { label: 'Total Steps', value: metrics.totalSteps, icon: <Timeline /> },
    { label: 'Iterations', value: metrics.iterations, icon: <Loop /> },
    { label: 'Total Time', value: metrics.totalTime, icon: <Timer /> },
    { label: 'Stop Reason', value: metrics.stopReason, icon: <CheckCircle /> },
  ];

  return (
    <Paper elevation={3} sx={{ p: 2, mb: 3, borderRadius: 3 }}>
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr 1fr', md: 'repeat(4, 1fr)' }, gap: 2 }}>
        {metricItems.map((item, index) => (
          <Box key={index} sx={{ textAlign: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1, color: 'primary.main' }}>
              {item.icon}
              <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                {item.label}
              </Typography>
            </Box>
            <Chip
              label={item.value}
              color="primary"
              variant="outlined"
              sx={{ fontWeight: 600, fontSize: '1rem' }}
            />
          </Box>
        ))}
      </Box>
    </Paper>
  );
}

export default MetricsStrip;
