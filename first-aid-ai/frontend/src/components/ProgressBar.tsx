import React from 'react';

export interface ProgressBarProps {
  progress: number; // 0-100
  className?: string;
  animated?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  className = '',
  animated = true
}) => {
  return (
    <div className={`w-full h-2 bg-surface-container rounded-full overflow-hidden ${className}`}>
      <div
        className={`
          h-full bg-primary rounded-full transition-all duration-700 ease-out
          ${animated ? 'animate-progress-fill' : ''}
        `}
        style={{
          width: `${Math.min(100, Math.max(0, progress))}%`,
          '--progress-width': `${Math.min(100, Math.max(0, progress))}%`
        } as React.CSSProperties}
        role="progressbar"
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Progress: ${progress}%`}
      />
    </div>
  );
};
