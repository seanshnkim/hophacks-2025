import axios from 'axios';
import { LearnRequest, LearnResponse } from '../types';

// const API_BASE_URL = 'http://localhost:8000';
const API_BASE_URL = 'https://hophacks-learnwiz-backend.sliplane.app';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for learning generation
});

export const learningAPI = {
  async generateLearningModule(request: LearnRequest): Promise<LearnResponse> {
    try {
      const response = await api.post<LearnResponse>('/learn', request);
      return response.data;
    } catch (error) {
      console.error('Error generating learning module:', error);
      throw new Error('Failed to generate learning module. Please try again.');
    }
  },

  getVisualizationUrl(visualizationPath: string): string {
    return `${API_BASE_URL}/visualization/${visualizationPath}`;
  },

  getNotebookUrl(filename: string): string {
    return `${API_BASE_URL}/notebook/${filename}`;
  },

  async fetchNotebook(filename: string): Promise<any> {
    try {
      const response = await api.get(`/notebook/${filename}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching notebook:', error);
      throw new Error('Failed to fetch notebook. Please try again.');
    }
  },

  async checkHealth(): Promise<boolean> {
    try {
      const response = await api.get('/health');
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }
};
