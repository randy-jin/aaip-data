import axios from 'axios';

// Use relative URL in production (proxied by Nginx), localhost in development
const API_BASE_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.MODE === 'production' ? '' : 'http://localhost:8000');

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

// New stream-related endpoints
export const getStreamList = async () => {
  const response = await api.get('/api/streams/list');
  return response.data;
};

export const getStreamData = async (streamName, limit = 100) => {
  const response = await api.get(`/api/streams/${encodeURIComponent(streamName)}`, {
    params: { limit }
  });
  return response.data;
};

export const getAllStreams = async (limit = 100, offset = 0, streamType = null) => {
  const params = { limit, offset };
  if (streamType) params.stream_type = streamType;

  const response = await api.get('/api/streams', { params });
  return response.data;
};

// EOI Pool endpoints
export const getLatestEOIPool = async () => {
  const response = await api.get('/api/eoi/latest');
  return response.data;
};

export const getEOITrends = async (streamName = null, days = 7) => {
  const params = { days };
  if (streamName) params.stream_name = streamName;

  const response = await api.get('/api/eoi/trends', { params });
  return response.data;
};

export const getEOIAlerts = async (thresholdPercentage = 5.0) => {
  const response = await api.get('/api/eoi/alerts', {
    params: { threshold_percentage: thresholdPercentage }
  });
  return response.data;
};

export default api;
