// src/features/todos/components/TodoInbox.jsx
'use client';

import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import {
  Inbox,
  Archive,
  FilePlus,
} from 'lucide-react';
import { useState, useEffect, useCallback } from 'react';
import { useTodos } from '../application/useTodos';

import { TaskItem } from './TaskItem';
import { NewTaskForm } from './NewTaskForm';
import { TaskDetailPanel } from './TaskDetailPanel';

export default function TodoInbox() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const initialTab = searchParams.get('view') === 'archived' ? 'archive' : 'inbox';
  const initialQuery = searchParams.get('q') || '';
  const initialStatus = searchParams.get('status') || 'all';
  const initialSortBy = searchParams.get('sort_by') || 'created_at';
  const initialSortOrder = searchParams.get('sort_order') || 'desc';

  const {
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
    updateTodoDetails,
  } = useTodos();

  const [activeTab, setActiveTab] = useState(initialTab);
  const [query, setQuery] = useState(initialQuery);
  const [debouncedQuery, setDebouncedQuery] = useState(initialQuery);
  const [statusFilter, setStatusFilter] = useState(initialStatus);
  const [sortBy, setSortBy] = useState(initialSortBy);
  const [sortOrder, setSortOrder] = useState(initialSortOrder);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 400);

    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    if (activeTab === 'new') {
      return;
    }

    const view = activeTab === 'archive' ? 'archived' : 'inbox';

    fetchTodos({
      q: debouncedQuery || undefined,
      status: statusFilter,
      view,
      sort_by: sortBy,
      sort_order: sortOrder,
      page: currentPage,
      page_size: pageSize || 20,
    });
  }, [activeTab, currentPage, debouncedQuery, fetchTodos, pageSize, sortBy, sortOrder, statusFilter]);

  useEffect(() => {
    if (!selectedTodo && todos.length > 0) {
      getTodoDetails(todos[0].id);
    }
  }, [getTodoDetails, selectedTodo, todos]);

  useEffect(() => {
    if (activeTab === 'new') {
      return;
    }

    const params = new URLSearchParams();
    params.set('view', activeTab === 'archive' ? 'archived' : 'inbox');
    if (debouncedQuery) {
      params.set('q', debouncedQuery);
    }
    if (statusFilter !== 'all') {
      params.set('status', statusFilter);
    }
    if (sortBy !== 'created_at') {
      params.set('sort_by', sortBy);
    }
    if (sortOrder !== 'desc') {
      params.set('sort_order', sortOrder);
    }
    if (currentPage > 1) {
      params.set('page', String(currentPage));
    }

    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  }, [activeTab, currentPage, debouncedQuery, pathname, router, sortBy, sortOrder, statusFilter]);

  const handleAddTask = useCallback(async (taskData) => {
    await createNewTodo(taskData);
    setActiveTab('inbox');
    setCurrentPage(1);
  }, [createNewTodo]);

  const handleTaskClick = (id) => {
    getTodoDetails(id);
  };

  const handleResetFilters = useCallback(() => {
    setQuery('');
    setStatusFilter('all');
    setSortBy('created_at');
    setSortOrder('desc');
    setCurrentPage(1);
  }, []);

  const hasActiveFilters = Boolean(
    query || statusFilter !== 'all' || sortBy !== 'created_at' || sortOrder !== 'desc' || currentPage > 1
  );

  const totalPages = Math.max(1, Math.ceil((total || 0) / (pageSize || 20)));

  return (
    <div className="min-h-full">
      <div className="mb-5 flex items-center gap-3">
        <h2 className="text-3xl font-medium text-black">My Tasks</h2>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <section className="xl:col-span-6 rounded-md border border-zinc-400/60 p-5 shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]">
          <div className="bg-slate-50 rounded-2xl p-4 shadow-[0px_5px_11px_0px_rgba(0,0,0,0.04)]">
                <div className="mb-4 flex items-center justify-between">
                  <div className="flex items-center gap-6 border-b border-gray-100 pb-2">
                    <TabButton id="inbox" label="inbox" icon={<Inbox className="w-4 h-4" />} active={activeTab} onClick={setActiveTab} />
                    <TabButton id="archive" label="archive" icon={<Archive className="w-4 h-4" />} active={activeTab} onClick={setActiveTab} />
                    <TabButton id="new" label="new task" icon={<FilePlus className="w-4 h-4" />} active={activeTab} onClick={setActiveTab} />
                  </div>
                </div>

                {activeTab !== 'new' && (
                  <div className="mb-4 rounded-xl border border-gray-100 bg-gray-50/60 p-3">
                    <div className="mb-2">
                      <input
                        value={query}
                        onChange={(e) => {
                          setQuery(e.target.value);
                          setCurrentPage(1);
                        }}
                        placeholder="Search your task here..."
                        className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm outline-none"
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                      <select
                        value={statusFilter}
                        onChange={(e) => {
                          setStatusFilter(e.target.value);
                          setCurrentPage(1);
                        }}
                        className="rounded-lg border border-gray-200 bg-white px-2 py-2 text-sm"
                      >
                        <option value="all">All</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                        <option value="overdue">Overdue</option>
                      </select>

                      <select
                        value={sortBy}
                        onChange={(e) => {
                          setSortBy(e.target.value);
                          setCurrentPage(1);
                        }}
                        className="rounded-lg border border-gray-200 bg-white px-2 py-2 text-sm"
                      >
                        <option value="created_at">Newest</option>
                        <option value="due_date">Due date</option>
                        <option value="priority">Priority</option>
                      </select>

                      <select
                        value={sortOrder}
                        onChange={(e) => {
                          setSortOrder(e.target.value);
                          setCurrentPage(1);
                        }}
                        className="rounded-lg border border-gray-200 bg-white px-2 py-2 text-sm"
                      >
                        <option value="desc">Desc</option>
                        <option value="asc">Asc</option>
                      </select>
                    </div>

                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-xs text-gray-500">{total} task(s) found</span>
                      <button type="button" onClick={handleResetFilters} className="text-xs font-medium text-gray-600 hover:text-gray-900">
                        Reset filters
                      </button>
                    </div>
                  </div>
                )}

                {error && (
                  <p className="mb-3 rounded-md border border-red-100 bg-red-50 px-3 py-2 text-xs text-red-600">
                    {error}
                  </p>
                )}

                {activeTab === 'inbox' && (
                  <TaskList
                    todos={todos}
                    loading={loading}
                    emptyMsg="Hooray! No pending tasks."
                    onToggle={toggleTodo}
                    onRemove={removeTodo}
                    onItemClick={handleTaskClick}
                    showResetAction={hasActiveFilters}
                    onResetAction={handleResetFilters}
                  />
                )}

                {activeTab === 'archive' && (
                  <TaskList
                    todos={todos}
                    loading={loading}
                    emptyMsg="No completed tasks yet."
                    onToggle={toggleTodo}
                    onRemove={removeTodo}
                    onItemClick={handleTaskClick}
                    showResetAction={hasActiveFilters}
                    onResetAction={handleResetFilters}
                  />
                )}

                {activeTab === 'new' && <NewTaskForm onAdd={handleAddTask} loading={loading} />}

                {activeTab !== 'new' && totalPages > 1 && (
                  <div className="mt-4 flex items-center justify-end gap-2 text-sm">
                    <button
                      type="button"
                      disabled={currentPage <= 1}
                      onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                      className="rounded-md border border-gray-200 px-2 py-1 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      Prev
                    </button>
                    <span className="text-xs text-gray-500">Page {page} / {totalPages}</span>
                    <button
                      type="button"
                      disabled={currentPage >= totalPages}
                      onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                      className="rounded-md border border-gray-200 px-2 py-1 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      Next
                    </button>
                  </div>
                )}
          </div>
        </section>

        <aside className="xl:col-span-6">
          <TaskDetailPanel
            todo={selectedTodo}
            isLoading={isLoadingDetail}
            onUpdate={updateTodoDetails}
          />
        </aside>
      </div>
    </div>
  );
}

const TabButton = ({ id, label, icon, active, onClick }) => (
  <button
    onClick={() => onClick(id)}
    className={`flex items-center gap-2 pb-2 transition-all ${
      active === id ? 'border-b-2 border-gray-800 text-gray-900 font-semibold' : 'text-gray-400 hover:text-gray-600'
    }`}
  >
    {icon} {label}
  </button>
);

const TaskList = ({ todos, loading, emptyMsg, onToggle, onRemove, onItemClick, showResetAction, onResetAction }) => (
  <div className="space-y-1">
    {loading && <p className="text-sm text-gray-400 animate-pulse">Loading tasks...</p>}
    {todos.length === 0 && !loading && (
      <div className="py-4">
        <p className="text-sm italic text-gray-300">{emptyMsg}</p>
        {showResetAction && (
          <button
            type="button"
            onClick={onResetAction}
            className="mt-1 text-xs font-medium text-gray-500 hover:text-gray-800"
          >
            Clear filters
          </button>
        )}
      </div>
    )}
    {todos.map((todo) => (
      <TaskItem
        key={todo.id}
        todo={todo}
        onToggle={() => onToggle(todo)}
        onRemove={() => onRemove(todo.id)}
        onClick={() => onItemClick(todo.id)}
      />
    ))}
  </div>
);