import axios from 'axios';

// Use environment variable for API URL, fallback to localhost in development
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.MODE === 'production' ? '' : 'http://localhost:8000');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Existing functions
export const getStats = async () => {
  const response = await api.get('/api/stats');
  return response.data;
};

export const getSummaryData = async (limit = 100, offset = 0) => {
  const response = await api.get('/api/summary', {
    params: { limit, offset }
  });
  return response.data;
};

export const getLatestSummary = async () => {
  const response = await api.get('/api/summary/latest');
  return response.data;
};

export const getStreamList = async () => {
  const response = await api.get('/api/stream/list');
  return response.data;
};

export const getStreamData = async (streamName, limit = 1000) => {
  const response = await api.get(`/api/stream/${encodeURIComponent(streamName)}`, {
    params: { limit }
  });
  return response.data;
};

// New functions for draw data
export const getDrawRecords = async (params = {}) => {
  const response = await api.get('/api/draws', { params });
  return response.data;
};

export const getDrawStreams = async () => {
  const response = await api.get('/api/draws/streams');
  return response.data;
};

export const getDrawTrends = async (params = {}) => {
  const response = await api.get('/api/draws/trends', { params });
  return response.data;
};

export const getDrawStats = async (params = {}) => {
  const response = await api.get('/api/draws/stats', { params });
  return response.data;
};

export default api;
