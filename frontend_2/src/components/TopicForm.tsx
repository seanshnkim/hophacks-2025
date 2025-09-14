import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import { School, Psychology, Science, Code, Calculate } from '@mui/icons-material';
import { learningAPI } from '../services/api';
import { useLearning } from '../contexts/LearningContext';

const SUGGESTED_TOPICS = [
  { label: 'Linear Algebra', icon: <Calculate />, category: 'Math' },
  { label: 'Calculus', icon: <Calculate />, category: 'Math' },
  { label: 'Machine Learning', icon: <Psychology />, category: 'AI' },
  { label: 'Statistics', icon: <Science />, category: 'Math' },
  { label: 'Python Programming', icon: <Code />, category: 'Programming' },
  { label: 'Data Structures', icon: <Code />, category: 'Programming' },
  { label: 'Neural Networks', icon: <Psychology />, category: 'AI' },
  { label: 'Linear Functions', icon: <Calculate />, category: 'Math' },
];

const PERSONALIZATION_OPTIONS = [
  'I want to see visual examples',
  'Focus on practical applications',
  'I am a beginner',
  'Show me code examples',
  'I prefer mathematical explanations',
  'I want interactive content',
  'Focus on real-world use cases',
  'I learn better with step-by-step guides',
];

const TopicForm: React.FC = () => {
  const { setLearningData, setIsLoading, setError, error, isLoading } = useLearning();
  const [topic, setTopic] = useState('');
  const [userPreferences, setUserPreferences] = useState('');
  const [selectedPreferences, setSelectedPreferences] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const preferences = selectedPreferences.length > 0 
        ? selectedPreferences.join(', ')
        : userPreferences;

      const response = await learningAPI.generateLearningModule({
        topic: topic.trim(),
        user_preferences: preferences,
      });

      setLearningData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTopicClick = (selectedTopic: string) => {
    setTopic(selectedTopic);
  };

  const handlePreferenceToggle = (preference: string) => {
    setSelectedPreferences(prev => 
      prev.includes(preference)
        ? prev.filter(p => p !== preference)
        : [...prev, preference]
    );
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Card>
        <CardContent>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <School sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" component="h1" gutterBottom>
              AI Learning Module Generator
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Enter a topic for personalized learning with visualizations
            </Typography>
          </Box>

          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <Box>
                <TextField
                  fullWidth
                  label="What would you like to learn about?"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., Linear Algebra, Machine Learning, Python Programming"
                  variant="outlined"
                  required
                />
              </Box>

              <Box>
                <Typography variant="h6" gutterBottom>
                  Suggested Topics
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {SUGGESTED_TOPICS.map((suggestion) => (
                    <Chip
                      key={suggestion.label}
                      icon={suggestion.icon}
                      label={suggestion.label}
                      onClick={() => handleTopicClick(suggestion.label)}
                      variant={topic === suggestion.label ? 'filled' : 'outlined'}
                      color={topic === suggestion.label ? 'primary' : 'default'}
                    />
                  ))}
                </Box>
              </Box>

              <Box>
                <Typography variant="h6" gutterBottom>
                  Learning Preferences
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                  {PERSONALIZATION_OPTIONS.map((option) => (
                    <Chip
                      key={option}
                      label={option}
                      onClick={() => handlePreferenceToggle(option)}
                      variant={selectedPreferences.includes(option) ? 'filled' : 'outlined'}
                      color={selectedPreferences.includes(option) ? 'primary' : 'default'}
                    />
                  ))}
                </Box>
                <TextField
                  fullWidth
                  label="Additional preferences"
                  value={userPreferences}
                  onChange={(e) => setUserPreferences(e.target.value)}
                  placeholder="Specific learning style or focus areas..."
                  multiline
                  rows={2}
                  variant="outlined"
                />
              </Box>

              {error && (
                <Box>
                  <Alert severity="error">{error}</Alert>
                </Box>
              )}

              <Box>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  fullWidth
                  disabled={isLoading || !topic.trim()}
                  sx={{ py: 1.5 }}
                >
                  {isLoading ? (
                    <>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      Generating...
                    </>
                  ) : (
                    'Generate Learning Module'
                  )}
                </Button>
              </Box>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};

export default TopicForm;
