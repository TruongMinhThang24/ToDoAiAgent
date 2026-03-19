// src/features/todos/components/TaskItem.jsx
import { CheckSquare, Square, Tag, Trash2 } from 'lucide-react';

export const TaskItem = ({ todo, onToggle, onRemove, onClick }) => (
  <div className="group flex items-center gap-3 p-2 hover:bg-gray-50 rounded transition-colors border-b border-gray-50 last:border-0">
    <button
    onClick={(e) => { e.stopPropagation(); onToggle(); }}
    className="text-gray-400 hover:text-purple-600 transition"
    >
      {todo.completed ? <CheckSquare className="w-5 h-5 text-purple-600" /> : <Square className="w-5 h-5" />}
    </button>
    
    {/* Phần nội dung chính: Click vào đây sẽ mở modal */}
    <div className="flex-1 flex items-center gap-3" onClick={onClick}>
        <span className="bg-gray-100 text-gray-500 text-[10px] px-1.5 py-0.5 rounded uppercase tracking-wide font-medium">
        {todo.completed ? 'DONE' : 'TODO'}
        </span>
        <Tag className="w-3 h-3 text-gray-300" />

        <span className={`flex-1 text-[15px] ${todo.completed ? 'line-through text-gray-300' : 'text-gray-700'}`}>
        {todo.title}
        </span>

        {todo.due_date && (
        <span className="text-xs text-gray-400 font-mono flex items-center gap-1">
            {new Date(todo.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
        </span>
        )}
    </div>

    <button onClick={onRemove} className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-500 transition p-1">
      <Trash2 className="w-4 h-4" />
    </button>
  </div>
);