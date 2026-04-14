'use client';

import { AlertCircle, PencilLine, Trash2 } from 'lucide-react';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';
import AddTaskModal from '@/features/todos/components/AddTaskModal';
import { useTodos } from '@/features/todos/application/useTodos';

const statusMap = {
  not_started: { label: 'Not Started', color: 'text-red-600' },
  in_progress: { label: 'In Progress', color: 'text-blue-700' },
  completed: { label: 'Completed', color: 'text-green-700' },
};

const priorityLabel = (value) => {
  const numeric = Number(value || 0);
  if (numeric >= 5) return { text: 'Extreme', color: 'text-red-600' };
  if (numeric >= 3) return { text: 'Moderate', color: 'text-sky-500' };
  return { text: 'Low', color: 'text-emerald-600' };
};

export default function TodoDetailPage() {
  const router = useRouter();
  const params = useParams();
  const taskId = params?.id;

  const { selectedTodo, isLoadingDetail, getTodoDetails, updateTodoDetails } = useTodos();

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  useEffect(() => {
    if (!taskId) {
      return;
    }
    getTodoDetails(taskId);
  }, [getTodoDetails, taskId]);

  const task = useMemo(() => {
    if (!selectedTodo) {
      return null;
    }
    return String(selectedTodo.id) === String(taskId) ? selectedTodo : null;
  }, [selectedTodo, taskId]);

  const statusMeta = statusMap[task?.status || 'not_started'] || statusMap.not_started;
  const priorityMeta = priorityLabel(task?.priority);

  const descriptionItems = useMemo(() => {
    if (Array.isArray(task?.checklist_data) && task.checklist_data.length > 0) {
      return task.checklist_data;
    }

    if (!task?.description) {
      return [];
    }

    return task.description
      .split(/\n|\./)
      .map((item) => item.trim())
      .filter(Boolean);
  }, [task]);

  if (isLoadingDetail) {
    return <p className="text-sm text-gray-500">Loading task details...</p>;
  }

  if (!task) {
    return (
      <div className="rounded-xl border border-zinc-300 bg-white p-6">
        <p className="text-sm text-gray-500">Task not found.</p>
        <button
          type="button"
          onClick={() => router.back()}
          className="mt-3 text-sm font-semibold underline"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-full">
      <div className="mb-5 flex items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold text-black">Task Detail</h2>
        <button
          type="button"
          onClick={() => router.back()}
          className="text-sm font-semibold underline text-black"
        >
          Go Back
        </button>
      </div>

      <section className="rounded-2xl border border-zinc-400/60 bg-stone-50 p-5 shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]">
        <div className="grid grid-cols-1 gap-5 md:grid-cols-12">
          <div className="md:col-span-4">
            <img
              src={task.thumbnail_url || 'https://placehold.co/420x260'}
              alt={task.title}
              className="h-56 w-full rounded-2xl object-cover"
            />
          </div>

          <div className="md:col-span-8 rounded-2xl border border-zinc-300 bg-white p-4">
            <h3 className="text-xl font-semibold text-black">{task.title}</h3>
            <div className="mt-3 space-y-2 text-sm text-zinc-700">
              <p>
                Date:{' '}
                <span className="text-zinc-500">
                  {new Date(task.due_date || task.created_at || Date.now()).toLocaleDateString('en-GB')}
                </span>
              </p>
              <p>
                Priority: <span className={priorityMeta.color}>{priorityMeta.text}</span>
              </p>
              <p>
                Status: <span className={statusMeta.color}>{statusMeta.label}</span>
              </p>
            </div>
          </div>
        </div>

        <div className="mt-5 rounded-2xl border border-zinc-300 bg-white p-4">
          <h4 className="text-sm font-semibold text-black">Task Description</h4>

          {descriptionItems.length > 0 ? (
            <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-zinc-600">
              {descriptionItems.map((item, index) => (
                <li key={`${task.id}-desc-${index}`}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-zinc-500">No description provided.</p>
          )}
        </div>

        <div className="mt-5 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={() => console.log('Delete Task ID:', task.id)}
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-red-500 text-white transition hover:bg-red-600"
            aria-label="Delete task"
          >
            <Trash2 className="h-4 w-4" />
          </button>

          <button
            type="button"
            onClick={() => setIsEditModalOpen(true)}
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-orange-500 text-white transition hover:bg-orange-600"
            aria-label="Edit task"
          >
            <PencilLine className="h-4 w-4" />
          </button>

          <button
            type="button"
            onClick={() => console.log('Toggle Vital Status:', task.id)}
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-orange-500 text-white transition hover:bg-orange-600"
            aria-label="Mark as vital"
          >
            <AlertCircle className="h-4 w-4" />
          </button>
        </div>
      </section>

      <AddTaskModal
        isOpen={isEditModalOpen}
        mode="edit"
        initialData={task}
        onClose={() => setIsEditModalOpen(false)}
        onSubmit={(payload) => updateTodoDetails(task.id, payload)}
      />
    </div>
  );
}
