import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/Button';
import { TextInput } from '../components/TextInput';
import { apiFetch } from '../utils/api';
import { AuthenticatedAppShell } from '../components/AuthenticatedAppShell';
import {
  AccordionSection,
  ConfirmModal,
  InlineAlert,
  SoftCard,
  ToastMessage,
  ToastStack,
} from '../components/DesignSystem';

interface ProfileScreenProps {
  userId: string;
  onLogout: () => void;
}

type AccountProfile = {
  user_id: string;
  name: string;
  email: string;
  level: string | null;
  email_verified: boolean;
  latest_assessment?: {
    confidence?: number;
    classification_source?: string;
    created_ts?: string;
  } | null;
};

type MedicalProfile = {
  sex: string;
  age: string;
  blood_type: string;
  allergies: string;
  chronic_illnesses: string;
  everyday_medicines: string;
  special_conditions: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  medical_notes: string;
};

type PasswordForm = {
  current: string;
  next: string;
  confirm: string;
};

type FieldErrors = Record<string, string | undefined>;

const emptyMedicalProfile: MedicalProfile = {
  sex: '',
  age: '',
  blood_type: '',
  allergies: '',
  chronic_illnesses: '',
  everyday_medicines: '',
  special_conditions: '',
  emergency_contact_name: '',
  emergency_contact_phone: '',
  medical_notes: '',
};

const medicalProfileKeys = Object.keys(emptyMedicalProfile) as Array<keyof MedicalProfile>;

function toText(value: unknown): string {
  if (value == null) return '';
  if (Array.isArray(value)) return toText(value[0]);
  return String(value);
}

function normalizeMedicalProfile(data: Record<string, unknown>): MedicalProfile {
  return medicalProfileKeys.reduce((profile, key) => {
    profile[key] = toText(data[key]);
    return profile;
  }, { ...emptyMedicalProfile });
}

function normalizeAccountProfile(data: Record<string, any>, fallbackUserId: string): AccountProfile {
  const questionnaireData = data.questionnaire_data || {};
  const latestAssessment = data.latest_assessment || {};
  const source = toText(latestAssessment.classification_source || questionnaireData.classification_source);

  return {
    user_id: toText(data.user_id || data.id || fallbackUserId),
    name: toText(data.name) || 'Traveler',
    email: toText(data.email),
    level: toText(data.level) || null,
    email_verified: Boolean(data.email_verified ?? data.is_email_verified ?? true),
    latest_assessment: source ? {
      confidence: Number(latestAssessment.confidence ?? questionnaireData.confidence ?? 0),
      classification_source: source,
      created_ts: toText(latestAssessment.created_ts),
    } : null,
  };
}

function SectionTitle({ title, subtitle, icon }: { title: string; subtitle?: string; icon: string }) {
  return (
    <div className="mb-4 flex items-start justify-between gap-3">
      <div className="min-w-0">
        <h2 className="font-headline text-lg font-extrabold text-[#102A56]">{title}</h2>
        {subtitle && <p className="mt-0.5 text-xs font-semibold leading-5 text-[#5F6878]">{subtitle}</p>}
      </div>
      <span className="material-symbols-outlined flex h-10 w-10 shrink-0 items-center justify-center rounded-[1rem] bg-[#EAF2FF] text-[1.35rem] text-[#004AAD]">
        {icon}
      </span>
    </div>
  );
}

function FieldLabel({ children }: { children: React.ReactNode }) {
  return <label className="block text-sm font-semibold text-[#30415F]">{children}</label>;
}

function TextAreaField({
  label,
  value,
  onChange,
  placeholder,
  error,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  error?: string;
}) {
  return (
    <div className="space-y-1.5">
      <FieldLabel>{label}</FieldLabel>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        rows={2}
        className="w-full resize-none rounded-[1.15rem] border border-[#D7DEEA] bg-white px-3.5 py-2.5 text-sm font-medium text-[#102A56] shadow-[0_5px_14px_rgba(15,23,42,0.05)] outline-none transition focus:border-[#0057D9] focus:ring-4 focus:ring-[#EAF2FF]"
        aria-invalid={Boolean(error)}
      />
      {error && <p className="text-sm font-semibold text-[#B0002A]">{error}</p>}
    </div>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
  error,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: Array<{ value: string; label: string }>;
  error?: string;
}) {
  return (
    <div className="space-y-1.5">
      <FieldLabel>{label}</FieldLabel>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="h-[52px] w-full rounded-[1.15rem] border border-[#D7DEEA] bg-white px-3.5 text-sm font-bold text-[#102A56] shadow-[0_5px_14px_rgba(15,23,42,0.05)] outline-none transition focus:border-[#0057D9] focus:ring-4 focus:ring-[#EAF2FF]"
        aria-invalid={Boolean(error)}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>{option.label}</option>
        ))}
      </select>
      {error && <p className="text-sm font-semibold text-[#B0002A]">{error}</p>}
    </div>
  );
}

async function passwordFetch(path: string, options: RequestInit) {
  const token = localStorage.getItem('access_token');
  return fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
}

export const ProfileScreen: React.FC<ProfileScreenProps> = ({ userId, onLogout }) => {
  const navigate = useNavigate();
  const [account, setAccount] = useState<AccountProfile | null>(null);
  const [medical, setMedical] = useState<MedicalProfile>(emptyMedicalProfile);
  const [name, setName] = useState('');
  const [passwords, setPasswords] = useState<PasswordForm>({ current: '', next: '', confirm: '' });
  const [profileErrors, setProfileErrors] = useState<FieldErrors>({});
  const [medicalErrors, setMedicalErrors] = useState<FieldErrors>({});
  const [passwordErrors, setPasswordErrors] = useState<FieldErrors>({});
  const [loading, setLoading] = useState(true);
  const [savingAccount, setSavingAccount] = useState(false);
  const [savingMedical, setSavingMedical] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);
  const [medicalUnavailable, setMedicalUnavailable] = useState('');
  const [confirmClearOpen, setConfirmClearOpen] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const pushToast = (message: string, tone: ToastMessage['tone'] = 'info') => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    setToasts((current) => [...current, { id, message, tone }]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((toast) => toast.id !== id));
    }, tone === 'success' ? 3500 : 5000);
  };

  useEffect(() => {
    const loadProfile = async () => {
      setLoading(true);
      setMedicalUnavailable('');
      try {
        const [accountResponse, medicalResponse] = await Promise.all([
          apiFetch('/api/profile/me'),
          apiFetch('/api/profile/medical'),
        ]);
        const accountData = await accountResponse.json().catch(() => ({}));
        const medicalData = await medicalResponse.json().catch(() => ({}));

        let nextAccount: AccountProfile | null = null;
        if (accountResponse.ok) {
          nextAccount = normalizeAccountProfile(accountData, userId);
        } else if (userId) {
          const legacyResponse = await apiFetch(`/api/auth/users/${userId}`);
          const legacyData = await legacyResponse.json().catch(() => ({}));
          if (legacyResponse.ok) {
            nextAccount = normalizeAccountProfile(legacyData, userId);
          } else {
            throw new Error(accountData.detail || legacyData.detail || 'Failed to load account profile');
          }
        } else {
          throw new Error(accountData.detail || 'Failed to load account profile');
        }

        setAccount(nextAccount);
        setName(nextAccount.name || '');

        if (medicalResponse.ok) {
          setMedical(normalizeMedicalProfile(medicalData));
        } else {
          setMedical(emptyMedicalProfile);
          setMedicalUnavailable('Medical profile details are unavailable until the updated backend is running.');
        }
      } catch (err) {
        pushToast(err instanceof Error ? err.message : 'Network error loading profile', 'error');
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const completion = useMemo(() => {
    const filled = medicalProfileKeys.filter((key) => medical[key].trim()).length;
    return { filled, total: medicalProfileKeys.length };
  }, [medical]);

  const sectionCompletion = useMemo(() => {
    const progress = (keys: Array<keyof MedicalProfile>) =>
      `${keys.filter((key) => medical[key].trim()).length}/${keys.length}`;

    return {
      basic: progress(['sex', 'age', 'blood_type']),
      conditions: progress(['allergies', 'chronic_illnesses', 'special_conditions']),
      medicines: progress(['everyday_medicines']),
      emergency: progress(['emergency_contact_name', 'emergency_contact_phone']),
      notes: progress(['medical_notes']),
    };
  }, [medical]);

  const latestSource = toText(account?.latest_assessment?.classification_source);
  const hasAccountNameChanged = Boolean(account && name.trim() !== account.name.trim());

  const bottomNavItems = [
    { id: 'home', label: 'Home', icon: 'home', active: false, onClick: () => navigate('/dashboard') },
    { id: 'history', label: 'History', icon: 'history', active: false, onClick: () => {} },
    { id: 'map', label: 'Map', icon: 'map', active: false, onClick: () => {} },
    { id: 'assessment', label: 'Assessment', icon: 'assignment_turned_in', active: false, onClick: () => navigate('/assessment') },
    { id: 'profile', label: 'Profile', icon: 'person', active: true, onClick: () => {} },
  ];

  const updateMedical = (key: keyof MedicalProfile, value: string) => {
    setMedical((prev) => ({ ...prev, [key]: value }));
    setMedicalErrors((prev) => ({ ...prev, [key]: undefined }));
  };

  const validateMedical = (): boolean => {
    const errors: FieldErrors = {};
    const age = medical.age.trim();
    if (age) {
      const parsedAge = Number(age);
      if (!Number.isInteger(parsedAge) || parsedAge < 0 || parsedAge > 120) {
        errors.age = 'Age must be a whole number from 0 to 120.';
      }
    }
    if (medical.emergency_contact_phone.length > 40) {
      errors.emergency_contact_phone = 'Phone number must be 40 characters or fewer.';
    }
    setMedicalErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validatePassword = (): boolean => {
    const errors: FieldErrors = {};
    if (!passwords.current) errors.current = 'Current password is required.';
    if (!passwords.next) errors.next = 'New password is required.';
    else if (passwords.next.length < 8) errors.next = 'Use at least 8 characters.';
    else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(passwords.next)) {
      errors.next = 'Use uppercase, lowercase, and a number.';
    }
    if (!passwords.confirm) errors.confirm = 'Confirm your new password.';
    else if (passwords.next !== passwords.confirm) errors.confirm = 'Passwords do not match.';
    setPasswordErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const saveAccount = async () => {
    const trimmedName = name.trim();
    if (trimmedName.length < 2) {
      setProfileErrors({ name: 'Name must be at least 2 characters.' });
      return;
    }

    setSavingAccount(true);
    setProfileErrors({});
    try {
      const response = await apiFetch('/api/profile/me', {
        method: 'PATCH',
        body: JSON.stringify({ name: trimmedName }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || 'Could not save account profile');
      const nextAccount = normalizeAccountProfile(data, userId);
      setAccount(nextAccount);
      setName(nextAccount.name || '');
      pushToast('Account information saved.', 'success');
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Could not save account profile', 'error');
    } finally {
      setSavingAccount(false);
    }
  };

  const saveMedical = async () => {
    if (!validateMedical()) return;

    setSavingMedical(true);
    const payload = {
      ...medical,
      age: medical.age.trim() ? Number(medical.age) : null,
    };
    try {
      const response = await apiFetch('/api/profile/medical', {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || 'Could not save medical profile');
      setMedical(normalizeMedicalProfile(data));
      setMedicalUnavailable('');
      pushToast('Medical profile saved.', 'success');
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Could not save medical profile', 'error');
    } finally {
      setSavingMedical(false);
    }
  };

  const clearMedical = async () => {
    setConfirmClearOpen(false);
    try {
      const response = await apiFetch('/api/profile/medical', { method: 'DELETE' });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || 'Could not clear medical profile');
      setMedical(emptyMedicalProfile);
      setMedicalErrors({});
      pushToast('Medical profile cleared.', 'success');
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Could not clear medical profile', 'error');
    }
  };

  const changePassword = async () => {
    if (!validatePassword()) return;

    setChangingPassword(true);
    try {
      const response = await passwordFetch('/api/auth/change-password', {
        method: 'POST',
        body: JSON.stringify({ current_password: passwords.current, new_password: passwords.next }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || 'Could not change password');
      setPasswords({ current: '', next: '', confirm: '' });
      setPasswordErrors({});
      pushToast('Password changed successfully.', 'success');
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Could not change password', 'error');
    } finally {
      setChangingPassword(false);
    }
  };

  return (
    <AuthenticatedAppShell title="Profile" navItems={bottomNavItems} showBackButton onBackClick={() => navigate(-1)}>
      <ToastStack toasts={toasts} onDismiss={(id) => setToasts((current) => current.filter((toast) => toast.id !== id))} />
      <ConfirmModal
        open={confirmClearOpen}
        title="Clear Medical Profile?"
        description="This removes optional medical profile fields from this demo account. Your login email and password stay unchanged."
        confirmLabel="Clear Data"
        danger
        onConfirm={clearMedical}
        onCancel={() => setConfirmClearOpen(false)}
      />
      <div>
        {loading ? (
          <div className="flex h-40 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-[#0057D9]" />
          </div>
        ) : account ? (
          <div className="space-y-4">
            <section className="flex items-center gap-3 rounded-[1.5rem] border border-[#E1E6EF] bg-white p-4 shadow-[0_10px_24px_rgba(16,42,86,0.07)]">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-[1.1rem] bg-[#EAF2FF] text-[#004AAD]">
                <span className="material-symbols-outlined text-[1.8rem]">person</span>
              </div>
              <div className="min-w-0 flex-1">
                <h1 className="truncate font-headline text-xl font-extrabold text-[#102A56]">{account.name}</h1>
                <p className="mt-0.5 truncate text-xs font-semibold text-[#5F6878]">{account.email}</p>
                <div className="mt-2 inline-flex max-w-full items-center gap-1.5 rounded-full bg-[#F7F8FB] px-2.5 py-1 text-xs font-extrabold text-[#004AAD]">
                  <span className="material-symbols-outlined text-base">military_tech</span>
                  <span className="truncate capitalize">{account.level || 'Not assessed'}</span>
                </div>
              </div>
            </section>

            <SoftCard className="p-4">
              <SectionTitle title="Account" subtitle="Basic identity for your First Aid AI account." icon="badge" />
              <div className="space-y-3">
                <TextInput
                  label="Display Name"
                  value={name}
                  onChange={(value) => {
                    setName(value);
                    setProfileErrors((prev) => ({ ...prev, name: undefined }));
                  }}
                  placeholder="Your name"
                  error={profileErrors.name}
                />
                <div className="rounded-[1.15rem] border border-[#E1E6EF] bg-[#F7F8FB] px-3.5 py-3">
                  <p className="text-sm font-semibold text-[#30415F]">Email</p>
                  <p className="mt-1 break-all text-sm font-bold text-[#102A56]">{account.email}</p>
                  <p className="mt-1 text-xs font-medium leading-5 text-[#5F6878]">
                    Used for login and recovery. Not editable in this version.
                  </p>
                </div>
                <Button size="sm" onClick={saveAccount} loading={savingAccount} disabled={!hasAccountNameChanged} className="w-full">
                  Save Account
                </Button>
              </div>
            </SoftCard>

            <SoftCard className="p-4">
              <div className="mb-4 flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h2 className="font-headline text-lg font-extrabold text-[#102A56]">Medical Profile</h2>
                  <p className="mt-0.5 text-xs font-semibold leading-5 text-[#5F6878]">Optional details stored separately from account login data.</p>
                </div>
                <span className="shrink-0 rounded-full bg-[#EAF2FF] px-2.5 py-1.5 text-xs font-extrabold text-[#004AAD]">
                  {completion.filled}/{completion.total} completed
                </span>
              </div>

              <div className="space-y-3">
                <InlineAlert title="Medical information is optional and sensitive." collapsible>
                  Medical information is optional and sensitive. It is used only to personalize first-aid guidance in this demo. Do not enter information you do not want to store.
                </InlineAlert>
                <InlineAlert title="Privacy and AI use" collapsible>
                  Medical profile data is stored separately from account login data. It is not automatically sent to the AI unless a later personalization feature explicitly uses it.
                </InlineAlert>
                {medicalUnavailable && (
                  <InlineAlert tone="warning" title="Medical profile API is not available yet." collapsible>
                    {medicalUnavailable}
                  </InlineAlert>
                )}

                <AccordionSection title="Basic Information" subtitle="Age, sex, and blood type" icon="patient_list" meta={sectionCompletion.basic} defaultOpen>
                  <SelectField
                    label="Sex"
                    value={medical.sex}
                    onChange={(value) => updateMedical('sex', value)}
                    error={medicalErrors.sex}
                    options={[
                      { value: '', label: 'Not specified' },
                      { value: 'female', label: 'Female' },
                      { value: 'male', label: 'Male' },
                      { value: 'other', label: 'Other' },
                      { value: 'prefer_not_to_say', label: 'Prefer not to say' },
                    ]}
                  />
                  <TextInput label="Age" type="number" value={medical.age} onChange={(value) => updateMedical('age', value)} placeholder="Optional" error={medicalErrors.age} />
                  <SelectField
                    label="Blood Type"
                    value={medical.blood_type}
                    onChange={(value) => updateMedical('blood_type', value)}
                    error={medicalErrors.blood_type}
                    options={[
                      { value: '', label: 'Not specified' },
                      { value: 'unknown', label: 'Unknown' },
                      { value: 'A+', label: 'A+' },
                      { value: 'A-', label: 'A-' },
                      { value: 'B+', label: 'B+' },
                      { value: 'B-', label: 'B-' },
                      { value: 'AB+', label: 'AB+' },
                      { value: 'AB-', label: 'AB-' },
                      { value: 'O+', label: 'O+' },
                      { value: 'O-', label: 'O-' },
                    ]}
                  />
                </AccordionSection>

                <AccordionSection title="Medical Conditions" subtitle="Allergies and chronic conditions" icon="health_and_safety" meta={sectionCompletion.conditions}>
                  <TextAreaField label="Allergies" value={medical.allergies} onChange={(value) => updateMedical('allergies', value)} error={medicalErrors.allergies} placeholder="Food, medicine, insect allergy..." />
                  <TextAreaField label="Chronic Illnesses" value={medical.chronic_illnesses} onChange={(value) => updateMedical('chronic_illnesses', value)} error={medicalErrors.chronic_illnesses} />
                  <TextAreaField label="Special Conditions" value={medical.special_conditions} onChange={(value) => updateMedical('special_conditions', value)} error={medicalErrors.special_conditions} />
                </AccordionSection>

                <AccordionSection title="Medicines" subtitle="Everyday medicines or supplies" icon="medication" meta={sectionCompletion.medicines}>
                  <TextAreaField label="Everyday Medicines" value={medical.everyday_medicines} onChange={(value) => updateMedical('everyday_medicines', value)} error={medicalErrors.everyday_medicines} />
                </AccordionSection>

                <AccordionSection title="Emergency Contact" subtitle="Optional contact for urgent situations" icon="contact_emergency" meta={sectionCompletion.emergency}>
                  <TextInput label="Emergency Contact Name" value={medical.emergency_contact_name} onChange={(value) => updateMedical('emergency_contact_name', value)} error={medicalErrors.emergency_contact_name} />
                  <TextInput label="Emergency Contact Phone" value={medical.emergency_contact_phone} onChange={(value) => updateMedical('emergency_contact_phone', value)} error={medicalErrors.emergency_contact_phone} />
                </AccordionSection>

                <AccordionSection title="Notes" subtitle="Anything else you want to remember" icon="notes" meta={sectionCompletion.notes}>
                  <TextAreaField label="Medical Notes" value={medical.medical_notes} onChange={(value) => updateMedical('medical_notes', value)} error={medicalErrors.medical_notes} />
                </AccordionSection>

                <div className="grid grid-cols-2 gap-3">
                  <Button size="sm" onClick={saveMedical} loading={savingMedical} className="w-full">Save Medical</Button>
                  <Button size="sm" variant="outline" onClick={() => setConfirmClearOpen(true)} className="w-full text-[#A50022]">
                    <span className="material-symbols-outlined text-base">delete</span>
                    Clear Data
                  </Button>
                </div>
              </div>
            </SoftCard>

            <SoftCard className="p-4">
              <SectionTitle title="Security" subtitle="Change your signed-in account password." icon="lock" />
              <div className="space-y-3">
                <TextInput label="Current Password" type="password" value={passwords.current} onChange={(value) => setPasswords((prev) => ({ ...prev, current: value }))} error={passwordErrors.current} />
                <TextInput label="New Password" type="password" value={passwords.next} onChange={(value) => setPasswords((prev) => ({ ...prev, next: value }))} error={passwordErrors.next} />
                <TextInput label="Confirm New Password" type="password" value={passwords.confirm} onChange={(value) => setPasswords((prev) => ({ ...prev, confirm: value }))} error={passwordErrors.confirm} />
                <Button size="sm" onClick={changePassword} loading={changingPassword} className="w-full">Change Password</Button>
              </div>
            </SoftCard>

            <SoftCard className="p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-[1rem] bg-[#EAF2FF] text-[#004AAD]">
                  <span className="material-symbols-outlined text-[1.55rem]">
                    {account.level === 'expert' ? 'local_hospital' : account.level === 'intermediate' ? 'explore' : 'school'}
                  </span>
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-bold uppercase text-[#5F6878]">Assessment</p>
                  <h3 className="font-headline text-xl font-extrabold capitalize text-[#102A56]">{account.level || 'Not assessed'}</h3>
                  {latestSource && <p className="mt-0.5 truncate text-xs font-bold uppercase text-[#7A8494]">{latestSource.replace(/_/g, ' ')}</p>}
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <Button size="sm" variant="secondary" onClick={() => navigate('/questionnaire')} className="w-full">
                  <span className="material-symbols-outlined text-base">refresh</span>
                  Retake
                </Button>
                <Button size="sm" variant="outline" onClick={() => navigate('/assessment')} className="w-full">
                  <span className="material-symbols-outlined text-base">military_tech</span>
                  Result
                </Button>
              </div>
            </SoftCard>

            <button
              type="button"
              onClick={onLogout}
              className="flex w-full items-center justify-between rounded-[1.25rem] bg-red-50 px-4 py-3 font-bold text-[#A50022] transition hover:bg-red-100"
            >
              <span className="inline-flex items-center gap-3">
                <span className="material-symbols-outlined">logout</span>
                Sign Out
              </span>
              <span className="material-symbols-outlined">chevron_right</span>
            </button>
          </div>
        ) : (
          <InlineAlert tone="error" title="Profile could not be loaded." collapsible>
            Please sign out, sign in again, and reopen Profile.
          </InlineAlert>
        )}
      </div>
    </AuthenticatedAppShell>
  );
};
