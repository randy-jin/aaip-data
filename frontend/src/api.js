import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

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

export const getScrapeLogs = async (limit = 50) => {
  const response = await api.get('/api/logs', {
    params: { limit }
  });
  return response.data;
};

export default api;
