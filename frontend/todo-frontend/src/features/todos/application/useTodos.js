// src/features/todos/application/useTodos.js
"use client";

import { useState, useCallback } from 'react';
import { todoRepository } from '../infrastructure/todoRepository';

// ✅ FIX: export default function useTodos() -> export const useTodos
export const useTodos = () => {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [selectedTodo, setSelectedTodo] = useState(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);

  const fetchTodos = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await todoRepository.getAllTodos();
      setTodos(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch todos');
    } finally {
      setLoading(false);
    }
  }, []);

  const createNewTodo = useCallback(async (todoData) => {
    setLoading(true); // Có thể dùng state riêng
    setError(null);
    try {
      const newTodo = await todoRepository.addTodo(todoData);
      setTodos(prev => [...prev, newTodo]);
    } catch (err) {
      setError(err.message || 'Failed to add todo');
    } finally {
      setLoading(false); // Tắt loading chung
    }
  }, []);

  const removeTodo = useCallback(async (id) => {
    // Không set loading để UI mượt hơn
    try {
      await todoRepository.deleteTodo(id);
      setTodos(prev => prev.filter(t => t.id !== id));
    } catch (err) {
      setError(err.message || 'Failed to delete todo');
    }
    // Không set loading
  }, []);

  const toggleTodo = useCallback(async (todo) => {
    // ✅ FIX: Logic cho API 204 NO CONTENT
    // 1. Tạo dữ liệu sẽ được gửi đi
    const updatedData = { 
      ...todo, 
      completed: !todo.completed,
      due_date: todo.due_date // Đảm bảo gửi đủ các trường
    }; 
    
    try {
      // 2. Cập nhật "lạc quan" (optimistic update) ngay lập tức
      setTodos(prev => prev.map(t => (t.id === todo.id ? updatedData : t)));
      
      // 3. Gửi request lên API
      // (Repo không trả về gì cả)
      await todoRepository.updateTodo(todo.id, updatedData);
      
      // 4. Nếu thành công, state đã đúng.
      
    } catch (err) {
      setError(err.message || 'Failed to update todo');
      // 5. Nếu lỗi, rollback lại state cũ
      setTodos(prev => prev.map(t => (t.id === todo.id ? todo : t)));
    }
    // Không set loading để toggle mượt hơn
  }, []);


  const getTodoDetails = useCallback(async (id) => {
    setIsLoadingDetail(true);
    try {
      // Gọi repo lấy dữ liệu mới nhất từ server
      const data = await todoRepository.getTodoById(id);
      setSelectedTodo(data);
    } catch (err) {
      console.error(err);
      // Fallback: Nếu lỗi mạng, thử tìm trong danh sách local
      const localTodo = todos.find(t => t.id === id);
      if (localTodo) setSelectedTodo(localTodo);
    } finally {
      setIsLoadingDetail(false);
    }
  }, [todos]);

  // ✅ THÊM: Hàm clear selection khi đóng modal
  const clearSelectedTodo = useCallback(() => {
    setSelectedTodo(null);
  }, []);

  const updateTodoDetails = useCallback(async (id, updatedData) => {
    // 1. Chuẩn bị dữ liệu mới (để cập nhật giao diện ngay lập tức)
    const newOptimisticData = { 
        ...updatedData, 
        due_date: updatedData.due_date || null 
    };

    // ✅ FIX QUAN TRỌNG: Cập nhật ngay cái Todo đang được chọn (để Modal hiển thị cái mới)
    setSelectedTodo(prev => {
        if (prev && prev.id === id) {
            return { ...prev, ...newOptimisticData };
        }
        return prev;
    });

    // 2. Cập nhật danh sách tổng (như cũ)
    setTodos(prev => prev.map(t =>
        t.id === id ? { ...t, ...newOptimisticData } : t
    ));

    try {
      // 3. Gọi API update
      await todoRepository.updateTodo(id, updatedData);
    } catch (err) {
      console.error("Update failed:", err);
      setError("Cập nhật thất bại, vui lòng thử lại.");
      // Rollback nếu lỗi: Fetch lại từ server để lấy data đúng
      fetchTodos(); 
    }
  }, [fetchTodos]);

  return { todos, loading, error, fetchTodos, createNewTodo, removeTodo, toggleTodo, selectedTodo, getTodoDetails, isLoadingDetail, clearSelectedTodo, updateTodoDetails };
}