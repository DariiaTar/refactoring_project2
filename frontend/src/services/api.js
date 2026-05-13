import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      globalThis.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
};

export const locationsApi = {
  getAll: (category) => api.get('/locations/', { params: category ? { category } : {} }),
  getById: (id) => api.get(`/locations/${Number.parseInt(id, 10)}`),
  create: (data) => api.post('/locations/', data),
  update: (id, data) => api.put(`/locations/${Number.parseInt(id, 10)}`, data),
  delete: (id) => api.delete(`/locations/${Number.parseInt(id, 10)}`),
  uploadImage: (id, file, isPrimary = false) => {
    const form = new FormData();
    form.append('file', file);
    return api.post(`/locations/${Number.parseInt(id, 10)}/images`, form, {
      params: { is_primary: isPrimary },
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  deleteImage: (imageId) => api.delete(`/locations/images/${Number.parseInt(imageId, 10)}`),
};

export const slotsApi = {
  getByLocation: (locationId) => api.get(`/slots/location/${Number.parseInt(locationId, 10)}`),
  getAvailable: (locationId) => api.get(`/slots/location/${Number.parseInt(locationId, 10)}/available`),
  create: (data) => api.post('/slots/', data),
  delete: (id) => api.delete(`/slots/${Number.parseInt(id, 10)}`),
};

export const bookingsApi = {
  create: (data) => api.post('/bookings/', data),
  getMy: () => api.get('/bookings/my'),
  getAll: () => api.get('/bookings/'),
  getOne: (id) => api.get(`/bookings/${Number.parseInt(id, 10)}`),
  pay: (id) => api.post(`/bookings/${Number.parseInt(id, 10)}/pay`),
  cancel: (id) => api.post(`/bookings/${Number.parseInt(id, 10)}/cancel`),
  updateStatus: (id, status) => api.put(`/bookings/${Number.parseInt(id, 10)}/status`, { status }),
};

export const usersApi = {
  getAll: () => api.get('/users/'),
  deactivate: (id) => api.put(`/users/${Number.parseInt(id, 10)}/deactivate`),
};

export default api;
