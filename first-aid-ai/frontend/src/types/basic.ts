// Basic types for the First Aid AI application

export type UserLevel = 'beginner' | 'intermediate' | 'expert';

export interface AuthSession {
  userId: string;
  name: string;
  token: string;
  level?: UserLevel | null;
}

export interface AssessmentState {
  level: UserLevel;
  explanation?: string;
  classificationSource?: string;
  confidence?: number;
}

export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}

export interface TextInputProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  type?: 'text' | 'email' | 'password' | 'number';
  className?: string;
}

export interface RadioOptionCardProps {
  title: string;
  description: string;
  icon: string;
  selected: boolean;
  onClick: () => void;
  className?: string;
}

export interface RegistrationForm {
  name: string;
  email: string;
  password: string;
}

export interface RegistrationScreenProps {
  onSuccess: (session: AuthSession) => void;
  onError: (error: string) => void;
}

export interface LoginForm {
  email: string;
  password: string;
}

export interface LoginScreenProps {
  onSuccess: (session: AuthSession) => void;
  onError: (error: string) => void;
}

export interface QuestionnaireAnswer {
  id: string;
  text: string;
  selected: boolean;
}

export interface QuestionnaireStep {
  id: number;
  question: string;
  description: string;
  answers: QuestionnaireAnswer[];
  contextualImage?: {
    src: string;
    alt: string;
    caption: string;
  };
}

export interface AssessmentResult {
  level: 'beginner' | 'intermediate' | 'expert';
  confidence: number;
  title: string;
  description: string;
  metrics: Array<{
    label: string;
    value: string;
    icon: string;
  }>;
}

export interface User {
  id: string;
  name: string;
  email: string;
  level: 'beginner' | 'intermediate' | 'expert';
  registrationDate: Date;
  questionnaireData?: any;
}

export interface TopAppBarProps {
  title?: string;
  showBackButton?: boolean;
  onBackClick?: () => void;
  actions?: React.ReactNode;
  className?: string;
}

export interface BottomNavigationItem {
  id: string;
  label: string;
  icon: string;
  active?: boolean;
  onClick?: () => void;
}

export interface BottomNavigationProps {
  items: BottomNavigationItem[];
  className?: string;
}

export interface AnimatedBadgeProps {
  level: number;
  icon: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export interface ProgressBarProps {
  progress: number; // 0-100
  className?: string;
  animated?: boolean;
}

export interface QuestionnaireScreenProps {
  userId: string;
  onComplete: (assessment: AssessmentState) => void;
  onError: (error: string) => void;
  onLogout?: () => void;
}

export interface AssessmentResultScreenProps {
  userId: string;
  userName: string;
  level: 'beginner' | 'intermediate' | 'expert';
  explanation?: string;
  classificationSource?: string;
  confidence?: number;
  onNavigateToDashboard: () => void;
  onNavigateToProfile?: () => void;
  onRetakeQuestionnaire: () => void;
  onRefreshProfile?: () => Promise<boolean>;
  onLogout?: () => void;
}

export interface MainDashboardScreenProps {
  userId: string;
  userName: string;
  userLevel: 'beginner' | 'intermediate' | 'expert';
  onNavigateToModule: (moduleId: number) => void;
  onNavigateToProfile: () => void;
  onRefreshProfile?: () => Promise<boolean>;
  isOffline?: boolean;
  onLogout?: () => void;
}
