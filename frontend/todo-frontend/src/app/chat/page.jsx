'use client';

import { Mic, Paperclip, Plus, SendHorizontal } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';
const STREAM_TIMEOUT_MS = 60_000;
const GEMINI_KEY_STORAGE = 'todo_gemini_api_key';

const readCookie = (name) => {
  if (typeof document === 'undefined') return null;
  const parts = document.cookie.split(';').map((item) => item.trim());
  const cookie = parts.find((item) => item.startsWith(`${name}=`));
  return cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : null;
};

const parseSseFrames = (raw) => {
  return raw
    .split('\n\n')
    .map((frame) => frame.trim())
    .filter(Boolean)
    .map((frame) => {
      const dataLine = frame
        .split('\n')
        .find((line) => line.startsWith('data:'));
      if (!dataLine) return null;
      const payload = dataLine.replace(/^data:\s*/, '');
      try {
        return JSON.parse(payload);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
};

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'ai', text: 'Hello! I am your AI assistant. How can I help you today?' },
  ]);
  const [historyItems, setHistoryItems] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [activeHistoryId, setActiveHistoryId] = useState(null);
  const [threadId, setThreadId] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const toUiMessages = (items = []) => {
    if (!items.length) {
      return [{ id: Date.now(), sender: 'ai', text: 'New chat started. Ask me anything.' }];
    }

    return items.map((item) => ({
      id: `db-${item.id}`,
      sender: item.role === 'assistant' ? 'ai' : 'user',
      text: item.content || '',
    }));
  };

  const loadThreads = async () => {
    setIsLoadingHistory(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/threads?limit=30&offset=0`, {
        method: 'GET',
        credentials: 'include',
      });
      if (!response.ok) {
        throw new Error(`Failed to load threads (${response.status})`);
      }
      const data = await response.json();
      const items = data.items || [];
      setHistoryItems(items);
      return items;
    } catch (error) {
      console.error('chat.history.load.error', error);
      setHistoryItems([]);
      return [];
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const loadThreadMessages = async (targetThreadId) => {
    if (!targetThreadId) {
      setMessages([{ id: Date.now(), sender: 'ai', text: 'New chat started. Ask me anything.' }]);
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/chat/threads/${targetThreadId}/messages?limit=200&offset=0`,
        {
          method: 'GET',
          credentials: 'include',
        }
      );
      if (!response.ok) {
        throw new Error(`Failed to load messages (${response.status})`);
      }
      const data = await response.json();
      setMessages(toUiMessages(data.items || []));
    } catch (error) {
      console.error('chat.messages.load.error', error);
      setMessages([
        {
          id: Date.now(),
          sender: 'ai',
          text: 'Không thể tải lịch sử hội thoại. Vui lòng thử lại.',
        },
      ]);
    }
  };

  useEffect(() => {
    const bootstrap = async () => {
      const items = await loadThreads();
      if (!items.length) return;
      const firstThreadId = items[0].thread_id;
      setThreadId(firstThreadId);
      setActiveHistoryId(firstThreadId);
      await loadThreadMessages(firstThreadId);
    };

    bootstrap();
  }, []);

  const handleUploadFileOnly = async () => {
    if (!selectedFile) return { uploaded: false, message: null };

    const csrfToken = readCookie('csrf_token');
    const formData = new FormData();
    formData.append('file', selectedFile);

    const response = await fetch(`${API_BASE_URL}/api/v1/chat/knowledge/upload`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        ...(csrfToken ? { 'X-CSRF-Token': csrfToken } : {}),
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed (${response.status})`);
    }

    const payload = await response.json();
    const fileName = payload?.file_name || selectedFile.name;
    setSelectedFile(null);

    return {
      uploaded: true,
      message: `Đã tải tài liệu '${fileName}' vào Knowledge Base.`,
    };
  };

  const handleSend = async () => {
    const trimmed = inputText.trim();
    if ((!trimmed && !selectedFile) || isSending) return;

    const userMessageId = Date.now();
    const assistantMessageId = userMessageId + 1;

    const nextMessages = [...messages];
    if (trimmed) {
      nextMessages.push({ id: userMessageId, sender: 'user', text: trimmed });
    }
    nextMessages.push({ id: assistantMessageId, sender: 'ai', text: '' });
    setMessages(nextMessages);
    setInputText('');
    setIsSending(true);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), STREAM_TIMEOUT_MS);

    try {
      let uploadInfo = { uploaded: false, message: null };
      if (selectedFile) {
        uploadInfo = await handleUploadFileOnly();
      }

      if (!trimmed) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? {
                  ...msg,
                  text: uploadInfo.message || 'Đã tải tài liệu thành công.',
                }
              : msg
          )
        );
        await loadThreads();
        return;
      }

      const csrfToken = readCookie('csrf_token');
      const runtimeGeminiKey = window.localStorage.getItem(GEMINI_KEY_STORAGE);
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...(csrfToken ? { 'X-CSRF-Token': csrfToken } : {}),
          ...(runtimeGeminiKey ? { 'X-Gemini-API-Key': runtimeGeminiKey } : {}),
        },
        body: JSON.stringify({
          message: trimmed,
          thread_id: threadId,
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Request failed (${response.status})`);
      }

      if (!response.body) {
        throw new Error('No response stream from server');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const frames = parseSseFrames(buffer);

        // Keep last partial frame in buffer.
        const lastBoundary = buffer.lastIndexOf('\n\n');
        if (lastBoundary >= 0) {
          buffer = buffer.slice(lastBoundary + 2);
        }

        frames.forEach((event) => {
          if (event.type === 'chunk') {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? { ...msg, text: `${msg.text}${event.content || ''}` }
                  : msg
              )
            );
          }

          if (event.thread_id) {
            setThreadId(event.thread_id);
            setActiveHistoryId(event.thread_id);
          }

          if (event.type === 'error') {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? {
                      ...msg,
                      text: event.message || 'Xin lỗi, đã có lỗi xảy ra.',
                    }
                  : msg
              )
            );
          }
        });
      }

      await loadThreads();
    } catch (error) {
      const fallbackMessage =
        error?.name === 'AbortError'
          ? 'Yêu cầu bị timeout. Vui lòng thử lại sau ít phút.'
          : 'Không thể kết nối AI lúc này. Vui lòng thử lại.';

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                text: fallbackMessage,
              }
            : msg
        )
      );
      console.error('chat.send.error', error);
    } finally {
      clearTimeout(timeoutId);
      setIsSending(false);
    }
  };

  const handleToggleRecording = () => {
    setIsRecording((prev) => !prev);
    console.log('chat.recording', !isRecording);
  };

  const handleSelectHistory = async (targetThreadId) => {
    setThreadId(targetThreadId);
    setActiveHistoryId(targetThreadId);
    await loadThreadMessages(targetThreadId);
  };

  const handleChooseFile = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] || null;
    setSelectedFile(file);
  };

  return (
    <div className="h-full min-h-0">
      <div className="grid h-full min-h-0 grid-cols-1 gap-4 lg:grid-cols-12">
        <aside className="lg:col-span-3 min-h-0 rounded-2xl border border-gray-100 bg-white shadow-sm flex flex-col">
          <div className="flex items-center justify-between border-b border-gray-100 px-4 py-4">
            <h2 className="text-base font-semibold text-gray-900">Chat History</h2>
            <button
              type="button"
              onClick={() => {
                setActiveHistoryId(0);
                setThreadId(null);
                setMessages([{ id: Date.now(), sender: 'ai', text: 'New chat started. Ask me anything.' }]);
                setSelectedFile(null);
                console.log('chat.newThread');
              }}
              className="inline-flex items-center gap-1 rounded-lg bg-blue-600 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
            >
              <Plus className="h-3.5 w-3.5" />
              New Chat
            </button>
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto p-2">
            <div className="space-y-1">
              {isLoadingHistory && <p className="px-2 py-1 text-xs text-gray-400">Loading history...</p>}
              {historyItems.map((item) => (
                <button
                  key={item.thread_id}
                  type="button"
                  onClick={() => handleSelectHistory(item.thread_id)}
                  className={`w-full rounded-xl px-3 py-2 text-left transition ${
                    activeHistoryId === item.thread_id ? 'bg-blue-50' : 'hover:bg-gray-50'
                  }`}
                >
                  <p className="text-sm font-medium text-gray-900">{item.title || 'New conversation'}</p>
                  <p className="mt-0.5 truncate text-xs text-gray-500">{item.last_message || 'No messages yet'}</p>
                </button>
              ))}
            </div>
          </div>
        </aside>

        <section className="lg:col-span-9 min-h-0 rounded-2xl border border-gray-100 bg-white shadow-sm flex flex-col">
          <div className="border-b border-gray-100 px-4 py-4">
            <h3 className="text-base font-semibold text-gray-900">AI Assistant Chat</h3>
            <p className="text-xs text-gray-500">Ask anything about your tasks and planning.</p>
          </div>

          <div className="flex-1 min-h-0 overflow-y-auto p-4">
            <div className="flex flex-col gap-3">
              {messages.map((message) => {
                const isUser = message.sender === 'user';

                return (
                  <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                    <div
                      className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm leading-6 ${
                        isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      {message.text}
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>
          </div>

          <div className="border-t border-gray-100 p-3">
            {selectedFile && (
              <div className="mb-2 rounded-lg bg-blue-50 px-3 py-2 text-xs text-blue-700">
                File attached: <span className="font-medium">{selectedFile.name}</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleToggleRecording}
                className={`grid h-10 w-10 place-items-center rounded-xl border transition ${
                  isRecording
                    ? 'animate-pulse border-red-200 bg-red-50 text-red-500'
                    : 'border-gray-200 bg-white text-gray-500 hover:bg-gray-50'
                }`}
                aria-label="Toggle voice recording"
              >
                <Mic className="h-4 w-4" />
              </button>

              <button
                type="button"
                onClick={handleChooseFile}
                className="grid h-10 w-10 place-items-center rounded-xl border border-gray-200 bg-white text-gray-500 hover:bg-gray-50"
                aria-label="Upload file"
              >
                <Paperclip className="h-4 w-4" />
              </button>
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileChange}
                className="hidden"
                accept=".pdf,.docx,.txt"
              />

              <input
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Type your message..."
                disabled={isSending}
                className="h-10 flex-1 rounded-xl border border-gray-200 px-3 text-sm outline-none focus:border-blue-400"
              />

              <button
                type="button"
                onClick={handleSend}
                disabled={isSending}
                className="inline-flex h-10 items-center gap-1 rounded-xl bg-blue-600 px-3 text-sm font-medium text-white hover:bg-blue-700"
              >
                <SendHorizontal className="h-4 w-4" />
                {isSending ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}