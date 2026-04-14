'use client';

import { X, ChevronDown } from 'lucide-react';

const defaultMembers = [
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
];

export default function InviteModal({
  isOpen,
  onClose,
  inviteEmail,
  onInviteEmailChange,
  onSendInvite,
  members = defaultMembers,
  onMemberRoleChange,
  projectLink,
  onCopyLink,
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="w-full max-w-[620px] rounded-2xl border border-gray-100 bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
          <h3 className="text-sm font-semibold text-gray-900">Send an invite to a new member</h3>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center gap-1 text-xs font-medium text-gray-900 hover:text-gray-700"
          >
            Go Back
            <X className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="space-y-5 px-6 py-6">
          <div>
            <label className="mb-2 block text-xs font-medium text-gray-900">Email</label>
            <div className="flex gap-2">
              <input
                value={inviteEmail}
                onChange={(e) => onInviteEmailChange?.(e.target.value)}
                placeholder="newregurung36@gmail.com"
                className="h-9 flex-1 rounded-md border border-gray-300 px-3 text-xs text-gray-800 outline-none focus:border-orange-400"
              />
              <button
                type="button"
                onClick={() => onSendInvite?.(inviteEmail)}
                className="h-9 rounded-md bg-orange-500 px-4 text-xs font-medium text-white hover:bg-orange-600"
              >
                Send Invite
              </button>
            </div>
          </div>

          <div>
            <p className="mb-2 text-xs font-semibold text-gray-900">Members</p>
            <div className="max-h-[230px] space-y-2 overflow-auto pr-1">
              {members.map((member) => (
                <div
                  key={member.id}
                  className="grid grid-cols-[1fr_auto] items-center gap-3 rounded-lg border border-gray-100 bg-white px-2.5 py-2"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <img
                      src={member.avatar || 'https://placehold.co/32x32'}
                      alt={member.name}
                      className="h-8 w-8 rounded-full object-cover"
                    />
                    <div className="min-w-0">
                      <p className="truncate text-xs font-semibold text-gray-900">{member.name}</p>
                      <p className="truncate text-[11px] text-gray-500">{member.email}</p>
                    </div>
                  </div>

                  <div className="relative">
                    <select
                      value={member.role}
                      onChange={(e) => onMemberRoleChange?.(member.id, e.target.value)}
                      className="h-8 appearance-none rounded-md border border-gray-300 bg-white pl-2 pr-7 text-[11px] text-gray-900 outline-none"
                    >
                      <option value="can_edit">Can edit</option>
                      <option value="owner">Owner</option>
                    </select>
                    <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-gray-500" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-2 block text-xs font-medium text-gray-900">Project Link</label>
            <div className="flex gap-2">
              <input
                readOnly
                value={projectLink}
                className="h-9 flex-1 rounded-md border border-gray-300 bg-gray-50 px-3 text-xs text-gray-500 outline-none"
              />
              <button
                type="button"
                onClick={() => onCopyLink?.(projectLink)}
                className="h-9 rounded-md bg-orange-500 px-4 text-xs font-medium text-white hover:bg-orange-600"
              >
                Copy Link
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
