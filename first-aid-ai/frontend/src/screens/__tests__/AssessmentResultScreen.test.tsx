import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AssessmentResultScreen } from '../AssessmentResultScreen';

describe('AssessmentResultScreen', () => {
  it('renders the user name, assigned level, explanation, and dashboard action', () => {
    render(
      <AssessmentResultScreen
        userId="user-1"
        userName="Jane Traveler"
        level="intermediate"
        explanation=""
        onNavigateToDashboard={vi.fn()}
        onRetakeQuestionnaire={vi.fn()}
      />,
    );

    expect(screen.getByText('Jane Traveler')).toBeInTheDocument();
    expect(screen.getByText('Your Level: Intermediate')).toBeInTheDocument();
    expect(screen.getByText(/some experience with outdoor activities and basic first aid/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /go to dashboard/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retake assessment/i })).toBeInTheDocument();
  });

  it('shows a fallback notice when deterministic fallback is used', () => {
    render(
      <AssessmentResultScreen
        userId="user-1"
        userName="Jane Traveler"
        level="beginner"
        explanation="The deterministic fallback was used."
        onNavigateToDashboard={vi.fn()}
        onRetakeQuestionnaire={vi.fn()}
      />,
    );

    expect(screen.getByRole('status')).toHaveTextContent('The deterministic fallback was used.');
  });
});
