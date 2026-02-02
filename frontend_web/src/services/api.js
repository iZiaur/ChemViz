import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Inject token into every request if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('chemviz_token');
  if (token) {
    config.headers['Authorization'] = `Token ${token}`;
  }
  return config;
});

// --- Auth ---
export const register = (username, email, password) =>
  api.post('/auth/register/', { username, email, password });

export const login = (username, password) =>
  api.post('/auth/login/', { username, password });

// --- Equipment ---
export const uploadCSV = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getHistory = () => api.get('/history/');

export const getDatasetDetail = (id) => api.get(`/dataset/${id}/`);

export const deleteDataset = (id) => api.delete(`/dataset/${id}/delete/`);

export const downloadPDF = (id) =>
  api.get(`/dataset/${id}/report/`, { responseType: 'blob' });

export default api;
