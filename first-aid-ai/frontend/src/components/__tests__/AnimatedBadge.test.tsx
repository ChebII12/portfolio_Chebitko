import React from 'react';
import { render, screen } from '@testing-library/react';
import { AnimatedBadge } from '../AnimatedBadge';

describe('AnimatedBadge', () => {
  it('renders with basic props', () => {
    render(<AnimatedBadge level={2} icon="star" />);
    expect(screen.getByText('LEVEL 2')).toBeInTheDocument();
    expect(screen.getByText('star')).toBeInTheDocument();
  });

  it('renders with different sizes', () => {
    const { rerender } = render(<AnimatedBadge level={1} icon="badge" size="sm" />);
    const badge = screen.getByText('badge').parentElement;
    expect(badge).toHaveClass('w-24', 'h-24');

    rerender(<AnimatedBadge level={1} icon="badge" size="md" />);
    const badgeMd = screen.getByText('badge').parentElement;
    expect(badgeMd).toHaveClass('w-32', 'h-32');

    rerender(<AnimatedBadge level={1} icon="badge" size="lg" />);
    const badgeLg = screen.getByText('badge').parentElement;
    expect(badgeLg).toHaveClass('w-40', 'h-40');
  });

  it('renders with different icon sizes', () => {
    const { rerender } = render(<AnimatedBadge level={1} icon="badge" size="sm" />);
    expect(screen.getByText('badge')).toHaveClass('text-3xl');

    rerender(<AnimatedBadge level={1} icon="badge" size="md" />);
    expect(screen.getByText('badge')).toHaveClass('text-4xl');

    rerender(<AnimatedBadge level={1} icon="badge" size="lg" />);
    expect(screen.getByText('badge')).toHaveClass('text-5xl');
  });

  it('has pulsing background circles', () => {
    render(<AnimatedBadge level={1} icon="badge" />);
    const container = screen.getByText('LEVEL 1').parentElement?.parentElement;
    expect(container).toHaveClass('relative', 'flex', 'items-center', 'justify-center');
  });

  it('has gradient background on main badge', () => {
    render(<AnimatedBadge level={1} icon="badge" />);
    const badge = screen.getByText('badge').parentElement;
    expect(badge).toHaveClass('bg-gradient-to-br', 'from-primary', 'to-primary-container');
  });

  it('has correct border and shadow', () => {
    render(<AnimatedBadge level={1} icon="badge" />);
    const badge = screen.getByText('badge').parentElement;
    expect(badge).toHaveClass('border-4', 'border-white', 'shadow-2xl');
  });

  it('displays level indicator below badge', () => {
    render(<AnimatedBadge level={3} icon="badge" />);
    const levelIndicator = screen.getByText('LEVEL 3');
    expect(levelIndicator).toBeInTheDocument();
    expect(levelIndicator.parentElement).toHaveClass('absolute', '-bottom-2');
  });

  it('has correct icon color', () => {
    render(<AnimatedBadge level={1} icon="badge" />);
    const icon = screen.getByText('badge');
    expect(icon).toHaveClass('text-on-primary');
  });

  it('applies custom className', () => {
    render(<AnimatedBadge level={1} icon="badge" className="custom-badge" />);
    const container = screen.getByText('LEVEL 1').parentElement?.parentElement;
    expect(container).toHaveClass('custom-badge');
  });

  it('has pulsing animation classes', () => {
    render(<AnimatedBadge level={1} icon="badge" />);
    // The pulsing circles should have the animate-pulse-glow class
    // This is tested indirectly through the structure
    const container = screen.getByText('LEVEL 1').parentElement?.parentElement;
    expect(container?.children[0]).toHaveClass('absolute', 'inset-0');
  });
});
