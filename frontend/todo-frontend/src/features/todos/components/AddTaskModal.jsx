'use client';

import { useEffect, useRef, useState } from 'react';
import { UploadCloud } from 'lucide-react';

const INITIAL_FORM = {
  title: '',
  date: '',
  priority: 'moderate',
  description: '',
  image: null,
};

const getPriorityKey = (priority) => {
  if (typeof priority === 'string') {
    const normalized = priority.toLowerCase();
    if (normalized === 'extreme' || normalized === 'moderate' || normalized === 'low') {
      return normalized;
    }
  }

  const numericPriority = Number(priority || 0);
  if (numericPriority >= 5) {
    return 'extreme';
  }
  if (numericPriority >= 3) {
    return 'moderate';
  }
  return 'low';
};

const formatDateInputValue = (value) => {
  if (!value) {
    return '';
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return '';
  }
  return parsed.toISOString().slice(0, 10);
};

const toPriorityNumber = (value) => {
  if (value === 'extreme') return 5;
  if (value === 'moderate') return 3;
  return 1;
};

export default function AddTaskModal({ isOpen, onClose, initialData = null, mode = 'add', onSubmit }) {
  const [formData, setFormData] = useState(INITIAL_FORM);
  const [imagePreview, setImagePreview] = useState('');
  const [submitError, setSubmitError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    if (mode === 'edit' && initialData) {
      setFormData({
        title: initialData.title || '',
        date: formatDateInputValue(initialData.due_date || initialData.date || initialData.created_at),
        priority: getPriorityKey(initialData.priority),
        description: initialData.description || '',
        image: null,
      });
      setImagePreview(initialData.thumbnail_url || '');
      setSubmitError('');
      return;
    }

    setFormData(INITIAL_FORM);
    setImagePreview('');
    setSubmitError('');
  }, [initialData, isOpen, mode]);

  if (!isOpen) {
    return null;
  }

  const setField = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleChooseFile = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] || null;
    setField('image', file);
    if (file) {
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0] || null;
    setField('image', file);
    if (file) {
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleDone = async () => {
    const trimmedTitle = formData.title.trim();
    if (!trimmedTitle) {
      setSubmitError('Title is required.');
      return;
    }

    const dueDateIso = formData.date ? new Date(`${formData.date}T00:00:00Z`).toISOString() : null;
    const normalizedThumbnailUrl = imagePreview && !imagePreview.startsWith('blob:')
      ? imagePreview
      : (initialData?.thumbnail_url || null);
    const status =
      mode === 'edit'
        ? (initialData?.status || 'not_started')
        : 'not_started';

    const payload = {
      id: initialData?.id,
      title: trimmedTitle,
      description: formData.description.trim() || '',
      priority: toPriorityNumber(formData.priority),
      due_date: dueDateIso,
      status,
      completed: status === 'completed',
      thumbnail_url: normalizedThumbnailUrl,
      image: formData.image
        ? { name: formData.image.name, size: formData.image.size, type: formData.image.type }
        : null,
    };

    setSubmitError('');
    setIsSubmitting(true);

    try {
      console.log(mode === 'edit' ? 'Edit Task payload:' : 'Add New Task payload:', payload);
      await onSubmit?.(payload);
      setFormData(INITIAL_FORM);
      setImagePreview('');
      onClose?.();
    } catch (error) {
      const message = error?.message || 'Unable to save task. Please try again.';
      setSubmitError(message);
      alert(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOverlayClick = (event) => {
    if (event.target === event.currentTarget) {
      onClose?.();
    }
  };

  const priorityOptions = [
    { value: 'extreme', label: 'Extreme', dot: 'bg-red-600' },
    { value: 'moderate', label: 'Moderate', dot: 'bg-blue-700' },
    { value: 'low', label: 'Low', dot: 'bg-green-700' },
  ];

  return (
    <div
      className="fixed inset-0 z-50 bg-black/50 p-4 flex items-center justify-center"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-label={mode === 'edit' ? 'Edit Task' : 'Add New Task'}
    >
      <div className="w-full max-w-4xl rounded-xl bg-stone-50 p-6 md:p-8 shadow-[0px_24px_60px_rgba(0,0,0,0.18)]">
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <h3 className="text-base md:text-lg font-semibold text-black">{mode === 'edit' ? 'Edit Task' : 'Add New Task'}</h3>
            <div className="mt-1 h-[2px] w-14 bg-orange-600" />
          </div>

          <button
            type="button"
            onClick={onClose}
            className="text-sm font-semibold text-black underline"
          >
            Go Back
          </button>
        </div>

        <div className="rounded-md border border-zinc-400/60 p-4 md:p-5">
          <div className="space-y-4">
            <div>
              <label className="mb-2 block text-sm font-semibold text-black">Title</label>
              <input
                value={formData.title}
                onChange={(e) => setField('title', e.target.value)}
                placeholder="Enter task title..."
                className="w-full rounded-md border border-zinc-400 bg-white px-3 py-2 text-sm outline-none focus:border-orange-300 focus:ring-2 focus:ring-orange-100"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-black">Date</label>
              <input
                type="date"
                value={formData.date}
                onChange={(e) => setField('date', e.target.value)}
                className="w-full rounded-md border border-zinc-400 bg-white px-3 py-2 text-sm outline-none focus:border-orange-300 focus:ring-2 focus:ring-orange-100"
              />
            </div>

            <div>
              <p className="mb-2 text-sm font-semibold text-black">Priority</p>
              <div className="flex flex-wrap items-center gap-5">
                {priorityOptions.map((option) => {
                  const checked = formData.priority === option.value;
                  return (
                    <label key={option.value} className="inline-flex cursor-pointer items-center gap-2">
                      <input
                        type="radio"
                        name="priority"
                        value={option.value}
                        checked={checked}
                        onChange={(e) => setField('priority', e.target.value)}
                        className="sr-only"
                      />
                      <span
                        className={`inline-flex h-4 w-4 items-center justify-center rounded-sm border ${
                          checked ? 'border-orange-500' : 'border-zinc-400'
                        }`}
                      >
                        {checked ? <span className="h-2 w-2 rounded-sm bg-orange-500" /> : null}
                      </span>
                      <span className={`h-2.5 w-2.5 rounded-full ${option.dot}`} />
                      <span className="text-xs text-zinc-500">{option.label}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-5">
              <div className="md:col-span-3">
                <label className="mb-2 block text-sm font-semibold text-black">Task Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setField('description', e.target.value)}
                  placeholder="Start writing here..."
                  rows={8}
                  className="w-full resize-none rounded-md border border-zinc-400 bg-white px-3 py-2 text-sm outline-none focus:border-orange-300 focus:ring-2 focus:ring-orange-100"
                />
              </div>

              <div className="md:col-span-2">
                <label className="mb-2 block text-sm font-semibold text-black">Upload Image</label>
                <div
                  onDrop={handleDrop}
                  onDragOver={(e) => e.preventDefault()}
                  className="h-full min-h-[220px] rounded-md border border-dashed border-zinc-400 bg-white p-4 flex flex-col items-center justify-center text-center"
                >
                  <UploadCloud className="h-8 w-8 text-zinc-400" />
                  <p className="mt-3 text-xs text-zinc-400">Drag & Drop files here</p>
                  <p className="text-xs text-zinc-400">or</p>

                  <button
                    type="button"
                    onClick={handleChooseFile}
                    className="mt-3 rounded-md border border-zinc-400 px-4 py-1.5 text-xs font-medium text-zinc-500 hover:bg-zinc-50"
                  >
                    Browse
                  </button>

                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleFileChange}
                  />

                  {formData.image ? (
                    <p className="mt-3 max-w-full truncate text-[11px] text-zinc-500">
                      {formData.image.name}
                    </p>
                  ) : null}

                  {!formData.image && imagePreview ? (
                    <img src={imagePreview} alt="Task preview" className="mt-3 h-16 w-16 rounded-lg object-cover" />
                  ) : null}
                </div>
              </div>
            </div>
          </div>

          {submitError ? (
            <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
              {submitError}
            </p>
          ) : null}

          <div className="mt-6">
            <button
              type="button"
              onClick={handleDone}
              disabled={isSubmitting}
              className="rounded-md bg-orange-600 px-7 py-2 text-sm font-medium text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? 'Saving...' : 'Done'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
