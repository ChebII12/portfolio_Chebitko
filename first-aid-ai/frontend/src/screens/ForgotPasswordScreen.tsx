import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/Button';
import { TextInput } from '../components/TextInput';
import { TopAppBar } from '../components/TopAppBar';
import { AppShell, ScreenHeader, ToastMessage, ToastStack } from '../components/DesignSystem';

const GENERIC_RESET_MESSAGE = 'If an account with this email exists, reset instructions have been sent.';

export function ForgotPasswordScreen() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [canEnterCode, setCanEnterCode] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const pushToast = (message: string, tone: ToastMessage['tone'] = 'info') => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    setToasts((current) => [...current, { id, message, tone }]);
    window.setTimeout(() => setToasts((current) => current.filter((toast) => toast.id !== id)), 4000);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    setCanEnterCode(false);

    if (!email.trim()) {
      setError('Email is required');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase() }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        setError(data.detail || 'Could not request password reset');
        return;
      }
      pushToast(data.message || GENERIC_RESET_MESSAGE, 'success');
      setCanEnterCode(true);
    } catch {
      setError('Network error. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell>
      <ToastStack toasts={toasts} onDismiss={(id) => setToasts((current) => current.filter((toast) => toast.id !== id))} />
      <TopAppBar title="Password Help" showEmergencyButton={false} showBackButton onBackClick={() => navigate('/login')} />
      <main className="px-5 pb-10 pt-24">
        <ScreenHeader
          title="Reset your password"
          subtitle="Enter your account email. In local demo mode, check the backend terminal for the reset code."
          icon="lock_reset"
          centered
        />

        <form onSubmit={handleSubmit} className="mt-6 space-y-4 rounded-[1.5rem] border border-[#E1E6EF] bg-white p-4 shadow-[0_12px_28px_rgba(16,42,86,0.07)]">
          <TextInput
            label="Email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(value) => {
              setEmail(value);
              setError('');
              setCanEnterCode(false);
            }}
            error={error}
            required
          />

          {canEnterCode && (
            <Button
              type="button"
              variant="secondary"
              className="w-full"
              onClick={() => navigate('/reset-password', { state: { email: email.trim().toLowerCase() } })}
            >
              Enter Reset Code
            </Button>
          )}

          <Button type="submit" loading={isSubmitting} className="w-full">Send Reset Code</Button>
        </form>

        <p className="mt-6 text-center text-sm text-[#4D5565]">
          Remembered it?{' '}
          <button type="button" className="font-bold text-[#003E91] hover:underline" onClick={() => navigate('/login')}>Back to login</button>
        </p>
      </main>
    </AppShell>
  );
}
