// src/lib/service/apiClient.js
import axios from 'axios';

const CSRF_COOKIE_NAME = 'csrf_token';

const readCookie = (name) => {
  if (typeof document === 'undefined') {
    return null;
  }

  const parts = document.cookie.split(';').map((item) => item.trim());
  const cookie = parts.find((item) => item.startsWith(`${name}=`));
  return cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : null;
};

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 180000,
  // SECURITY: bật credentials để browser tự gửi HttpOnly cookie (access_token).
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',   // ← quan trọng nhất
    'Accept': 'application/json',
  },
});

// Interceptor request
apiClient.interceptors.request.use(
  (config) => {
    const method = config.method?.toLowerCase();

    // Đảm bảo luôn luôn gửi JSON (phòng trường hợp bị override)
    if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json';
    }

    // SECURITY: Double-submit cookie cho request thay đổi dữ liệu.
    if (['post', 'put', 'patch', 'delete'].includes(method)) {
      const csrfToken = readCookie(CSRF_COOKIE_NAME);
      if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken;
      }
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
      const isCsrfError =
        error.response.status === 403
        && error.response.data?.detail === 'CSRF token missing or invalid';

      if (isCsrfError) {
        error.message = 'CSRF token missing or invalid. Please refresh and login again.';
      }

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