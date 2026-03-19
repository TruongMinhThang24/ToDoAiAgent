'use client'; // ✅ Directive bắt buộc cho client-side hooks
//src/app/layout.jsx
import './globals.css';

export default function RootLayout({ children }) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <head>
        <title>Chat AI - Todo App</title>
        <meta name="description" content="Chat với AI trợ lý" />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}