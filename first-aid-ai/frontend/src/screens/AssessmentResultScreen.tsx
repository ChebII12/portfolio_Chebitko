import React, { useEffect } from 'react';
import { Button } from '../components/Button';
import { AssessmentResultScreenProps } from '../types';
import { MetricCard, SoftCard, StatusAlert } from '../components/DesignSystem';
import { AuthenticatedAppShell } from '../components/AuthenticatedAppShell';

export const AssessmentResultScreen: React.FC<AssessmentResultScreenProps> = ({
  userId: _userId,
  userName,
  level,
  explanation,
  classificationSource,
  confidence,
  onNavigateToDashboard,
  onNavigateToProfile,
  onRetakeQuestionnaire,
  onRefreshProfile,
  onLogout
}) => {
  useEffect(() => {
    onRefreshProfile?.();
    // Profile refresh is intentionally one-shot on screen entry.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getLevelData = (level: 'beginner' | 'intermediate' | 'expert') => {
    switch (level) {
      case 'beginner':
        return {
          badgeIcon: 'school',
          title: 'Your Level: Beginner',
          description: 'You are new to outdoor activities and first aid. We\'ll provide detailed, step-by-step instructions to help you feel confident in emergencies.',
          metrics: [
            { label: 'Response Time', value: '85th %', icon: 'schedule' },
            { label: 'Knowledge Base', value: 'Basic', icon: 'lightbulb' }
          ]
        };
      case 'intermediate':
        return {
          badgeIcon: 'explore',
          title: 'Your Level: Intermediate',
          description: 'You have some experience with outdoor activities and basic first aid. We\'ll offer clear guidance while providing important medical context.',
          metrics: [
            { label: 'Response Time', value: '94th %', icon: 'bolt' },
            { label: 'Logic Pattern', value: 'Clinical', icon: 'science' }
          ]
        };
      case 'expert':
        return {
          badgeIcon: 'local_hospital',
          title: 'Your Level: Expert',
          description: 'You are well-versed in emergency response and medical procedures. We\'ll provide concise instructions, focusing on critical actions.',
          metrics: [
            { label: 'Response Time', value: '98th %', icon: 'bolt' },
            { label: 'Decision Making', value: 'Advanced', icon: 'psychology' }
          ]
        };
    }
  };

  const levelData = getLevelData(level);
  const levelNumber = level === 'beginner' ? 1 : level === 'intermediate' ? 2 : 3;

  const bottomNavItems = [
    { id: 'home', label: 'Home', icon: 'home', active: false, onClick: onNavigateToDashboard },
    { id: 'history', label: 'History', icon: 'history', active: false, onClick: () => {} },
    { id: 'map', label: 'Map', icon: 'map', active: false, onClick: () => {} },
    { id: 'assessment', label: 'Assessment', icon: 'assignment_turned_in', active: true, onClick: () => {} },
    { id: 'profile', label: 'Profile', icon: 'person', active: false, onClick: onNavigateToProfile || onNavigateToDashboard }
  ];

  return (
    <AuthenticatedAppShell
      title="Assessment"
      navItems={bottomNavItems}
      showBackButton
      onBackClick={onRetakeQuestionnaire}
      actions={onLogout ? (
          <button
            type="button"
            onClick={onLogout}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full text-[#5F6878] transition-colors hover:bg-[#EAF2FF] hover:text-[#004AAD]"
            aria-label="Sign out"
          >
            <span className="material-symbols-outlined text-xl">logout</span>
          </button>
      ) : undefined}
    >

      <div>
        <section className="mb-4 rounded-[1.5rem] bg-gradient-to-br from-[#004AAD] to-[#006DE8] p-4 text-white shadow-[0_14px_32px_rgba(0,74,173,0.22)]">
          <div className="flex items-center gap-3">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-[1.1rem] bg-white/18">
              <span className="material-symbols-outlined text-[1.9rem]">{levelData.badgeIcon}</span>
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold uppercase text-white/75">Assessment Complete</p>
              <h1 className="mt-0.5 font-headline text-2xl font-extrabold leading-tight">{levelData.title}</h1>
              <p className="mt-1 truncate text-xs font-bold uppercase text-white/75">{userName}</p>
            </div>
            <span className="rounded-full bg-white/18 px-2.5 py-1 text-xs font-extrabold">Level {levelNumber}</span>
          </div>
          <p className="mt-4 text-sm font-medium leading-6 text-white/86">{levelData.description}</p>
        </section>

        {explanation && (
          <div className="mb-4"><StatusAlert tone="info">{explanation}</StatusAlert></div>
        )}

        {(classificationSource || typeof confidence === 'number') && (
          <div className="mb-4 flex flex-wrap gap-2 text-xs font-bold uppercase text-[#687386]">
            {classificationSource && (
              <span className="rounded-full bg-white px-3 py-2 shadow-sm">
                Source: {classificationSource.replace(/_/g, ' ')}
              </span>
            )}
            {typeof confidence === 'number' && (
              <span className="rounded-full bg-white px-3 py-2 shadow-sm">
                Confidence: {Math.round(confidence * 100)}%
              </span>
            )}
          </div>
        )}

        <div className="mb-4 grid grid-cols-2 gap-3">
          {levelData.metrics.map((metric, index) => (
            <MetricCard key={index} icon={metric.icon} label={metric.label} value={metric.value} />
          ))}
        </div>

        <SoftCard className="p-4">
          <h2 className="font-headline text-lg font-extrabold text-[#102A56]">Next Steps</h2>
          <p className="mt-1 text-sm font-medium leading-6 text-[#5F6878]">
            Continue to the dashboard or retake the questionnaire if the level does not feel accurate.
          </p>
        </SoftCard>

        <div className="mt-4 space-y-3">
          <Button
            onClick={onNavigateToDashboard}
            className="w-full"
          >
            Go to Dashboard
            <span className="material-symbols-outlined">arrow_forward</span>
          </Button>

          <Button
            variant="secondary"
            onClick={onRetakeQuestionnaire}
            className="w-full"
          >
            <span className="material-symbols-outlined">refresh</span>
            Retake Assessment
          </Button>
        </div>
      </div>
    </AuthenticatedAppShell>
  );
};
