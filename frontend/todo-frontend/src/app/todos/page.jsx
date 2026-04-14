'use client';

import { useCallback, useEffect, useState } from 'react';
import { PencilLine, Trash2, Plus } from 'lucide-react';
import { taskCategoryRepository } from '@/features/todos/infrastructure/taskCategoryRepository';
import ActionModal from '@/features/todos/components/ActionModal';
import CreateCategoryForm from '@/features/todos/components/CreateCategoryForm';

export default function TodosPage() {
  const [statuses, setStatuses] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [loadingStatuses, setLoadingStatuses] = useState(false);
  const [loadingPriorities, setLoadingPriorities] = useState(false);
  const [errorStatuses, setErrorStatuses] = useState('');
  const [errorPriorities, setErrorPriorities] = useState('');
  const [isCreatingCategory, setIsCreatingCategory] = useState(false);
  const [modalConfig, setModalConfig] = useState(null);

  const loadStatuses = useCallback(async () => {
    setLoadingStatuses(true);
    setErrorStatuses('');
    try {
      const data = await taskCategoryRepository.getStatuses();
      setStatuses(data || []);
    } catch (error) {
      setErrorStatuses(error?.message || 'Failed to load task statuses');
    } finally {
      setLoadingStatuses(false);
    }
  }, []);

  const loadPriorities = useCallback(async () => {
    setLoadingPriorities(true);
    setErrorPriorities('');
    try {
      const data = await taskCategoryRepository.getPriorities();
      setPriorities(data || []);
    } catch (error) {
      setErrorPriorities(error?.message || 'Failed to load task priorities');
    } finally {
      setLoadingPriorities(false);
    }
  }, []);

  useEffect(() => {
    loadStatuses();
    loadPriorities();
  }, [loadPriorities, loadStatuses]);

  const openAddStatusModal = () => {
    setModalConfig({
      mode: 'add-status',
      title: 'Add Task Status',
      inputLabel: 'Task Status Name',
      initialValue: '',
      submitText: 'Create',
      targetId: null,
    });
  };

  const openAddPriorityModal = () => {
    setModalConfig({
      mode: 'add-priority',
      title: 'Add Task Priority',
      inputLabel: 'Task Priority Title',
      initialValue: '',
      submitText: 'Create',
      targetId: null,
    });
  };

  const openEditPriorityModal = (item) => {
    setModalConfig({
      mode: 'edit-priority',
      title: 'Edit Task Priority',
      inputLabel: 'Task Priority Title',
      initialValue: item?.name || '',
      submitText: 'Update',
      targetId: item?.id ?? null,
    });
  };

  const openEditStatusModal = (item) => {
    setModalConfig({
      mode: 'edit-status',
      title: 'Edit Task Status',
      inputLabel: 'Task Status Name',
      initialValue: item?.name || '',
      submitText: 'Update',
      targetId: item?.id ?? null,
    });
  };

  const closeModal = () => {
    setModalConfig(null);
  };

  const handleModalSubmit = (value) => {
    if (!modalConfig) {
      return;
    }

    console.log('Task category modal submit (dummy):', {
      mode: modalConfig.mode,
      targetId: modalConfig.targetId,
      value,
    });

    closeModal();
  };

  const handleOpenCreateCategory = () => {
    setIsCreatingCategory(true);
  };

  const handleCancelCreateCategory = () => {
    setIsCreatingCategory(false);
  };

  const handleSubmitCreateCategory = (categoryName) => {
    console.log('Create Category (dummy):', { categoryName });
    setIsCreatingCategory(false);
  };

  const deleteStatus = async (item) => {
    const confirmed = window.confirm(`Delete status "${item.name}"?`);
    if (!confirmed) {
      return;
    }
    await taskCategoryRepository.deleteStatus(item.id);
    await loadStatuses();
  };

  const deletePriority = async (item) => {
    const confirmed = window.confirm(`Delete priority "${item.name}"?`);
    if (!confirmed) {
      return;
    }
    await taskCategoryRepository.deletePriority(item.id);
    await loadPriorities();
  };

  if (isCreatingCategory) {
    return (
      <CreateCategoryForm
        onSubmit={handleSubmitCreateCategory}
        onCancel={handleCancelCreateCategory}
      />
    );
  }

  return (
    <div className="min-h-full">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold text-black">Task Categories</h2>
          <div className="mt-2 h-[2px] w-12 bg-orange-600" />
        </div>
        <button
          type="button"
          onClick={() => window.history.back()}
          className="text-sm font-semibold underline text-black"
        >
          Go Back
        </button>
      </div>

      <div className="mb-4">
        <button
          type="button"
          onClick={handleOpenCreateCategory}
          className="rounded-md bg-orange-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-orange-700"
        >
          Add Category
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <section className="rounded-md border border-zinc-400/60 p-5 shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-black">Task Status</h3>
              <div className="mt-1 h-[2px] w-12 bg-orange-600" />
            </div>
            <button
              type="button"
              onClick={openAddStatusModal}
              className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs font-medium text-zinc-500 hover:bg-gray-50"
            >
              <Plus className="h-3.5 w-3.5 text-orange-600" />
              Add Task Status
            </button>
          </div>

          {errorStatuses && (
            <p className="mb-3 rounded-md border border-red-100 bg-red-50 px-3 py-2 text-xs text-red-600">{errorStatuses}</p>
          )}

          <div className="overflow-x-auto rounded-2xl border border-zinc-400/60">
            <table className="min-w-full text-sm">
              <thead className="bg-white">
                <tr className="border-b border-zinc-400/60">
                  <th className="w-16 px-4 py-3 text-left font-semibold">SN</th>
                  <th className="px-4 py-3 text-left font-semibold">Task Status</th>
                  <th className="w-72 px-4 py-3 text-left font-semibold">Action</th>
                </tr>
              </thead>
              <tbody className="bg-slate-50">
                {loadingStatuses && (
                  <tr>
                    <td colSpan={3} className="px-4 py-4 text-gray-400">Loading task statuses...</td>
                  </tr>
                )}

                {!loadingStatuses && statuses.length === 0 && (
                  <tr>
                    <td colSpan={3} className="px-4 py-4 text-gray-500">No task status found.</td>
                  </tr>
                )}

                {!loadingStatuses && statuses.map((item, index) => (
                  <tr key={item.id} className="border-b border-zinc-400/30 last:border-b-0">
                    <td className="px-4 py-3">{index + 1}</td>
                    <td className="px-4 py-3 font-medium">{item.name}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-2">
                        <button
                          type="button"
                          onClick={() => openEditStatusModal(item)}
                          className="inline-flex items-center gap-2 rounded-lg bg-orange-500 px-3 py-2 text-xs font-medium text-white transition hover:bg-orange-600"
                        >
                          <PencilLine className="h-3.5 w-3.5" />
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => deleteStatus(item)}
                          className="inline-flex items-center gap-2 rounded-lg bg-red-500 px-3 py-2 text-xs font-medium text-white transition hover:bg-red-600"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-md border border-zinc-400/60 p-5 shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-black">Task Priority</h3>
              <div className="mt-1 h-[2px] w-12 bg-orange-600" />
            </div>
            <button
              type="button"
              onClick={openAddPriorityModal}
              className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs font-medium text-zinc-500 hover:bg-gray-50"
            >
              <Plus className="h-3.5 w-3.5 text-orange-600" />
              Add New Priority
            </button>
          </div>

          {errorPriorities && (
            <p className="mb-3 rounded-md border border-red-100 bg-red-50 px-3 py-2 text-xs text-red-600">{errorPriorities}</p>
          )}

          <div className="overflow-x-auto rounded-2xl border border-zinc-400/60">
            <table className="min-w-full text-sm">
              <thead className="bg-white">
                <tr className="border-b border-zinc-400/60">
                  <th className="w-16 px-4 py-3 text-left font-semibold">SN</th>
                  <th className="px-4 py-3 text-left font-semibold">Task Priority</th>
                  <th className="w-72 px-4 py-3 text-left font-semibold">Action</th>
                </tr>
              </thead>
              <tbody className="bg-slate-50">
                {loadingPriorities && (
                  <tr>
                    <td colSpan={3} className="px-4 py-4 text-gray-400">Loading task priorities...</td>
                  </tr>
                )}

                {!loadingPriorities && priorities.length === 0 && (
                  <tr>
                    <td colSpan={3} className="px-4 py-4 text-gray-500">No task priority found.</td>
                  </tr>
                )}

                {!loadingPriorities && priorities.map((item, index) => (
                  <tr key={item.id} className="border-b border-zinc-400/30 last:border-b-0">
                    <td className="px-4 py-3">{index + 1}</td>
                    <td className="px-4 py-3 font-medium">{item.name}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-2">
                        <button
                          type="button"
                          onClick={() => openEditPriorityModal(item)}
                          className="inline-flex items-center gap-2 rounded-lg bg-orange-500 px-3 py-2 text-xs font-medium text-white transition hover:bg-orange-600"
                        >
                          <PencilLine className="h-3.5 w-3.5" />
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => deletePriority(item)}
                          className="inline-flex items-center gap-2 rounded-lg bg-red-500 px-3 py-2 text-xs font-medium text-white transition hover:bg-red-600"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <ActionModal
        isOpen={Boolean(modalConfig)}
        title={modalConfig?.title || ''}
        inputLabel={modalConfig?.inputLabel || ''}
        initialValue={modalConfig?.initialValue || ''}
        submitText={modalConfig?.submitText || 'Submit'}
        onClose={closeModal}
        onSubmit={handleModalSubmit}
      />
    </div>
  );
}