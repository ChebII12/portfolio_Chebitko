import React from 'react';
import { RadioOptionCardProps } from '../types';

export const RadioOptionCard: React.FC<RadioOptionCardProps> = ({
  icon,
  title,
  description,
  selected,
  onClick,
  className = ''
}) => {
  return (
    <button
      onClick={onClick}
      className={`
        w-full text-left p-4 rounded-[1.5rem] border transition-all duration-200
        ${selected 
          ? 'border-[#0057D9] bg-white shadow-[0_12px_28px_rgba(0,87,217,0.12)]'
          : 'border-[#E1E6EF] bg-white/82 shadow-[0_8px_20px_rgba(16,42,86,0.05)] hover:bg-white'
        }
        cursor-pointer active:scale-95
        ${className}
      `}
      aria-pressed={selected}
    >
      <div className="flex items-center gap-3">
        <div className={`
          w-10 h-10 rounded-[1rem] flex items-center justify-center text-[1.35rem] shrink-0
          ${selected ? 'bg-[#EAF2FF] text-[#004AAD]' : 'bg-[#EEF2F6] text-[#687386]'}
        `}>
          <span className="material-symbols-outlined">{icon}</span>
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="font-headline text-base font-extrabold leading-tight text-[#102A56]">{title}</h3>
          {description && <p className="mt-1 font-body text-xs font-medium leading-5 text-[#5F6878]">{description}</p>}
        </div>
        <div className={`
          w-6 h-6 rounded-full border-2 flex items-center justify-center shrink-0
          ${selected ? 'bg-[#004AAD] text-white border-[#004AAD]' : 'border-[#D6DDE8]'}
        `}>
          {selected && <span className="material-symbols-outlined text-sm">check</span>}
        </div>
      </div>
    </button>
  );
};
