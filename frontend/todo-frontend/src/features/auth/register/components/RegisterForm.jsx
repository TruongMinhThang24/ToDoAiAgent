// frontend/todo-frontend/src/features/auth/components/LoginForm.jsx
'use client';

import Image from 'next/image';
import { FaTwitter, FaFacebookF, FaGoogle } from 'react-icons/fa';
import Link from 'next/link';
import { useState } from 'react';

export const RegisterForm = ({ onRegisterSubmit, loading, error }) => {
  const [form, setForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    phone_number: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    await onRegisterSubmit(form);
  };

  const handleChange =(e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  }

  return (
      <div className="min-h-screen bg-[#55a8ff] flex items-center justify-center px-4 py-8 ">
        <div className="w-full max-w-md rounded-xl hover:shadow-2xl overflow-hidden bg-white">
          {}
          <div className="bg-white p-8 md:p-12 flex items-center">
            <div className="w-full max-w-md mx-auto">
              <form className="space-y-6" onSubmit={handleSubmit}>
              <input name="username" placeholder="Username" onChange={handleChange} required className="w-full p-2 border rounded" />
              <input name="email" type="email" placeholder="Email" onChange={handleChange} required className="w-full p-2 border rounded" />
              <input name="first_name" placeholder="First Name" onChange={handleChange} required className="w-full p-2 border rounded" />
              <input name="last_name" placeholder="Last Name" onChange={handleChange} required className="w-full p-2 border rounded" />
              <input name="password" type="password" placeholder="Password" onChange={handleChange} required className="w-full p-2 border rounded" />
              <input name="phone_number" placeholder="Phone Number" onChange={handleChange} className="w-full p-2 border rounded" />
              {error && <p className="text-red-500">{error}</p>}
              <button type="submit" disabled={loading} className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700">
                {loading ? 'Signing Up...' : 'Sign Up'}
              </button>
            </form>
  
              <p className="text-xs text-gray-500 text-center my-6">Quick sign up with your favorite social profile</p>
  
              <div className="flex justify-center gap-4">
                <div className="w-9 h-9 rounded-full bg-blue-400 flex items-center justify-center text-white cursor-pointer hover:opacity-90">
                  <FaTwitter className="w-5 h-5" />
                </div>
                <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center text-white cursor-pointer hover:opacity-90">
                  <FaFacebookF className="w-5 h-5" />
                </div>
                <div className="w-9 h-9 rounded-full bg-red-500 flex items-center justify-center text-white cursor-pointer hover:opacity-90">
                  <FaGoogle className="w-5 h-5" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  