'use client';

import { Undo2 } from 'lucide-react';

const fallbackNotifications = [
  {
    id: 1,
    title: 'Complete the UI design of Landing Page for FoodVentures.',
    priority: 'High',
    time: '2h',
    thumbnail: 'https://placehold.co/52x52',
  },
  {
    id: 2,
    title: 'Complete the UI design of Landing Page for Travel Days.',
    priority: 'High',
    time: '2h',
    thumbnail: 'https://placehold.co/52x52',
  },
  {
    id: 3,
    title: 'Complete the Mobile app design for Pet Warden.',
    priority: 'Extremely High',
    time: '2h',
    thumbnail: 'https://placehold.co/52x52',
  },
  {
    id: 4,
    title: 'Complete the entire design for Juice Slider.',
    priority: 'High',
    time: '2h',
    thumbnail: 'https://placehold.co/52x52',
  },
];

export default function NotificationPopover({ notifications = fallbackNotifications, onGoBack }) {
  return (
    <div className="absolute right-0 top-full mt-2 w-80 rounded-2xl border border-gray-100 bg-white shadow-xl z-50 overflow-hidden">
      <div className="border-b border-gray-100 px-5 py-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-base font-semibold text-gray-900">Notifications</p>
            <p className="mt-1 text-sm font-medium text-gray-400">Today</p>
          </div>
          <button
            type="button"
            onClick={onGoBack}
            className="text-[#FF6767] hover:opacity-80"
            aria-label="Go back notifications"
          >
            <Undo2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="max-h-[400px] overflow-auto">
        {notifications.map((item) => (
          <div
            key={item.id}
            className="grid grid-cols-[1fr_52px] gap-3 border-b border-gray-100 px-5 py-3 transition-colors hover:bg-gray-50"
          >
            <div>
              <p className="text-sm leading-5 text-gray-900">{item.title}</p>
              <p className="mt-1 text-xs text-gray-400">{item.time}</p>
              <p className="mt-1 text-xs">
                <span className="text-gray-900">Priority: </span>
                <span className="font-medium text-red-500">{item.priority}</span>
              </p>
            </div>
            <img
              src={item.thumbnail || 'https://placehold.co/52x52'}
              alt={item.title}
              className="h-12 w-12 rounded object-cover"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
