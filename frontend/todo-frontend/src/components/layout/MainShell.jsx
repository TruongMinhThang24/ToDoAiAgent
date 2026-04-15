'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  Bell,
  CalendarDays,
  CheckSquare,
  Circle,
  HelpCircle,
  LayoutDashboard,
  ListTodo,
  LogOut,
  Mic,
  Search,
  Settings,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { authRepository } from '@/features/auth/login/infrastructure/authRepository';
import NotificationPopover from '@/components/overlay/NotificationPopover';
import CalendarPopover from '@/components/overlay/CalendarPopover';
import FloatingChatWidget from '@/components/overlay/FloatingChatWidget';

const SHELL_ROUTES = ['/dashboard', '/my-task', '/todos', '/vitals', '/profile', '/chat', '/voice-room', '/settings'];

const isRouteActive = (pathname, href) => pathname === href || pathname.startsWith(`${href}/`);

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/vitals', label: 'Vital Task', icon: Circle },
  { href: '/my-task', label: 'My Task', icon: CheckSquare },
  { href: '/todos', label: 'Task Categories', icon: ListTodo },
  { href: '/voice-room', label: 'Phòng trò chuyện', icon: Mic },
  { href: '/settings', label: 'Settings', icon: Settings },
  { href: '#', label: 'Help', icon: HelpCircle },
];

export default function MainShell({ children }) {
  const pathname = usePathname();
  const router = useRouter();

  const shouldRenderShell = useMemo(
    () => SHELL_ROUTES.some((route) => isRouteActive(pathname, route)),
    [pathname]
  );

  const today = new Date();
  const weekday = today.toLocaleDateString('en-US', { weekday: 'long' });
  const dateText = today.toLocaleDateString('en-GB');

  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState(today);
  const [currentMonth, setCurrentMonth] = useState(new Date(today.getFullYear(), today.getMonth(), 1));

  const notifRef = useRef(null);
  const calendarRef = useRef(null);

  useEffect(() => {
    const handleMouseDown = (event) => {
      const target = event.target;

      if (isNotifOpen && notifRef.current && !notifRef.current.contains(target)) {
        setIsNotifOpen(false);
      }

      if (isCalendarOpen && calendarRef.current && !calendarRef.current.contains(target)) {
        setIsCalendarOpen(false);
      }
    };

    document.addEventListener('mousedown', handleMouseDown);
    return () => {
      document.removeEventListener('mousedown', handleMouseDown);
    };
  }, [isNotifOpen, isCalendarOpen]);

  const handleLogout = useCallback(async () => {
    try {
      await authRepository.logout();
    } finally {
      router.push('/login');
    }
  }, [router]);

  if (!shouldRenderShell) {
    return children;
  }

  return (
    <div className="h-screen w-full bg-slate-50 text-gray-800 overflow-hidden">
      <header className="h-24 bg-stone-50 shadow-[0px_4px_12px_0px_rgba(0,0,0,0.07)] px-4 md:px-8 lg:px-12 flex items-center gap-4">
        <h1 className="min-w-[180px] text-3xl font-semibold">
          <span className="text-red-400">To</span>
          <span className="text-black">-Do</span>
        </h1>

        <div className="flex-1 flex items-center justify-center">
          <div className="w-full max-w-[695px] h-9 rounded-lg bg-slate-50 px-4 flex items-center gap-3 shadow-[-1px_4px_10px_0px_rgba(0,0,0,0.04)]">
            <input
              placeholder="Search your task here..."
              className="w-full bg-transparent text-xs font-semibold text-zinc-500 outline-none placeholder:text-zinc-400"
            />
            <button type="button" className="h-9 w-9 shrink-0 rounded-lg bg-[#FF6767] text-white grid place-items-center">
              <Search className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="hidden lg:flex items-center gap-2">
          <div ref={notifRef} className="relative">
            <button
              type="button"
              onClick={() => {
                setIsNotifOpen((prev) => !prev);
                setIsCalendarOpen(false);
              }}
              className="h-[34px] w-[34px] rounded-lg bg-[#FF6767] text-white grid place-items-center"
            >
              <Bell className="h-4 w-4" />
            </button>

            {isNotifOpen && <NotificationPopover onGoBack={() => setIsNotifOpen(false)} />}
          </div>

          <div ref={calendarRef} className="relative">
            <button
              type="button"
              onClick={() => {
                setIsCalendarOpen((prev) => !prev);
                setIsNotifOpen(false);
              }}
              className="h-[34px] w-[34px] rounded-lg bg-[#FF6767] text-white grid place-items-center"
            >
              <CalendarDays className="h-4 w-4" />
            </button>

            {isCalendarOpen && (
              <CalendarPopover
                currentMonth={currentMonth}
                selectedDate={selectedDate}
                onPrevMonth={() => setCurrentMonth((prev) => new Date(prev.getFullYear(), prev.getMonth() - 1, 1))}
                onNextMonth={() => setCurrentMonth((prev) => new Date(prev.getFullYear(), prev.getMonth() + 1, 1))}
                onSelectDate={(date) => {
                  setSelectedDate(date);
                  console.log('calendar.selectDate', date.toISOString());
                }}
                onGoBack={() => setIsCalendarOpen(false)}
                onClear={() => {
                  console.log('calendar.clearDate');
                  setSelectedDate(new Date());
                }}
              />
            )}
          </div>

          <div className="ml-2">
            <p className="text-base font-medium text-black leading-4">{weekday}</p>
            <p className="text-sm font-medium text-sky-400 mt-1 leading-4">{dateText}</p>
          </div>
        </div>
      </header>

      <div className="h-[calc(100vh-96px)] flex min-w-0">
        <aside className="hidden lg:flex w-[340px] px-4 py-8">
          <div className="w-full rounded-tr-lg rounded-br-lg bg-red-400 shadow-[0px_4px_12px_0px_rgba(0,0,0,0.08)] px-5 py-6 flex flex-col text-white">
            <div className="flex flex-col items-center text-center mb-6">
              <Link href="/profile" className="inline-flex">
                <img
                  className="h-20 w-20 rounded-full border border-white object-cover"
                  src="https://placehold.co/86x86"
                  alt="avatar"
                />
              </Link>
              <p className="mt-4 text-base font-semibold">Sundar Gurung</p>
              <p className="text-xs">sundargurung360@gmail.com</p>
            </div>

            <nav className="space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = item.href !== '#' && isRouteActive(pathname, item.href);

                if (item.href === '#') {
                  return (
                    <button
                      key={item.label}
                      type="button"
                      className="w-full flex items-center gap-3 rounded-2xl px-4 py-4 text-left transition hover:bg-white/10 text-white"
                    >
                      <Icon className="h-4 w-4" />
                      <span className="text-base font-medium">{item.label}</span>
                    </button>
                  );
                }

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`w-full flex items-center gap-3 rounded-2xl px-4 py-4 text-left transition ${
                      active ? 'bg-white text-red-400' : 'hover:bg-white/10 text-white'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="text-base font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </nav>

            <button
              type="button"
              onClick={handleLogout}
              className="mt-auto flex items-center gap-3 rounded-2xl px-3 py-3 hover:bg-white/10 transition"
            >
              <LogOut className="h-4 w-4" />
              <span className="text-base font-medium">Logout</span>
            </button>
          </div>
        </aside>

        <main className="flex-1 min-w-0 overflow-auto px-4 md:px-6 lg:px-8 py-6">{children}</main>
      </div>

      {pathname !== '/chat' && pathname !== '/voice-room' && <FloatingChatWidget />}
    </div>
  );
}
