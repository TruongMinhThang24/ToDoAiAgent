// src/features/todos/components/TaskItem.jsx
import Link from 'next/link';
import { CalendarDays, CheckCircle2, Circle, MoreHorizontal, Trash2 } from 'lucide-react';

const statusLabelMap = {
  not_started: { label: 'Not Started', color: 'text-red-600' },
  in_progress: { label: 'In Progress', color: 'text-blue-700' },
  completed: { label: 'Completed', color: 'text-green-700' },
};

const priorityLabel = (value) => {
  if (value >= 5) return { text: 'Extreme', color: 'text-red-600' };
  if (value >= 3) return { text: 'Moderate', color: 'text-sky-500' };
  return { text: 'Low', color: 'text-emerald-600' };
};

export const TaskItem = ({ todo, onToggle, onRemove, onClick }) => {
  const status = todo.status || (todo.completed ? 'completed' : 'not_started');
  const statusMeta = statusLabelMap[status] || statusLabelMap.not_started;
  const priorityMeta = priorityLabel(Number(todo.priority || 1));
  const createdOn = todo.created_at || todo.due_date;

  return (
    <article className="group rounded-2xl border border-zinc-300 bg-white p-3 transition hover:shadow-sm">
      <div className="flex items-start gap-3">
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onToggle();
          }}
          className="mt-1 text-gray-500 hover:text-gray-800"
        >
          {todo.completed ? <CheckCircle2 className="h-5 w-5 text-green-600" /> : <Circle className="h-5 w-5" />}
        </button>

        <Link href={`/todos/${todo.id}`} onClick={onClick} className="flex-1 text-left">
          <div className="flex gap-3">
            <img
              src={todo.thumbnail_url || 'https://placehold.co/88x88'}
              alt={todo.title}
              className="h-16 w-16 rounded-xl object-cover"
            />
            <div className="min-w-0 flex-1">
              <h4 className={`text-base font-semibold ${todo.completed ? 'line-through text-gray-400' : 'text-gray-900'}`}>
                {todo.title}
              </h4>
              <p className="mt-1 line-clamp-2 text-sm text-neutral-500">
                {todo.description || 'No description'}
              </p>
              <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px]">
                <span>
                  Priority: <span className={priorityMeta.color}>{priorityMeta.text}</span>
                </span>
                <span>
                  Status: <span className={statusMeta.color}>{statusMeta.label}</span>
                </span>
                {createdOn && (
                  <span className="inline-flex items-center gap-1 text-zinc-400">
                    <CalendarDays className="h-3 w-3" />
                    {new Date(createdOn).toLocaleDateString('en-GB')}
                  </span>
                )}
              </div>
            </div>
          </div>
        </Link>

        <div className="flex flex-col items-center gap-1">
          <button type="button" className="text-zinc-400 hover:text-zinc-700">
            <MoreHorizontal className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={onRemove}
            className="opacity-0 group-hover:opacity-100 text-zinc-300 hover:text-red-500 transition"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>
    </article>
  );
};