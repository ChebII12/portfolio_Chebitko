import React from 'react';

export interface BottomNavigationItem {
  id: string;
  label: string;
  icon: string;
  active?: boolean;
  onClick?: () => void;
}

export interface BottomNavigationProps {
  items: BottomNavigationItem[];
  className?: string;
}

export const BottomNavigation: React.FC<BottomNavigationProps> = ({
  items,
  className = ''
}) => {
  return (
    <nav className={`fixed bottom-0 left-1/2 z-50 w-full max-w-[430px] -translate-x-1/2 px-4 pb-[calc(10px+env(safe-area-inset-bottom))] pt-2 ${className}`}>
      <div className="mx-auto rounded-[1.6rem] border border-[#E1E6EF]/80 bg-white/95 px-2 py-2 shadow-[0_-14px_30px_rgba(16,42,86,0.10)] backdrop-blur-xl">
      <div className="flex items-stretch justify-around gap-1">
        {items.map((item) => (
          <button
            key={item.id}
            onClick={item.onClick}
            className={`
              flex min-h-[52px] min-w-[58px] flex-1 flex-col items-center justify-center gap-0.5 rounded-[1.15rem] px-2 py-1.5 transition-all duration-200
              ${item.active
                ? 'bg-[#EAF2FF] text-[#004AAD] shadow-sm'
                : 'text-[#687386] hover:bg-[#F1F5FA] hover:text-[#004AAD]'
              }
            `}
            aria-label={item.label}
            aria-current={item.active ? 'page' : undefined}
          >
            <span className={`material-symbols-outlined text-[1.45rem] ${item.active ? 'text-[#004AAD]' : ''}`}>
              {item.icon}
            </span>
            <span className={`text-[11px] font-bold ${item.active ? 'text-[#004AAD]' : ''}`}>
              {item.label.toUpperCase()}
            </span>
          </button>
        ))}
      </div>
      </div>
    </nav>
  );
};
