// src/features/todos/infrastructure/todoRepository.js
import apiClient from '@/lib/service/apiClient';

const getErrorMessage = (error, fallback) => (
  error?.response?.data?.detail
  || error?.response?.data?.message
  || error?.message
  || fallback
);

const normalizeStatus = (status, completed) => {
  if (status === 'completed' || completed === true) {
    return 'completed';
  }
  if (status === 'in_progress') {
    return 'in_progress';
  }
  return 'not_started';
};

const normalizeThumbnailUrl = (url) => {
  if (!url || typeof url !== 'string') {
    return null;
  }
  const normalized = url.trim();
  if (!normalized || normalized.startsWith('blob:')) {
    return null;
  }
  return normalized;
};

const sanitizeChecklistData = (value) => {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((item) => item && typeof item === 'object');
};

const sanitizeTodoPayload = (data = {}) => {
  const normalizedStatus = normalizeStatus(data.status, data.completed);
  return {
    title: String(data.title || '').trim(),
    description: String(data.description || '').trim(),
    priority: Number(data.priority || 1),
    status: normalizedStatus,
    completed: normalizedStatus === 'completed',
    due_date: data.due_date || null,
    thumbnail_url: normalizeThumbnailUrl(data.thumbnail_url),
    is_vital: Boolean(data.is_vital),
    checklist_data: sanitizeChecklistData(data.checklist_data),
  };
};

export const todoRepository = {
  /**
   * Get all todos
   */
  getAllTodos: async (params = {}) => {
    try {
      const response = await apiClient.get('/api/v1/todos/', { params });
      const payload = response.data;

      // Backward compatibility nếu backend cũ trả về array thuần
      if (Array.isArray(payload)) {
        return {
          items: payload,
          total: payload.length,
          page: params.page ?? 1,
          page_size: params.page_size ?? payload.length,
        };
      }

      return payload;
    } catch (error) {
      throw new Error(getErrorMessage(error, 'Failed to fetch todos'));
    }
  },

  /**
   * Add a new todo
   */
  addTodo: async (data) => {
    try {
      const payload = sanitizeTodoPayload(data);
      const response = await apiClient.post('/api/v1/todos/', payload);
      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error, 'Failed to add todo'));
    }
  },

  /**
   * Update a todo
   */
  updateTodo: async (id, data) => {
    try {
      const payload = sanitizeTodoPayload(data);
      await apiClient.put(`/api/v1/todos/${id}`, payload);
    } catch (error) {
      throw new Error(getErrorMessage(error, 'Failed to update todo'));
    }
  },

  /**
   * Delete a todo
   */
  deleteTodo: async (id) => {
    try {
      await apiClient.delete(`/api/v1/todos/${id}`);
    } catch (error) {
      throw new Error(getErrorMessage(error, 'Failed to delete todo'));
    }
  },

  /**
   * Search todos (compat route)
   */
  searchTodos: async (params) => {
    try {
      const response = await apiClient.get('/api/v1/todos/search/', { params });
      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error, 'Failed to search todos'));
    }
  },

  /**
   * Get todo details by ID
   */
  getTodoById: async (id) => {
    try {
      const response = await apiClient.get(`/api/v1/todos/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(getErrorMessage(error, 'Failed to fetch todo details'));
    }
  },
};