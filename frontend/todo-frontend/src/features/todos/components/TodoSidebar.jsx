// src/features/todos/components/TodoSidebar.jsx
import { Plus, Sparkles } from 'lucide-react';

export const TodoSidebar = ({ onAddTaskClick }) => (
  <aside className="w-full md:w-[35%] p-8 md:pr-12 flex flex-col gap-8 border-r border-dashed border-gray-200 md:h-full overflow-y-auto">
    <div className="space-y-4">
      <h1 className="text-4xl font-serif font-bold text-gray-900">to-do inbox</h1>
      <div className="flex items-center gap-2 text-gray-500 font-mono text-sm tracking-wide">
        <span className="text-xl">🐻</span>
        <span className="font-bold text-gray-700">熊吃 BEARCHI</span>
      </div>
      <div className="flex items-center gap-2 text-sm text-gray-400 italic">
        <span>♥</span>
        <span>by daniel & danielle</span>
      </div>
    </div>

    <p className="text-gray-600 leading-relaxed font-light">
      A simple way to keep track and organize your everyday life through an intuitive and aesthetic to-do list.
    </p>

    <div className="flex gap-4 mt-2">
      <button 
        onClick={onAddTaskClick}
        className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition text-sm font-medium"
      >
        <Plus className="w-4 h-4" /> add task
      </button>
      <button className="flex items-center gap-2 bg-gray-50 hover:bg-gray-100 text-gray-500 px-4 py-2 rounded-lg transition text-sm font-medium border border-gray-200">
        <Sparkles className="w-4 h-4" /> getting started
      </button>
    </div>
  </aside>
);