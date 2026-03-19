// src/app/login/page.jsx
"use client";

import useLogin from '@/features/auth/login/application/useLogin'; // Import hook
import { LoginForm } from '@/features/auth/login/components/LoginForm'; // Import UI
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const { execute: performLogin, loading, error } = useLogin();
  const router = useRouter();

  const handleLoginSubmit = async (name, password) => {
    try {
      const result = await performLogin(name, password);
      alert(`Welcome, HOW ARE YOU TODAY`); // Có thể thay bằng toast nếu muốn UX tốt hơn
      router.push('/todos'); // Chuyển hướng khi thành công
    } catch (err) {
      console.error(err);
      // Lỗi đã được hook `useLogin` xử lý và hiển thị qua `error` prop
    }
  };

  return (
    <LoginForm
      onLoginSubmit={handleLoginSubmit}
      loading={loading}
      error={error}
    />
  );
}