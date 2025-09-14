import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Divider,
  Chip,
  Paper,
} from '@mui/material';
import { PlayArrow, TextSnippet } from '@mui/icons-material';
import VideoPlayer from './VideoPlayer';
import LatexRenderer from './LatexRenderer';
import { LearningBlock } from '../types';

interface LearningModuleProps {
  learningBlocks: LearningBlock[];
  mainTopic: string;
  components: string[];
}

const LearningModule: React.FC<LearningModuleProps> = ({
  learningBlocks,
  mainTopic,
  components,
}) => {
  const renderMarkdownContent = (content: string) => {
    // Simple markdown-like rendering for basic formatting
    const lines = content.split('\n');
    return lines.map((line, index) => {
      if (line.startsWith('## ')) {
        return (
          <Typography key={index} variant="h4" component="h2" sx={{ mt: 4, mb: 3, fontWeight: 'bold', color: 'primary.main' }}>
            {line.replace('## ', '')}
          </Typography>
        );
      } else if (line.startsWith('### ')) {
        return (
          <Typography key={index} variant="h5" component="h3" sx={{ mt: 3, mb: 2, fontWeight: 'bold', color: 'text.primary' }}>
            {line.replace('### ', '')}
          </Typography>
        );
      } else if (line.startsWith('**') && line.endsWith('**')) {
        return (
          <Typography key={index} variant="h6" sx={{ fontWeight: 'bold', mb: 2, color: 'text.primary' }}>
            {line.replace(/\*\*/g, '')}
          </Typography>
        );
      } else if (line.startsWith('*   ')) {
        return (
          <Typography key={index} variant="body1" sx={{ ml: 3, mb: 1, fontSize: '1.1rem', lineHeight: 1.6 }}>
            • {line.replace('*   ', '')}
          </Typography>
        );
      } else if (line.trim() === '') {
        return <Box key={index} sx={{ height: 16 }} />;
      } else if (line.includes('$') && line.includes('$')) {
        // LaTeX math rendering
        return (
          <Box key={index} sx={{ mb: 2, fontSize: '1.1rem' }}>
            <LatexRenderer content={line} />
          </Box>
        );
      } else {
        return (
          <Typography key={index} variant="body1" sx={{ mb: 2, fontSize: '1.1rem', lineHeight: 1.7 }}>
            <LatexRenderer content={line} />
          </Typography>
        );
      }
    });
  };

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 2 }}>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {mainTopic}
        </Typography>
        <Typography variant="body1" sx={{ mb: 2 }}>
          Interactive learning with visualizations
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {components.map((component, index) => (
            <Chip
              key={index}
              label={component}
              variant="outlined"
              sx={{ color: 'white', borderColor: 'white' }}
            />
          ))}
        </Box>
      </Paper>

      {/* Learning Blocks */}
      {learningBlocks.map((block, index) => (
        <Card key={block.id} sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" component="h2" sx={{ flexGrow: 1 }}>
                {block.topic}
              </Typography>
              <Chip
                label={`Block ${block.id}`}
                size="small"
                color="primary"
                variant="outlined"
              />
            </Box>

            {block.text_content ? (
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <TextSnippet color="primary" />
                  <Typography variant="h6" color="primary">
                    Content
                  </Typography>
                </Box>
                <Box sx={{ 
                  backgroundColor: '#f8f9fa', 
                  p: 3, 
                  borderRadius: 2,
                  border: '1px solid #e9ecef'
                }}>
                  {renderMarkdownContent(block.text_content)}
                </Box>
              </Box>
            ) : (
              <Typography variant="body1" color="text.secondary" sx={{ fontStyle: 'italic', mb: 3 }}>
                No content available
              </Typography>
            )}

            <Divider sx={{ my: 3 }} />

            {/* Video Player */}
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <PlayArrow color="primary" sx={{ fontSize: 28 }} />
                <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
                  Visualization
                </Typography>
              </Box>
              <Box sx={{ 
                backgroundColor: '#f8f9fa', 
                p: 2, 
                borderRadius: 2,
                border: '1px solid #e9ecef'
              }}>
                <VideoPlayer
                  videoPath={block.visualization_path}
                  title={block.topic}
                />
              </Box>
            </Box>
          </CardContent>
        </Card>
      ))}

      {learningBlocks.length === 0 && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary">
              No content available
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default LearningModule;
