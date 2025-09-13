import axios from 'axios';
import { LearnRequest, LearnResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

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

  async checkHealth(): Promise<boolean> {
    try {
      const response = await api.get('/health');
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }
};
