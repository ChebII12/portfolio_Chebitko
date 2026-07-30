import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { RadioOptionCard } from '../RadioOptionCard';
import { vi } from 'vitest';

describe('RadioOptionCard', () => {
  const defaultProps = {
    title: 'Test Option',
    description: 'This is a test option',
    icon: 'star',
    selected: false,
    onClick: vi.fn()
  };

  it('renders with basic props', () => {
    render(<RadioOptionCard {...defaultProps} />);
    expect(screen.getByText('Test Option')).toBeInTheDocument();
    expect(screen.getByText('This is a test option')).toBeInTheDocument();
    expect(screen.getByText('star')).toBeInTheDocument();
  });

  it('renders as selected', () => {
    render(<RadioOptionCard {...defaultProps} selected={true} />);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('border-[#0057D9]', 'bg-white', 'shadow-[0_12px_28px_rgba(0,87,217,0.12)]');
    expect(button).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByText('check')).toBeInTheDocument();
  });

  it('renders as unselected', () => {
    render(<RadioOptionCard {...defaultProps} selected={false} />);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('border-[#E1E6EF]', 'bg-white/82');
    expect(button).toHaveAttribute('aria-pressed', 'false');
    expect(screen.queryByText('check')).not.toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<RadioOptionCard {...defaultProps} onClick={handleClick} />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('has correct styling for icon container when selected', () => {
    render(<RadioOptionCard {...defaultProps} selected={true} />);
    const iconContainer = screen.getByText('star').parentElement;
    expect(iconContainer).toHaveClass('bg-[#EAF2FF]', 'text-[#004AAD]');
  });

  it('has correct styling for icon container when unselected', () => {
    render(<RadioOptionCard {...defaultProps} selected={false} />);
    const iconContainer = screen.getByText('star').parentElement;
    expect(iconContainer).toHaveClass('bg-[#EEF2F6]', 'text-[#687386]');
  });

  it('has correct typography classes', () => {
    render(<RadioOptionCard {...defaultProps} />);
    const title = screen.getByText('Test Option');
    const description = screen.getByText('This is a test option');

    expect(title).toHaveClass('font-headline', 'font-extrabold', 'text-base', 'text-[#102A56]');
    expect(description).toHaveClass('font-body', 'text-xs', 'text-[#5F6878]');
  });

  it('applies custom className', () => {
    render(<RadioOptionCard {...defaultProps} className="custom-card" />);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('custom-card');
  });

  it('has correct border radius', () => {
    render(<RadioOptionCard {...defaultProps} />);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('rounded-[1.5rem]');
  });

  it('has correct padding', () => {
    render(<RadioOptionCard {...defaultProps} />);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('p-4');
  });
});
