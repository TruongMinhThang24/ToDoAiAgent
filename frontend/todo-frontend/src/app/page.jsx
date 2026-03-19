// src/app/page.jsx
// Trang chủ, chuyển hướng người dùng đến trang đăng nhập
import { redirect } from 'next/navigation';

export default function HomePage() {
  // Mặc định chuyển hướng đến trang /login
  redirect('/login');
  
  // Trả về null hoặc một loading spinner nếu cần
  return null;
}