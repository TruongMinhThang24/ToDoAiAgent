import apiClient from '@/lib/service/apiClient';

export const taskCategoryRepository = {
  getStatuses: async () => {
    const response = await apiClient.get('/api/v1/task-categories/statuses');
    return response.data;
  },

  createStatus: async (name) => {
    const response = await apiClient.post('/api/v1/task-categories/statuses', { name });
    return response.data;
  },

  updateStatus: async (id, name) => {
    await apiClient.put(`/api/v1/task-categories/statuses/${id}`, { name });
  },

  deleteStatus: async (id) => {
    await apiClient.delete(`/api/v1/task-categories/statuses/${id}`);
  },

  getPriorities: async () => {
    const response = await apiClient.get('/api/v1/task-categories/priorities');
    return response.data;
  },

  createPriority: async (name, level) => {
    const response = await apiClient.post('/api/v1/task-categories/priorities', { name, level });
    return response.data;
  },

  updatePriority: async (id, name, level) => {
    await apiClient.put(`/api/v1/task-categories/priorities/${id}`, { name, level });
  },

  deletePriority: async (id) => {
    await apiClient.delete(`/api/v1/task-categories/priorities/${id}`);
  },
};
