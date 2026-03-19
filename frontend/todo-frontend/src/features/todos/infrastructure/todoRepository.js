// src/features/todos/infrastructure/todoRepository.js
import apiClient from '@/lib/service/apiClient';

export const todoRepository = {
  /**
   * Get all todos
   */
  getAllTodos: async () => {
    // ✅ FIX: Thêm prefix /api/v1
    const response = await apiClient.get('/api/v1/todos/');
    return response.data;
  },

  /**
   * Add a new todo
   */
  addTodo: async (data) => {
    // ✅ FIX: Thêm prefix /api/v1
    const response = await apiClient.post('/api/v1/todos/', data);
    return response.data; // API 201 CREATED CÓ trả về data
  },

  /**
   * Update a todo
   */
  updateTodo: async (id, data) => {
    // ✅ FIX: Thêm prefix /api/v1
    // ✅ FIX: API 204 (No Content) không trả về data, nên ta không return gì cả
    await apiClient.put(`/api/v1/todos/${id}`, null, { params: data });
  },

  /**
   * Delete a todo
   */
  deleteTodo: async (id) => {
    // ✅ FIX: Thêm prefix /api/v1
    // ✅ FIX: API 204 (No Content) không trả về data
    await apiClient.delete(`/api/v1/todos/${id}`);
  },

  /**
   * Search todos
   */
  searchTodos: async (params) => {
    // ✅ FIX: Thêm prefix /api/v1
    const response = await apiClient.get('/api/v1/todos/search/', { params });
    return response.data;
  },

  /**
   * Get todo details by ID
   */
  getTodoById: async (id) => {
    const response = await apiClient.get(`/api/v1/todos/${id}`);
    return response.data;
  },
};