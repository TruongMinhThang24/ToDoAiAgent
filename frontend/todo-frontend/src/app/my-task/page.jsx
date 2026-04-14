import TodoInbox from '@/features/todos/components/TodoInbox';
import { Suspense } from 'react';

export default function MyTaskPage() {
  return (
    <Suspense fallback={<div className="p-6 text-sm text-gray-400">Loading my tasks...</div>}>
      <TodoInbox />
    </Suspense>
  );
}
