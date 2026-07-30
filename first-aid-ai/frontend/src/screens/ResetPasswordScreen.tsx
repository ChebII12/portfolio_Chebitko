import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '../components/Button';
import { TextInput } from '../components/TextInput';
import { TopAppBar } from '../components/TopAppBar';
import { AppShell, ScreenHeader, ToastMessage, ToastStack } from '../components/DesignSystem';

export function ResetPasswordScreen() {
  const navigate = useNavigate();
  const location = useLocation();
  const initialEmail = String((location.state as { email?: string } | null)?.email || '');
  const [form, setForm] = useState({ email: initialEmail, resetCode: '', newPassword: '', confirmPassword: '' });
  const [errors, setErrors] = useState<Partial<Record<keyof typeof form, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const pushToast = (message: string, tone: ToastMessage['tone'] = 'info') => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    setToasts((current) => [...current, { id, message, tone }]);
    window.setTimeout(() => setToasts((current) => current.filter((toast) => toast.id !== id)), 4000);
  };

  const update = (key: keyof typeof form, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => ({ ...prev, [key]: undefined }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const nextErrors: Partial<Record<keyof typeof form, string>> = {};

    if (!form.email.trim()) nextErrors.email = 'Email is required.';
    if (!form.resetCode.trim()) nextErrors.resetCode = 'Reset code is required.';
    if (!form.newPassword) nextErrors.newPassword = 'New password is required.';
    else if (form.newPassword.length < 8) nextErrors.newPassword = 'Password must be at least 8 characters.';
    else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(form.newPassword)) {
      nextErrors.newPassword = 'Use uppercase, lowercase, and a number.';
    }
    if (!form.confirmPassword) nextErrors.confirmPassword = 'Confirm your new password.';
    else if (form.newPassword !== form.confirmPassword) nextErrors.confirmPassword = 'Passwords do not match.';

    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: form.email.trim().toLowerCase(),
          reset_code: form.resetCode.trim(),
          new_password: form.newPassword,
        }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        pushToast(data.detail || 'Could not reset password.', 'error');
        return;
      }
      pushToast(data.message || 'Password reset successfully.', 'success');
      window.setTimeout(() => navigate('/login'), 900);
    } catch {
      pushToast('Network error. Please try again.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell>
      <ToastStack toasts={toasts} onDismiss={(id) => setToasts((current) => current.filter((toast) => toast.id !== id))} />
      <TopAppBar title="New Password" showEmergencyButton={false} showBackButton onBackClick={() => navigate('/forgot-password')} />
      <main className="px-5 pb-10 pt-24">
        <ScreenHeader
          title="Create a new password"
          subtitle="Use the reset code from your email or, in local demo mode, from the backend terminal."
          icon="password"
          centered
        />

        <form onSubmit={handleSubmit} className="mt-6 space-y-4 rounded-[1.5rem] border border-[#E1E6EF] bg-white p-4 shadow-[0_12px_28px_rgba(16,42,86,0.07)]">
          <TextInput label="Email" type="email" placeholder="you@example.com" value={form.email} onChange={(value) => update('email', value)} error={errors.email} required />
          <TextInput label="Reset Code" placeholder="6-digit code" value={form.resetCode} onChange={(value) => update('resetCode', value)} error={errors.resetCode} required />
          <div className="relative">
            <TextInput label="New Password" type={showPassword ? 'text' : 'password'} placeholder="New password" value={form.newPassword} onChange={(value) => update('newPassword', value)} error={errors.newPassword} required />
            <button type="button" onClick={() => setShowPassword((visible) => !visible)} className="absolute right-3 top-8 p-2 text-on-surface-variant transition-colors hover:text-primary" aria-label={showPassword ? 'Hide password' : 'Show password'}>
              <span className="material-symbols-outlined">{showPassword ? 'visibility_off' : 'visibility'}</span>
            </button>
          </div>
          <TextInput label="Confirm Password" type={showPassword ? 'text' : 'password'} placeholder="Repeat new password" value={form.confirmPassword} onChange={(value) => update('confirmPassword', value)} error={errors.confirmPassword} required />

          <Button type="submit" loading={isSubmitting} className="w-full">Reset Password</Button>
        </form>
      </main>
    </AppShell>
  );
}
