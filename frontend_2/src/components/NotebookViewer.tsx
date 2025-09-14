import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Button,
  Paper,
  Divider,
} from '@mui/material';
import { Code, PlayArrow, Refresh } from '@mui/icons-material';
// Pyodide will be loaded dynamically from CDN

// Extend window interface for Pyodide
declare global {
  interface Window {
    loadPyodide: (config: any) => Promise<any>;
  }
}

interface NotebookCell {
  cell_type: 'markdown' | 'code';
  source: string[];
  metadata: any;
  outputs?: NotebookOutput[];
  execution_count?: number;
}

interface NotebookData {
  cells: NotebookCell[];
  metadata: any;
  nbformat: number;
  nbformat_minor: number;
}

interface NotebookOutput {
  output_type: 'execute_result' | 'stream' | 'error';
  data?: {
    'text/plain': string[];
  };
  text?: string[];
  name?: string;
  ename?: string;
  evalue?: string;
  traceback?: string[];
  execution_count?: number;
}

interface NotebookViewerProps {
  notebookData: NotebookData | null;
  isLoading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
}

const NotebookViewer: React.FC<NotebookViewerProps> = ({
  notebookData,
  isLoading = false,
  error = null,
  onRefresh,
}) => {
  const [pyodide, setPyodide] = useState<any>(null);
  const [isPyodideLoading, setIsPyodideLoading] = useState(true);
  const [executedCells, setExecutedCells] = useState<Set<number>>(new Set());
  const [cellOutputs, setCellOutputs] = useState<Map<number, NotebookOutput[]>>(new Map());
  const [editableCode, setEditableCode] = useState<Map<number, string>>(new Map());
  const pyodideRef = useRef<any>(null);

  // Initialize Pyodide
  useEffect(() => {
    const initPyodide = async () => {
      try {
        console.log('Loading Pyodide...');
        // Load Pyodide from CDN dynamically
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js';
        script.onload = async () => {
          try {
            const pyodideInstance = await window.loadPyodide({
              indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/',
            });
            setPyodide(pyodideInstance);
            pyodideRef.current = pyodideInstance;
            setIsPyodideLoading(false);
            console.log('Pyodide loaded successfully');
          } catch (error) {
            console.error('Failed to initialize Pyodide:', error);
            setIsPyodideLoading(false);
          }
        };
        script.onerror = () => {
          console.error('Failed to load Pyodide script');
          setIsPyodideLoading(false);
        };
        document.head.appendChild(script);
      } catch (error) {
        console.error('Failed to load Pyodide:', error);
        setIsPyodideLoading(false);
      }
    };

    initPyodide();
  }, []);

  const executeCode = async (code: string, cellIndex: number) => {
    if (!pyodideRef.current) {
      console.error('Pyodide not loaded');
      return;
    }

    try {
      console.log(`Executing code in cell ${cellIndex}:`, code);
      
      // Clear previous outputs for this cell
      setCellOutputs(prev => {
        const newOutputs = new Map(prev);
        newOutputs.delete(cellIndex);
        return newOutputs;
      });

      // Execute the code and capture both result and stdout
      const result = pyodideRef.current.runPython(`
        import sys
        from io import StringIO
        import traceback
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Execute the user code
            exec("""${code.replace(/"/g, '\\"').replace(/\n/g, '\\n')}""")
            result = None
        except Exception as e:
            result = e
            traceback.print_exc()
        finally:
            sys.stdout = old_stdout
        
        # Get the captured output
        stdout_content = captured_output.getvalue()
        
        # Return both result and stdout
        (result, stdout_content)
      `);

      const [execResult, stdout] = result;

      // Create output objects
      const outputs: NotebookOutput[] = [];

      // Add stdout if there's any
      if (stdout && stdout.trim()) {
        outputs.push({
          output_type: 'stream',
          name: 'stdout',
          text: [stdout],
        });
      }

      // Add result or error
      if (execResult instanceof Error) {
        outputs.push({
          output_type: 'error',
          ename: execResult.constructor.name,
          evalue: String(execResult),
          traceback: [String(execResult)],
        });
      } else if (execResult !== null) {
        outputs.push({
          output_type: 'execute_result',
          data: {
            'text/plain': [String(execResult)],
          },
          execution_count: cellIndex + 1,
        });
      }

      // Update outputs
      setCellOutputs(prev => {
        const newOutputs = new Map(prev);
        newOutputs.set(cellIndex, outputs);
        return newOutputs;
      });

      // Mark cell as executed
      setExecutedCells(prev => {
        const newSet = new Set(prev);
        newSet.add(cellIndex);
        return newSet;
      });

    } catch (error) {
      console.error(`Error executing code in cell ${cellIndex}:`, error);
      
      // Create error output
      const errorOutput: NotebookOutput = {
        output_type: 'error',
        ename: 'PythonError',
        evalue: String(error),
        traceback: [String(error)],
      };

      setCellOutputs(prev => {
        const newOutputs = new Map(prev);
        newOutputs.set(cellIndex, [errorOutput]);
        return newOutputs;
      });
    }
  };

  const renderMarkdown = (source: string[]) => {
    const content = source.join('');
    return (
      <Box
        sx={{
          '& h1': { fontSize: '1.5rem', fontWeight: 'bold', mb: 2, color: 'primary.main' },
          '& h2': { fontSize: '1.3rem', fontWeight: 'bold', mb: 1.5, color: 'text.primary' },
          '& h3': { fontSize: '1.1rem', fontWeight: 'bold', mb: 1, color: 'text.primary' },
          '& p': { mb: 1.5, lineHeight: 1.6 },
          '& ul': { mb: 1.5, pl: 2 },
          '& li': { mb: 0.5 },
          '& code': { 
            backgroundColor: '#f5f5f5', 
            padding: '2px 4px', 
            borderRadius: '3px',
            fontFamily: 'monospace',
            fontSize: '0.9em'
          },
          '& pre': {
            backgroundColor: '#f5f5f5',
            padding: '12px',
            borderRadius: '4px',
            overflow: 'auto',
            mb: 2,
          },
        }}
        dangerouslySetInnerHTML={{ __html: content.replace(/\n/g, '<br/>') }}
      />
    );
  };

  const renderCodeCell = (cell: NotebookCell, index: number) => {
    const originalCode = cell.source.join('');
    const editableCodeValue = editableCode.get(index) || originalCode;
    const isExecuted = executedCells.has(index);
    const outputs = cellOutputs.get(index) || [];

    const handleCodeChange = (newCode: string) => {
      setEditableCode(prev => {
        const newMap = new Map(prev);
        newMap.set(index, newCode);
        return newMap;
      });
    };

    return (
      <Paper key={index} sx={{ mb: 2, border: '1px solid #e0e0e0' }}>
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="caption" sx={{ mr: 2, color: 'text.secondary' }}>
              In [{cell.execution_count || ' '}]:
            </Typography>
            <Button
              size="small"
              startIcon={<PlayArrow />}
              onClick={() => executeCode(editableCodeValue, index)}
              disabled={!pyodide || isPyodideLoading}
              variant="outlined"
              sx={{ ml: 'auto' }}
            >
              {isPyodideLoading ? 'Loading...' : 'Run'}
            </Button>
          </Box>
          
          <Box
            component="textarea"
            value={editableCodeValue}
            onChange={(e) => handleCodeChange(e.target.value)}
            sx={{
              backgroundColor: '#f8f9fa',
              p: 2,
              borderRadius: 1,
              fontFamily: 'monospace',
              fontSize: '0.9rem',
              width: '100%',
              minHeight: '100px',
              border: '1px solid #e0e0e0',
              resize: 'vertical',
              outline: 'none',
              '&:focus': {
                borderColor: '#1976d2',
                boxShadow: '0 0 0 2px rgba(25, 118, 210, 0.2)',
              },
              mb: outputs.length > 0 ? 2 : 0,
            }}
            placeholder="Enter your Python code here..."
          />

          {outputs.map((output, outputIndex) => (
            <Box key={outputIndex} sx={{ mb: 1 }}>
              {output.output_type === 'execute_result' && (
                <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                  <Typography variant="caption" sx={{ mr: 2, color: 'text.secondary', minWidth: '60px' }}>
                    Out [{output.execution_count}]:
                  </Typography>
                  <Box
                    component="pre"
                    sx={{
                      backgroundColor: '#f8f9fa',
                      p: 1,
                      borderRadius: 1,
                      fontFamily: 'monospace',
                      fontSize: '0.9rem',
                      flex: 1,
                    }}
                  >
                    {output.data?.['text/plain']?.join('') || String(output.data || '')}
                  </Box>
                </Box>
              )}

              {output.output_type === 'stream' && (
                <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                  <Typography variant="caption" sx={{ mr: 2, color: 'text.secondary', minWidth: '60px' }}>
                    {output.name}:
                  </Typography>
                  <Box
                    component="pre"
                    sx={{
                      backgroundColor: '#f8f9fa',
                      p: 1,
                      borderRadius: 1,
                      fontFamily: 'monospace',
                      fontSize: '0.9rem',
                      flex: 1,
                    }}
                  >
                    {output.text?.join('') || String(output.text)}
                  </Box>
                </Box>
              )}
              
              {output.output_type === 'error' && (
                <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                  <Typography variant="caption" sx={{ mr: 2, color: 'error.main', minWidth: '60px' }}>
                    Error:
                  </Typography>
                  <Box
                    component="pre"
                    sx={{
                      backgroundColor: '#ffebee',
                      p: 1,
                      borderRadius: 1,
                      fontFamily: 'monospace',
                      fontSize: '0.9rem',
                      color: 'error.main',
                      flex: 1,
                    }}
                  >
                    {output.evalue}
                  </Box>
                </Box>
              )}
            </Box>
          ))}
        </Box>
      </Paper>
    );
  };

  if (isLoading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            Loading notebook...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
          <Alert severity="error" sx={{ mb: 2, width: '100%' }}>
            {error}
          </Alert>
          {onRefresh && (
            <Button startIcon={<Refresh />} onClick={onRefresh} variant="outlined">
              Try Again
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  if (!notebookData) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
          <Typography variant="h6" color="text.secondary">
            No notebook data available
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ height: '100%', overflow: 'auto', p: 2 }}>
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <Code color="primary" sx={{ fontSize: 28 }} />
            <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
              Interactive Notebook
            </Typography>
            {onRefresh && (
              <Button
                startIcon={<Refresh />}
                onClick={onRefresh}
                variant="outlined"
                size="small"
                sx={{ ml: 'auto' }}
              >
                Refresh
              </Button>
            )}
          </Box>

          {isPyodideLoading && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Loading Python runtime...
            </Alert>
          )}

          <Box sx={{ flex: 1, overflow: 'auto' }}>
            {notebookData.cells.map((cell, index) => (
              <Box key={index}>
                {cell.cell_type === 'markdown' ? (
                  <Box sx={{ mb: 3, p: 2, backgroundColor: '#fafafa', borderRadius: 1 }}>
                    {renderMarkdown(cell.source)}
                  </Box>
                ) : (
                  renderCodeCell(cell, index)
                )}
                {index < notebookData.cells.length - 1 && <Divider sx={{ my: 2 }} />}
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default NotebookViewer;
