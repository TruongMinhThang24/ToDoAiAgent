/**
 * Chat Repository - Infrastructure layer
 * Real API calls (thay thế mock)
 */

import apiClient from '@/lib/service/apiClient';

export const chatRepository = {
  async getThreads(limit = 20, offset = 0) {
    const response = await apiClient.get('/api/v1/chat/threads', {
      params: { limit, offset },
    });
    return response.data;
  },

  async createThread(title = null) {
    const response = await apiClient.post('/api/v1/chat/threads', { title });
    return response.data;
  },

  async deleteThread(threadId) {
    await apiClient.delete(`/api/v1/chat/threads/${threadId}`);
  },

  async getThreadMessages(threadId, limit = 200, offset = 0) {
    const response = await apiClient.get(`/api/v1/chat/threads/${threadId}/messages`, {
      params: { limit, offset },
    });
    return response.data;
  },

  /**
   * Gửi tin nhắn text đến AI
   * POST /api/v1/chat
   */
  async sendMessage(message, threadId) {
    console.log('📤 API /chat called with:', { message, threadId });

    const response = await apiClient.post('/api/v1/chat/', {
      message,
      thread_id: threadId || null,
    });

    // Response: AgentChatResponse JSON
    // { thread_id, friendly_message, ... }
    return response.data;
  },

  /**
   * Voice-to-text + AI response (audio)
   * POST /api/v1/chat/voice
   */
  async sendVoiceMessage(audioBlob, threadId) {
    console.log('🎤 API /voice called with:', { 
      audioBlob, 
      threadId,
      size: audioBlob.size,
      type: audioBlob.type
    });

    // ✅ Validation chi tiết hơn
    if (audioBlob.size < 1000) {
      throw new Error('Audio file quá nhỏ (< 1KB). Có thể là audio rỗng.');
    }

    if (audioBlob.size > 10 * 1024 * 1024) {
      throw new Error('Audio file quá lớn (> 10MB). Vui lòng thu ngắn hơn.');
    }

    // ✅ Map MIME type đúng với backend
    const mimeToExtension = {
      'audio/webm': 'webm',
      'audio/wav': 'wav',
      'audio/ogg': 'ogg',
      'audio/mpeg': 'mp3',
      'audio/mp4': 'm4a'
    };

    const extension = mimeToExtension[audioBlob.type] || 'audio';
    const fileName = `voice-${Date.now()}.${extension}`;

    const formData = new FormData();
    formData.append('audio', audioBlob, fileName);
    
    // ✅ FIX 1: Chỉ append thread_id khi có value (tránh gửi chuỗi rỗng)
    if (threadId) {
      formData.append('thread_id', threadId);
    }

    console.log('📤 FormData prepared:', {
      fileName,
      audioSize: audioBlob.size,
      audioType: audioBlob.type,
      hasThreadId: !!threadId
    });

    try {
      const response = await apiClient.post('/api/v1/chat/voice', formData, {
        // ✅ FIX 2: XÓA headers object (để axios tự thêm boundary)
        // headers: {
        //   'Content-Type': 'multipart/form-data', // ❌ XÓA dòng này
        // },
        
        responseType: 'blob',
        timeout: 180000,  // ✅ Tăng lên 3 phút (cho retry logic)
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log('📤 Upload progress:', percentCompleted + '%');
        }
      });

      console.log('✅ Voice API response:', {
        status: response.status,
        size: response.data.size,
        type: response.data.type,
        headers: response.headers
      });

      // ✅ Validate response là audio
      if (!response.data.type.startsWith('audio/')) {
        console.error('❌ Response không phải audio:', response.data.type);
        throw new Error('Server trả về dữ liệu không phải audio. Vui lòng thử lại.');
      }

      // ✅ FIX 3: Trả về object với audioBlob + clarification headers
      return {
        audioBlob: response.data,
        needsClarification: response.headers['x-needs-clarification'] === 'true',
        clarificationPrompt: decodeURIComponent(
          response.headers['x-clarification-prompt'] || ''
        )
      };

    } catch (error) {
      // ✅ Enhanced error handling
      if (error.code === 'ECONNABORTED') {
        throw new Error('⏱️ Timeout! Audio quá dài hoặc mạng chậm. Vui lòng thử lại.');
      }
      
      const status = error.response?.status;
      const detail = error.response?.data?.detail;

      if (status === 415) {
        throw new Error(`🎵 Format ${audioBlob.type} không được hỗ trợ.`);
      }
      if (status === 400) {
        throw new Error(`❌ ${detail || 'Audio không hợp lệ'}`);
      }
      if (status >= 500) {
        throw new Error('🔥 Lỗi server. Vui lòng thử lại sau.');
      }

      console.error('❌ Voice API error:', {
        message: error.message,
        status,
        detail
      });
      throw new Error('🔥 Lỗi không xác định. Vui lòng thử lại.');
    }
  },

  // Backward-compatible alias used by old code
  async getChatHistory() {
    const data = await this.getThreads();
    return data.items || [];
  },
};