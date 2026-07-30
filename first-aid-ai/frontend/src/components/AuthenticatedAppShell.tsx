import React from 'react';
import { AppShell } from './DesignSystem';
import { TopAppBar } from './TopAppBar';
import { BottomNavigation, BottomNavigationItem } from './BottomNavigation';

interface AuthenticatedAppShellProps {
  title: string;
  children: React.ReactNode;
  navItems: BottomNavigationItem[];
  showBackButton?: boolean;
  onBackClick?: () => void;
  actions?: React.ReactNode;
  showEmergencyButton?: boolean;
  className?: string;
}

export function AuthenticatedAppShell({
  title,
  children,
  navItems,
  showBackButton = false,
  onBackClick,
  actions,
  showEmergencyButton = false,
  className = '',
}: AuthenticatedAppShellProps) {
  return (
    <AppShell className={className}>
      <TopAppBar
        title={title}
        showBackButton={showBackButton}
        onBackClick={onBackClick}
        showEmergencyButton={showEmergencyButton}
        actions={actions}
      />
      <main className="min-h-screen overflow-y-auto px-5 pb-[calc(96px+env(safe-area-inset-bottom))] pt-[calc(76px+env(safe-area-inset-top))]">
        {children}
      </main>
      <BottomNavigation items={navItems} />
    </AppShell>
  );
}
