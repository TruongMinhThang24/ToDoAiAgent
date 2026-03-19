'use client';

import { useState } from 'react';

export const NewTaskForm = ({ onAdd, loading }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState(1); // hoặc '1' nếu backend nhận string
  const [dueDate, setDueDate] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    const newTask = {
      title: title.trim(),
      description: description.trim() || null, // backend thường chấp nhận null hoặc chuỗi rỗng
      priority: Number(priority),               // chắc chắn là số
      completed: false,
      // ✅ FIX: Format ISO 8601 with timezone 
      due_date: dueDate ? new Date(dueDate + 'T00:00:00Z').toISOString() : null,
    };

    console.log('📤 Sending task:', newTask);
    onAdd(newTask);

    // Reset form
    setTitle('');
    setDescription('');
    setPriority(1);
    setDueDate('');
  };

  return (
    <div className="max-w-md mx-auto mt-4 animate-fade-in">
      <h2 className="text-3xl font-bold text-gray-900 mb-2">New Task</h2>
      <p className="text-gray-400 mb-8 text-sm">Tạo công việc mới</p>

      <div className="bg-gray-50 p-3 rounded text-xs text-gray-500 mb-6 flex items-center gap-2">
        <span>🔒</span> Chỉ người dùng đã đăng nhập mới tạo được task.
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* TITLE */}
        <div className="space-y-2">
          <label className="text-lg font-serif font-medium text-gray-800">
            Task Name *
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:border-purple-400 transition shadow-sm"
            placeholder="Nhập tên công việc…"
            autoFocus
            required
          />
        </div>

        {/* DESCRIPTION */}
        <div className="space-y-2">
          <label className="text-lg font-serif font-medium text-gray-800">
            Description (optional)
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:border-purple-400 transition shadow-sm"
            placeholder="Mô tả công việc…"
            rows={3}
          />
        </div>

        {/* PRIORITY */}
        <div className="space-y-2">
          <label className="text-lg font-serif font-medium text-gray-800">
            Priority
          </label>
          <select
            value={priority}
            onChange={(e) => setPriority(Number(e.target.value))}
            className="w-full p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:border-purple-400 transition shadow-sm"
          >
            <option value={1}>⭐ Priority 1 (Thấp nhất)</option>
            <option value={2}>⭐⭐ Priority 2</option>
            <option value={3}>⭐⭐⭐ Priority 3</option>
            <option value={4}>⭐⭐⭐⭐ Priority 4</option>
            <option value={5}>⭐⭐⭐⭐⭐ Priority 5 (Cao nhất)</option>
          </select>
        </div>

        {/* DUE DATE */}
        <div className="space-y-2">
          <label className="text-lg font-serif font-medium text-gray-800">
            Due Date (tùy chọn)
          </label>
          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="w-full p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:border-purple-400 transition shadow-sm"
          />
        </div>

        <div className="pt-4">
          <button
            type="submit"
            disabled={loading || !title.trim()}
            className="bg-gray-900 hover:bg-gray-800 disabled:hover:bg-gray-900 text-white px-8 py-3 rounded-lg font-medium transition w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Đang thêm...' : 'Add Task'}
          </button>
        </div>
      </form>
    </div>
  );
};