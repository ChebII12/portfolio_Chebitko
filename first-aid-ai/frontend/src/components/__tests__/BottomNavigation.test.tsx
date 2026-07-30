import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BottomNavigation } from '../BottomNavigation';
import { vi } from 'vitest';

describe('BottomNavigation', () => {
  const mockItems = [
    { id: 'home', label: 'Home', icon: 'home', active: true, onClick: vi.fn() },
    { id: 'search', label: 'Search', icon: 'search', active: false, onClick: vi.fn() },
    { id: 'profile', label: 'Profile', icon: 'person', active: false, onClick: vi.fn() }
  ];

  it('renders with navigation items', () => {
    render(<BottomNavigation items={mockItems} />);
    expect(screen.getByText('HOME')).toBeInTheDocument();
    expect(screen.getByText('SEARCH')).toBeInTheDocument();
    expect(screen.getByText('PROFILE')).toBeInTheDocument();
  });

  it('renders icons for each item', () => {
    render(<BottomNavigation items={mockItems} />);
    expect(screen.getByText('home')).toBeInTheDocument();
    expect(screen.getByText('search')).toBeInTheDocument();
    expect(screen.getByText('person')).toBeInTheDocument();
  });

  it('highlights active item', () => {
    render(<BottomNavigation items={mockItems} />);
    const activeButton = screen.getByText('HOME').closest('button');
    expect(activeButton).toHaveClass('bg-[#EAF2FF]', 'text-[#004AAD]', 'shadow-sm');
  });

  it('styles inactive items correctly', () => {
    render(<BottomNavigation items={mockItems} />);
    const inactiveButton = screen.getByText('SEARCH').closest('button');
    expect(inactiveButton).toHaveClass('text-[#687386]');
  });

  it('handles click events', () => {
    render(<BottomNavigation items={mockItems} />);
    const searchButton = screen.getByText('SEARCH').closest('button');
    fireEvent.click(searchButton!);
    expect(mockItems[1].onClick).toHaveBeenCalledTimes(1);
  });

  it('has correct fixed positioning', () => {
    render(<BottomNavigation items={mockItems} />);
    const nav = screen.getByRole('navigation');
    expect(nav).toHaveClass('fixed', 'bottom-0', 'left-1/2', 'max-w-[430px]');
  });

  it('has correct background and backdrop blur', () => {
    render(<BottomNavigation items={mockItems} />);
    const nav = screen.getByRole('navigation');
    const container = nav.firstElementChild;
    expect(container).toHaveClass('bg-white/95', 'backdrop-blur-xl', 'border');
  });

  it('has correct border radius', () => {
    render(<BottomNavigation items={mockItems} />);
    const nav = screen.getByRole('navigation');
    const container = nav.firstElementChild;
    expect(container).toHaveClass('rounded-[1.6rem]');
  });

  it('has correct height/padding', () => {
    render(<BottomNavigation items={mockItems} />);
    const container = screen.getByRole('navigation').firstElementChild;
    expect(container).toHaveClass('px-2', 'py-2');
  });

  it('has correct accessibility attributes', () => {
    render(<BottomNavigation items={mockItems} />);
    const homeButton = screen.getByLabelText('Home');
    expect(homeButton).toHaveAttribute('aria-current', 'page');

    const searchButton = screen.getByLabelText('Search');
    expect(searchButton).not.toHaveAttribute('aria-current');
  });

  it('applies custom className', () => {
    render(<BottomNavigation items={mockItems} className="custom-nav" />);
    const nav = screen.getByRole('navigation');
    expect(nav).toHaveClass('custom-nav');
  });

  it('distributes items evenly', () => {
    render(<BottomNavigation items={mockItems} />);
    const container = screen.getByRole('navigation').firstElementChild?.firstElementChild;
    expect(container).toHaveClass('flex', 'justify-around', 'items-stretch');
  });
});
