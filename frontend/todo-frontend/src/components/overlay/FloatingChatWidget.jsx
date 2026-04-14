'use client';

import Link from 'next/link';
import { MessageCircle, Sparkles, X } from 'lucide-react';
import { useState } from 'react';

export default function FloatingChatWidget() {
  const [isPopoverOpen, setIsPopoverOpen] = useState(true);
  const [isPinned, setIsPinned] = useState(false);

  const handleMouseEnter = () => setIsPopoverOpen(true);
  const handleMouseLeave = () => {
    if (!isPinned) {
      setIsPopoverOpen(false);
    }
  };

  return (
    <div
      className="fixed bottom-8 right-8 z-50"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {isPopoverOpen && (
        <div className="mb-3 w-[320px] rounded-2xl border border-gray-100 bg-white p-4 shadow-2xl">
          <div className="mb-3 flex items-start justify-between gap-3">
            <div className="flex items-center gap-3">
              <img
                src="https://placehold.co/48x48"
                alt="assistant-avatar"
                className="h-12 w-12 rounded-full object-cover"
              />
              <div>
                <p className="text-sm font-semibold text-gray-900">AI Assistant</p>
                <p className="text-xs text-gray-500">Online now</p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => {
                setIsPinned((prev) => !prev);
                setIsPopoverOpen((prev) => !prev);
              }}
              className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
              aria-label="Toggle chat widget popover"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <p className="text-sm leading-6 text-gray-700">
            Welcome to our website! Need help with your tasks? Our AI assistant is ready to support you.
          </p>

          <Link
            href="/chat"
            className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700"
          >
            <Sparkles className="h-4 w-4" />
            Chat with us
          </Link>
        </div>
      )}

      <Link
        href="/chat"
        className="ml-auto grid h-14 w-14 place-items-center rounded-full bg-blue-600 text-white shadow-2xl transition hover:scale-[1.03] hover:bg-blue-700"
        aria-label="Open AI chat"
        onClick={() => console.log('chat-widget.openChat')}
      >
        <MessageCircle className="h-6 w-6" />
      </Link>
    </div>
  );
}
