'use client';

import { useState } from 'react';
import { TextInput, Button } from 'flowbite-react';

export const MessageInput = ({
  onSend,
  onVoice,
  onSendVoice,
  isRecording,
  recordedAudio,
  isLoading
}) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim()) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="w-full max-w-4xl mx-auto flex items-center gap-2 flex-nowrap">
        <div className="flex-1 min-w-0">
          <TextInput
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Nhập tin nhắn hoặc ghi âm..."
            disabled={isLoading}
            sizing="md"
          />
        </div>

        {/* Send button */}
        <Button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          color="blue"
          size="md"
          className="p-2 flex-shrink-0"
        >
          <img
            src="/send.png"
            alt="Send"
            className="h-5 w-5"
          />
        </Button>

        {/* Voice button */}
        <Button
          onClick={onVoice}
          color={isRecording ? 'failure' : 'gray'}
          size="md"
          disabled={isLoading}
          className={`p-2 flex-shrink-0 ${isRecording ? 'animate-pulse' : ''}`}
        >
          <img
            src="/audio.png"
            alt="Microphone"
            className="h-5 w-5"
          />
        </Button>
      </div>

      {/* ✅ THÊM: Recorded audio player + Send button */}
      {recordedAudio && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-600 mb-2 font-medium">🎤 Audio đã ghi:</p>
          <audio controls className="w-full mb-3">
            <source src={recordedAudio} type="audio/wav" />
            Trình duyệt không hỗ trợ audio.
          </audio>
          <Button
            onClick={onSendVoice}
            disabled={isLoading}
            color="success"
            size="sm"
            className="w-full"
          >
            📤 Gửi Audio đến AI
          </Button>
        </div>
      )}

      {/* Recording status */}
      {isRecording && (
        <p className="text-center text-sm text-red-600 mt-2 animate-pulse">
          🔴 Đang ghi âm... Nhấn lại để dừng
        </p>
      )}
    </div>
  );
};