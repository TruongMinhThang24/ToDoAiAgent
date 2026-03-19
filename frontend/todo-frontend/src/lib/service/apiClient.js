// src/lib/service/apiClient.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 180000,
  headers: {
    'Content-Type': 'application/json',   // ← quan trọng nhất
    'Accept': 'application/json',
  },
});

// Interceptor request
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Đảm bảo luôn luôn gửi JSON (phòng trường hợp bị override)
    if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json';
    }

    console.log('API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      fullURL: `${config.baseURL}${config.url}`,
      contentType: config.headers['Content-Type'], // để kiểm tra
    });

    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor response (giữ nguyên của bạn)
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      status: response.status,
      url: response.config.url,
    });
    return response;
  },
  (error) => {
    if (error.response) {
      console.error('Server Error:', {
        status: error.response.status,
        data: error.response.data,
        url: error.config?.url,
      });
    } else if (error.request) {
      console.error('Network/CORS Error:', error.message);
    } else {
      console.error('Setup Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;