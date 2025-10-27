import { Typography, Box, Paper, Chip, Link, List, ListItem } from '@mui/material';
import { RecommendOutlined, DescriptionOutlined, LinkOutlined } from '@mui/icons-material';

function Results({ steps }) {
  const answerStep = steps.find(step => step.type === 'answer');
  
  if (!answerStep) {
    return (
      <div>
        <Typography variant="h5" gutterBottom fontWeight={600} color="primary">
          Results & Recommendation
        </Typography>
        <Typography variant="body2" color="text.secondary" fontStyle="italic">
          Analysis in progress...
        </Typography>
      </div>
    );
  }

  const answer = answerStep.content;

  let decision = 'See Analysis Below';
  let decisionColor = 'default';
  
  const lowerAnswer = answer.toLowerCase();
  
  // Check for membership recommendation
  if ((lowerAnswer.includes('buy') || lowerAnswer.includes('purchase') || lowerAnswer.includes('get')) && 
      (lowerAnswer.includes('membership') || lowerAnswer.includes('monthly') || lowerAnswer.includes('annual'))) {
    decision = 'Buy Monthly Membership';
    decisionColor = 'success';
  } 
  // Check for pay-per-ride recommendation
  else if ((lowerAnswer.includes('pay per') || lowerAnswer.includes('pay-per') || 
            lowerAnswer.includes('single ride') || lowerAnswer.includes('per ride')) && 
           !lowerAnswer.includes('recommended') && !lowerAnswer.includes('buy')) {
    decision = 'Pay Per Ride/Minute';
    decisionColor = 'warning';
  }
  // Check for explicit "not recommended" or "don't buy"
  else if (lowerAnswer.includes('not recommended') || lowerAnswer.includes("don't buy") || 
           lowerAnswer.includes('avoid')) {
    decision = 'Pay Per Ride/Minute';
    decisionColor = 'warning';
  }
  // Check if membership is recommended
  else if (lowerAnswer.includes('recommended') && lowerAnswer.includes('membership')) {
    decision = 'Buy Monthly Membership';
    decisionColor = 'success';
  }

  return (
    <div>
      <Typography variant="h5" gutterBottom fontWeight={600} color="primary">
        Results & Recommendation
      </Typography>
      
      <Paper
        elevation={0}
        sx={{
          background: 'linear-gradient(135deg, #ff5722 0%, #ff9800 100%)',
          color: 'white',
          p: 3,
          mb: 2,
          borderRadius: 3,
          boxShadow: '0 4px 20px rgba(255, 87, 34, 0.3)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <RecommendOutlined />
          <Typography variant="subtitle2" sx={{ opacity: 0.9 }}>
            Recommendation
          </Typography>
        </Box>
        <Chip
          label={decision}
          color={decisionColor}
          sx={{
            fontSize: '1.1rem',
            fontWeight: 700,
            height: 'auto',
            py: 1,
            px: 2,
            bgcolor: 'white',
            color: decisionColor === 'success' ? 'success.main' : 'warning.main',
          }}
        />
      </Paper>

      <Paper elevation={2} sx={{ p: 2.5, mb: 2, bgcolor: 'grey.50', borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <DescriptionOutlined color="primary" />
          <Typography variant="h6" fontWeight={600} color="primary">
            Analysis & Justification
          </Typography>
        </Box>
        <Typography
          variant="body2"
          sx={{
            lineHeight: 1.8,
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            color: 'text.primary',
          }}
        >
          {answer}
        </Typography>
      </Paper>

      <Paper elevation={2} sx={{ p: 2.5, bgcolor: 'grey.50', borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <LinkOutlined color="primary" />
          <Typography variant="h6" fontWeight={600} color="primary">
            Citations & Sources
          </Typography>
        </Box>
        <List dense>
          {steps
            .filter(step => step.type === 'observation' && step.content.success)
            .map((step, index) => {
              let urls = new Set();
              
              if (step.content.data?.passages) {
                step.content.data.passages.forEach(p => {
                  if (p.source && p.source.startsWith('http')) {
                    urls.add(p.source);
                  }
                });
              }
              
              const source = step.content.source || step.content.data?.source;
              if (source && typeof source === 'string' && source.startsWith('http')) {
                urls.add(source);
              }
              
              return Array.from(urls).map((url, urlIndex) => (
                <ListItem key={`${index}-${urlIndex}`} sx={{ py: 0.5 }}>
                  <Link
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{
                      fontFamily: 'monospace',
                      fontSize: '0.875rem',
                      wordBreak: 'break-all',
                    }}
                  >
                    {url}
                  </Link>
                </ListItem>
              ));
            })
            .flat()
            .filter(Boolean)}
          
          {steps.filter(step => step.type === 'observation' && step.content.success).length === 0 && (
            <ListItem>
              <Typography variant="body2" color="text.secondary" fontStyle="italic">
                No external sources cited
              </Typography>
            </ListItem>
          )}
        </List>
      </Paper>
    </div>
  );
}

export default Results;
