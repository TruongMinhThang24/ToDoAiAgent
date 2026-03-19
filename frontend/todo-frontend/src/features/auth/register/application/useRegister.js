"use client";

import { useState } from 'react';
import { authRepository } from '../infrastructure/authRepository';

export default function useRegister() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = async (formData) => {
    setLoading(true);
    setError(null);

    // Validation cơ bản
    if (!formData.username || !formData.email || !formData.password) {
      setLoading(false);
      const err = new Error("Username, email, and password are required.");
      setError(err.message);
      throw err;
    }

    try {
      const result = await authRepository.register(formData);
      setLoading(false);
      return result;
    } catch (err) {
      setLoading(false);
      setError(err.message || "Registration failed.");
      throw err;
    }
  };

  return { execute, loading, error };
}