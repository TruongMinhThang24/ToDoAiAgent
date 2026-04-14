'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { useTodos } from '@/features/todos/application/useTodos';
import AddTaskModal from '@/features/todos/components/AddTaskModal';
import InviteModal from '@/components/overlay/InviteModal';

export default function DashboardPage() {
  const { todos, loading, error, total, fetchTodos, createNewTodo } = useTodos();

  const [query, setQuery] = useState('');
  const [isAddTaskOpen, setIsAddTaskOpen] = useState(false);
  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [projectLink] = useState('https://chatapp.com/invite/member?token=QWlkxLy2b');
  const [members, setMembers] = useState([
    {
      id: 1,
      name: 'Jonathan Gurung',
      email: 'jonathangurung36@gmail.com',
      avatar: 'https://placehold.co/32x32',
      role: 'can_edit',
    },
    {
      id: 2,
      name: 'Jeremy Lee',
      email: 'jeremy1849@gmail.com',
      avatar: 'https://placehold.co/32x32',
      role: 'can_edit',
    },
    {
      id: 3,
      name: 'Thomas Park',
      email: 'thomas49park.com',
      avatar: 'https://placehold.co/32x32',
      role: 'owner',
    },
    {
      id: 4,
      name: 'Rachel Takahasi',
      email: 'rachelhowe29@gmail.com',
      avatar: 'https://placehold.co/32x32',
      role: 'can_edit',
    },
  ]);

  useEffect(() => {
    fetchTodos({
      page: 1,
      page_size: 12,
      sort_by: 'created_at',
      sort_order: 'desc',
      q: query || undefined,
    });
  }, [fetchTodos, query]);

  const doneCount = useMemo(() => todos.filter((t) => t.status === 'completed' || t.completed).length, [todos]);
  const inProgressCount = useMemo(() => todos.filter((t) => t.status === 'in_progress').length, [todos]);
  const notStartedCount = useMemo(
    () => todos.filter((t) => (t.status || 'not_started') === 'not_started' && !t.completed).length,
    [todos]
  );

  const donePct = total ? Math.round((doneCount / total) * 100) : 0;
  const inProgressPct = total ? Math.round((inProgressCount / total) * 100) : 0;
  const notStartedPct = total ? Math.round((notStartedCount / total) * 100) : 0;

  const completedPreview = useMemo(() => todos.filter((t) => t.status === 'completed' || t.completed).slice(0, 2), [todos]);

  const handleSendInvite = (email) => {
    console.log('invite.send', email);
  };

  const handleCopyLink = (link) => {
    console.log('invite.copyLink', link);
  };

  const handleMemberRoleChange = (memberId, role) => {
    setMembers((prev) => prev.map((member) => (member.id === memberId ? { ...member, role } : member)));
    console.log('invite.updateRole', { memberId, role });
  };

  return (
    <div className="min-h-full">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h2 className="text-3xl font-medium text-black">Welcome back, Sundar</h2>
          <span className="text-2xl" role="img" aria-label="wave">👋</span>
        </div>

        <div className="hidden md:flex items-center gap-2">
          <img src="https://placehold.co/32x32" alt="member-1" className="h-8 w-8 rounded-md object-cover" />
          <img src="https://placehold.co/32x32" alt="member-2" className="h-8 w-8 rounded-md object-cover" />
          <img src="https://placehold.co/32x32" alt="member-3" className="h-8 w-8 rounded-md object-cover" />
          <img src="https://placehold.co/32x32" alt="member-4" className="h-8 w-8 rounded-md object-cover" />
          <button
            type="button"
            onClick={() => setIsInviteOpen(true)}
            className="ml-1 rounded-lg border border-red-300 px-3 py-1 text-xs font-medium text-red-400 hover:bg-red-50"
          >
            + Invite
          </button>
        </div>
      </div>

      <div className="mb-4 rounded-xl border border-gray-100 bg-gray-50/60 p-3">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search task in dashboard..."
          className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm outline-none"
        />
      </div>

      {error && <p className="mb-3 rounded-md border border-red-100 bg-red-50 px-3 py-2 text-xs text-red-600">{error}</p>}

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <section className="xl:col-span-7 rounded-md border border-zinc-400/60 p-5 shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]">
          <div className="bg-slate-50 rounded-2xl p-4 shadow-[0px_5px_11px_0px_rgba(0,0,0,0.04)]">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-red-400 text-base font-medium">To-Do</h3>
              <button
                type="button"
                onClick={() => setIsAddTaskOpen(true)}
                className="rounded-lg bg-red-300 px-3 py-1 text-xs font-medium text-white hover:bg-red-400"
              >
                ADD TASK
              </button>
            </div>

                <div className="space-y-3">
                  {loading && <p className="text-sm text-gray-400">Loading tasks...</p>}
                  {!loading && todos.length === 0 && <p className="text-sm text-gray-500">No tasks found.</p>}

                  {todos.slice(0, 3).map((todo) => (
                    <Link
                      key={todo.id}
                      href={`/todos/${todo.id}`}
                      className="block rounded-2xl border border-zinc-400 bg-white p-3 transition hover:shadow-sm"
                    >
                      <div className="flex gap-3">
                        <span className={`mt-1 h-3 w-3 rounded-full ${
                          (todo.status || 'not_started') === 'completed'
                            ? 'bg-green-700'
                            : (todo.status || 'not_started') === 'in_progress'
                              ? 'bg-blue-700'
                              : 'bg-red-600'
                        }`} />
                        <div className="flex-1 min-w-0">
                          <h4 className="text-base font-semibold text-black">{todo.title}</h4>
                          <p className="mt-1 text-sm text-neutral-500 line-clamp-2">{todo.description || 'No description'}</p>
                          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px]">
                            <span>
                              Priority: <span className="text-sky-400">{Number(todo.priority || 1) >= 5 ? 'Extreme' : 'Moderate'}</span>
                            </span>
                            <span>
                              Status:{' '}
                              <span className={
                                (todo.status || 'not_started') === 'completed'
                                  ? 'text-green-700'
                                  : (todo.status || 'not_started') === 'in_progress'
                                    ? 'text-blue-700'
                                    : 'text-red-600'
                              }>
                                {(todo.status || 'not_started') === 'completed'
                                  ? 'Completed'
                                  : (todo.status || 'not_started') === 'in_progress'
                                    ? 'In Progress'
                                    : 'Not Started'}
                              </span>
                            </span>
                            <span className="text-zinc-400">
                              Created on: {new Date(todo.created_at || todo.due_date || Date.now()).toLocaleDateString('en-GB')}
                            </span>
                          </div>
                        </div>
                        <img src={todo.thumbnail_url || 'https://placehold.co/88x88'} alt={todo.title} className="h-20 w-20 rounded-2xl object-cover" />
                      </div>
                    </Link>
                  ))}
                </div>
          </div>
        </section>

        <aside className="xl:col-span-5 space-y-6">
          <section className="rounded-2xl bg-violet-50 p-4 shadow-[0px_3px_7px_0px_rgba(0,0,0,0.04)]">
            <h3 className="text-red-400 font-medium mb-4">Task Status</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <StatusBox title="Completed" percent={donePct} color="bg-green-700" />
              <StatusBox title="In Progress" percent={inProgressPct} color="bg-blue-700" />
              <StatusBox title="Not Started" percent={notStartedPct} color="bg-red-600" />
            </div>
          </section>

          <section className="rounded-2xl bg-violet-50 p-4 shadow-[0px_3px_7px_0px_rgba(0,0,0,0.04)]">
            <h3 className="text-orange-600 font-medium mb-4">Completed Task</h3>
            <div className="space-y-3">
              {(completedPreview.length ? completedPreview : todos.slice(0, 2)).map((todo) => (
                <Link key={todo.id} href={`/todos/${todo.id}`} className="block rounded-xl border border-gray-200 bg-white p-3 transition hover:shadow-sm">
                  <div className="flex items-start gap-3">
                    <span className="mt-1 h-2.5 w-2.5 rounded-full bg-green-700" />
                    <div className="min-w-0 flex-1">
                      <p className="font-semibold text-sm">{todo.title}</p>
                      <p className="text-xs text-gray-500 mt-1 line-clamp-2">{todo.description || 'No description'}</p>
                      <p className="text-[10px] text-gray-500 mt-2">
                        Status: <span className="text-green-700">Completed</span>
                      </p>
                    </div>
                    <img src={todo.thumbnail_url || 'https://placehold.co/88x88'} alt={todo.title} className="h-16 w-16 rounded-xl object-cover" />
                  </div>
                </Link>
              ))}
            </div>
          </section>
        </aside>
      </div>

      <AddTaskModal
        isOpen={isAddTaskOpen}
        onClose={() => setIsAddTaskOpen(false)}
        onSubmit={createNewTodo}
      />
      <InviteModal
        isOpen={isInviteOpen}
        onClose={() => setIsInviteOpen(false)}
        inviteEmail={inviteEmail}
        onInviteEmailChange={setInviteEmail}
        onSendInvite={handleSendInvite}
        members={members}
        onMemberRoleChange={handleMemberRoleChange}
        projectLink={projectLink}
        onCopyLink={handleCopyLink}
      />
    </div>
  );
}

const StatusBox = ({ title, percent, color }) => (
  <div className="rounded-xl border border-gray-200 bg-white p-3">
    <div className="flex items-center justify-between">
      <p className="text-xs font-medium text-black">{title}</p>
      <span className="text-sm font-semibold">{percent}%</span>
    </div>
    <div className="mt-2 h-2 w-full rounded-full bg-gray-100 overflow-hidden">
      <div className={`h-full ${color}`} style={{ width: `${Math.max(0, Math.min(100, percent))}%` }} />
    </div>
  </div>
);
