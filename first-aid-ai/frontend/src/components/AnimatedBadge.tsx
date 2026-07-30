import React from 'react';

export interface AnimatedBadgeProps {
  level: number;
  icon: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const AnimatedBadge: React.FC<AnimatedBadgeProps> = ({
  level,
  icon,
  size = 'md',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-24 h-24',
    md: 'w-32 h-32',
    lg: 'w-40 h-40'
  };

  const iconSizes = {
    sm: 'text-3xl',
    md: 'text-4xl',
    lg: 'text-5xl'
  };

  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-full h-full rounded-full bg-primary/20" />
        <div className="absolute w-4/5 h-4/5 rounded-full bg-primary/15" />
      </div>
      <div className={`
        relative ${sizeClasses[size]} rounded-3xl bg-gradient-to-br from-primary to-primary-container
        shadow-2xl shadow-primary/20 flex flex-col items-center justify-center border-4 border-white overflow-hidden
      `}>
        <span className={`material-symbols-outlined ${iconSizes[size]} text-on-primary`}>
          {icon}
        </span>
      </div>
      <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 bg-surface-container px-3 py-1 rounded-full shadow-md">
        <span className="text-sm font-headline font-bold text-on-surface">
          LEVEL {level}
        </span>
      </div>
    </div>
  );
};
