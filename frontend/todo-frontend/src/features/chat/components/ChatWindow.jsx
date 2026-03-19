'use client';

import { useEffect, useRef, useMemo } from 'react';
import { Spinner } from 'flowbite-react';
import ReactMarkdown from 'react-markdown';      // ✅ THÊM DÒNG NÀY
import remarkGfm from 'remark-gfm';

export const ChatWindow = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  // Auto-scroll xuống tin nhắn mới nhất
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Client-side formatted times (tránh hydration mismatch)
  const formattedTimes = useMemo(() => {
    const formatter = new Intl.DateTimeFormat('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
    });
    return messages.map((message) => {
      const date = new Date(message.timestamp || Date.now());
      return formatter.format(date);
    });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 bg-white">
      <div className="max-w-4xl mx-auto space-y-4">
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={`
              flex
              ${message.role === 'user' ? 'justify-end' : 'justify-start'}
              animate-fade-in
            `}
          >
            <div
              className={`
                max-w-xs md:max-w-md lg:max-w-lg
                px-4 py-3
                rounded-2xl
                shadow-sm
                ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white rounded-br-none'
                    : 'bg-gray-200 text-gray-900 rounded-bl-none'
                }
              `}
            >
              {/* ✅ FIX: Render Markdown cho AI */}
              {message.type === 'text' && message.content && (
                <div className="prose prose-sm max-w-none">
                  {message.role === 'assistant' ? (
                    <div className="markdown-container">  {/* ✅ Thay prose */}
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          table: ({ node, ...props }) => (
                            <table 
                              className="min-w-full border-collapse border border-gray-300 my-2 text-sm"
                              {...props} 
                            />
                          ),
                          thead: ({ node, ...props }) => (
                            <thead className="bg-gray-50" {...props} />
                          ),
                          th: ({ node, ...props }) => (
                            <th 
                              className="border border-gray-300 px-2 py-1 text-left font-semibold text-gray-900"
                              {...props} 
                            />
                          ),
                          td: ({ node, ...props }) => (
                            <td 
                              className="border border-gray-300 px-2 py-1 text-gray-800"
                              {...props} 
                            />
                          ),
                          p: ({ node, ...props }) => (
                            <p className="mb-1 leading-relaxed" {...props} />
                          ),
                          strong: ({ node, ...props }) => (
                            <strong className="font-bold text-gray-900" {...props} />
                          ),
                          em: ({ node, ...props }) => (
                            <em className="italic" {...props} />
                          ),
                          ul: ({ node, ...props }) => (
                            <ul className="list-disc ml-4 mb-2" {...props} />
                          ),
                          ol: ({ node, ...props }) => (
                            <ol className="list-decimal ml-4 mb-2" {...props} />
                          ),
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap break-words text-sm">
                      {message.content}
                    </p>
                  )}
                </div>
              )}

              {/* ✅ Audio player */}
              {message.type === 'audio' && message.audioUrl && (
                <div className="mt-2">
                  <audio controls className="w-full">
                    <source src={message.audioUrl} /> {/* ✅ Bỏ type, browser tự detect */}
                    Trình duyệt không hỗ trợ audio.
                  </audio>
                  <p className="text-xs text-gray-500 mt-1">
                    🔊 Click để nghe lại
                  </p>
                </div>
              )}

              {/* Timestamp */}
              <p
                className={`
                  text-xs mt-1
                  ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'}
                `}
              >
                {formattedTimes[index]}
              </p>
            </div>
          </div>
        ))}

        {/* Loading spinner */}
        {isLoading && (
          <div className="flex justify-start animate-fade-in">
            <div className="bg-gray-200 px-4 py-3 rounded-2xl rounded-bl-none shadow-sm flex items-center space-x-2">
              <Spinner size="sm" />
              <span className="text-sm text-gray-700">Assistant đang xử lý...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};