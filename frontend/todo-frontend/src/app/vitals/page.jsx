'use client';

import { useEffect, useMemo, useState } from 'react';
import { MoreHorizontal, CheckCircle2, Circle, Trash2, PencilLine } from 'lucide-react';
import { useTodos } from '@/features/todos/application/useTodos';

const statusLabel = (status) => {
  if (status === 'completed') return { text: 'Completed', cls: 'text-green-700' };
  if (status === 'in_progress') return { text: 'In Progress', cls: 'text-blue-700' };
  return { text: 'Not Started', cls: 'text-red-600' };
};

const priorityLabel = (priority) => {
  if ((priority || 1) >= 5) return { text: 'Extreme', cls: 'text-red-600' };
  if ((priority || 1) >= 3) return { text: 'Moderate', cls: 'text-sky-400' };
  return { text: 'Low', cls: 'text-gray-500' };
};

export default function VitalsPage() {
  const {
    todos,
    loading,
    error,
    total,
    fetchTodos,
    selectedTodo,
    getTodoDetails,
    updateTodoDetails,
    removeTodo,
  } = useTodos();

  const [query, setQuery] = useState('');

  useEffect(() => {
    fetchTodos({
      is_vital: true,
      q: query || undefined,
      page: 1,
      page_size: 30,
      sort_by: 'priority',
      sort_order: 'desc',
      status: 'all',
      view: 'all',
    });
  }, [fetchTodos, query]);

  useEffect(() => {
    if (!selectedTodo && todos.length > 0) {
      getTodoDetails(todos[0].id);
    }
  }, [selectedTodo, todos, getTodoDetails]);

  const checklist = useMemo(() => {
    if (!selectedTodo?.checklist_data || !Array.isArray(selectedTodo.checklist_data)) return [];
    return selectedTodo.checklist_data;
  }, [selectedTodo]);

  const reloadVitals = async () => {
    await fetchTodos({
      is_vital: true,
      q: query || undefined,
      page: 1,
      page_size: 30,
      sort_by: 'priority',
      sort_order: 'desc',
      status: 'all',
      view: 'all',
    });
  };

  const handleToggleChecklist = async (index) => {
    if (!selectedTodo) return;
    const next = checklist.map((item, idx) => (
      idx === index ? { ...item, done: !item.done } : item
    ));
    await updateTodoDetails(selectedTodo.id, { ...selectedTodo, checklist_data: next });
    await getTodoDetails(selectedTodo.id);
  };

  const handleMarkInProgress = async () => {
    if (!selectedTodo) return;
    await updateTodoDetails(selectedTodo.id, { ...selectedTodo, status: 'in_progress', completed: false });
    await getTodoDetails(selectedTodo.id);
  };

  const handleMarkCompleted = async () => {
    if (!selectedTodo) return;
    await updateTodoDetails(selectedTodo.id, { ...selectedTodo, status: 'completed', completed: true });
    await getTodoDetails(selectedTodo.id);
  };

  const handleUnVital = async () => {
    if (!selectedTodo) return;
    await updateTodoDetails(selectedTodo.id, { ...selectedTodo, is_vital: false });
    await reloadVitals();
  };

  const handleDelete = async () => {
    if (!selectedTodo) return;
    await removeTodo(selectedTodo.id);
    await reloadVitals();
  };

  return (
    <div className="min-h-full">
      <div className="mb-5 flex items-center gap-3">
        <h2 className="text-3xl font-medium text-black">Vital Tasks</h2>
      </div>

      <div className="mb-4 rounded-xl border border-gray-100 bg-gray-50/60 p-3">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search vital task..."
          className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm outline-none"
        />
      </div>

      {error && <p className="mb-3 rounded-md border border-red-100 bg-red-50 px-3 py-2 text-xs text-red-600">{error}</p>}

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <section className="xl:col-span-5 rounded-md border border-zinc-400/60 p-5 shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]">
          <div className="mb-3">
            <h3 className="text-base font-semibold text-black">Vital Tasks</h3>
            <div className="mt-2 h-[2px] w-12 bg-orange-600" />
            <p className="mt-2 text-xs text-gray-500">{total} task(s)</p>
          </div>

          <div className="space-y-3">
            {loading && <p className="text-sm text-gray-400">Loading vital tasks...</p>}
            {!loading && todos.length === 0 && <p className="text-sm text-gray-500">No vital tasks found.</p>}

            {todos.map((todo) => {
              const status = statusLabel(todo.status || 'not_started');
              const priority = priorityLabel(todo.priority);

              return (
                <article
                  key={todo.id}
                  onClick={() => getTodoDetails(todo.id)}
                  className={`cursor-pointer rounded-2xl border p-3 transition ${
                    selectedTodo?.id === todo.id
                      ? 'border-red-300 bg-red-50/30'
                      : 'border-zinc-300 bg-white hover:border-red-200'
                  }`}
                >
                  <div className="flex gap-3">
                    <span className={`mt-1 h-3 w-3 rounded-full ${
                      todo.status === 'completed'
                        ? 'bg-green-700'
                        : todo.status === 'in_progress'
                          ? 'bg-blue-700'
                          : 'bg-red-600'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <h4 className="text-base font-semibold text-black">{todo.title}</h4>
                      <p className="mt-1 text-sm text-neutral-500 line-clamp-2">{todo.description || 'No description'}</p>
                      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px]">
                        <span>Priority: <span className={priority.cls}>{priority.text}</span></span>
                        <span>Status: <span className={status.cls}>{status.text}</span></span>
                        <span className="text-zinc-400">Created on: {new Date(todo.created_at || Date.now()).toLocaleDateString('en-GB')}</span>
                      </div>
                    </div>
                    <img
                      src={todo.thumbnail_url || 'https://placehold.co/88x88'}
                      alt={todo.title}
                      className="h-20 w-20 rounded-2xl object-cover"
                    />
                    <button type="button" className="self-start text-gray-400 hover:text-gray-600">
                      <MoreHorizontal className="h-4 w-4" />
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <aside className="xl:col-span-7 rounded-md border border-zinc-400/60 p-5 shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]">
          {!selectedTodo ? (
            <p className="text-sm text-gray-500">Select a vital task to view details.</p>
          ) : (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-[158px_1fr] gap-4">
                <img
                  src={selectedTodo.thumbnail_url || 'https://placehold.co/158x158'}
                  alt={selectedTodo.title}
                  className="h-40 w-40 rounded-2xl object-cover"
                />
                <div>
                  <h3 className="text-base font-semibold text-black">{selectedTodo.title}</h3>
                  <p className="mt-3 text-xs">
                    Priority:{' '}
                    <span className={priorityLabel(selectedTodo.priority).cls}>
                      {priorityLabel(selectedTodo.priority).text}
                    </span>
                  </p>
                  <p className="mt-2 text-xs">
                    Status:{' '}
                    <span className={statusLabel(selectedTodo.status || 'not_started').cls}>
                      {statusLabel(selectedTodo.status || 'not_started').text}
                    </span>
                  </p>
                  <p className="mt-2 text-[10px] text-zinc-400">
                    Created on: {new Date(selectedTodo.created_at || Date.now()).toLocaleDateString('en-GB')}
                  </p>
                </div>
              </div>

              <div className="mt-6">
                <h4 className="text-sm font-semibold text-black">Description</h4>
                <p className="mt-2 text-sm text-neutral-500 leading-7">
                  {selectedTodo.description || 'No description'}
                </p>
              </div>

              <div className="mt-6">
                <h4 className="text-sm font-semibold text-black">Checklist</h4>
                {checklist.length === 0 ? (
                  <p className="mt-2 text-sm text-gray-500">No checklist items.</p>
                ) : (
                  <ul className="mt-2 space-y-2">
                    {checklist.map((item, index) => (
                      <li key={`${item.label || 'item'}-${index}`} className="flex items-center gap-2 text-sm">
                        <button type="button" onClick={() => handleToggleChecklist(index)} className="text-gray-500">
                          {item.done ? <CheckCircle2 className="h-4 w-4 text-green-700" /> : <Circle className="h-4 w-4" />}
                        </button>
                        <span className={item.done ? 'line-through text-gray-400' : 'text-neutral-600'}>
                          {item.label || item.content || `Checklist #${index + 1}`}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="mt-8 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={handleMarkInProgress}
                  className="rounded-lg bg-blue-600 px-3 py-2 text-xs font-medium text-white hover:bg-blue-700"
                >
                  Mark In Progress
                </button>
                <button
                  type="button"
                  onClick={handleMarkCompleted}
                  className="rounded-lg bg-green-600 px-3 py-2 text-xs font-medium text-white hover:bg-green-700"
                >
                  Mark Completed
                </button>
                <button
                  type="button"
                  onClick={handleUnVital}
                  className="rounded-lg bg-amber-500 px-3 py-2 text-xs font-medium text-white hover:bg-amber-600"
                >
                  Remove Vital
                </button>
                <button
                  type="button"
                  className="rounded-lg border border-gray-300 px-3 py-2 text-xs font-medium text-gray-700 hover:bg-gray-50"
                >
                  <PencilLine className="mr-1 inline h-3.5 w-3.5" />
                  Edit
                </button>
                <button
                  type="button"
                  onClick={handleDelete}
                  className="rounded-lg bg-red-600 px-3 py-2 text-xs font-medium text-white hover:bg-red-700"
                >
                  <Trash2 className="mr-1 inline h-3.5 w-3.5" />
                  Delete
                </button>
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
