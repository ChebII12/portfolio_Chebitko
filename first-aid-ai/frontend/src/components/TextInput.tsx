// @ts-ignore
import React from 'react';
import { TextInputProps } from '../types';

export const TextInput: React.FC<TextInputProps> = ({
  label,
  placeholder,
  value,
  onChange,
  error,
  type = 'text',
  disabled = false,
  required = false,
  className = ''
}) => {
  return (
    <div className={`space-y-1.5 ${className}`}>
      {label && (
        <label className="block text-sm font-semibold text-[#30415F]">
          {label}
          {required && <span className="text-tertiary ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        className="form-input"
        aria-invalid={!!error}
        aria-describedby={error ? `${label}-error` : undefined}
      />
      {error && (
        <p id={`${label}-error`} className="text-sm text-error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
};
