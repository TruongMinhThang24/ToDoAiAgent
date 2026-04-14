'use client';

import { useState } from 'react';

export const NewTaskForm = ({ onAdd, loading }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState(1);
  const [dueDate, setDueDate] = useState('');
  const [status, setStatus] = useState('not_started');
  const [thumbnailUrl, setThumbnailUrl] = useState('');
  const [submitError, setSubmitError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    const newTask = {
      title: title.trim(),
      description: description.trim() || '',
      priority: Number(priority),
      status,
      completed: status === 'completed',
      thumbnail_url: thumbnailUrl.trim() || null,
      due_date: dueDate ? new Date(dueDate + 'T00:00:00Z').toISOString() : null,
    };

    try {
      setSubmitError('');
      await onAdd(newTask);

      // Reset form chỉ khi tạo thành công
      setTitle('');
      setDescription('');
      setPriority(1);
      setDueDate('');
      setStatus('not_started');
      setThumbnailUrl('');
    } catch (error) {
      setSubmitError(error?.message || 'Failed to add task. Please try again.');
    }
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

        <div className="space-y-2">
          <label className="text-lg font-serif font-medium text-gray-800">
            Status
          </label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="w-full p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:border-purple-400 transition shadow-sm"
          >
            <option value="not_started">Not Started</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
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

        <div className="space-y-2">
          <label className="text-lg font-serif font-medium text-gray-800">
            Thumbnail URL (optional)
          </label>
          <input
            type="url"
            value={thumbnailUrl}
            onChange={(e) => setThumbnailUrl(e.target.value)}
            className="w-full p-3 bg-white border border-gray-200 rounded-lg focus:outline-none focus:border-purple-400 transition shadow-sm"
            placeholder="https://example.com/image.jpg"
          />
        </div>

        <div className="pt-4">
          {submitError ? (
            <p className="mb-3 rounded-md border border-red-100 bg-red-50 px-3 py-2 text-xs text-red-600">
              {submitError}
            </p>
          ) : null}
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