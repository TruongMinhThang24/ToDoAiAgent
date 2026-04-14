'use client';

import { useMemo, useState } from 'react';
import AccountInfoForm from '@/features/user/components/AccountInfoForm';
import ChangePasswordForm from '@/features/user/components/ChangePasswordForm';
import apiClient from '@/lib/service/apiClient';

const VIEW_MODES = {
  INFO_VIEW: 'info_view',
  INFO_EDIT: 'info_edit',
  CHANGE_PASSWORD: 'change_password',
};

const INITIAL_PROFILE_FORM = {
  firstName: 'Sundar',
  lastName: 'Gurung',
  email: 'sundargurung360@gmail.com',
  contactNumber: '+977-9800000000',
  position: 'Frontend Developer',
};

const INITIAL_PASSWORD_FORM = {
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
};

export default function ProfilePage() {
  const [viewMode, setViewMode] = useState(VIEW_MODES.INFO_VIEW);
  const [profileForm, setProfileForm] = useState(INITIAL_PROFILE_FORM);
  const [passwordForm, setPasswordForm] = useState(INITIAL_PASSWORD_FORM);
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [isUpdatingPassword, setIsUpdatingPassword] = useState(false);

  const pageTitle = useMemo(() => {
    if (viewMode === VIEW_MODES.CHANGE_PASSWORD) {
      return 'Change Password';
    }
    return 'Account Information';
  }, [viewMode]);

  const handleGoBack = () => {
    setViewMode(VIEW_MODES.INFO_VIEW);
  };

  const handleProfileFieldChange = (field, value) => {
    setProfileForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const handlePasswordFieldChange = (field, value) => {
    setPasswordForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const handleOpenInfoEdit = () => {
    setViewMode(VIEW_MODES.INFO_EDIT);
  };

  const handleOpenChangePassword = () => {
    setPasswordError('');
    setPasswordSuccess('');
    setViewMode(VIEW_MODES.CHANGE_PASSWORD);
  };

  const handleSaveChanges = () => {
    console.log('Save profile info (dummy):', profileForm);
    setViewMode(VIEW_MODES.INFO_VIEW);
  };

  const handleUpdatePassword = async () => {
    const currentPassword = passwordForm.currentPassword.trim();
    const newPassword = passwordForm.newPassword.trim();
    const confirmPassword = passwordForm.confirmPassword.trim();

    setPasswordError('');
    setPasswordSuccess('');

    if (!currentPassword || !newPassword || !confirmPassword) {
      setPasswordError('Vui lòng nhập đầy đủ thông tin mật khẩu.');
      return;
    }

    if (newPassword.length < 6) {
      setPasswordError('Mật khẩu mới phải có ít nhất 6 ký tự.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError('Mật khẩu xác nhận không khớp.');
      return;
    }

    try {
      setIsUpdatingPassword(true);

      // Gửi payload camelCase theo frontend contract.
      await apiClient.put('/user/change_password', {
        currentPassword,
        newPassword,
      });

      setPasswordSuccess('Đổi mật khẩu thành công. Vui lòng đăng nhập lại nếu cần.');
      setPasswordForm(INITIAL_PASSWORD_FORM);
      setViewMode(VIEW_MODES.INFO_VIEW);
    } catch (error) {
      const message =
        error?.response?.data?.detail
        || error?.response?.data?.message
        || error?.message
        || 'Đổi mật khẩu thất bại. Vui lòng thử lại.';
      setPasswordError(message);
    } finally {
      setIsUpdatingPassword(false);
    }
  };

  return (
    <div className="min-h-full">
      <section className="rounded-2xl border border-zinc-400/60 bg-stone-50 p-6 shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]">
        <div className="mb-6 flex items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold text-black">{pageTitle}</h2>
            <div className="mt-2 h-[2px] w-24 bg-orange-600" />
          </div>

          <button
            type="button"
            onClick={handleGoBack}
            className="text-sm font-semibold underline text-black"
          >
            Go Back
          </button>
        </div>

        <div className="mb-8 flex flex-wrap items-center gap-4">
          <img
            className="h-24 w-24 rounded-full object-cover"
            src="https://placehold.co/100x100"
            alt="Profile avatar"
          />
          <div>
            <p className="text-xl font-semibold text-black">Sundar Gurung</p>
            <p className="text-base text-black">sundargurung360@gmail.com</p>
          </div>
        </div>

        {viewMode === VIEW_MODES.CHANGE_PASSWORD ? (
          <ChangePasswordForm
            formData={passwordForm}
            onFieldChange={handlePasswordFieldChange}
            onClickUpdatePassword={handleUpdatePassword}
            onClickCancel={handleGoBack}
            isSubmitting={isUpdatingPassword}
            errorMessage={passwordError}
            successMessage={passwordSuccess}
          />
        ) : (
          <AccountInfoForm
            formData={profileForm}
            isEditing={viewMode === VIEW_MODES.INFO_EDIT}
            onFieldChange={handleProfileFieldChange}
            onClickUpdateInfo={handleOpenInfoEdit}
            onClickChangePassword={handleOpenChangePassword}
            onClickSaveChanges={handleSaveChanges}
            onClickCancel={handleGoBack}
          />
        )}
      </section>
    </div>
  );
}
