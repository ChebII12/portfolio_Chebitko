import React from 'react';
import { ButtonProps } from '../types';

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  type = 'button',
  className = ''
}) => {
  const baseClasses = 'btn focus-ring min-w-0 whitespace-nowrap transition-all duration-300 shadow-sm disabled:shadow-none';

  const variantClasses = {
    primary: 'bg-[#0057D9] text-white hover:bg-[#004AAD] active:scale-95 font-headline font-extrabold shadow-[0_16px_28px_rgba(0,87,217,0.22)]',
    secondary: 'bg-white text-[#004AAD] hover:bg-[#EAF2FF] font-headline font-bold border border-[#E1E6EF]',
    outline: 'border border-[#D7DEEA] bg-transparent text-[#102A56] hover:bg-white font-headline font-bold'
  };

  const sizeClasses = {
    sm: 'h-12 px-4 text-sm',
    md: 'h-[52px] px-6 text-base',
    lg: 'h-14 px-7 text-lg'
  };

  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      {loading && <span className="material-symbols-outlined animate-spin">refresh</span>}
      {children}
    </button>
  );
};
