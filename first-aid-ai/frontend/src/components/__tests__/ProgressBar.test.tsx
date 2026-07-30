import React from 'react';
import { render, screen } from '@testing-library/react';
import { ProgressBar } from '../ProgressBar';

describe('ProgressBar', () => {
  it('renders with default props', () => {
    render(<ProgressBar progress={50} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toBeInTheDocument();
    expect(progressBar).toHaveAttribute('aria-valuenow', '50');
    expect(progressBar).toHaveAttribute('aria-valuemin', '0');
    expect(progressBar).toHaveAttribute('aria-valuemax', '100');
  });

  it('renders with 0 progress', () => {
    render(<ProgressBar progress={0} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveStyle({ width: '0%' });
  });

  it('renders with 100 progress', () => {
    render(<ProgressBar progress={100} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveStyle({ width: '100%' });
  });

  it('clamps progress to valid range', () => {
    const { rerender } = render(<ProgressBar progress={-10} />);
    expect(screen.getByRole('progressbar')).toHaveStyle({ width: '0%' });

    rerender(<ProgressBar progress={150} />);
    expect(screen.getByRole('progressbar')).toHaveStyle({ width: '100%' });
  });

  it('has correct background color', () => {
    render(<ProgressBar progress={50} />);
    const container = screen.getByRole('progressbar').parentElement;
    expect(container).toHaveClass('bg-surface-container');
  });

  it('has correct fill color', () => {
    render(<ProgressBar progress={50} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveClass('bg-primary');
  });

  it('has correct border radius', () => {
    render(<ProgressBar progress={50} />);
    const container = screen.getByRole('progressbar').parentElement;
    const progressBar = screen.getByRole('progressbar');
    expect(container).toHaveClass('rounded-full');
    expect(progressBar).toHaveClass('rounded-full');
  });

  it('has correct height', () => {
    render(<ProgressBar progress={50} />);
    const container = screen.getByRole('progressbar').parentElement;
    expect(container).toHaveClass('h-2');
  });

  it('applies animated class by default', () => {
    render(<ProgressBar progress={50} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveClass('animate-progress-fill');
  });

  it('does not apply animated class when animated is false', () => {
    render(<ProgressBar progress={50} animated={false} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).not.toHaveClass('animate-progress-fill');
  });

  it('has correct transition when animated', () => {
    render(<ProgressBar progress={50} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveClass('transition-all', 'duration-700', 'ease-out');
  });

  it('has correct accessibility label', () => {
    render(<ProgressBar progress={75} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-label', 'Progress: 75%');
  });

  it('applies custom className', () => {
    render(<ProgressBar progress={50} className="custom-progress" />);
    const container = screen.getByRole('progressbar').parentElement;
    expect(container).toHaveClass('custom-progress');
  });

  it('has overflow hidden on container', () => {
    render(<ProgressBar progress={50} />);
    const container = screen.getByRole('progressbar').parentElement;
    expect(container).toHaveClass('overflow-hidden');
  });
});
