import React, { createContext, useContext, useState, ReactNode } from 'react';
import { LearnResponse } from '../types';

interface NotebookData {
  cells: any[];
  metadata: any;
  nbformat: number;
  nbformat_minor: number;
}

interface LearningContextType {
  learningData: LearnResponse | null;
  setLearningData: (data: LearnResponse | null) => void;
  notebookData: NotebookData | null;
  setNotebookData: (data: NotebookData | null) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
  selectedVideo: string | null;
  setSelectedVideo: (video: string | null) => void;
}

const LearningContext = createContext<LearningContextType | undefined>(undefined);

export const useLearning = () => {
  const context = useContext(LearningContext);
  if (context === undefined) {
    throw new Error('useLearning must be used within a LearningProvider');
  }
  return context;
};

interface LearningProviderProps {
  children: ReactNode;
}

export const LearningProvider: React.FC<LearningProviderProps> = ({ children }) => {
  const [learningData, setLearningData] = useState<LearnResponse | null>(null);
  const [notebookData, setNotebookData] = useState<NotebookData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);

  return (
    <LearningContext.Provider
      value={{
        learningData,
        setLearningData,
        notebookData,
        setNotebookData,
        isLoading,
        setIsLoading,
        error,
        setError,
        selectedVideo,
        setSelectedVideo,
      }}
    >
      {children}
    </LearningContext.Provider>
  );
};
