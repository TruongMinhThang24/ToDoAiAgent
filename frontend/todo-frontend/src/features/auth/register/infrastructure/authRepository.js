// src/features/auth/register/infrastructure/authRepository.js
// Lớp Repository: chịu trách nhiệm lấy dữ liệu (API, localStorage, v.v.)
import apiClient from '@/lib/service/apiClient'; // ✅ Đã import và sửa lỗi chính tả

export const authRepository = {
  /**
   * Register new user
   * @param {object} formData {username, email, first_name, last_name, password, phone_number}
   * @returns {Promise<object>}
   */
  register: async (formData) => { // ✅ Chuyển sang async
    console.log(`[AuthRepository] Đang gọi API thật cho register: ${formData.username}`);
    
    try {
      // ✅ Gọi API thật, truyền thẳng object formData (backend /auth/register nhận JSON)
      const response = await apiClient.post('/auth/register', formData);
      console.log("[AuthRepository] Register thật thành công:", response.data);
      return response.data;

    } catch (err) {
      console.error("[AuthRepository] Register thật thất bại:", err.response?.data || err.message);
      // Ném lỗi để useRegister hook có thể bắt
      throw new Error(err.response?.data?.detail || "Đăng ký thất bại.");
    }
  },
};