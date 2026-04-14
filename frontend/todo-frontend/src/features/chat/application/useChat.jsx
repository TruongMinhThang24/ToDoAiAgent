'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { ChatMessage } from '@/features/chat/entities/ChatMessage';
import { chatRepository } from '@/features/chat/infrastructure/chatRepository';

const THREAD_STORAGE_KEY = 'todo_chat_current_thread_id';
const DEFAULT_ASSISTANT_MESSAGE = ChatMessage.createAssistantMessage(
  'Xin chào! Tôi là trợ lý AI. Hãy hỏi tôi hoặc ghi âm.'
);

export const useChat = () => {
  // State
  const [messages, setMessages] = useState([DEFAULT_ASSISTANT_MESSAGE]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [threads, setThreads] = useState([]);
  const [isLoadingThreads, setIsLoadingThreads] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [recordedAudio, setRecordedAudio] = useState(null);

  // Refs
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const toUiMessages = useCallback((items = []) => {
    if (!items.length) {
      return [DEFAULT_ASSISTANT_MESSAGE];
    }

    return items.map((item) =>
      new ChatMessage({
        id: `db-${item.id}`,
        role: item.role === 'assistant' ? 'assistant' : 'user',
        content: item.content || '',
        timestamp: new Date(item.created_at || Date.now()),
        type: 'text',
      })
    );
  }, []);

  const loadThreads = useCallback(async () => {
    setIsLoadingThreads(true);
    try {
      const response = await chatRepository.getThreads();
      setThreads(response.items || []);
      return response.items || [];
    } catch (error) {
      console.error('Error loading chat threads:', error);
      setThreads([]);
      return [];
    } finally {
      setIsLoadingThreads(false);
    }
  }, []);

  const loadThreadMessages = useCallback(
    async (threadId) => {
      if (!threadId) {
        setMessages([DEFAULT_ASSISTANT_MESSAGE]);
        return;
      }

      setIsLoading(true);
      try {
        const response = await chatRepository.getThreadMessages(threadId);
        setMessages(toUiMessages(response.items || []));
      } catch (error) {
        console.error('Error loading thread messages:', error);
        setMessages([
          ChatMessage.createAssistantMessage(
            'Không thể tải lịch sử hội thoại. Vui lòng thử lại.'
          ),
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [toUiMessages]
  );

  useEffect(() => {
    const bootstrap = async () => {
      const savedThreadId =
        typeof window !== 'undefined'
          ? window.localStorage.getItem(THREAD_STORAGE_KEY)
          : null;

      const items = await loadThreads();

      const selectedThreadId =
        savedThreadId && items.find((item) => item.thread_id === savedThreadId)
          ? savedThreadId
          : items[0]?.thread_id || null;

      setCurrentThreadId(selectedThreadId);
      await loadThreadMessages(selectedThreadId);
    };

    bootstrap();
  }, [loadThreads, loadThreadMessages]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (currentThreadId) {
      window.localStorage.setItem(THREAD_STORAGE_KEY, currentThreadId);
    } else {
      window.localStorage.removeItem(THREAD_STORAGE_KEY);
    }
  }, [currentThreadId]);

  // ✅ FIX: Cleanup chỉ khi component UNMOUNT (không phụ thuộc messages)
  useEffect(() => {
  const messagesToClean = messages;
  const recordedToClean = recordedAudio;

  return () => {
    messagesToClean.forEach((msg) => {
      if (msg.audioUrl && msg.audioUrl.startsWith('blob:')) {
        URL.revokeObjectURL(msg.audioUrl);
      }
    });
    if (recordedToClean && recordedToClean.startsWith('blob:')) {
      URL.revokeObjectURL(recordedToClean);
    }
    console.log('🧹 Cleaned up blob URLs on unmount');
  };
}, []); // ✅ CRITICAL: Empty dependency array

  // Helper: Tạo audio URL
  const createAudioUrl = useCallback((blob) => {
    return URL.createObjectURL(blob);
  }, []);

  // Helper: Phát audio
  const playAudio = useCallback((audioBlob) => {
    try {
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
      };
    } catch (e) {
      console.error('Lỗi khi phát âm thanh:', e);
    }
  }, []);

  // ✅ FIX: Send text message - XỬ LÝ CLARIFICATION
  const sendMessage = useCallback(async (content) => {
    if (!content || !content.trim()) return;

    const trimmedContent = content.trim();
    const userMessage = ChatMessage.createUserMessage(trimmedContent);
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const aiResponse = await chatRepository.sendMessage(trimmedContent, currentThreadId);
      
      // ✅ Cập nhật thread_id
      setCurrentThreadId(aiResponse.thread_id);
      await loadThreads();

      // ✅ XỬ LÝ CLARIFICATION: Luôn hiển thị friendly_message
      const assistantMessage = ChatMessage.createAssistantMessage(
        aiResponse.friendly_message || 'Đã xử lý yêu cầu.'
      );
      setMessages(prev => [...prev, assistantMessage]);

      // ✅ LOG để debug
      console.log('📨 AI Response:', {
        message: aiResponse.friendly_message,
        needs_clarification: aiResponse.needs_clarification,
        thread_id: aiResponse.thread_id
      });

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = ChatMessage.createAssistantMessage(
        'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.'
      );
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [currentThreadId, loadThreads]);

  const createNewThread = useCallback(async () => {
    setIsLoading(true);
    try {
      const newThread = await chatRepository.createThread();
      setCurrentThreadId(newThread.thread_id);
      setMessages([DEFAULT_ASSISTANT_MESSAGE]);
      await loadThreads();
    } catch (error) {
      console.error('Error creating new thread:', error);
    } finally {
      setIsLoading(false);
    }
  }, [loadThreads]);

  const selectThread = useCallback(
    async (threadId) => {
      if (!threadId || threadId === currentThreadId) return;
      setCurrentThreadId(threadId);
      await loadThreadMessages(threadId);
    },
    [currentThreadId, loadThreadMessages]
  );

  const deleteThread = useCallback(
    async (threadId) => {
      if (!threadId) return;
      try {
        await chatRepository.deleteThread(threadId);
        const updatedThreads = await loadThreads();

        if (currentThreadId === threadId) {
          const nextThreadId = updatedThreads[0]?.thread_id || null;
          setCurrentThreadId(nextThreadId);
          await loadThreadMessages(nextThreadId);
        }
      } catch (error) {
        console.error('Error deleting thread:', error);
      }
    },
    [currentThreadId, loadThreadMessages, loadThreads]
  );

  // Start recording
  const startRecording = useCallback(async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        sampleRate: 16000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
      } 
    });

    // ✅ FIX: Ưu tiên format backend support
    const supportedTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/wav',
      'audio/ogg;codecs=opus'
    ];
    
    let mimeType = 'audio/webm';  // Fallback
    for (const type of supportedTypes) {
      if (MediaRecorder.isTypeSupported(type)) {
        mimeType = type;
        break;
      }
    }

    console.log('🎙️ Selected MIME type:', mimeType);

    const mediaRecorder = new MediaRecorder(stream, { 
      mimeType,
      audioBitsPerSecond: 16000
    });
    
    const chunks = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        chunks.push(e.data);
      }
    };

    mediaRecorder.onstop = async () => {
      // ✅ FIX: Tạo Blob với MIME chuẩn (bỏ codecs detail)
      const baseMimeType = mimeType.split(';')[0];  // "audio/webm"
      const audioBlob = new Blob(chunks, { type: baseMimeType });
      
      console.log('🎤 Recorded audio:', {
        size: audioBlob.size,
        type: audioBlob.type,
        originalMimeType: mimeType
      });

      // ✅ Validate duration (estimate)
      const url = URL.createObjectURL(audioBlob);
      const audio = new Audio(url);
      audio.onloadedmetadata = () => {
        console.log('🕐 Audio duration:', audio.duration, 'seconds');
        if (audio.duration < 1) {
          alert('⚠️ Audio quá ngắn (< 1 giây). Vui lòng thu lại.');
          URL.revokeObjectURL(url);
          return;
        }
        if (audio.duration > 60) {
          alert('⚠️ Audio quá dài (> 60 giây). Vui lòng rút ngắn.');
          URL.revokeObjectURL(url);
          return;
        }
        
        // ✅ OK, lưu audio
        setRecordedAudio(url);
        mediaRecorder.audioBlob = audioBlob;
        mediaRecorder.mimeType = baseMimeType;
      };
    };

    mediaRecorder.start();
    mediaRecorderRef.current = mediaRecorder;
    setIsRecording(true);
    console.log('🎙️ Recording started:', { mimeType, sampleRate: 16000 });
  } catch (error) {
    console.error('Error starting recording:', error);
    alert('Không thể truy cập micro. Vui lòng cấp quyền.');
  }
}, []);

  const stopRecording = useCallback(() => {
    const mediaRecorder = mediaRecorderRef.current;
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      console.log('🛑 Recording stopped');
    }
  }, []);

  // Send voice message
  const sendVoiceMessage = useCallback(async () => {
  if (!recordedAudio) return;

  const mediaRecorder = mediaRecorderRef.current;
  const audioBlob = mediaRecorder?.audioBlob;
  if (!audioBlob) {
    alert('❌ Không tìm thấy audio. Vui lòng thu lại.');
    return;
  }

  const userMessage = ChatMessage.createUserMessage('', recordedAudio, 'audio');
  setMessages(prev => [...prev, userMessage]);
  setRecordedAudio(null);
  setIsLoading(true);

  const loadingMessage = ChatMessage.createAssistantMessage(
    '🎧 Đang xử lý giọng nói (30-120s)...\n⏳ Hệ thống sẽ retry 3 lần nếu AI quá tải.'
  );
  setMessages(prev => [...prev, loadingMessage]);

  try {
    console.log('📤 Sending voice:', {
      size: audioBlob.size,
      type: audioBlob.type,
      threadId: currentThreadId
    });

    // ✅ FIX: Repository giờ trả về object
    const responseData = await chatRepository.sendVoiceMessage(audioBlob, currentThreadId);

    setMessages(prev => prev.filter(msg => msg !== loadingMessage));

    // ✅ FIX: Hiển thị clarification text TRƯỚC audio (nếu có)
    if (responseData.needsClarification && responseData.clarificationPrompt) {
      const clarificationMessage = ChatMessage.createAssistantMessage(
        responseData.clarificationPrompt,
        null,
        'text'
      );
      setMessages(prev => [...prev, clarificationMessage]);
    }

    // Tạo audio message
    const aiAudioUrl = createAudioUrl(responseData.audioBlob);
    const aiMessage = ChatMessage.createAssistantMessage('', aiAudioUrl, 'audio');
    setMessages(prev => [...prev, aiMessage]);

    playAudio(responseData.audioBlob);

  } catch (error) {
    console.error('❌ Error sending voice:', error);
    
    setMessages(prev => prev.filter(msg => msg !== loadingMessage));
    
    const errorMessage = ChatMessage.createAssistantMessage(
      `❌ ${error.message}`
    );
    setMessages(prev => [...prev, errorMessage]);
  } finally {
    setIsLoading(false);
  }
}, [recordedAudio, currentThreadId, createAudioUrl, playAudio]);

  // Handle voice button
  const handleVoice = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  // Toggle sidebar
  const toggleSidebar = useCallback(() => {
    setSidebarVisible(prev => !prev);
  }, []);

  return {
    messages,
    isLoading,
    sidebarVisible,
    chatHistory: threads,
    threads,
    isLoadingThreads,
    isRecording,
    recordedAudio,
    currentThreadId,
    sendMessage,
    handleVoice,
    sendVoiceMessage,
    toggleSidebar,
    createNewThread,
    selectThread,
    deleteThread,
  };
};