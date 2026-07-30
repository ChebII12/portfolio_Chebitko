import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Button } from '../components/Button';
import { TextInput } from '../components/TextInput';
import { TopAppBar } from '../components/TopAppBar';
import { AuthSession } from '../types';
import { AppShell, ScreenHeader, StatusAlert } from '../components/DesignSystem';

const PENDING_VERIFICATION_EMAIL_KEY = 'module1-pending-verification-email';

interface VerificationScreenProps {
  onSuccess: (session: AuthSession) => void;
  onError: (error: string) => void;
}

export const VerificationScreen: React.FC<VerificationScreenProps> = ({ onSuccess, onError }) => {
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [message, setMessage] = useState('');
  const [devVerificationCode, setDevVerificationCode] = useState('');
  const hasDemoCode = Boolean(devVerificationCode);

  useEffect(() => {
    // Attempt to get email from location state
    const state = location.state as { email?: string; devVerificationCode?: string; notice?: string };
    if (state?.email) {
      const normalizedEmail = state.email.trim().toLowerCase();
      setEmail(normalizedEmail);
      setDevVerificationCode(state.devVerificationCode || '');
      setMessage(state.notice || '');
      try {
        localStorage.setItem(PENDING_VERIFICATION_EMAIL_KEY, normalizedEmail);
      } catch {}
    } else {
      try {
        const storedEmail = localStorage.getItem(PENDING_VERIFICATION_EMAIL_KEY);
        if (storedEmail) {
          setEmail(storedEmail);
          return;
        }
      } catch {}
      setSubmitError('Enter your email and use Resend Code to continue verification.');
    }
  }, [location]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code || code.length < 6) {
      setSubmitError('Please enter the 6-digit code');
      return;
    }

    setIsSubmitting(true);
    setSubmitError('');
    setMessage('');

    try {
      const response = await fetch('/api/auth/verify-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code })
      });

      const data = await response.json();

      if (response.ok) {
        try {
          localStorage.removeItem(PENDING_VERIFICATION_EMAIL_KEY);
        } catch {}
        const token = String(data.access_token || '');
        if (token) {
          try {
            localStorage.setItem('access_token', token);
          } catch {}
        }
        onSuccess({
          userId: data.user_id || data.user || '',
          name: data.name || '',
          token,
          level: data.level || 'beginner'
        });
      } else {
        const msg = data.detail || data.error?.message || 'Verification failed';
        setSubmitError(String(msg));
        onError(String(msg));
      }
    } catch (error) {
      const msg = 'Network error. Please try again.';
      setSubmitError(msg);
      onError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResend = async () => {
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      setSubmitError('Enter a valid email address before requesting a new code.');
      return;
    }

    setIsResending(true);
    setSubmitError('');
    setMessage('');

    try {
      const response = await fetch('/api/auth/resend-verification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.dev_verification_code ? 'A new code was generated. Use the demo code shown above, or check the inbox if email delivery succeeds.' : 'A new code has been sent to your email.');
        setDevVerificationCode(data.dev_verification_code || '');
        try {
          localStorage.setItem(PENDING_VERIFICATION_EMAIL_KEY, email.trim().toLowerCase());
        } catch {}
      } else {
        setSubmitError(data.detail || 'Verification email could not be sent. Please try again or contact support.');
      }
    } catch (error) {
      setSubmitError('Network error. Please try again.');
    } finally {
      setIsResending(false);
    }
  };

  return (
    <AppShell>
      <TopAppBar title="Verify Email" showEmergencyButton={false} />

      <main className="px-5 pb-10 pt-24">
        <ScreenHeader
          title="Verify your email"
          subtitle={`Enter the 6-digit verification code for ${email || 'your email'}.`}
          icon="mark_email_read"
          centered
        />

        <form onSubmit={handleSubmit} className="mt-6 space-y-4 rounded-[1.5rem] border border-[#E1E6EF] bg-white p-4 shadow-[0_12px_28px_rgba(16,42,86,0.07)]">
          <StatusAlert tone={hasDemoCode ? 'warning' : 'info'}>
            {hasDemoCode
              ? 'Demo verification is enabled. Email delivery may still be attempted, but you can use the code below if the inbox does not receive it.'
              : 'Check your email for the verification code. In local demo mode, the backend terminal may also show the code.'}
          </StatusAlert>

          {!email && (
            <TextInput
              label="Email Address"
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(value) => {
                setEmail(value.trim().toLowerCase());
                setSubmitError('');
                setMessage('');
              }}
              required
            />
          )}

          {hasDemoCode && (
            <div className="rounded-[1.25rem] border border-emerald-200 bg-emerald-50 p-3 text-emerald-800" role="status">
              <p className="text-xs font-bold uppercase tracking-[0.08em]">Local demo code</p>
              <div className="mt-2 flex items-center justify-between gap-3">
                <span className="font-headline text-3xl font-extrabold tracking-[0.18em] text-emerald-900">
                  {devVerificationCode}
                </span>
                <button
                  type="button"
                  onClick={() => {
                    setCode(devVerificationCode);
                    setSubmitError('');
                    setMessage('Demo code added. Press Verify Account to continue.');
                  }}
                  className="shrink-0 rounded-full bg-white px-4 py-2 text-sm font-extrabold text-emerald-800 shadow-sm transition hover:bg-emerald-100 focus:outline-none focus:ring-2 focus:ring-emerald-400"
                >
                  Use code
                </button>
              </div>
              <p className="mt-2 text-xs font-semibold leading-5">
                This is visible only because the backend is running in development/demo mode.
              </p>
            </div>
          )}

          <TextInput
            label="Verification Code"
            type="text"
            placeholder="123456"
            value={code}
            onChange={(value) => {
              setCode(value);
              setSubmitError('');
              setMessage('');
            }}
            required
          />

          {submitError && (
            <StatusAlert tone="error">{submitError}</StatusAlert>
          )}

          {message && (
            <StatusAlert tone="success">{message}</StatusAlert>
          )}

          <Button
            type="submit"
            loading={isSubmitting}
            disabled={!email}
            className="w-full"
          >
            Verify Account
            <span className="material-symbols-outlined">check_circle</span>
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="mb-3 text-sm text-[#5F6878]">Didn't receive the code?</p>
          <Button
            variant="secondary"
            onClick={handleResend}
            loading={isResending}
            className="w-full"
          >
            Resend Code
            <span className="material-symbols-outlined">refresh</span>
          </Button>
        </div>
      </main>
    </AppShell>
  );
};
