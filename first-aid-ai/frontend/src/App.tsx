import type { ReactNode } from 'react';
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import { RegistrationScreen } from './screens/RegistrationScreen';
import { LoginScreen } from './screens/LoginScreen';
import { VerificationScreen } from './screens/VerificationScreen';
import { ForgotPasswordScreen } from './screens/ForgotPasswordScreen';
import { ResetPasswordScreen } from './screens/ResetPasswordScreen';
import { ProfileScreen } from './screens/ProfileScreen';
import { QuestionnaireScreen } from './screens/QuestionnaireScreen';
import { AssessmentResultScreen } from './screens/AssessmentResultScreen';
import { MainDashboardScreen } from './screens/MainDashboardScreen';
import { useAuth } from './hooks/useAuth';
import type { AssessmentState, AuthSession } from './types';

function App() {
  const navigate = useNavigate();
  const {
    userId,
    userName,
    userLevel,
    explanation,
    classificationSource,
    confidence,
    isAuthenticated,
    setSession,
    setAssessment,
    refreshProfile,
    logout,
  } = useAuth();

  const handleRegistrationSuccess = (session: AuthSession) => {
    setSession(session);
    navigate('/questionnaire', { replace: true });
  };

  const handleLoginSuccess = (session: AuthSession) => {
    setSession(session);
    navigate('/dashboard', { replace: true });
  };

  const handleQuestionnaireComplete = (assessment: AssessmentState) => {
    setAssessment(assessment);
    navigate('/assessment', { replace: true });
  };

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const handleError = (error: string) => {
    console.error('Error:', error);
  };

  const protectedRoute = (element: ReactNode) => (
    isAuthenticated ? element : <Navigate to="/login" replace />
  );

  const publicRoute = (element: ReactNode) => (
    isAuthenticated ? <Navigate to="/dashboard" replace /> : element
  );

  return (
    <div className="App">
      <Routes>
        <Route
          path="/"
          element={publicRoute(
            <RegistrationScreen
              onSuccess={handleRegistrationSuccess}
              onError={handleError}
            />,
          )}
        />
        <Route
          path="/verify-email"
          element={publicRoute(
            <VerificationScreen
              onSuccess={handleRegistrationSuccess}
              onError={handleError}
            />,
          )}
        />
        <Route
          path="/login"
          element={publicRoute(
            <LoginScreen onSuccess={handleLoginSuccess} onError={handleError} />,
          )}
        />
        <Route path="/forgot-password" element={publicRoute(<ForgotPasswordScreen />)} />
        <Route path="/reset-password" element={publicRoute(<ResetPasswordScreen />)} />
        <Route
          path="/questionnaire"
          element={protectedRoute(
            <QuestionnaireScreen
              userId={userId}
              onComplete={handleQuestionnaireComplete}
              onError={handleError}
              onLogout={handleLogout}
            />,
          )}
        />
        <Route
          path="/assessment"
          element={protectedRoute(
            <AssessmentResultScreen
              userId={userId}
              userName={userName}
              level={userLevel}
              explanation={explanation}
              classificationSource={classificationSource}
              confidence={confidence || undefined}
              onNavigateToDashboard={() => navigate('/dashboard', { replace: true })}
              onNavigateToProfile={() => navigate('/profile')}
              onRetakeQuestionnaire={() => {
                navigate('/questionnaire', { replace: true });
              }}
              onRefreshProfile={refreshProfile}
              onLogout={handleLogout}
            />,
          )}
        />
        <Route
          path="/dashboard"
          element={protectedRoute(
            <MainDashboardScreen
              userId={userId}
              userName={userName}
              userLevel={userLevel}
              onNavigateToModule={(moduleId) => {
                if (moduleId === 1) navigate('/questionnaire');
              }}
              onNavigateToProfile={() => navigate('/profile')}
              onRefreshProfile={refreshProfile}
              onLogout={handleLogout}
            />,
          )}
        />
        <Route
          path="/profile"
          element={protectedRoute(
            <ProfileScreen
              userId={userId}
              onLogout={handleLogout}
            />,
          )}
        />
      </Routes>
    </div>
  );
}

export default App;
