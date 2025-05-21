import axios from 'axios';

// API endpoints
const USER_API = 'http://localhost:5001';
const TASK_API = 'http://localhost:5002';
const NOTIFICATION_API = 'http://localhost:5003';

// Add request interceptor for debugging
axios.interceptors.request.use(request => {
  console.log('Starting Request:', request.method.toUpperCase(), request.url);
  return request;
});

// Add response interceptor for debugging
axios.interceptors.response.use(
  response => {
    console.log('Response:', response.status, response.data);
    return response;
  },
  error => {
    console.error('API Error:', error.message);
    if (error.response) {
      console.error('Error Response:', error.response.data);
      console.error('Error Status:', error.response.status);
    }
    return Promise.reject(error);
  }
);

// User Service API calls
export const userApi = {
  login: (credentials) => axios.post(`${USER_API}/auth/login`, credentials),
  register: (userData) => axios.post(`${USER_API}/auth/register`, userData),
  getProfile: (token) => axios.get(`${USER_API}/users/me`, {
    headers: { Authorization: `Bearer ${token}` }
  })
};

// Task Service API calls
export const taskApi = {
  getTasks: (token) => axios.get(`${TASK_API}/tasks`, {
    headers: { Authorization: `Bearer ${token}` }
  }),
  createTask: (task, token) => axios.post(`${TASK_API}/tasks`, task, {
    headers: { Authorization: `Bearer ${token}` }
  }),
  updateTask: (id, task, token) => axios.put(`${TASK_API}/tasks/${id}`, task, {
    headers: { Authorization: `Bearer ${token}` }
  }),
  deleteTask: (id, token) => axios.delete(`${TASK_API}/tasks/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
};

// Notification Service API calls
export const notificationApi = {
  getNotifications: (token) => axios.get(`${NOTIFICATION_API}/notifications`, {
    headers: { Authorization: `Bearer ${token}` }
  }),
  markAsRead: (id, token) => axios.put(`${NOTIFICATION_API}/notifications/${id}/read`, {}, {
    headers: { Authorization: `Bearer ${token}` }
  })
}; 