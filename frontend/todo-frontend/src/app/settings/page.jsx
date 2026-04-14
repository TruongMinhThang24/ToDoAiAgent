'use client';

import { useEffect, useState } from 'react';

const GEMINI_KEY_STORAGE = 'todo_gemini_api_key';

export default function SettingsPage() {
  const [geminiApiKey, setGeminiApiKey] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const existing = window.localStorage.getItem(GEMINI_KEY_STORAGE) || '';
    setGeminiApiKey(existing);
    setSaved(Boolean(existing));
  }, []);

  const handleSave = () => {
    const cleaned = geminiApiKey.trim();
    if (!cleaned) {
      setSaved(false);
      return;
    }
    window.localStorage.setItem(GEMINI_KEY_STORAGE, cleaned);
    setSaved(true);
  };

  const handleClear = () => {
    window.localStorage.removeItem(GEMINI_KEY_STORAGE);
    setGeminiApiKey('');
    setSaved(false);
  };

  return (
    <div className="mx-auto w-full max-w-3xl rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
      <h1 className="text-xl font-semibold text-gray-900">Settings</h1>
      <p className="mt-1 text-sm text-gray-500">Manage your runtime Gemini API key for chat (BYOK).</p>

      <div className="mt-6 rounded-xl border border-gray-200 bg-gray-50 p-4">
        <label className="mb-2 block text-sm font-medium text-gray-700">Your Gemini API Key</label>
        <div className="flex flex-wrap items-center gap-2">
          <input
            type="password"
            value={geminiApiKey}
            onChange={(e) => setGeminiApiKey(e.target.value)}
            placeholder="AIza..."
            className="h-10 min-w-[260px] flex-1 rounded-lg border border-gray-200 bg-white px-3 text-sm outline-none focus:border-blue-400"
          />
          <button
            type="button"
            onClick={handleSave}
            className="h-10 rounded-lg bg-blue-600 px-4 text-sm font-medium text-white hover:bg-blue-700"
          >
            Save
          </button>
          <button
            type="button"
            onClick={handleClear}
            className="h-10 rounded-lg border border-gray-300 bg-white px-4 text-sm font-medium text-gray-700 hover:bg-gray-100"
          >
            Clear
          </button>
        </div>
        {saved && <p className="mt-2 text-xs text-green-600">API key saved in browser storage.</p>}
      </div>
    </div>
  );
}
