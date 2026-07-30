import React, { useEffect, useState } from 'react';
import { MainDashboardScreenProps } from '../types';
import { FeatureCard } from '../components/DesignSystem';
import { AuthenticatedAppShell } from '../components/AuthenticatedAppShell';

export const MainDashboardScreen: React.FC<MainDashboardScreenProps> = ({
  userId: _userId,
  userName,
  userLevel: _userLevel,
  onNavigateToModule,
  onNavigateToProfile,
  onRefreshProfile,
  isOffline = false,
  onLogout
}) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const levelSummary = {
    beginner: 'Detailed step-by-step guidance is enabled for safer first aid decisions.',
    intermediate: 'Balanced guidance with practical medical context is enabled.',
    expert: 'Concise advanced guidance is enabled for rapid emergency decisions.',
  }[_userLevel || 'beginner'];

  useEffect(() => {
    onRefreshProfile?.();
    // Profile refresh is intentionally one-shot on dashboard entry.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const bottomNavItems = [
    { id: 'home', label: 'Home', icon: 'home', active: true, onClick: () => {} },
    { id: 'history', label: 'History', icon: 'history', active: false, onClick: () => {} },
    { id: 'map', label: 'Map', icon: 'map', active: false, onClick: () => {} },
    { id: 'assessment', label: 'Assessment', icon: 'assignment_turned_in', active: false, onClick: () => onNavigateToModule(1) },
    { id: 'profile', label: 'Profile', icon: 'person', active: false, onClick: onNavigateToProfile }
  ];

  return (
    <AuthenticatedAppShell title="Home" navItems={bottomNavItems}>
      <div className="space-y-5">
        {/* Mobile Home Header */}
        <div className="flex items-start justify-between gap-3">
          <button
            type="button"
            onClick={onNavigateToProfile}
            className="flex items-center gap-3 text-left"
            aria-label="Open profile"
          >
            <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-[1.1rem] border border-[#E1E6EF] bg-[#EAF2FF] shadow-sm">
              <span className="material-symbols-outlined text-primary">person</span>
            </div>
            <div className="min-w-0">
              <h1 className="font-headline text-lg font-black leading-tight text-[#102A56]">First Aid AI</h1>
              <p className="mt-0.5 max-w-[11rem] truncate text-xs font-bold text-[#004AAD]">{userName}</p>
            </div>
          </button>

          <div className="flex items-center gap-2">
            {isOffline && (
              <div className="flex items-center gap-2 rounded-full bg-surface-container px-3 py-2 shadow-sm">
                <span className="material-symbols-outlined text-sm text-primary">cloud_done</span>
                <span className="text-xs font-semibold text-on-surface-variant">OFFLINE MODE READY</span>
              </div>
            )}

            {onLogout && (
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setMenuOpen((prev) => !prev)}
                className="flex h-10 w-10 items-center justify-center rounded-[1rem] bg-[#004AAD] text-white shadow-sm transition-all hover:opacity-90 active:scale-95"
                  aria-haspopup="menu"
                  aria-expanded={menuOpen}
                  aria-label="Open account menu"
                >
                  <span className="material-symbols-outlined text-sm">account_circle</span>
                </button>

                {menuOpen && (
                  <div className="absolute right-0 top-full z-50 mt-2 w-44 overflow-hidden rounded-[1.25rem] border border-[#E1E6EF] bg-white shadow-lg">
                    <button
                      type="button"
                      onClick={() => {
                        setMenuOpen(false);
                        onNavigateToProfile();
                      }}
                      className="flex w-full items-center gap-2 px-4 py-3 text-left text-sm font-medium text-on-surface hover:bg-surface-container transition-colors"
                      role="menuitem"
                    >
                      <span className="material-symbols-outlined text-sm">person</span>
                      My Profile
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setMenuOpen(false);
                        onLogout();
                      }}
                      className="flex w-full items-center gap-2 px-4 py-3 text-left text-sm font-medium text-error hover:bg-error/5 transition-colors"
                      role="menuitem"
                    >
                      <span className="material-symbols-outlined text-sm">logout</span>
                      Logout
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <section>
          <h2 className="font-headline text-3xl font-extrabold leading-tight text-[#102A56]">
            You are in safe hands.
          </h2>
          <p className="mt-3 text-sm font-medium leading-6 text-[#5F6878]">
            Choose a medical support tool. Your guidance is personalized for your current first aid level.
          </p>
        </section>

        {/* Upcoming Features (Placeholders) */}
        <div className="space-y-3">
          <FeatureCard title="Symptom Checker" subtitle="Guided AI diagnostic interview" icon="stethoscope" tone="red" disabled />

          <div className="grid grid-cols-2 gap-3">
            <FeatureCard title="Camera Analysis" subtitle="Scan bites, rashes or wounds" icon="camera_alt" tone="orange" disabled />
            <FeatureCard title="Nearby Clinics" subtitle="Find local medical help" icon="local_hospital" tone="blue" disabled />
          </div>
        </div>

        {/* Core Status Card */}
        <section className="space-y-3">
          <div className="flex justify-between items-end px-1">
            <h2 className="font-headline text-lg font-extrabold text-[#102A56]">My Medical Profile</h2>
            <button type="button" onClick={() => onNavigateToModule(1)} className="text-xs font-bold uppercase text-primary">Retake</button>
          </div>
          <button
            onClick={() => onNavigateToModule(1)} // Module 1: Assessment
            className="w-full rounded-[1.5rem] border border-[#E1E6EF] bg-white p-4 text-left shadow-[0_12px_28px_rgba(16,42,86,0.07)] transition-all duration-300 hover:-translate-y-0.5 active:scale-[0.98]"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-[1rem] bg-[#EAF2FF]">
                <span className="material-symbols-outlined text-[1.55rem] text-primary">
                  assignment_turned_in
                </span>
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="mb-0.5 font-headline text-base font-extrabold text-[#102A56]">
                  Assessment Level
                </h3>
                <p className="text-sm font-semibold capitalize text-[#5F6878]">
                  {_userLevel || 'Not completed'}
                </p>
                <p className="mt-1 text-xs font-medium leading-5 text-[#5F6878]">
                  {levelSummary}
                </p>
              </div>
              <span className="material-symbols-outlined text-primary">
                chevron_right
              </span>
            </div>
          </button>
        </section>

        {/* Next Steps / Profile Summary */}
        <div>
          <h2 className="mb-3 font-headline text-lg font-extrabold text-[#102A56]">
            Manage Data
          </h2>

          <button
            onClick={onNavigateToProfile}
            className="w-full rounded-[1.5rem] border border-[#E1E6EF] bg-white p-4 text-left shadow-[0_12px_28px_rgba(16,42,86,0.07)] transition-all duration-300 hover:-translate-y-0.5 active:scale-[0.98]"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-[1rem] bg-[#EAF2FF]">
                <span className="material-symbols-outlined text-[1.55rem] text-primary">
                  manage_accounts
                </span>
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="mb-0.5 font-headline text-base font-extrabold text-[#102A56]">
                  View Profile
                </h3>
                <p className="text-sm text-[#5F6878]">
                  Update your personal information
                </p>
              </div>
              <span className="material-symbols-outlined text-xl text-outline">
                chevron_right
              </span>
            </div>
          </button>
        </div>
      </div>
    </AuthenticatedAppShell>
  );
};
