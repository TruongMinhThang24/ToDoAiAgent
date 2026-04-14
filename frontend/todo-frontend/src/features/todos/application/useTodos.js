// src/features/todos/application/useTodos.js
"use client";

import { useState, useCallback, useRef } from 'react';
import { todoRepository } from '../infrastructure/todoRepository';

const normalizeTodo = (todo) => {
  const status = todo?.status || (todo?.completed ? 'completed' : 'not_started');
  return {
    ...todo,
    status,
    completed: status === 'completed',
    is_vital: Boolean(todo?.is_vital),
    checklist_data: Array.isArray(todo?.checklist_data) ? todo.checklist_data : [],
    thumbnail_url: todo?.thumbnail_url || null,
  };
};

const getErrorMessage = (err, fallback) => (
  err?.response?.data?.detail
  || err?.response?.data?.message
  || err?.message
  || fallback
);

// ✅ FIX: export default function useTodos() -> export const useTodos
export const useTodos = () => {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const [selectedTodo, setSelectedTodo] = useState(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const lastQueryRef = useRef({ page: 1, page_size: 20 });

  const fetchTodos = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const mergedParams = {
        ...lastQueryRef.current,
        ...params,
      };
      lastQueryRef.current = mergedParams;

      const data = await todoRepository.getAllTodos(mergedParams);
      setTodos((data.items || []).map(normalizeTodo));
      setTotal(data.total ?? 0);
      setPage(data.page ?? mergedParams.page ?? 1);
      setPageSize(data.page_size ?? mergedParams.page_size ?? 20);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to fetch todos'));
    } finally {
      setLoading(false);
    }
  }, []);

  const createNewTodo = useCallback(async (todoData) => {
    setLoading(true); // Có thể dùng state riêng
    setError(null);
    try {
      const payload = {
        ...todoData,
        status: todoData.status || (todoData.completed ? 'completed' : 'not_started'),
      };
      const createdTodo = await todoRepository.addTodo(payload);
      await fetchTodos(lastQueryRef.current);
      if (createdTodo?.id) {
        setSelectedTodo(normalizeTodo(createdTodo));
      }
      return true;
    } catch (err) {
      const message = getErrorMessage(err, 'Failed to add todo');
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false); // Tắt loading chung
    }
  }, [fetchTodos]);

  const removeTodo = useCallback(async (id) => {
    try {
      await todoRepository.deleteTodo(id);
      await fetchTodos(lastQueryRef.current);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to delete todo'));
    }
  }, [fetchTodos]);

  const toggleTodo = useCallback(async (todo) => {
    const nextStatus = todo.completed ? 'in_progress' : 'completed';
    const updatedData = { 
      ...todo, 
      completed: !todo.completed,
      status: nextStatus,
      due_date: todo.due_date,
    }; 
    
    try {
      setTodos(prev => prev.map(t => (t.id === todo.id ? updatedData : t)));
      await todoRepository.updateTodo(todo.id, updatedData);
      await fetchTodos(lastQueryRef.current);
      
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to update todo'));
      setTodos(prev => prev.map(t => (t.id === todo.id ? todo : t)));
    }
  }, [fetchTodos]);


  const getTodoDetails = useCallback(async (id) => {
    setIsLoadingDetail(true);
    try {
      // Gọi repo lấy dữ liệu mới nhất từ server
      const data = await todoRepository.getTodoById(id);
      setSelectedTodo(normalizeTodo(data));
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
    const mergedData = {
      ...updatedData,
      status: updatedData.status || (updatedData.completed ? 'completed' : 'in_progress'),
    };
    // 1. Chuẩn bị dữ liệu mới (để cập nhật giao diện ngay lập tức)
    const newOptimisticData = { 
        ...mergedData,
        due_date: mergedData.due_date || null 
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
      await todoRepository.updateTodo(id, mergedData);
      await fetchTodos(lastQueryRef.current);
      await getTodoDetails(id);
      return true;
    } catch (err) {
      const message = getErrorMessage(err, 'Cập nhật thất bại, vui lòng thử lại.');
      console.error("Update failed:", err);
      setError(message);
      await fetchTodos(lastQueryRef.current);
      throw new Error(message);
    }
  }, [fetchTodos, getTodoDetails]);

  return {
    todos,
    loading,
    error,
    total,
    page,
    pageSize,
    fetchTodos,
    createNewTodo,
    removeTodo,
    toggleTodo,
    selectedTodo,
    getTodoDetails,
    isLoadingDetail,
    clearSelectedTodo,
    updateTodoDetails,
  };
}