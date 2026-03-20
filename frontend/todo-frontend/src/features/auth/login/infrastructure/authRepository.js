// src/features/auth/login/infrastructure/authRepository.js
// Lớp Repository: chịu trách nhiệm lấy dữ liệu (API)

import apiClient from '@/lib/service/apiClient';

export const authRepository = {
  /**
   * Gửi form-encoded tới backend (/auth/token) vì backend dùng OAuth2PasswordRequestForm
   * @param {string} name
   * @param {string} password
   * @returns {Promise<object>} response.data
   */
  login: async (name, password) => {
    if (!name || !password) {
      throw new Error('Tên và mật khẩu là bắt buộc.');
    }

    const params = new URLSearchParams();
    params.append('username', name);
    params.append('password', password);

    try {
      const response = await apiClient.post('/auth/token', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const data = response?.data;
      if (!data) {
        throw new Error('Không nhận được phản hồi hợp lệ từ server.');
      }

      return data;
    } catch (err) {
      // Lấy thông điệp lỗi "an toàn" từ server nếu có, ngược lại dùng thông điệp chung
      const serverMsg = err?.response?.data?.detail || err?.response?.data?.error;
      const status = err?.response?.status;
      const safeMessage = serverMsg
        || (status === 401 ? 'Tên hoặc mật khẩu không đúng.' : 'Đăng nhập thất bại. Vui lòng thử lại.');

      // Log chi tiết cho debug (client-side)
      console.error('[AuthRepository] login error:', {
        status,
        serverData: err?.response?.data,
        message: err?.message,
        code: err?.code,
      });

      throw new Error(safeMessage);
    }
  },

  logout: async () => {
    // SECURITY: backend sẽ xóa HttpOnly cookie bằng /auth/logout.
    await apiClient.post('/auth/logout');
  },

  getToken: () => {
    // HttpOnly cookie không thể đọc bằng JS.
    return null;
  },

  isAuthenticated: () => {
    // Trạng thái xác thực nên được xác minh qua API (/auth/me).
    return false;
  },
};
// ...existing code...