// src/features/todos/components/TodoNavbar.jsx
import Link from 'next/link';
import { Search, MessageCircle } from 'lucide-react';

export const TodoNavbar = ({ onLogout }) => (
  <nav className="h-14 border-b border-gray-100 flex items-center justify-between px-6 sticky top-0 bg-white/80 backdrop-blur-sm z-50">
    <div className="flex items-center gap-2">
      <span className="font-medium text-lg tracking-tight">TODO-BEAR</span>
    </div>
    <div className="flex items-center gap-4 text-gray-500">
      <button className="hover:bg-gray-100 p-1.5 rounded transition">
        <Search className="w-5 h-5" />
      </button>
      <Link href="/chat" className="hover:bg-gray-100 p-1.5 rounded transition text-gray-600 hover:text-blue-600">
        <MessageCircle className="w-5 h-5" />
      </Link>
      <button
        type="button"
        onClick={onLogout}
        className="text-sm font-medium text-red-500 hover:text-red-600 transition"
      >
        Logout
      </button>
    </div>
  </nav>
);