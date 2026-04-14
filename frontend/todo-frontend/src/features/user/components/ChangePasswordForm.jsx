'use client';

export default function ChangePasswordForm({
  formData,
  onFieldChange,
  onClickUpdatePassword,
  onClickCancel,
  isSubmitting = false,
  errorMessage = '',
  successMessage = '',
}) {
  return (
    <section className="rounded-xl border border-zinc-400 p-6">
      <div className="grid grid-cols-1 gap-5 max-w-[520px]">
        <div>
          <label className="mb-2 block text-sm font-semibold text-black">Current Password</label>
          <input
            type="password"
            value={formData.currentPassword}
            onChange={(event) => onFieldChange('currentPassword', event.target.value)}
            className="w-full rounded-md border border-zinc-400 bg-white px-3 py-2 text-sm outline-none focus:border-orange-300 focus:ring-2 focus:ring-orange-100"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-semibold text-black">New Password</label>
          <input
            type="password"
            value={formData.newPassword}
            onChange={(event) => onFieldChange('newPassword', event.target.value)}
            className="w-full rounded-md border border-zinc-400 bg-white px-3 py-2 text-sm outline-none focus:border-orange-300 focus:ring-2 focus:ring-orange-100"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-semibold text-black">Confirm Password</label>
          <input
            type="password"
            value={formData.confirmPassword}
            onChange={(event) => onFieldChange('confirmPassword', event.target.value)}
            className="w-full rounded-md border border-zinc-400 bg-white px-3 py-2 text-sm outline-none focus:border-orange-300 focus:ring-2 focus:ring-orange-100"
          />
        </div>
      </div>

      {errorMessage ? (
        <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
          {errorMessage}
        </p>
      ) : null}

      {successMessage ? (
        <p className="mt-4 rounded-md border border-green-200 bg-green-50 px-3 py-2 text-xs text-green-700">
          {successMessage}
        </p>
      ) : null}

      <div className="mt-8 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={onClickUpdatePassword}
          disabled={isSubmitting}
          className="rounded-md bg-orange-600 px-6 py-2 text-sm font-medium text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? 'Updating...' : 'Update Password'}
        </button>
        <button
          type="button"
          onClick={onClickCancel}
          disabled={isSubmitting}
          className="rounded-md border border-zinc-300 bg-white px-6 py-2 text-sm font-medium text-zinc-700 transition hover:bg-zinc-100"
        >
          Cancel
        </button>
      </div>
    </section>
  );
}
