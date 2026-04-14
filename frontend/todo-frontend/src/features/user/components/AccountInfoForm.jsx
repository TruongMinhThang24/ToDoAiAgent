'use client';

export default function AccountInfoForm({
  formData,
  isEditing,
  onFieldChange,
  onClickUpdateInfo,
  onClickChangePassword,
  onClickSaveChanges,
  onClickCancel,
}) {
  const inputClass = `w-full rounded-md border border-zinc-400 bg-white px-3 py-2 text-sm outline-none ${
    isEditing ? 'focus:border-orange-300 focus:ring-2 focus:ring-orange-100' : 'text-zinc-700'
  }`;

  return (
    <section className="rounded-xl border border-zinc-400 p-6">
      <div className="grid grid-cols-1 gap-5 max-w-[520px]">
        <div>
          <label className="mb-2 block text-sm font-semibold text-black">First Name</label>
          <input
            value={formData.firstName}
            onChange={(event) => onFieldChange('firstName', event.target.value)}
            readOnly={!isEditing}
            disabled={!isEditing}
            className={inputClass}
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-semibold text-black">Last Name</label>
          <input
            value={formData.lastName}
            onChange={(event) => onFieldChange('lastName', event.target.value)}
            readOnly={!isEditing}
            disabled={!isEditing}
            className={inputClass}
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-semibold text-black">Email Address</label>
          <input
            value={formData.email}
            onChange={(event) => onFieldChange('email', event.target.value)}
            readOnly={!isEditing}
            disabled={!isEditing}
            className={inputClass}
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-semibold text-black">Contact Number</label>
          <input
            value={formData.contactNumber}
            onChange={(event) => onFieldChange('contactNumber', event.target.value)}
            readOnly={!isEditing}
            disabled={!isEditing}
            className={inputClass}
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-semibold text-black">Position</label>
          <input
            value={formData.position}
            onChange={(event) => onFieldChange('position', event.target.value)}
            readOnly={!isEditing}
            disabled={!isEditing}
            className={inputClass}
          />
        </div>
      </div>

      <div className="mt-8 flex flex-wrap items-center gap-3">
        {isEditing ? (
          <>
            <button
              type="button"
              onClick={onClickSaveChanges}
              className="rounded-md bg-orange-600 px-6 py-2 text-sm font-medium text-white transition hover:bg-orange-700"
            >
              Save Changes
            </button>
            <button
              type="button"
              onClick={onClickCancel}
              className="rounded-md border border-zinc-300 bg-white px-6 py-2 text-sm font-medium text-zinc-700 transition hover:bg-zinc-100"
            >
              Cancel
            </button>
          </>
        ) : (
          <>
            <button
              type="button"
              onClick={onClickUpdateInfo}
              className="rounded-md bg-orange-600 px-6 py-2 text-sm font-medium text-white transition hover:bg-orange-700"
            >
              Update Info
            </button>
            <button
              type="button"
              onClick={onClickChangePassword}
              className="rounded-md border border-orange-600 bg-white px-6 py-2 text-sm font-medium text-orange-600 transition hover:bg-orange-50"
            >
              Change Password
            </button>
          </>
        )}
      </div>
    </section>
  );
}
