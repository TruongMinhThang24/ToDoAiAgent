'use client';

import { useEffect, useState } from 'react';

export default function ActionModal({
  isOpen,
  title,
  inputLabel,
  initialValue = '',
  submitText = 'Submit',
  onClose,
  onSubmit,
}) {
  const [value, setValue] = useState(initialValue);

  useEffect(() => {
    if (isOpen) {
      setValue(initialValue || '');
    }
  }, [isOpen, initialValue]);

  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    const handleEsc = (event) => {
      if (event.key === 'Escape') {
        onClose?.();
      }
    };

    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmedValue = value.trim();
    if (!trimmedValue) {
      return;
    }
    onSubmit?.(trimmedValue);
  };

  const handleOverlayClick = (event) => {
    if (event.target === event.currentTarget) {
      onClose?.();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/70"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      <div className="mx-auto mt-24 w-[min(92vw,918px)] rounded-[5px] bg-stone-50 px-14 py-10 shadow-[4px_6px_16px_0px_rgba(0,0,0,0.04)]">
        <div className="mb-9 flex items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-semibold text-black">{title}</h3>
            <div className="mt-1 h-[2px] w-12 bg-orange-600" />
          </div>

          <button
            type="button"
            onClick={onClose}
            className="text-sm font-semibold underline text-black"
          >
            Go Back
          </button>
        </div>

        <div className="rounded-sm border border-zinc-400/60 p-4">
          <form onSubmit={handleSubmit}>
            <label className="mb-2 block text-sm font-semibold text-black">
              {inputLabel}
            </label>

            <input
              value={value}
              onChange={(event) => setValue(event.target.value)}
              placeholder={`Enter ${inputLabel?.toLowerCase() || 'value'}...`}
              className="w-full rounded-md border border-zinc-400 bg-white px-3 py-2 text-sm outline-none focus:border-orange-300 focus:ring-2 focus:ring-orange-100"
            />

            <div className="mt-7 flex items-center gap-3">
              <button
                type="submit"
                className="rounded-md bg-orange-600 px-6 py-2 text-sm font-medium text-white transition hover:bg-orange-700"
              >
                {submitText}
              </button>

              <button
                type="button"
                onClick={onClose}
                className="rounded-md border border-zinc-300 bg-white px-6 py-2 text-sm font-medium text-zinc-700 transition hover:bg-zinc-100"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
