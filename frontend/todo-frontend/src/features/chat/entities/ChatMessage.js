/**
 * ChatMessage Entity - Domain layer
 * Định nghĩa cấu trúc một tin nhắn chat (text + audio)
 */

export class ChatMessage {
  constructor({ id, role, content, timestamp, audioUrl, type }) {
    this.id = id;
    this.role = role; // 'user' | 'assistant'
    this.content = content || ''; // Text content (optional)
    this.timestamp = timestamp;
    this.audioUrl = audioUrl || null; // Audio blob URL (optional)
    this.type = type || 'text'; // 'text' | 'audio'
  }

  static createUserMessage(content, audioUrl = null, type = 'text') {
    return new ChatMessage({
      id: `user-${Date.now()}-${Math.random()}`,
      role: 'user',
      content,
      timestamp: new Date(),
      audioUrl,
      type,
    });
  }

  static createAssistantMessage(content, audioUrl = null, type = 'text') {
    return new ChatMessage({
      id: `assistant-${Date.now()}-${Math.random()}`,
      role: 'assistant',
      content,
      timestamp: new Date(),
      audioUrl,
      type,
    });
  }
}