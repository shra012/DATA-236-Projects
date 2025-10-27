import { Typography, Box, Chip, Paper } from '@mui/material';
import { Lightbulb, Build, Visibility, CheckCircle } from '@mui/icons-material';

function Timeline({ steps }) {
  const getIcon = (type) => {
    switch (type) {
      case 'thought': return <Lightbulb />;
      case 'action': return <Build />;
      case 'observation': return <Visibility />;
      case 'answer': return <CheckCircle />;
      default: return null;
    }
  };

  const getColor = (type) => {
    switch (type) {
      case 'thought': return 'primary';
      case 'action': return 'warning';
      case 'observation': return 'success';
      case 'answer': return 'secondary';
      default: return 'default';
    }
  };

  return (
    <div>
      <Typography variant="h5" gutterBottom fontWeight={600} color="primary">
        Agent Timeline
      </Typography>
      
      <Box sx={{ position: 'relative', pl: 4, pt: 2 }}>
        {/* Vertical line */}
        <Box
          sx={{
            position: 'absolute',
            left: 15,
            top: 0,
            bottom: 0,
            width: 2,
            bgcolor: 'grey.300',
          }}
        />

        {steps.map((step, index) => (
          <Box key={index} sx={{ position: 'relative', mb: 3, pb: 3 }}>
            {/* Timeline dot */}
            <Box
              sx={{
                position: 'absolute',
                left: -32,
                width: 32,
                height: 32,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'background.paper',
                border: 2,
                borderColor: `${getColor(step.type)}.main`,
                color: `${getColor(step.type)}.main`,
              }}
            >
              {getIcon(step.type)}
            </Box>

            {/* Content */}
            <Paper
              elevation={2}
              sx={{
                p: 2,
                bgcolor: step.type === 'answer' ? 'info.50' : 'grey.50',
                borderLeft: 4,
                borderColor: `${getColor(step.type)}.main`,
                borderRadius: 2,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Typography variant="subtitle2" fontWeight={600}>
                  {step.type.charAt(0).toUpperCase() + step.type.slice(1)}
                </Typography>
                {step.tool && (
                  <Chip label={step.tool} size="small" variant="outlined" />
                )}
              </Box>

              <Box>
                {step.type === 'thought' && (
                  <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                    {step.content}
                  </Typography>
                )}

                {step.type === 'action' && (
                  <Paper
                    variant="outlined"
                    sx={{
                      p: 1.5,
                      bgcolor: 'background.paper',
                      fontFamily: 'monospace',
                      fontSize: '0.813rem',
                      overflow: 'auto',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                    }}
                  >
                    {JSON.stringify(JSON.parse(step.input), null, 2)}
                  </Paper>
                )}

                {step.type === 'observation' && (
                  <Box>
                    <Chip
                      label={step.content.success ? 'Success' : 'Error'}
                      color={step.content.success ? 'success' : 'error'}
                      size="small"
                      sx={{ mb: 1 }}
                    />
                    <Paper
                      variant="outlined"
                      sx={{
                        p: 1.5,
                        bgcolor: 'background.paper',
                        fontFamily: 'monospace',
                        fontSize: '0.813rem',
                        overflow: 'auto',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {JSON.stringify(step.content, null, 2)}
                    </Paper>
                  </Box>
                )}

                {step.type === 'answer' && (
                  <Typography
                    variant="body2"
                    sx={{
                      lineHeight: 1.7,
                      whiteSpace: 'pre-wrap',
                      wordWrap: 'break-word',
                    }}
                  >
                    {step.content}
                  </Typography>
                )}
              </Box>
            </Paper>
          </Box>
        ))}
      </Box>
    </div>
  );
}

export default Timeline;
