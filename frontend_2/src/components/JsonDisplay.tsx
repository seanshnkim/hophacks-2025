import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
} from '@mui/material';
import { Code, VideoLibrary, TextSnippet } from '@mui/icons-material';
import { LearnResponse } from '../types';

interface JsonDisplayProps {
  data: LearnResponse | null;
}

const JsonDisplay: React.FC<JsonDisplayProps> = ({ data }) => {
  if (!data) {
    return (
      <Card sx={{ height: '100vh', overflow: 'auto' }}>
        <CardContent>
          <Typography variant="h6" color="text.secondary" textAlign="center">
            No data to display
          </Typography>
        </CardContent>
      </Card>
    );
  }


  const getBlockStats = () => {
    const totalBlocks = data.learning_blocks.length;
    const blocksWithContent = data.learning_blocks.filter(block => block.text_content.trim()).length;
    const blocksWithVideo = data.learning_blocks.filter(block => block.visualization_path).length;
    
    return { totalBlocks, blocksWithContent, blocksWithVideo };
  };

  const stats = getBlockStats();

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 2 }}>
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <Code color="primary" sx={{ fontSize: 28 }} />
            <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
              Interactive Playground
            </Typography>
          </Box>

          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Interactive Jupyter notebook for hands-on learning.
          </Typography>

          {/* Data Display */}
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Learning data loaded successfully. Use the left panel to explore content.
            </Typography>
          </Box>

          {/* Quick Stats */}
          <Box sx={{ mt: 3, p: 2, backgroundColor: '#f8f9fa', borderRadius: 2, border: '1px solid #e9ecef' }}>
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
              Module Summary
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Chip
                icon={<TextSnippet />}
                label={`${stats.blocksWithContent}/${stats.totalBlocks} topics`}
                color="success"
                variant="outlined"
              />
              <Chip
                icon={<VideoLibrary />}
                label={`${stats.blocksWithVideo}/${stats.totalBlocks} videos`}
                color="primary"
                variant="outlined"
              />
              <Chip
                label={`${data.components.length} components`}
                color="secondary"
                variant="outlined"
              />
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default JsonDisplay;
