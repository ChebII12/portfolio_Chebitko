import React, { useState } from 'react';
import { Button } from '../components/Button';
import { ProgressBar } from '../components/ProgressBar';
import { RadioOptionCard } from '../components/RadioOptionCard';
import { QuestionnaireScreenProps, QuestionnaireStep } from '../types';
import { apiFetch } from '../utils/api';
import { StatusAlert } from '../components/DesignSystem';
import { AuthenticatedAppShell } from '../components/AuthenticatedAppShell';

export const QuestionnaireScreen: React.FC<QuestionnaireScreenProps> = ({
  userId,
  onComplete,
  onError,
  onLogout
}) => {
  const answerPayloadMap: Array<Record<string, string>> = [
    { rarely: 'Rarely', monthly: 'Monthly', weekly: 'Weekly' },
    { close: 'Always close', hours: 'A few hours away', day: 'Day or more' },
    { none: 'No', old: 'Yes, but a long time ago', current: 'Yes, currently certified', advanced: 'Advanced training (EMT, etc.)' },
    { none: 'No', minor: 'Yes, for minor injuries', critical: 'Critical emergencies' },
    { unknown: "Don't know what they are", theory: 'Know in theory only', trained: 'Trained and comfortable using' },
    { solo: 'Travel solo', group: 'In groups, not designated medic', medic: 'Designated group medic/leader' }
  ];

  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSkipping, setIsSkipping] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const questionnaireSteps: QuestionnaireStep[] = [
    {
      id: 1,
      question: "How frequently do you engage in remote travel?",
      description: "This helps us understand your travel patterns and emergency preparedness needs.",
      answers: [
        { id: 'rarely', text: 'Rarely - Once yearly or less', selected: false },
        { id: 'monthly', text: 'Monthly - A few times a year', selected: false },
        { id: 'weekly', text: 'Weekly - Frequent traveler', selected: false }
      ],
      contextualImage: {
        src: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAHExUNHYZ6J6frTLsPvZ8oHutELhmLwj4CfoBninPRv1-MzDMsuhqtkuAltF8cK8ln7VU6U0tbNCpe4MOjzM9YN7kQwjK6WWIWgaOy-9HH-s1C28ggFgF3mZ-i86IFZ1uPKOKJwexyuwLzuYHeT3np989drBciZG2Eag6yvpWYhtKHeGrqPichUx1yRH0OmLmFFkiXJWx3sFZK-nBh0nWWHBfEgIKDtWFsRZQZJrrqXv9RgrQ_Rydmxb3SdPFgs9YVUPq6tKgWu3o',
        alt: 'Mountain landscape',
        caption: 'Remote travel requires specialized first aid kits.'
      }
    },
    {
      id: 2,
      question: "How far are you typically from medical facilities?",
      description: "Distance from professional medical care affects your emergency response strategy.",
      answers: [
        { id: 'close', text: 'Always close - Within 30 minutes', selected: false },
        { id: 'hours', text: 'A few hours away - 1-4 hours', selected: false },
        { id: 'day', text: 'Day or more - Remote locations', selected: false }
      ]
    },
    {
      id: 3,
      question: "What's your first aid certification status?",
      description: "Formal training provides a strong foundation for emergency response.",
      answers: [
        { id: 'none', text: 'No certification', selected: false },
        { id: 'old', text: 'Certified long ago - Need refresh', selected: false },
        { id: 'current', text: 'Currently certified', selected: false },
        { id: 'advanced', text: 'Advanced training (EMT, etc.)', selected: false }
      ]
    },
    {
      id: 4,
      question: "What's your real-life emergency experience?",
      description: "Hands-on experience builds confidence and decision-making skills.",
      answers: [
        { id: 'none', text: 'No real experience', selected: false },
        { id: 'minor', text: 'Minor injuries only', selected: false },
        { id: 'critical', text: 'Critical emergencies', selected: false }
      ]
    },
    {
      id: 5,
      question: "How comfortable are you with trauma supplies?",
      description: "Familiarity with medical equipment affects your ability to respond effectively.",
      answers: [
        { id: 'unknown', text: "Don't know what they are", selected: false },
        { id: 'theory', text: 'Know in theory only', selected: false },
        { id: 'trained', text: 'Trained and comfortable using', selected: false }
      ]
    },
    {
      id: 6,
      question: "What's your role in group travel situations?",
      description: "Group dynamics affect responsibility and resource allocation.",
      answers: [
        { id: 'solo', text: 'Travel solo - Self-reliant', selected: false },
        { id: 'group', text: 'In groups - Not designated medic', selected: false },
        { id: 'medic', text: 'Designated group medic/leader', selected: false }
      ]
    }
  ];

  const currentStepData = questionnaireSteps[currentStep];
  const totalSteps = questionnaireSteps.length;
  const currentDisplayStep = currentStep + 1;
  const progress = (currentDisplayStep / totalSteps) * 100;

  const handleAnswerSelect = (answerId: string) => {
    const newAnswers = [...answers];
    newAnswers[currentStep] = answerId;
    setAnswers(newAnswers);
    setSubmitError('');
  };

  const handleNext = () => {
    if (currentStep < questionnaireSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    if (!userId) {
      const message = 'Please complete registration first.';
      setSubmitError(message);
      onError(message);
      return;
    }

    const hasAllAnswers = questionnaireSteps.every((_, index) => Boolean(answers[index]));
    if (!hasAllAnswers) {
      const message = 'Please answer all questions';
      setSubmitError(message);
      onError(message);
      return;
    }

    const mappedAnswers = answers.map((answerId, index) => answerPayloadMap[index][answerId]);
    if (mappedAnswers.some((value) => !value)) {
      const message = 'Invalid questionnaire answer detected. Please review your selections.';
      setSubmitError(message);
      onError(message);
      return;
    }

    setIsSubmitting(true);
    setSubmitError('');

    try {
      const response = await apiFetch('/api/questionnaire/analyze', {
        method: 'POST',
        body: JSON.stringify({
          // server derives user from the access token; still include for backward compatibility
          user_id: userId,
          answers: mappedAnswers,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        onComplete({
          level: data.level || 'beginner',
          explanation: data.explanation || '',
          classificationSource: data.classification_source || '',
          confidence: typeof data.confidence === 'number' ? data.confidence : undefined,
        });
      } else {
        const message = data.detail || data.error?.message || 'Analysis failed';
        setSubmitError(String(message));
        onError(String(message));
      }
    } catch (error) {
      const message = 'Network issue detected. Please retry when the backend is available.';
      setSubmitError(message);
      onError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSkip = async () => {
    setIsSkipping(true);
    setSubmitError('');

    try {
      const response = await apiFetch('/api/questionnaire/skip', { method: 'POST' });
      const data = await response.json();

      if (response.ok) {
        onComplete({
          level: 'beginner',
          explanation: data.explanation || 'Beginner was assigned as the safest default.',
          classificationSource: data.classification_source || 'questionnaire_skipped',
          confidence: typeof data.confidence === 'number' ? data.confidence : 1,
        });
      } else {
        const message = data.detail || 'Unable to skip questionnaire. Please retry.';
        setSubmitError(String(message));
        onError(String(message));
      }
    } catch {
      const message = 'Backend unavailable. Please retry or complete the questionnaire when the service is online.';
      setSubmitError(message);
      onError(message);
    } finally {
      setIsSkipping(false);
    }
  };

  const canProceed = answers[currentStep] !== undefined;
  const navItems = [
    { id: 'home', label: 'Home', icon: 'home', active: false, onClick: () => {} },
    { id: 'history', label: 'History', icon: 'history', active: false, onClick: () => {} },
    { id: 'map', label: 'Map', icon: 'map', active: false, onClick: () => {} },
    { id: 'assessment', label: 'Assessment', icon: 'assignment_turned_in', active: true, onClick: () => {} },
    { id: 'profile', label: 'Profile', icon: 'person', active: false, onClick: () => {} }
  ];

  return (
    <AuthenticatedAppShell
      title="Medical Profile"
      navItems={navItems}
      showBackButton={currentStep > 0}
      onBackClick={handlePrevious}
      actions={onLogout ? (
          <button
            type="button"
            onClick={onLogout}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full text-[#5F6878] transition-colors hover:bg-[#EAF2FF] hover:text-[#004AAD]"
            aria-label="Sign out"
          >
            <span className="material-symbols-outlined text-xl">logout</span>
          </button>
      ) : undefined}
    >

      {/* Progress Bar */}
      <div>
        <div className="mb-3 flex items-end justify-between">
          <span className="font-headline text-sm font-bold text-[#102A56]">Step {currentDisplayStep} of {totalSteps}</span>
          <span className="text-xs font-bold uppercase text-[#102A56]">{Math.round(progress)}%</span>
        </div>
        <ProgressBar progress={progress} />
      </div>

      {/* Main Content */}
      <div>
        <div className="mb-5 mt-5">
          <h2 className="mb-3 font-headline text-3xl font-extrabold leading-tight text-[#102A56]">
            Let's personalize your experience
          </h2>
          <p className="text-sm font-medium leading-6 text-[#5F6878]">
            {currentStepData.description}
          </p>
        </div>

        <h3 className="mb-4 font-headline text-xl font-extrabold leading-tight text-[#102A56]">
          {currentStepData.question}
        </h3>

        {submitError && (
          <div className="mt-4"><StatusAlert tone="error">{submitError}</StatusAlert></div>
        )}

        {/* Contextual Image */}
        {currentStepData.contextualImage && (
          <div
            aria-label={currentStepData.contextualImage.alt}
            className="relative mt-5 h-36 overflow-hidden rounded-[1.5rem] bg-gradient-to-br from-[#0B1F3A] via-[#004AAD] to-[#79A7D8] shadow-[0_14px_30px_rgba(16,42,86,0.16)]"
          >
            <span className="material-symbols-outlined absolute bottom-7 right-7 text-6xl text-white/80">terrain</span>
            <div className="absolute bottom-4 left-4 right-4">
              <p className="mb-2 inline-block rounded-full bg-white/20 px-3 py-1 text-[10px] font-bold uppercase text-white backdrop-blur-md">
                Contextual Insight
              </p>
              <p className="text-sm font-bold text-white">
                {currentStepData.contextualImage.caption}
              </p>
            </div>
          </div>
        )}

        {/* Answer Options */}
        <div className="mt-5 space-y-3">
          {currentStepData.answers.map((answer) => (
            <RadioOptionCard
              key={answer.id}
              title={answer.text.split(' - ')[0]}
              description={answer.text.split(' - ')[1] || ''}
              icon={answer.id === 'rarely' ? 'schedule' :
                    answer.id === 'monthly' ? 'calendar_month' :
                    answer.id === 'weekly' ? 'flight' :
                    answer.id === 'close' ? 'location_on' :
                    answer.id === 'hours' ? 'schedule' :
                    answer.id === 'day' ? 'terrain' :
                    answer.id === 'none' ? 'school' :
                    answer.id === 'old' ? 'history' :
                    answer.id === 'current' ? 'verified' :
                    answer.id === 'advanced' ? 'local_hospital' :
                    answer.id === 'minor' ? 'healing' :
                    answer.id === 'critical' ? 'emergency' :
                    answer.id === 'unknown' ? 'help' :
                    answer.id === 'theory' ? 'lightbulb' :
                    answer.id === 'trained' ? 'medical_services' :
                    answer.id === 'solo' ? 'person' :
                    answer.id === 'group' ? 'group' :
                    'person'}
              selected={answers[currentStep] === answer.id}
              onClick={() => handleAnswerSelect(answer.id)}
            />
          ))}
        </div>

        {/* Navigation Buttons */}
        <div className="mt-6 flex gap-3">
          {currentStep > 0 && (
            <Button
              variant="secondary"
              onClick={handlePrevious}
            className="flex-1 text-base"
            >
              <span className="material-symbols-outlined">arrow_back</span>
              Previous
            </Button>
          )}

          <Button
            onClick={handleNext}
            disabled={!canProceed}
            loading={isSubmitting}
            className={`${currentStep > 0 ? 'flex-1' : 'w-full'} text-base shadow-lg`}
          >
            {currentStep === questionnaireSteps.length - 1 ? 'Analyze My Level' : 'Next'}
            <span className="material-symbols-outlined">
              {currentStep === questionnaireSteps.length - 1 ? 'analytics' : 'arrow_forward'}
            </span>
          </Button>
        </div>

        <button
          type="button"
          onClick={handleSkip}
          disabled={isSubmitting || isSkipping}
          className="mt-4 w-full text-center text-sm font-bold text-[#5F6878] hover:text-[#004AAD] disabled:opacity-60"
        >
          {isSkipping ? 'Assigning beginner level...' : 'Skip for now'}
        </button>
      </div>
    </AuthenticatedAppShell>
  );
};
