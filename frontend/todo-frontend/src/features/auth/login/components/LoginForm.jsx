// frontend/todo-frontend/src/features/auth/components/LoginForm.jsx
'use client';

import Image from 'next/image';
import { FaTwitter, FaFacebookF, FaGoogle } from 'react-icons/fa';
import Link from 'next/link';
import { useState } from 'react';

export const LoginForm = ({ onLoginSubmit, loading, error }) => {
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !password) return;
    await onLoginSubmit(name, password);
  };

  return (
      <div className="min-h-screen bg-[#55a8ff] flex items-center justify-center px-6 py-12 ">
        <div className="w-full max-w-4xl rounded-xl hover:shadow-2xl overflow-hidden grid grid-cols-1 md:grid-cols-2 bg-white">
  
          {/* Phần Trái: Giống 100% ảnh */}
          <div className="relative h-96 md:h-[520px]">
            <Image
              src="/chilltodo.jpg"
              alt="Background"
              fill
              className="object-cover object-center"
              priority
            />
            <div className="absolute inset-0 bg-black/55" />
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center text-white p-8">
              <div className="p-6 bg-white/20 backdrop-blur-sm rounded-full mb-6">
                
                <Image 
                src="/wish-list.png"
                alt="Wish-List"
                width={48}
                height={48}
                className="w-12 h-12 object-contain"
                />
              </div>
              <h2 className="text-4xl font-bold login-title">Days..</h2> {/* Giống ảnh */}
              <p className="mt-3 text-sm max-w-xs">We have all forgot more than we remember</p>
            </div>
          </div>
  
          {/* Phần Phải: Form Đăng Nhập (2 trường) */}
          <div className="bg-white p-8 md:p-12 flex items-center">
            <div className="w-full max-w-md mx-auto">
              <form className="space-y-6" onSubmit={handleSubmit}> {/* Dùng space-y-6 cho thoáng như ảnh */}
                {/* Input Name */}
                <div>
                  <label className="text-sm font-medium text-gray-700 block mb-1">Name</label>
                  <input
                    type="text"
                    placeholder="Your name..." // Placeholder cho Name
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    // SỬA CỐT LÕI: Style gạch chân giống ảnh
                    className="mt-1 block w-full pb-1 border-0 border-b-2 border-gray-200 placeholder-gray-400 focus:border-blue-500 outline-none"
                    required
                  />
                </div>
  
                {/* KHÔNG CÓ EMAIL */}
  
                {/* Input Password */}
                <div>
                  <label className="text-sm font-medium text-gray-700 block mb-1">Password</label>
                  <input
                    type="password"
                    placeholder="Password..." // Placeholder trống như ảnh
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    // SỬA CỐT LÕI: Style gạch chân giống ảnh
                    className="mt-1 block w-full pb-1 border-0 border-b-2 border-gray-200 placeholder-gray-400 focus:border-blue-500 outline-none"
                    required
                  />
                </div>
  
                {error && <p className="text-sm text-red-600 text-center mt-2">{error}</p>}
  
                <div>
                  <button
                    type="submit"
                    disabled={loading}
                    // Sửa: py-3 (dày) giống nút "Sign Up" trong ảnh
                    className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-md w-full shadow transition duration-200 disabled:opacity-50"
                  >
                    {/* Sửa: Logic Đăng Nhập */}
                    {loading ? 'Signing In...' : 'Sign In'}
                  </button>
                </div>
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
  
              {/* Sửa: Logic Đăng Nhập (hỏi tạo tài khoản) */}
              <p className="text-xs text-gray-500 text-center mt-8"> {/* mt-8 (xa) giống ảnh */}
                Don't have an account?{' '}
                <Link href="/register" className="text-blue-600 hover:underline">
                  Sign up
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }
  