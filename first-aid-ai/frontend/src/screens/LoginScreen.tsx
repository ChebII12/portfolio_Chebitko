import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/Button';
import { TextInput } from '../components/TextInput';
import { TopAppBar } from '../components/TopAppBar';
import { LoginScreenProps, LoginForm } from '../types/basic';
import { AppShell, ScreenHeader, StatusAlert } from '../components/DesignSystem';

const PENDING_VERIFICATION_EMAIL_KEY = 'module1-pending-verification-email';

export const LoginScreen: React.FC<LoginScreenProps> = ({ onSuccess, onError }) => {
  const navigate = useNavigate();
  const [form, setForm] = useState<LoginForm>({ email: '', password: '' });
  const [errors, setErrors] = useState<Partial<LoginForm>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const validate = (): boolean => {
    const newErrors: Partial<LoginForm> = {};
    setSubmitError('');
    if (!form.email.trim()) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(form.email)) newErrors.email = 'Invalid email format';
    if (!form.password) newErrors.password = 'Password is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setIsSubmitting(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: form.email, password: form.password }),
      });
      const data = await res.json();
      if (res.ok) {
        const token = String(data.access_token || '');
        try {
          localStorage.setItem('access_token', token);
        } catch {}
        onSuccess({
          userId: data.user_id || '',
          name: data.name || '',
          token,
          level: data.level || 'beginner'
        });
        // let the parent handle navigation
      } else {
        const message = data.detail || data.error?.message || 'Login failed';
        if (res.status === 403 && String(message).toLowerCase().includes('verify')) {
          try {
            localStorage.setItem(PENDING_VERIFICATION_EMAIL_KEY, form.email.trim().toLowerCase());
          } catch {}
        }
        setSubmitError(String(message));
        onError(String(message));
      }
    } catch (err) {
      const message = 'Network error. Please try again.';
      setSubmitError(message);
      onError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell>
      <TopAppBar title="Sign In" showEmergencyButton={false} />

      <main className="px-5 pb-10 pt-24">
        <ScreenHeader
          title="Welcome back"
          subtitle="Sign in to continue your first aid profile and saved assessment."
          icon="shield_person"
          centered
        />

        <form onSubmit={handleSubmit} className="mt-6 space-y-4 rounded-[1.5rem] border border-[#E1E6EF] bg-white p-4 shadow-[0_12px_28px_rgba(16,42,86,0.07)]">
          <TextInput
            label="Email"
            type="email"
            placeholder="you@example.com"
            value={form.email}
            onChange={(v) => { setForm(prev => ({ ...prev, email: v })); setErrors(prev => ({ ...prev, email: undefined })); setSubmitError(''); }}
            error={errors.email}
            required
          />

          <div className="relative">
            <TextInput
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Your password"
              value={form.password}
              onChange={(v) => { setForm(prev => ({ ...prev, password: v })); setErrors(prev => ({ ...prev, password: undefined })); setSubmitError(''); }}
              error={errors.password}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword((visible) => !visible)}
              className="absolute right-3 top-8 p-2 text-on-surface-variant transition-colors hover:text-primary"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              <span className="material-symbols-outlined">
                {showPassword ? 'visibility_off' : 'visibility'}
              </span>
            </button>
          </div>

          <div className="text-right">
            <button
              type="button"
              className="text-sm font-bold text-[#003E91] hover:underline"
              onClick={() => navigate('/forgot-password', { state: { email: form.email.trim().toLowerCase() } })}
            >
              Forgot password?
            </button>
          </div>

          {submitError && (
            <StatusAlert tone="error">
              {submitError}
              {submitError.toLowerCase().includes('verify') && (
                <button
                  type="button"
                  className="mt-2 block font-bold text-primary hover:underline"
                  onClick={() => navigate('/verify-email', { state: { email: form.email.trim().toLowerCase() } })}
                >
                  Go to email verification
                </button>
              )}
            </StatusAlert>
          )}

          <Button type="submit" loading={isSubmitting} className="w-full">Sign In</Button>
        </form>

        <p className="mt-6 text-center text-sm leading-6 text-[#4D5565]">
          <span className="whitespace-nowrap">New here?</span>{' '}
          <button type="button" className="whitespace-nowrap font-bold text-[#003E91] hover:underline" onClick={() => navigate('/')}>Create Account</button>
        </p>
      </main>
    </AppShell>
  );
};

