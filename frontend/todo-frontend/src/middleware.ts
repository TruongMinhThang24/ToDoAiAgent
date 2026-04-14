import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_PATHS = ['/login', '/register'];
const PROTECTED_PREFIXES = ['/dashboard', '/my-task', '/todos', '/chat', '/vitals'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasAccessToken = Boolean(request.cookies.get('access_token')?.value);

  const isPublic = PUBLIC_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`));
  const isProtected = PROTECTED_PREFIXES.some((path) => pathname === path || pathname.startsWith(`${path}/`));

  if (isPublic && hasAccessToken) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  if (isProtected && !hasAccessToken) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/login', '/register', '/dashboard/:path*', '/my-task/:path*', '/todos/:path*', '/chat/:path*', '/vitals/:path*'],
};
