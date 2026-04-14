'use client';

import { ChevronLeft, ChevronRight, Undo2, X } from 'lucide-react';

const WEEK_DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];

const isSameDate = (a, b) =>
  a &&
  b &&
  a.getFullYear() === b.getFullYear() &&
  a.getMonth() === b.getMonth() &&
  a.getDate() === b.getDate();

const formatInputDate = (date) =>
  date.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });

export default function CalendarPopover({
  currentMonth,
  selectedDate,
  onPrevMonth,
  onNextMonth,
  onSelectDate,
  onGoBack,
  onClear,
}) {
  const firstDay = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1);
  const daysInMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0).getDate();

  const startOffset = (firstDay.getDay() + 6) % 7;

  const cells = [
    ...Array.from({ length: startOffset }, () => null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ];

  return (
    <div className="absolute right-0 top-full mt-2 w-80 rounded-2xl border border-gray-100 bg-white shadow-xl z-50 overflow-hidden">
      <div className="p-5">
        <div className="mb-2 flex items-start justify-between">
          <p className="text-base font-semibold text-gray-900">Calendar</p>
          <button
            type="button"
            onClick={onGoBack}
            className="text-[#FF6767] hover:opacity-80"
            aria-label="Go back calendar"
          >
            <Undo2 className="h-4 w-4" />
          </button>
        </div>

        <div className="mb-3 flex items-center gap-2 rounded-md border border-zinc-400 px-3 py-1.5">
          <input
            readOnly
            value={formatInputDate(selectedDate)}
            className="w-full bg-transparent text-sm font-semibold text-gray-900 outline-none"
          />
          <button
            type="button"
            onClick={onClear}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Clear selected date"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="mb-3 grid grid-cols-[38px_1fr_38px] items-center gap-2">
          <button
            type="button"
            onClick={onPrevMonth}
            className="grid h-[38px] w-[38px] place-items-center rounded-md border border-gray-300 text-gray-900"
            aria-label="Previous month"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>

          <p className="text-center text-sm font-semibold text-gray-900">
            {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
          </p>

          <button
            type="button"
            onClick={onNextMonth}
            className="grid h-[38px] w-[38px] place-items-center rounded-md border border-gray-300 text-gray-900"
            aria-label="Next month"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>

        <div className="grid grid-cols-7 gap-y-2 text-center">
          {WEEK_DAYS.map((day) => (
            <span key={day} className="text-[11px] font-semibold text-gray-400">
              {day}
            </span>
          ))}

          {cells.map((day, idx) => {
            if (!day) return <span key={`empty-${idx}`} className="h-9" />;

            const dateObj = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
            const selected = isSameDate(dateObj, selectedDate);

            return (
              <button
                key={day}
                type="button"
                onClick={() => onSelectDate?.(dateObj)}
                className={`mx-auto w-8 h-8 flex items-center justify-center rounded-full text-xs font-semibold transition ${
                  selected ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-100'
                }`}
              >
                {day}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
