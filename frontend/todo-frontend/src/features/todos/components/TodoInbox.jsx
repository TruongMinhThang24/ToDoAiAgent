// src/features/todos/components/TodoInbox.jsx
'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Inbox, Archive, FilePlus, MessageCircle } from 'lucide-react';
import { useState, useEffect, useCallback } from 'react';
import { useTodos } from '../application/useTodos';
import { authRepository } from '@/features/auth/login/infrastructure/authRepository';

// Import các components con
import { TodoNavbar } from './TodoNavbar';
import { TodoSidebar } from './TodoSidebar';
import { TaskItem } from './TaskItem';
import { NewTaskForm } from './NewTaskForm';
import { TodoDetailModal } from './TodoDetailModal';

export default function TodoInbox() {
  const router = useRouter();
  // 1. Lấy logic từ Hook (Application Layer)
  const { todos, loading, fetchTodos, createNewTodo, removeTodo, toggleTodo, selectedTodo, getTodoDetails, clearSelectedTodo, isLoadingDetail, updateTodoDetails } = useTodos();
  
  // 2. Local State (Presentation Layer)
  const [activeTab, setActiveTab] = useState('inbox');

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  // 3. Event Handlers
  const handleAddTask = useCallback(async (taskData) => {
    await createNewTodo(taskData);
    setActiveTab('inbox'); // Chuyển về inbox sau khi thêm
  }, [createNewTodo]);

  const handleTaskClick = (id) => {
    getTodoDetails(id);
  };

  const handleLogout = useCallback(async () => {
    try {
      // SECURITY: gọi backend để xóa HttpOnly cookie phiên đăng nhập.
      await authRepository.logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      router.push('/login');
    }
  }, [router]);

  const inboxTodos = todos.filter(t => !t.completed);
  const archiveTodos = todos.filter(t => t.completed);

  // 4. Render Layout
  return (
    <div className="flex flex-col h-screen w-full bg-white font-sans text-gray-800">
      <TodoNavbar onLogout={handleLogout} />

      {/* Banner */}
      <div className="relative w-full h-48 md:h-64 shrink-0">
        <Image src="/banner.png" alt="Banner" fill className="object-cover object-center" priority />
      </div>

      {/* Main Content Grid */}
      <div className="flex flex-col md:flex-row w-full max-w-6xl mx-auto h-full overflow-hidden">
        
        {/* Left Column */}
        <TodoSidebar onAddTaskClick={() => setActiveTab('new')} />

        {/* Right Column (Content) */}
        <main className="w-full md:w-[65%] p-8 flex flex-col h-full overflow-hidden">
           
           {/* Tab Bar */}
           <div className="flex items-center gap-8 border-b border-gray-100 pb-2 mb-6">
              <TabButton id="inbox" label="inbox" icon={<Inbox className="w-4 h-4"/>} active={activeTab} onClick={setActiveTab} />
              <TabButton id="archive" label="archive" icon={<Archive className="w-4 h-4"/>} active={activeTab} onClick={setActiveTab} />
              <TabButton id="new" label="new task" icon={<FilePlus className="w-4 h-4"/>} active={activeTab} onClick={setActiveTab} />
           </div>

           {/* Content Area */}
           <div className="flex-1 overflow-y-auto pr-2 pb-20">
              
              {activeTab === 'inbox' && (
                <TaskList 
                  todos={inboxTodos} 
                  loading={loading} 
                  emptyMsg="Hooray! No pending tasks." 
                  onToggle={toggleTodo} 
                  onRemove={removeTodo}
                  onItemClick={handleTaskClick}
                />
              )}

              {activeTab === 'archive' && (
                <TaskList 
                  todos={archiveTodos} 
                  loading={loading} 
                  emptyMsg="No completed tasks yet." 
                  onToggle={toggleTodo} 
                  onRemove={removeTodo}
                  onItemClick={handleTaskClick}
                />
              )}

              {activeTab === 'new' && (
                 <NewTaskForm onAdd={handleAddTask} loading={loading} />
              )}
           </div>
        </main>
      </div>

      {/* ✅ Thêm Modal vào cuối */}
      <TodoDetailModal 
        isOpen={!!selectedTodo} 
        todo={selectedTodo} 
        onClose={clearSelectedTodo}
        isLoading={isLoadingDetail}
        onUpdate={updateTodoDetails}
      />

      {/* Floating Chat Button */}
      <Link href="/chat">
        <div className="fixed bottom-8 right-8 p-4 bg-white rounded-full shadow-xl hover:shadow-2xl transition-all cursor-pointer border border-gray-100 group z-50">
           <div className="absolute -top-2 -right-2 w-4 h-4 bg-red-500 rounded-full animate-ping"></div>
           <div className="absolute -top-2 -right-2 w-4 h-4 bg-red-500 rounded-full"></div>
           <MessageCircle className="w-8 h-8 text-gray-700 group-hover:text-blue-600 transition-colors" />
        </div>
      </Link>
    </div>
  );
}

// --- Helper Components (có thể để ở file riêng nếu muốn tái sử dụng nhiều) ---

const TabButton = ({ id, label, icon, active, onClick }) => (
  <button 
    onClick={() => onClick(id)}
    className={`flex items-center gap-2 pb-2 transition-all ${active === id ? 'border-b-2 border-gray-800 text-gray-900 font-semibold' : 'text-gray-400 hover:text-gray-600'}`}
  >
    {icon} {label}
  </button>
);

const TaskList = ({ todos, loading, emptyMsg, onToggle, onRemove, onItemClick }) => (
  <div className="space-y-1">
    {loading && <p className="text-sm text-gray-400 animate-pulse">Loading tasks...</p>}
    {todos.length === 0 && !loading && (
       <p className="text-gray-300 italic py-4 text-sm">{emptyMsg}</p>
    )}
    {todos.map(todo => (
       <TaskItem key={todo.id} todo={todo} onToggle={() => onToggle(todo)} onRemove={() => onRemove(todo.id)} onClick={() => onItemClick(todo.id)} />
    ))}
  </div>
);