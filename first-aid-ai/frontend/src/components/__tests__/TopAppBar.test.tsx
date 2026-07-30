import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TopAppBar } from '../TopAppBar';
import { vi } from 'vitest';

describe('TopAppBar', () => {
  it('renders with default props', () => {
    render(<TopAppBar />);
    expect(screen.getByText('medical_services')).toBeInTheDocument();
    expect(screen.getByText('First Aid AI')).toBeInTheDocument();
    expect(screen.getByText('SOS')).toBeInTheDocument();
  });

  it('renders with back button when showBackButton is true', () => {
    const handleBack = vi.fn();
    render(<TopAppBar showBackButton={true} onBackClick={handleBack} />);
    const backButton = screen.getByLabelText('Go back');
    expect(backButton).toBeInTheDocument();
    fireEvent.click(backButton);
    expect(handleBack).toHaveBeenCalledTimes(1);
  });

  it('does not render back button when showBackButton is false', () => {
    render(<TopAppBar showBackButton={false} />);
    expect(screen.queryByLabelText('Go back')).not.toBeInTheDocument();
  });

  it('renders custom actions', () => {
    const customAction = <button>Custom Action</button>;
    render(<TopAppBar actions={customAction} />);
    expect(screen.getByText('Custom Action')).toBeInTheDocument();
  });

  it('has correct fixed positioning classes', () => {
    render(<TopAppBar />);
    const header = screen.getByRole('banner');
    expect(header).toHaveClass('fixed', 'top-0', 'w-full', 'z-50');
  });

  it('has correct background and backdrop blur', () => {
    render(<TopAppBar />);
    const header = screen.getByRole('banner');
    expect(header).toHaveClass('bg-[#F7F8FB]/88', 'backdrop-blur-xl', 'border-b');
  });

  it('has correct height', () => {
    render(<TopAppBar />);
    const header = screen.getByRole('banner');
    expect(header).toHaveClass('h-[calc(60px+env(safe-area-inset-top))]');
  });

  it('applies custom className', () => {
    render(<TopAppBar className="custom-header" />);
    const header = screen.getByRole('banner');
    expect(header).toHaveClass('custom-header');
  });

  it('has correct flex layout', () => {
    render(<TopAppBar />);
    const header = screen.getByRole('banner');
    expect(header).toHaveClass('flex', 'justify-between', 'items-center', 'px-5');
  });

  it('renders logo and title in left section', () => {
    render(<TopAppBar />);
    const leftSection = screen.getByRole('banner').firstElementChild;
    expect(leftSection).toHaveClass('flex', 'items-center', 'gap-3');
  });

  it('renders actions in right section', () => {
    render(<TopAppBar />);
    const header = screen.getByRole('banner');
    const rightSection = header.lastElementChild;
    expect(rightSection).toHaveClass('flex', 'items-center', 'gap-2');
  });
});
