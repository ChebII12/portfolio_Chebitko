import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { AssessmentState, AuthSession, UserLevel } from '../types';
import { apiFetch } from '../utils/api';

const FLOW_STATE_KEY = 'module1-flow-state';
const ACCESS_TOKEN_KEY = 'access_token';

export interface AuthState {
  userId: string;
  userName: string;
  userLevel: UserLevel;
  explanation: string;
  classificationSource: string;
  confidence: number | null;
  token: string;
}

interface AuthContextValue extends AuthState {
  isAuthenticated: boolean;
  setSession: (session: AuthSession) => void;
  setAssessment: (assessment: AssessmentState) => void;
  refreshProfile: () => Promise<boolean>;
  logout: () => void;
}

const defaultState: AuthState = {
  userId: '',
  userName: 'Traveler',
  userLevel: 'beginner',
  explanation: '',
  classificationSource: '',
  confidence: null,
  token: '',
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function safeRead<T>(reader: () => T, fallback: T): T {
  try {
    return reader();
  } catch {
    return fallback;
  }
}

function isTokenUsable(token: string): boolean {
  if (!token) return false;
  const payload = decodeTokenPayload(token);
  if (!payload) return false;
  if (!payload.exp) return true;
  return payload.exp * 1000 > Date.now();
}

function decodeTokenPayload(token: string): { sub?: string; email?: string; exp?: number } | null {
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  try {
    const normalized = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized.padEnd(normalized.length + ((4 - normalized.length % 4) % 4), '=');
    return JSON.parse(atob(padded));
  } catch {
    return null;
  }
}

function safeLevel(value: unknown): UserLevel {
  return value === 'intermediate' || value === 'expert' ? value : 'beginner';
}

function sourceNotice(source: string, level: UserLevel): string {
  if (source === 'questionnaire_skipped') {
    return 'Beginner was assigned as the safest default because the questionnaire was skipped.';
  }
  if (source === 'deterministic_fallback') {
    return `Your ${level} level was assigned with deterministic fallback because AI classification was unavailable or failed.`;
  }
  if (source === 'local_rules') {
    return `Your ${level} level was assigned with local deterministic rules.`;
  }
  return '';
}

function loadInitialState(): AuthState {
  const storedState = safeRead(() => localStorage.getItem(FLOW_STATE_KEY), null as string | null);
  const storedToken = safeRead(() => localStorage.getItem(ACCESS_TOKEN_KEY), null as string | null);

  const token = storedToken && isTokenUsable(storedToken) ? storedToken : '';
  const tokenPayload = token ? decodeTokenPayload(token) : null;
  if (!token) {
    safeRead(() => {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      return null;
    }, null);
  }

  if (!storedState) {
    return { ...defaultState, userId: tokenPayload?.sub || '', token };
  }

  try {
    const parsed = JSON.parse(storedState) as Partial<AuthState>;

    return {
      userId: parsed.userId || tokenPayload?.sub || '',
      userName: parsed.userName || 'Traveler',
      userLevel: safeLevel(parsed.userLevel),
      explanation: parsed.explanation || '',
      classificationSource: parsed.classificationSource || '',
      confidence: typeof parsed.confidence === 'number' ? parsed.confidence : null,
      token,
    };
  } catch {
    return { ...defaultState, token };
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>(loadInitialState);

  const persistState = useCallback((next: AuthState) => {
    setState(next);
    safeRead(() => {
      localStorage.setItem(FLOW_STATE_KEY, JSON.stringify(next));
      if (next.token) {
        localStorage.setItem(ACCESS_TOKEN_KEY, next.token);
      } else {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
      }
      return null;
    }, null);
  }, []);

  const setSession = useCallback((session: AuthSession) => {
    const next: AuthState = {
      userId: session.userId,
      userName: session.name || 'Traveler',
      userLevel: safeLevel(session.level),
      explanation: '',
      classificationSource: '',
      confidence: null,
      token: session.token,
    };
    persistState(next);
  }, [persistState]);

  const setAssessment = useCallback((assessment: AssessmentState) => {
    setState((prev) => {
      const next = {
        ...prev,
        userLevel: safeLevel(assessment.level),
        explanation: assessment.explanation || '',
        classificationSource: assessment.classificationSource || '',
        confidence: typeof assessment.confidence === 'number' ? assessment.confidence : null,
      };
      safeRead(() => {
        localStorage.setItem(FLOW_STATE_KEY, JSON.stringify(next));
        return null;
      }, null);
      return next;
    });
  }, []);

  const logout = useCallback(() => {
    setState({ ...defaultState });
    safeRead(() => {
      localStorage.removeItem(FLOW_STATE_KEY);
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      return null;
    }, null);
  }, []);

  const refreshProfile = useCallback(async () => {
    if (!state.token || !isTokenUsable(state.token) || !state.userId) {
      logout();
      return false;
    }

    try {
      const response = await apiFetch(`/api/auth/users/${state.userId}`);
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) logout();
        return false;
      }
      const data = await response.json();
      const questionnaireData = data.questionnaire_data || {};
      const nextLevel = safeLevel(data.level);
      const source = String(questionnaireData.classification_source || '');
      const next: AuthState = {
        userId: data.id || state.userId,
        userName: data.name || state.userName || 'Traveler',
        userLevel: nextLevel,
        explanation: state.explanation || sourceNotice(source, nextLevel),
        classificationSource: source || state.classificationSource || '',
        confidence: typeof questionnaireData.confidence === 'number' ? questionnaireData.confidence : state.confidence,
        token: state.token,
      };
      persistState(next);
      return true;
    } catch {
      return false;
    }
  }, [logout, persistState, state]);

  useEffect(() => {
    const handleAuthError = () => logout();
    window.addEventListener('module1-auth-error', handleAuthError);
    return () => window.removeEventListener('module1-auth-error', handleAuthError);
  }, [logout]);

  const value = useMemo<AuthContextValue>(() => ({
    ...state,
    isAuthenticated: isTokenUsable(state.token) && Boolean(state.userId),
    setSession,
    setAssessment,
    refreshProfile,
    logout,
  }), [state, setSession, setAssessment, refreshProfile, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

