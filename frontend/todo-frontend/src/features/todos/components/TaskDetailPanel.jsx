'use client';

import { useEffect, useState } from 'react';
import { Calendar, Save, XCircle } from 'lucide-react';

const statusOptions = [
  { value: 'not_started', label: 'Not Started' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
];

const statusColor = {
  not_started: 'text-red-600',
  in_progress: 'text-blue-700',
  completed: 'text-green-700',
};

export const TaskDetailPanel = ({ todo, isLoading, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState(null);

  useEffect(() => {
    if (todo) {
      setFormData({
        title: todo.title || '',
        description: todo.description || '',
        priority: Number(todo.priority || 1),
        due_date: todo.due_date ? todo.due_date.slice(0, 16) : '',
        status: todo.status || (todo.completed ? 'completed' : 'not_started'),
        thumbnail_url: todo.thumbnail_url || '',
      });
      setIsEditing(false);
    }
  }, [todo]);

  if (isLoading) {
    return <section className="rounded-2xl border border-zinc-300/60 bg-white p-5">Loading detail...</section>;
  }

  if (!todo || !formData) {
    return (
      <section className="rounded-2xl border border-zinc-300/60 bg-white p-5">
        <h3 className="text-base font-semibold">Task Detail</h3>
        <p className="mt-3 text-sm text-gray-500">Select a task to preview details.</p>
      </section>
    );
  }

  const onSave = () => {
    const payload = {
      title: formData.title.trim(),
      description: formData.description.trim(),
      priority: Number(formData.priority),
      status: formData.status,
      completed: formData.status === 'completed',
      thumbnail_url: formData.thumbnail_url.trim() || null,
      due_date: formData.due_date ? new Date(formData.due_date).toISOString() : null,
    };
    onUpdate(todo.id, payload);
    setIsEditing(false);
  };

  const createdOn = todo.created_at || todo.due_date;

  return (
    <section className="rounded-2xl border border-zinc-300/60 bg-white p-5 shadow-[0px_4px_8px_rgba(0,0,0,0.08)]">
      <h3 className="text-base font-semibold">Task Detail</h3>

      <div className="mt-4 grid gap-4 sm:grid-cols-[160px_1fr]">
        <img
          src={formData.thumbnail_url || todo.thumbnail_url || 'https://placehold.co/158x158'}
          alt={todo.title}
          className="h-40 w-40 rounded-2xl object-cover"
        />

        <div>
          {isEditing ? (
            <div className="space-y-3">
              <input
                value={formData.title}
                onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
              />
              <textarea
                value={formData.description}
                onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                rows={6}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
              />
              <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData((prev) => ({ ...prev, priority: Number(e.target.value) }))}
                  className="rounded-lg border border-gray-300 px-3 py-2"
                >
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>{`Priority ${n}`}</option>
                  ))}
                </select>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData((prev) => ({ ...prev, status: e.target.value }))}
                  className="rounded-lg border border-gray-300 px-3 py-2"
                >
                  {statusOptions.map((item) => (
                    <option key={item.value} value={item.value}>{item.label}</option>
                  ))}
                </select>
                <input
                  type="datetime-local"
                  value={formData.due_date}
                  onChange={(e) => setFormData((prev) => ({ ...prev, due_date: e.target.value }))}
                  className="rounded-lg border border-gray-300 px-3 py-2"
                />
                <input
                  type="url"
                  value={formData.thumbnail_url}
                  onChange={(e) => setFormData((prev) => ({ ...prev, thumbnail_url: e.target.value }))}
                  placeholder="Thumbnail URL"
                  className="rounded-lg border border-gray-300 px-3 py-2"
                />
              </div>
            </div>
          ) : (
            <div>
              <h4 className="text-xl font-semibold text-gray-900">{todo.title}</h4>
              <p className="mt-2 text-sm text-gray-600 whitespace-pre-wrap">{todo.description || 'No description'}</p>
              <div className="mt-3 space-y-1 text-sm">
                <p>
                  Priority: <span className="text-red-600">{Number(todo.priority || 1) >= 5 ? 'Extreme' : Number(todo.priority || 1) >= 3 ? 'Moderate' : 'Low'}</span>
                </p>
                <p>
                  Status: <span className={statusColor[todo.status || 'not_started']}>{statusOptions.find((s) => s.value === (todo.status || 'not_started'))?.label || 'Not Started'}</span>
                </p>
                {createdOn && (
                  <p className="inline-flex items-center gap-1 text-zinc-500">
                    <Calendar className="h-3 w-3" />
                    Created on: {new Date(createdOn).toLocaleDateString('en-GB')}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap justify-end gap-2">
        {isEditing ? (
          <>
            <button
              type="button"
              onClick={() => setIsEditing(false)}
              className="inline-flex items-center gap-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm"
            >
              <XCircle className="h-4 w-4" /> Cancel
            </button>
            <button
              type="button"
              onClick={onSave}
              className="inline-flex items-center gap-1 rounded-lg bg-[#FF6767] px-3 py-2 text-sm text-white"
            >
              <Save className="h-4 w-4" /> Save
            </button>
          </>
        ) : (
          <button
            type="button"
            onClick={() => setIsEditing(true)}
            className="rounded-lg bg-gray-900 px-3 py-2 text-sm text-white"
          >
            Edit
          </button>
        )}
      </div>
    </section>
  );
};
