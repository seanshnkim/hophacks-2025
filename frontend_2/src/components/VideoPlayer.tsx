import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  Typography,
  IconButton,
} from '@mui/material';
import {
  PlayArrow,
  VolumeOff,
  VolumeUp,
  Fullscreen,
} from '@mui/icons-material';
import { learningAPI } from '../services/api';

interface VideoPlayerProps {
  videoPath: string | null;
  title: string;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoPath, title }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!videoPath) {
    return (
      <Card sx={{ minHeight: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary" textAlign="center">
            No visualization available for this topic
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const handlePlay = () => {
    setIsLoading(true);
    setError(null);
    setIsPlaying(true);
  };

  const handleVideoLoad = () => {
    setIsLoading(false);
  };

  const handleVideoError = () => {
    setIsLoading(false);
    setError('Failed to load video');
    setIsPlaying(false);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const toggleFullscreen = () => {
    const video = document.getElementById(`video-${videoPath}`);
    if (video) {
      if (video.requestFullscreen) {
        video.requestFullscreen();
      }
    }
  };

  return (
    <Card sx={{ minHeight: 200 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        
        {!isPlaying ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: 200,
              backgroundColor: '#f5f5f5',
              borderRadius: 1,
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: '#eeeeee',
              },
            }}
            onClick={handlePlay}
          >
            <PlayArrow sx={{ fontSize: 48, color: 'primary.main' }} />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Click to play visualization
            </Typography>
          </Box>
        ) : (
          <Box sx={{ position: 'relative' }}>
            <video
              id={`video-${videoPath}`}
              src={learningAPI.getVisualizationUrl(videoPath)}
              controls
              muted={isMuted}
              autoPlay
              onLoadedData={handleVideoLoad}
              onError={handleVideoError}
              style={{
                width: '100%',
                maxHeight: '400px',
                borderRadius: '4px',
              }}
            />
            
            {isLoading && (
              <Box
                sx={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                }}
              >
                <CircularProgress />
              </Box>
            )}
            
            {error && (
              <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                {error}
              </Typography>
            )}
            
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              <IconButton onClick={toggleMute} size="small">
                {isMuted ? <VolumeOff /> : <VolumeUp />}
              </IconButton>
              <IconButton onClick={toggleFullscreen} size="small">
                <Fullscreen />
              </IconButton>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default VideoPlayer;
