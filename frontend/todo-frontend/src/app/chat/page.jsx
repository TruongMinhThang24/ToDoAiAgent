'use client';

import { Sidebar } from '@/features/chat/components/Sidebar';
import { ChatWindow } from '@/features/chat/components/ChatWindow';
import { MessageInput } from '@/features/chat/components/MessageInput';
import { useChat } from '@/features/chat/application/useChat';

export default function ChatPage() {
  const {
    messages,
    isLoading,
    sidebarVisible,
    chatHistory,
    isRecording,
    recordedAudio,
    sendMessage,
    handleVoice,
    sendVoiceMessage,
    toggleSidebar,
  } = useChat();

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        visible={sidebarVisible}
        toggleSidebar={toggleSidebar}
        chatHistory={chatHistory}
      />
      
      <div className="flex-1 flex flex-col">
        <ChatWindow messages={messages} isLoading={isLoading} />
        <MessageInput
          onSend={sendMessage}
          onVoice={handleVoice}
          onSendVoice={sendVoiceMessage}
          isRecording={isRecording}
          recordedAudio={recordedAudio}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}