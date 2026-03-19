// src/features/auth/application/useLogin.js
// (Đã bao gồm FIX BUG 2: Security Patch)
"use client"; // Hooks chạy ở client

import { useState } from 'react';
import { authRepository } from '../infrastructure/authRepository';

export default function useLogin() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Hàm thực thi use case đăng nhập
  * @param {string} name 
  * @param {string} password 
   * @returns {Promise<object>} Kết quả đăng nhập
   */
  const execute = async (name, password) => {
    setLoading(true);
    setError(null);

    // 1. Validation cơ bản
    if (!name || !password) {
      setLoading(false);
      const err = new Error("Tên và Mật khẩu là bắt buộc.");
      setError(err.message);
      throw err;
    }

    try {
      // 2. Gọi đến lớp Infrastructure (Repository)
      const result = await authRepository.login(name, password);
      
      setLoading(false);
      return result;
      
    } catch (err) {
      // 4. Xử lý lỗi (FIX BUG 2: Security Patch)
      setLoading(false);
      
      // Chỉ hiển thị lỗi "an toàn" (từ logic của repo) hoặc lỗi chung
      const safeMessage = (err.message && (err.message.includes("Tên" ) || err.message.includes("mật khẩu")))
        ? err.message
        : "Đăng nhập thất bại. Vui lòng thử lại.";
        
      setError(safeMessage);
      throw err; // Vẫn ném lỗi gốc cho console
    }
  };

  return { execute, loading, error };
}
