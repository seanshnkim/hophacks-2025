import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Alert, Snackbar } from '@mui/material';
import { LearningProvider, useLearning } from './contexts/LearningContext';
import TopicForm from './components/TopicForm';
import LearningModule from './components/LearningModule';
import JsonDisplay from './components/JsonDisplay';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

const AppContent: React.FC = () => {
  const { learningData, error, setError } = useLearning();

  const handleCloseError = () => {
    setError(null);
  };

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <CssBaseline />
      
      {!learningData ? (
        <TopicForm />
      ) : (
        <Box sx={{ 
          display: 'flex', 
          flexDirection: { xs: 'column', md: 'row' },
          height: '100vh',
          width: '100%'
        }}>
          <Box sx={{ 
            width: { xs: '100%', md: '50%' },
            height: { xs: '50%', md: '100%' },
            overflow: 'hidden'
          }}>
            <LearningModule
              learningBlocks={learningData.learning_blocks}
              mainTopic={learningData.main_topic}
              components={learningData.components}
            />
          </Box>
          <Box sx={{ 
            width: { xs: '100%', md: '50%' },
            height: { xs: '50%', md: '100%' },
            overflow: 'hidden'
          }}>
            <JsonDisplay data={learningData} />
          </Box>
        </Box>
      )}

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={handleCloseError}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <LearningProvider>
        <AppContent />
      </LearningProvider>
    </ThemeProvider>
  );
};

export default App;
