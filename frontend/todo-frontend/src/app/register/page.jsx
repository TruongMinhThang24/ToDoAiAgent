"use client";

import useRegister from '@/features/auth/register/application/useRegister';
import { RegisterForm } from '@/features/auth/register/components/RegisterForm';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
  const { execute: performRegister, loading, error } = useRegister();
  const router = useRouter();

  const handleRegisterSubmit = async (formData) => {
    try {
      await performRegister(formData);
      alert('Registration successful! Please login.');
      router.push('/login');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <RegisterForm
      onRegisterSubmit={handleRegisterSubmit}
      loading={loading}
      error={error}
    />
  );
}