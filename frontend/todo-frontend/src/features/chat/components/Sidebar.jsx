'use client';

import { Card, Button } from 'flowbite-react';
import { HiMenu, HiX } from 'react-icons/hi'; // ← SỬA: hi thay vì hi2

export const Sidebar = ({ visible, toggleSidebar, chatHistory }) => {
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

        <div className="space-y-2">
          {chatHistory.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">
              Chưa có lịch sử chat
            </p>
          ) : (
            chatHistory.map((chat) => (
              <Card
                key={chat.id}
                className="cursor-pointer hover:bg-gray-100 transition-colors"
              >
                <h5 className="text-sm font-semibold text-gray-900 truncate">
                  {chat.title}
                </h5>
                <p className="text-xs text-gray-600 truncate">
                  {chat.lastMessage}
                </p>
                <p className="text-xs text-gray-400">
                  {chat.timestamp.toLocaleDateString('vi-VN')}
                </p>
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