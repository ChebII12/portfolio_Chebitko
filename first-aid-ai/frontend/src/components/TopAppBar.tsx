import React from 'react';

export interface TopAppBarProps {
  title?: string;
  showBackButton?: boolean;
  onBackClick?: () => void;
  actions?: React.ReactNode;
  showEmergencyButton?: boolean;
  onEmergencyClick?: () => void;
  className?: string;
}

export const TopAppBar: React.FC<TopAppBarProps> = ({
  title,
  showBackButton = false,
  onBackClick,
  actions,
  showEmergencyButton = true,
  onEmergencyClick,
  className = ''
}) => {
  return (
    <header className={`fixed left-1/2 top-0 z-50 flex h-[calc(60px+env(safe-area-inset-top))] w-full max-w-[430px] -translate-x-1/2 items-center justify-between border-b border-[#E1E6EF]/80 bg-[#F7F8FB]/88 px-5 pt-[env(safe-area-inset-top)] shadow-[0_8px_24px_rgba(16,42,86,0.06)] backdrop-blur-xl ${className}`}>
      <div className="flex min-w-0 items-center gap-3">
        {showBackButton && (
          <button
            onClick={onBackClick}
            className="-ml-2 rounded-full p-2 text-[#004AAD] transition-colors hover:bg-[#EAF2FF]"
            aria-label="Go back"
          >
            <span className="material-symbols-outlined">arrow_back</span>
          </button>
        )}
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#0057D9] text-white shadow-sm">
            <span className="material-symbols-outlined text-lg">medical_services</span>
          </div>
          <h1 className="truncate font-headline text-lg font-extrabold text-[#102A56]">{title || 'First Aid AI'}</h1>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {actions}
        {showEmergencyButton && (
          <button
            type="button"
            onClick={onEmergencyClick}
            className="inline-flex h-9 items-center justify-center rounded-full bg-[#A50022] px-4 text-sm font-headline font-extrabold text-white shadow-[0_10px_20px_rgba(165,0,34,0.18)] transition-all duration-300 hover:bg-[#B0002A] active:scale-95"
            aria-label="Emergency SOS"
          >
            SOS
          </button>
        )}
      </div>
    </header>
  );
};
