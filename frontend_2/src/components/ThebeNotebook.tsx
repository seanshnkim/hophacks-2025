import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { PlayArrow, Stop, Code, CheckCircle } from '@mui/icons-material';
import { LearnResponse } from '../types';

interface ThebeNotebookProps {
  data: LearnResponse | null;
}

// Declare thebelab on window
declare global {
  interface Window {
    thebelab?: {
      bootstrap: (config?: any) => void;
    };
  }
}

const ThebeNotebook: React.FC<ThebeNotebookProps> = ({ data }) => {
  const notebookRef = useRef<HTMLDivElement>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [kernelStatus, setKernelStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');

  useEffect(() => {
    const initializeThebe = () => {
      if (!data?.playground || isInitialized) return;

      try {
        setConnectionError(null);

        // Check if Thebe is available
        if (!window.thebelab) {
          setConnectionError('Thebe not loaded. Please refresh the page.');
          return;
        }

        // Configure Thebe with proper options
        const thebeConfig = {
          requestKernel: false,
          binderOptions: {
            repo: 'binder-examples/requirements',
            ref: 'master'
          },
          codeMirrorConfig: {
            theme: 'default'
          },
          selector: '.thebe-notebook'
        };

        // Store config globally
        (window as any).thebeConfig = thebeConfig;

        setIsInitialized(true);
        console.log('Thebe configured successfully');
      } catch (error) {
        console.error('Failed to configure Thebe:', error);
        setConnectionError('Failed to configure Thebe');
      }
    };

    // Wait a bit for the script to load
    const timer = setTimeout(initializeThebe, 1000);
    return () => clearTimeout(timer);
  }, [data?.playground, isInitialized]);

  const handleConnect = async () => {
    if (!window.thebelab) {
      setConnectionError('Thebe not loaded');
      return;
    }
    
    try {
      setIsConnecting(true);
      setConnectionError(null);
      setKernelStatus('connecting');
      
      // Configure Thebe with the current config
      const config = (window as any).thebeConfig || {
        requestKernel: true,
        binderOptions: {
          repo: 'binder-examples/requirements',
          ref: 'master'
        },
        codeMirrorConfig: {
          theme: 'default'
        },
        selector: '.thebe-notebook'
      };
      
      // Initialize Thebe with the config
      window.thebelab.bootstrap(config);
      
      // Listen for status changes
      setTimeout(() => {
        setKernelStatus('connected');
        setIsConnecting(false);
      }, 3000);
      
    } catch (error) {
      console.error('Connection error:', error);
      setConnectionError('Failed to connect to kernel');
      setIsConnecting(false);
      setKernelStatus('disconnected');
    }
  };

  const handleDisconnect = () => {
    setKernelStatus('disconnected');
  };

  const renderNotebookContent = () => {
    if (!data?.playground) {
      return (
        <Alert severity="info">
          No playground content available. Generate a learning module to see the interactive notebook.
        </Alert>
      );
    }

    // Parse the playground content and render as notebook cells
    try {
      const playgroundData = typeof data.playground === 'string' 
        ? JSON.parse(data.playground) 
        : data.playground;

      // Handle the correct structure: playground.cells is the array
      const cells = playgroundData?.cells || [];
      
      if (Array.isArray(cells) && cells.length > 0) {
        return cells.map((cell: any, index: number) => {
          if (cell.cell_type === 'code') {
            const codeContent = Array.isArray(cell.source) 
              ? cell.source.join('') 
              : cell.source || '';
            return (
              <div key={index} style={{ marginBottom: '16px' }}>
                <div style={{ 
                  border: '1px solid #e0e0e0', 
                  borderRadius: '4px',
                  overflow: 'hidden'
                }}>
                  <div style={{ 
                    backgroundColor: '#f5f5f5', 
                    padding: '8px', 
                    borderBottom: '1px solid #e0e0e0',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    <Code fontSize="small" />
                    <Typography variant="caption" color="text.secondary">
                      Code Cell {index + 1}
                    </Typography>
                    {kernelStatus === 'connected' && (
                      <Chip 
                        icon={<CheckCircle />} 
                        label="Ready" 
                        size="small" 
                        color="success" 
                        variant="outlined"
                      />
                    )}
                  </div>
                  <pre 
                    data-executable="true"
                    data-language="python"
                    style={{ 
                      padding: '16px', 
                      margin: 0, 
                      backgroundColor: '#fafafa',
                      fontFamily: 'monospace',
                      fontSize: '14px',
                      lineHeight: 1.5,
                      overflow: 'auto'
                    }}
                  >
                    {codeContent}
                  </pre>
                </div>
              </div>
            );
          } else if (cell.cell_type === 'markdown') {
            return (
              <div key={index} style={{ marginBottom: '16px' }}>
                <div style={{ 
                  border: '1px solid #e0e0e0', 
                  borderRadius: '4px',
                  padding: '16px',
                  backgroundColor: '#f9f9f9'
                }}>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    {Array.isArray(cell.source) 
                      ? cell.source.join('') 
                      : cell.source || ''}
                  </Typography>
                </div>
              </div>
            );
          }
          return null;
        });
      } else {
        // Fallback for empty or invalid playground data
        return (
          <Alert severity="info">
            No notebook cells available. Generate a learning module to see content.
          </Alert>
        );
      }
    } catch (error) {
      console.error('Error parsing playground data:', error);
      return (
        <Alert severity="error">
          Error parsing playground content. Please try regenerating the learning module.
        </Alert>
      );
    }
  };

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 2 }}>
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <Code color="primary" sx={{ fontSize: 28 }} />
            <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
              Interactive Notebook
            </Typography>
          </Box>

          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Execute code cells interactively using the Python kernel. Click "Connect" to start the session.
          </Typography>

          {/* Debug Info */}
          <Box sx={{ mb: 2, p: 1, backgroundColor: '#f0f0f0', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Debug: Thebe initialized: {isInitialized ? 'Yes' : 'No'} | 
              Kernel status: {kernelStatus} | 
              Playground data: {data?.playground ? 'Available' : 'None'}
            </Typography>
          </Box>

          {/* Connection Controls */}
          <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            {!isInitialized && (
              <Button
                variant="outlined"
                onClick={() => {
                  console.log('Manually triggering Thebe initialization...');
                  setIsInitialized(false);
                }}
                size="small"
              >
                Initialize Thebe
              </Button>
            )}
            {kernelStatus === 'disconnected' && isInitialized && (
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={handleConnect}
                disabled={isConnecting}
              >
                {isConnecting ? 'Connecting...' : 'Connect to Kernel'}
              </Button>
            )}
            
            {kernelStatus === 'connecting' && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={20} />
                <Typography variant="body2">Connecting to kernel...</Typography>
              </Box>
            )}
            
            {kernelStatus === 'connected' && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Chip 
                  icon={<CheckCircle />} 
                  label="Connected" 
                  color="success" 
                  variant="outlined"
                />
                <Button
                  variant="outlined"
                  startIcon={<Stop />}
                  onClick={handleDisconnect}
                  size="small"
                >
                  Disconnect
                </Button>
              </Box>
            )}
          </Box>

          {/* Error Display */}
          {connectionError && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {connectionError}
            </Alert>
          )}

          {/* Notebook Content */}
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
              Notebook Cells
            </Typography>
            <div 
              ref={notebookRef}
              className="thebe-notebook"
              style={{ 
                flex: 1, 
                overflow: 'auto',
                border: '1px solid #e0e0e0',
                borderRadius: '4px',
                padding: '16px',
                backgroundColor: '#fafafa'
              }}
            >
              {/* Simple test cell */}
              <pre data-executable="true" data-language="python" style={{ 
                padding: '16px', 
                backgroundColor: '#f5f5f5',
                borderRadius: '4px',
                fontFamily: 'monospace',
                fontSize: '14px',
                lineHeight: 1.5,
                overflow: 'auto',
                border: '1px solid #e0e0e0',
                marginBottom: '16px'
              }}>
                {`print("Hello from Thebe!")
print("This should be executable")`}
              </pre>
              
              {/* Render actual content */}
              {renderNotebookContent()}
            </div>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ThebeNotebook;
