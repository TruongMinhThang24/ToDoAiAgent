'use client';

import { Card, Button } from 'flowbite-react';
import { HiMenu, HiX } from 'react-icons/hi'; // ← SỬA: hi thay vì hi2

export const Sidebar = ({
  visible,
  toggleSidebar,
  chatHistory,
  currentThreadId,
  onCreateThread,
  onSelectThread,
  onDeleteThread,
  isLoadingThreads,
}) => {
  const formatDate = (value) => {
    if (!value) return '';
    return new Date(value).toLocaleDateString('vi-VN');
  };

  return (
    <>
      {!visible && (
        <div className="fixed top-4 left-4 z-50 md:hidden">
          <Button size="sm" color="gray" onClick={toggleSidebar}>
            <HiMenu className="h-5 w-5" />
          </Button>
        </div>
      )}

      <div
        className={`
          ${visible ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0
          fixed md:relative
          top-0 left-0
          h-full w-64 md:w-1/4
          bg-gray-100 border-r border-gray-200
          p-4
          transition-transform duration-300 ease-in-out
          z-40
          overflow-y-auto
        `}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">
          <img
            src="history.png"
            alt="History"
            className="h-10 w-10"
            aria-hidden="true"
          />
          </h2>
          <Button size="xs" color="gray" onClick={toggleSidebar} className="md:hidden">
            <HiX className="h-4 w-4" />
          </Button>
        </div>

        <Button size="sm" color="blue" className="w-full mb-3" onClick={onCreateThread}>
          + New Chat
        </Button>

        <div className="space-y-2">
          {isLoadingThreads ? (
            <p className="text-sm text-gray-500 text-center py-4">Đang tải hội thoại...</p>
          ) : chatHistory.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">
              Chưa có lịch sử chat
            </p>
          ) : (
            chatHistory.map((chat) => (
              <Card
                key={chat.thread_id}
                className={`cursor-pointer hover:bg-gray-100 transition-colors ${
                  currentThreadId === chat.thread_id ? 'ring-2 ring-blue-300' : ''
                }`}
                onClick={() => onSelectThread(chat.thread_id)}
              >
                <div className="flex items-start justify-between gap-2">
                  <h5 className="text-sm font-semibold text-gray-900 truncate">
                  {chat.title}
                  </h5>
                  <button
                    type="button"
                    className="text-xs text-red-500 hover:text-red-700"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteThread(chat.thread_id);
                    }}
                  >
                    Xóa
                  </button>
                </div>
                <p className="text-xs text-gray-600 truncate">{chat.last_message}</p>
                <p className="text-xs text-gray-400">{formatDate(chat.updated_at)}</p>
              </Card>
            ))
          )}
        </div>
      </div>

      {visible && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={toggleSidebar}
        />
      )}
    </>
  );
};