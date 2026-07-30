import React, { useState } from 'react';

export function AppShell({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className="min-h-screen bg-[#eef2f7] px-0 sm:px-6 sm:py-6">
      <div className={`relative mx-auto min-h-screen w-full max-w-[430px] overflow-hidden bg-[#F7F8FB] shadow-[0_24px_70px_rgba(16,42,86,0.14)] sm:rounded-[2.25rem] ${className}`}>
        {children}
      </div>
    </div>
  );
}

export function BrandMark({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizes = {
    sm: 'h-9 w-9 text-xl',
    md: 'h-12 w-12 text-2xl',
    lg: 'h-20 w-20 text-4xl',
  };

  return (
    <div className={`${sizes[size]} inline-flex items-center justify-center rounded-[1.35rem] bg-[#EAF2FF] text-[#004AAD] shadow-[0_12px_30px_rgba(0,74,173,0.12)]`}>
      <span className="material-symbols-outlined">medical_services</span>
    </div>
  );
}

export function ScreenHeader({
  title,
  subtitle,
  icon = 'shield_with_heart',
  centered = false,
}: {
  title: string;
  subtitle?: string;
  icon?: string;
  centered?: boolean;
}) {
  return (
    <section className={`${centered ? 'text-center' : ''}`}>
      <div className={`${centered ? 'mx-auto' : ''} mb-4 flex h-16 w-16 items-center justify-center rounded-[1.25rem] bg-[#EAF2FF] text-[#004AAD] shadow-[0_10px_24px_rgba(16,42,86,0.07)]`}>
        <span className="material-symbols-outlined text-[2rem]">{icon}</span>
      </div>
      <h1 className="font-headline text-3xl font-extrabold leading-tight text-[#102A56]">
        {title}
      </h1>
      {subtitle && (
        <p className="mt-3 text-sm font-medium leading-6 text-[#5F6878]">
          {subtitle}
        </p>
      )}
    </section>
  );
}

export function StatusAlert({
  tone = 'info',
  children,
}: {
  tone?: 'info' | 'error' | 'success' | 'warning';
  children: React.ReactNode;
}) {
  const styles = {
    info: 'border-[#C9D8F5] bg-[#EAF2FF] text-[#0B3A7D]',
    error: 'border-red-200 bg-red-50 text-red-700',
    success: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    warning: 'border-amber-200 bg-amber-50 text-amber-800',
  };

  return (
    <div className={`rounded-[1rem] border px-3 py-2.5 text-sm font-semibold leading-5 ${styles[tone]}`} role={tone === 'error' ? 'alert' : 'status'}>
      {children}
    </div>
  );
}

export type ToastMessage = {
  id: string;
  tone?: 'info' | 'error' | 'success' | 'warning';
  message: string;
};

export function ToastStack({ toasts, onDismiss }: { toasts: ToastMessage[]; onDismiss: (id: string) => void }) {
  const styles = {
    info: 'border-[#C9D8F5] bg-[#EAF2FF] text-[#0B3A7D]',
    error: 'border-red-200 bg-red-50 text-red-700',
    success: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    warning: 'border-amber-200 bg-amber-50 text-amber-800',
  };

  return (
    <div className="pointer-events-none absolute inset-x-4 top-24 z-[80] space-y-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto flex items-start gap-3 rounded-[1.25rem] border px-4 py-3 text-sm font-semibold leading-6 shadow-[0_16px_34px_rgba(16,42,86,0.12)] ${styles[toast.tone || 'info']}`}
          role={toast.tone === 'error' ? 'alert' : 'status'}
        >
          <span className="material-symbols-outlined text-xl">
            {toast.tone === 'success' ? 'check_circle' : toast.tone === 'error' ? 'error' : toast.tone === 'warning' ? 'warning' : 'info'}
          </span>
          <span className="min-w-0 flex-1">{toast.message}</span>
          <button
            type="button"
            onClick={() => onDismiss(toast.id)}
            className="-mr-1 rounded-full p-1 hover:bg-white/50"
            aria-label="Dismiss notification"
          >
            <span className="material-symbols-outlined text-base">close</span>
          </button>
        </div>
      ))}
    </div>
  );
}

export function InlineAlert({
  tone = 'info',
  title,
  children,
  collapsible = false,
}: {
  tone?: 'info' | 'error' | 'success' | 'warning';
  title: string;
  children?: React.ReactNode;
  collapsible?: boolean;
}) {
  const [open, setOpen] = useState(!collapsible);
  const styles = {
    info: 'border-[#C9D8F5] bg-[#EAF2FF] text-[#0B3A7D]',
    error: 'border-red-200 bg-red-50 text-red-700',
    success: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    warning: 'border-amber-200 bg-amber-50 text-amber-800',
  };

  return (
    <div className={`rounded-[1rem] border px-3 py-2.5 text-sm font-semibold leading-5 ${styles[tone]}`}>
      <button
        type="button"
        className="flex w-full items-center justify-between gap-3 text-left"
        onClick={() => collapsible && setOpen((current) => !current)}
      >
        <span className="min-w-0">{title}</span>
        {collapsible && <span className="material-symbols-outlined text-lg">{open ? 'expand_less' : 'expand_more'}</span>}
      </button>
      {open && children && <div className="mt-2 text-xs font-medium leading-5 opacity-90">{children}</div>}
    </div>
  );
}

export function ConfirmModal({
  open,
  title,
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  danger = false,
  onConfirm,
  onCancel,
}: {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  if (!open) return null;

  return (
    <div className="absolute inset-0 z-[90] flex items-center justify-center bg-[#0B1F3A]/35 px-5 backdrop-blur-sm" role="dialog" aria-modal="true">
      <div className="w-full rounded-[1.5rem] bg-white p-4 shadow-[0_20px_48px_rgba(16,42,86,0.22)]">
        <h2 className="font-headline text-xl font-extrabold text-[#102A56]">{title}</h2>
        <p className="mt-2 text-sm font-medium leading-6 text-[#5F6878]">{description}</p>
        <div className="mt-5 grid grid-cols-2 gap-3">
          <button type="button" onClick={onCancel} className="h-12 rounded-full border border-[#D7DEEA] font-bold text-[#102A56]">
            {cancelLabel}
          </button>
          <button type="button" onClick={onConfirm} className={`h-12 rounded-full font-bold text-white ${danger ? 'bg-[#A50022]' : 'bg-[#0057D9]'}`}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export function AccordionSection({
  title,
  subtitle,
  icon,
  meta,
  defaultOpen = false,
  children,
}: {
  title: string;
  subtitle?: string;
  icon: string;
  meta?: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="overflow-hidden rounded-[1.15rem] border border-[#E1E6EF] bg-[#F9FBFE]">
      <button type="button" onClick={() => setOpen((current) => !current)} className="flex min-h-[58px] w-full items-center gap-3 px-3 py-2.5 text-left">
        <span className="material-symbols-outlined flex h-10 w-10 items-center justify-center rounded-[1rem] bg-[#EAF2FF] text-[1.35rem] text-[#004AAD]">{icon}</span>
        <span className="min-w-0 flex-1">
          <span className="block font-headline text-[0.95rem] font-extrabold leading-5 text-[#102A56]">{title}</span>
          {subtitle && <span className="mt-0.5 block truncate text-xs font-semibold text-[#5F6878]">{subtitle}</span>}
        </span>
        {meta && <span className="shrink-0 rounded-full bg-white px-2 py-1 text-xs font-extrabold text-[#004AAD]">{meta}</span>}
        <span className="material-symbols-outlined text-[#5F6878]">{open ? 'expand_less' : 'expand_more'}</span>
      </button>
      {open && <div className="space-y-3 border-t border-[#E1E6EF] bg-white p-3.5">{children}</div>}
    </div>
  );
}

export function SoftCard({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`rounded-[1.5rem] border border-[#E1E6EF] bg-white shadow-[0_12px_28px_rgba(16,42,86,0.07)] ${className}`}>
      {children}
    </div>
  );
}

export function FeatureCard({
  title,
  subtitle,
  icon,
  tone = 'light',
  disabled = false,
}: {
  title: string;
  subtitle: string;
  icon: string;
  tone?: 'red' | 'blue' | 'orange' | 'light';
  disabled?: boolean;
}) {
  const toneClasses = {
    red: 'bg-gradient-to-br from-[#A50022] to-[#C91136] text-white shadow-[0_14px_30px_rgba(165,0,34,0.20)]',
    blue: 'bg-gradient-to-br from-[#004AAD] to-[#0066E5] text-white shadow-[0_14px_30px_rgba(0,74,173,0.20)]',
    orange: 'bg-gradient-to-br from-[#F59E0B] to-[#F97316] text-white shadow-[0_14px_30px_rgba(245,158,11,0.18)]',
    light: 'bg-white text-[#102A56] shadow-[0_12px_28px_rgba(16,42,86,0.07)]',
  };
  const iconTone = tone === 'light' ? 'bg-[#EAF2FF] text-[#004AAD]' : 'bg-white/18 text-white';

  return (
    <button
      type="button"
      disabled={disabled}
      className={`relative flex min-h-[8rem] w-full flex-col justify-between overflow-hidden rounded-[1.5rem] p-4 text-left transition-all hover:-translate-y-0.5 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-70 ${toneClasses[tone]}`}
    >
      <div className={`flex h-11 w-11 items-center justify-center rounded-[1rem] ${iconTone}`}>
        <span className="material-symbols-outlined text-[1.55rem]">{icon}</span>
      </div>
      <div className="relative z-10">
        <h3 className="font-headline text-base font-extrabold leading-tight">{title}</h3>
        <p className={`mt-1 text-xs font-medium leading-4 ${tone === 'light' ? 'text-[#5F6878]' : 'text-white/82'}`}>{subtitle}</p>
      </div>
    </button>
  );
}

export function MetricCard({ icon, label, value }: { icon: string; label: string; value: string }) {
  return (
    <div className="rounded-[1.5rem] bg-white p-4 shadow-[0_12px_28px_rgba(16,42,86,0.07)]">
      <span className="material-symbols-outlined text-xl text-[#004AAD]">{icon}</span>
      <p className="mt-3 text-[10px] font-bold uppercase text-[#6B778A]">{label}</p>
      <p className="mt-1 font-headline text-xl font-extrabold text-[#102A56]">{value}</p>
    </div>
  );
}
