'use client';

import { useState } from 'react';

export default function CreateCategoryForm({ onSubmit, onCancel }) {
  const [categoryName, setCategoryName] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    const value = categoryName.trim();
    if (!value) {
      return;
    }
    onSubmit?.(value);
    setCategoryName('');
  };

  return (
    <div className="min-h-full">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold text-black">Create Categories</h2>
          <div className="mt-2 h-[2px] w-12 bg-orange-600" />
        </div>

        <button
          type="button"
          onClick={onCancel}
          className="text-sm font-semibold underline text-black"
        >
          Go Back
        </button>
      </div>

      <section className="rounded-md border border-zinc-400/60 p-5 shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]">
        <form
          onSubmit={handleSubmit}
          className="bg-slate-50 rounded-2xl p-4 shadow-[0px_5px_11px_0px_rgba(0,0,0,0.04)]"
        >
          <label className="mb-2 block text-sm font-semibold text-black">Category Name</label>

          <input
            value={categoryName}
            onChange={(event) => setCategoryName(event.target.value)}
            placeholder="Enter category name..."
            className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm outline-none"
          />

          <div className="mt-6 flex items-center gap-2">
            <button
              type="submit"
              className="rounded-lg bg-orange-500 px-3 py-2 text-xs font-medium text-white transition hover:bg-orange-600"
            >
              Create
            </button>

            <button
              type="button"
              onClick={onCancel}
              className="rounded-lg bg-orange-500 px-3 py-2 text-xs font-medium text-white transition hover:bg-orange-600"
            >
              Cancel
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
