import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TextInput } from '../TextInput';
import { vi } from 'vitest';

describe('TextInput', () => {
  it('renders with basic props', () => {
    render(<TextInput value="" onChange={() => {}} />);
    const input = screen.getByRole('textbox');
    expect(input).toBeInTheDocument();
    expect(input).toHaveClass('form-input');
  });

  it('renders with label', () => {
    render(<TextInput label="Email" value="" onChange={() => {}} />);
    const label = screen.getByText('Email');
    expect(label).toBeInTheDocument();
  });

  it('renders with placeholder', () => {
    render(<TextInput placeholder="Enter email" value="" onChange={() => {}} />);
    const input = screen.getByPlaceholderText('Enter email');
    expect(input).toBeInTheDocument();
  });

  it('handles value changes', () => {
    const handleChange = vi.fn();
    render(<TextInput value="test" onChange={handleChange} />);
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'new value' } });
    expect(handleChange).toHaveBeenCalledWith('new value');
  });

  it('renders with different input types', () => {
    const { rerender } = render(<TextInput type="email" value="" onChange={() => {}} />);
    expect(screen.getByDisplayValue('')).toHaveAttribute('type', 'email');

    rerender(<TextInput type="password" value="" onChange={() => {}} />);
    expect(screen.getByDisplayValue('')).toHaveAttribute('type', 'password');
  });

  it('shows required indicator', () => {
    render(<TextInput label="Name" required value="" onChange={() => {}} />);
    const asterisk = screen.getByText('*');
    expect(asterisk).toBeInTheDocument();
    expect(asterisk).toHaveClass('text-tertiary');
  });

  it('shows error message', () => {
    render(<TextInput label="Email" error="Invalid email" value="" onChange={() => {}} />);
    const error = screen.getByText('Invalid email');
    expect(error).toBeInTheDocument();
    expect(error).toHaveAttribute('role', 'alert');
  });

  it('is disabled when disabled prop is true', () => {
    render(<TextInput disabled value="disabled" onChange={() => {}} />);
    const input = screen.getByRole('textbox');
    expect(input).toBeDisabled();
  });

  it('has correct accessibility attributes', () => {
    render(<TextInput label="Name" error="Required" value="" onChange={() => {}} />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAttribute('aria-describedby', 'Name-error');
  });

  it('applies custom className', () => {
    render(<TextInput className="custom-input" value="" onChange={() => {}} />);
    const container = screen.getByRole('textbox').parentElement;
    expect(container).toHaveClass('custom-input');
  });
});
