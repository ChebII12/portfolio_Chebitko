import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/Button';
import { TextInput } from '../components/TextInput';
import { TopAppBar } from '../components/TopAppBar';
import { RegistrationScreenProps, RegistrationForm } from '../types';
import { AppShell, ScreenHeader, StatusAlert } from '../components/DesignSystem';

const PENDING_VERIFICATION_EMAIL_KEY = 'module1-pending-verification-email';

export const RegistrationScreen: React.FC<RegistrationScreenProps> = ({
  onSuccess,
  onError
}) => {
  const navigate = useNavigate();
  const [form, setForm] = useState<RegistrationForm>({
    name: '',
    email: '',
    password: ''
  });

  const [errors, setErrors] = useState<Partial<RegistrationForm>>({});
  const [submitError, setSubmitError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const applyBackendError = (message: string) => {
    const normalized = message.toLowerCase();
    if (normalized.includes('email')) {
      setErrors((prev) => ({ ...prev, email: message }));
      return;
    }
    if (normalized.includes('password')) {
      setErrors((prev) => ({ ...prev, password: message }));
      return;
    }
    if (normalized.includes('name')) {
      setErrors((prev) => ({ ...prev, name: message }));
      return;
    }
    setSubmitError(message);
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<RegistrationForm> = {};
    setSubmitError('');

    if (!form.name.trim()) newErrors.name = 'Name is required';
    if (!form.email.trim()) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(form.email)) newErrors.email = 'Invalid email format';
    if (!form.password) newErrors.password = 'Password is required';
    else if (form.password.length < 8) newErrors.password = 'Password must be at least 8 characters';
    else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(form.password)) {
      newErrors.password = 'Password must contain uppercase, lowercase, and number';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsSubmitting(true);

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.name,
          email: form.email,
          password: form.password
        })
      });

      const data = await response.json();

      if (response.ok) {
        if (data.requires_verification) {
          try {
            localStorage.setItem(PENDING_VERIFICATION_EMAIL_KEY, form.email.trim().toLowerCase());
          } catch {}
          navigate('/verify-email', {
            state: {
              email: form.email,
              devVerificationCode: data.dev_verification_code || '',
            },
          });
        } else {
          // Fallback just in case
          const token = String(data.access_token || '');
          if (token) {
            try {
              localStorage.setItem('access_token', token);
            } catch {}
          }
          onSuccess({
            userId: data.user_id || data.user || '',
            name: data.name || form.name.trim(),
            token,
            level: data.level || 'beginner'
          });
        }
      } else {
        const message = data.detail || data.error?.message || 'Registration failed';
        if (response.status === 503 && String(message).toLowerCase().includes('verification email')) {
          try {
            localStorage.setItem(PENDING_VERIFICATION_EMAIL_KEY, form.email.trim().toLowerCase());
          } catch {}
          navigate('/verify-email', {
            state: {
              email: form.email.trim().toLowerCase(),
              notice: 'The account was created, but the email could not be sent. Use Resend Code or ask the backend to run in console email mode.',
            },
          });
          return;
        }
        applyBackendError(String(message));
        onError(String(message));
      }
    } catch (error) {
      const message = 'Network error. Please try again.';
      setSubmitError(message);
      onError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell>
      <TopAppBar title="First Aid AI" showEmergencyButton={false} />

      <main className="px-5 pb-10 pt-24">
        <ScreenHeader
          title="Welcome to First Aid AI"
          subtitle="Your clinical companion for immediate medical guidance and travel safety."
          icon="shield_with_heart"
        />

        <form onSubmit={handleSubmit} className="mt-6 space-y-4 rounded-[1.5rem] border border-[#E1E6EF] bg-white p-4 shadow-[0_12px_28px_rgba(16,42,86,0.07)]">
          <StatusAlert>
            Create your account, then verify your email before the medical profile questionnaire.
          </StatusAlert>

          <TextInput
            label="Full Name"
            placeholder="John Doe"
            value={form.name}
            onChange={(value) => {
              setForm(prev => ({ ...prev, name: value }));
              setErrors(prev => ({ ...prev, name: undefined }));
              setSubmitError('');
            }}
            error={errors.name}
            required
          />

          <TextInput
            label="Email Address"
            type="email"
            placeholder="name@example.com"
            value={form.email}
            onChange={(value) => {
              setForm(prev => ({ ...prev, email: value }));
              setErrors(prev => ({ ...prev, email: undefined }));
              setSubmitError('');
            }}
            error={errors.email}
            required
          />

          <div className="relative">
            <TextInput
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Create a secure password"
              value={form.password}
              onChange={(value) => {
                setForm(prev => ({ ...prev, password: value }));
                setErrors(prev => ({ ...prev, password: undefined }));
                setSubmitError('');
              }}
              error={errors.password}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-8 p-2 text-on-surface-variant hover:text-primary transition-colors"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              <span className="material-symbols-outlined">
                {showPassword ? 'visibility_off' : 'visibility'}
              </span>
            </button>
          </div>

          {submitError && (
            <StatusAlert tone="error">{submitError}</StatusAlert>
          )}

          <Button
            type="submit"
            loading={isSubmitting}
            className="w-full shadow-md"
          >
            Create Account
            <span className="material-symbols-outlined">arrow_forward</span>
          </Button>
        </form>

          <p className="mt-6 text-center text-sm text-[#4D5565]">
            Already have an account?{' '}
            <button
              type="button"
              className="font-bold text-[#003E91] hover:underline"
              onClick={() => navigate('/login')}
            >
              Log In
            </button>
          </p>
      </main>
    </AppShell>
  );
};
