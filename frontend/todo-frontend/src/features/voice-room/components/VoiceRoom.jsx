'use client';

import Link from 'next/link';
import { Mic, Square } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';
const VOICE_ENDPOINT = `${API_BASE_URL}/api/v1/chat/voice`;
const GEMINI_KEY_STORAGE = 'todo_gemini_api_key';

const readCookie = (name) => {
  if (typeof document === 'undefined') return null;

  const cookie = document.cookie
    .split(';')
    .map((item) => item.trim())
    .find((item) => item.startsWith(`${name}=`));

  return cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : null;
};

const getPreferredMimeType = () => {
  if (typeof window === 'undefined' || typeof MediaRecorder === 'undefined') {
    return '';
  }

  const candidates = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/ogg'];
  return candidates.find((candidate) => MediaRecorder.isTypeSupported(candidate)) || '';
};

export default function VoiceRoom() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [statusMessage, setStatusMessage] = useState('Sẵn sàng nhận giọng nói.');
  const [errorMessage, setErrorMessage] = useState('');
  const [savedKey, setSavedKey] = useState('');

  const mediaRecorderRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const audioChunksRef = useRef([]);
  const playbackUrlRef = useRef('');

  const hasSavedKey = useMemo(() => Boolean(savedKey.trim()), [savedKey]);

  const cleanupMediaStream = () => {
    mediaStreamRef.current?.getTracks?.().forEach((track) => track.stop());
    mediaStreamRef.current = null;
  };

  const cleanupPlaybackUrl = () => {
    if (playbackUrlRef.current) {
      URL.revokeObjectURL(playbackUrlRef.current);
      playbackUrlRef.current = '';
    }
  };

  useEffect(() => {
    if (typeof window === 'undefined') return undefined;

    setSavedKey(window.localStorage.getItem(GEMINI_KEY_STORAGE) || '');

    return () => {
      cleanupPlaybackUrl();
      cleanupMediaStream();
    };
  }, []);

  const sendVoiceBlob = async (audioBlob) => {
    const formData = new FormData();
    const fileName = audioBlob.type.includes('ogg') ? 'voice.ogg' : 'voice.webm';
    formData.append('audio', audioBlob, fileName);

    const csrfToken = readCookie('csrf_token');
    const runtimeKey = window.localStorage.getItem(GEMINI_KEY_STORAGE) || '';
    const response = await fetch(VOICE_ENDPOINT, {
      method: 'POST',
      credentials: 'include',
      headers: {
        ...(csrfToken ? { 'X-CSRF-Token': csrfToken } : {}),
        ...(runtimeKey ? { 'X-Gemini-API-Key': runtimeKey } : {}),
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Voice request failed (${response.status})`);
    }

    const responseAudioBlob = await response.blob();
    cleanupPlaybackUrl();

    const audioUrl = URL.createObjectURL(responseAudioBlob);
    playbackUrlRef.current = audioUrl;
    const audio = new Audio(audioUrl);

    audio.onended = () => {
      cleanupPlaybackUrl();
      setStatusMessage('Sẵn sàng nhận giọng nói.');
    };

    audio.onerror = () => {
      cleanupPlaybackUrl();
      setErrorMessage('Không thể phát phản hồi âm thanh từ AI.');
      setStatusMessage('Sẵn sàng nhận giọng nói.');
    };

    setStatusMessage('AI đang nói...');
    await audio.play();
  };

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current;
    if (!recorder || recorder.state === 'inactive') return;

    setIsRecording(false);
    setIsProcessing(true);
    setStatusMessage('Đang xử lý...');
    recorder.stop();
  };

  const startRecording = async () => {
    setErrorMessage('');

    if (isProcessing) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      audioChunksRef.current = [];

      const mimeType = getPreferredMimeType();
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        try {
          const fallbackType = mimeType || audioChunksRef.current[0]?.type || 'audio/webm';
          const audioBlob =
            audioChunksRef.current.length > 0
              ? new Blob(audioChunksRef.current, { type: fallbackType })
              : new Blob([], { type: fallbackType });

          cleanupMediaStream();
          await sendVoiceBlob(audioBlob);
        } catch (sendError) {
          console.error('voice-room.send.error', sendError);
          setErrorMessage('Gửi yêu cầu voice thất bại. Vui lòng thử lại.');
          setStatusMessage('Sẵn sàng nhận giọng nói.');
        } finally {
          setIsProcessing(false);
          mediaRecorderRef.current = null;
          audioChunksRef.current = [];
        }
      };

      recorder.start();
      setIsRecording(true);
      setStatusMessage('Đang nghe...');
    } catch (recordError) {
      console.error('voice-room.record.error', recordError);
      cleanupMediaStream();
      setIsRecording(false);
      setIsProcessing(false);
      setErrorMessage('Không thể truy cập micro. Hãy cấp quyền ghi âm cho trình duyệt.');
      setStatusMessage('Sẵn sàng nhận giọng nói.');
    }
  };

  const handleMicClick = () => {
    if (isRecording) {
      stopRecording();
      return;
    }

    startRecording();
  };

  return (
    <div className="mx-auto flex min-h-[calc(100vh-8rem)] w-full max-w-4xl flex-col items-center justify-center rounded-3xl border border-gray-100 bg-white px-6 py-10 text-center shadow-sm">
      <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-red-50 text-red-500 shadow-inner">
        <Mic className="h-11 w-11" />
      </div>

      <h1 className="text-3xl font-semibold text-gray-900">Phòng trò chuyện</h1>
      <p className="mt-3 max-w-xl text-sm leading-6 text-gray-500">
        Thu âm bằng micro, gửi âm thanh đến AI và nghe lại phản hồi ngay trong phòng trò chuyện độc lập.
      </p>

      <div className="mt-8 flex flex-col items-center gap-3">
        <button
          type="button"
          onClick={handleMicClick}
          disabled={isProcessing && !isRecording}
          className={`flex h-28 w-28 items-center justify-center rounded-full text-white shadow-lg transition-transform duration-200 hover:scale-105 active:scale-95 ${
            isRecording ? 'bg-rose-600' : 'bg-emerald-600'
          } ${isProcessing && !isRecording ? 'cursor-not-allowed opacity-70' : ''}`}
          aria-label={isRecording ? 'Dừng ghi âm' : 'Bắt đầu ghi âm'}
        >
          {isRecording ? <Square className="h-11 w-11" /> : <Mic className="h-11 w-11" />}
        </button>

        <p className="text-sm font-medium text-gray-700">{statusMessage}</p>
        {hasSavedKey && <p className="text-xs text-emerald-600">Gemini API key đã được tải từ browser storage.</p>}
        {!hasSavedKey && <p className="text-xs text-amber-600">Chưa có Gemini API key trong browser storage.</p>}
        {errorMessage && <p className="max-w-lg text-sm text-red-600">{errorMessage}</p>}
      </div>

      <div className="mt-10 flex flex-wrap items-center justify-center gap-3 text-sm text-gray-500">
        <span className="rounded-full bg-gray-100 px-4 py-2">Endpoint: /api/v1/chat/voice</span>
        <Link href="/chat" className="rounded-full bg-red-50 px-4 py-2 text-red-600 hover:bg-red-100">
          Quay lại Chat
        </Link>
      </div>
    </div>
  );
}