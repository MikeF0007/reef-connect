import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LoginPage, RegisterPage } from './components/AuthPages';
import { Navigation } from './components/Navigation';
import { ProfilePage } from './components/ProfilePage';
import { DiveLogPage } from './components/DiveLogPage';
import { ScubaDexPage } from './components/ScubaDexPage';
import { FriendsPage } from './components/FriendsPage';
import { ActivityFeedPage } from './components/ActivityFeedPage';
import { StatsPage } from './components/StatsPage';
import { LeaderboardPage } from './components/LeaderboardPage';
import { NotificationsPage } from './components/NotificationsPage';
import { Toaster } from './components/ui/sonner';
import { initializeDemoData } from './utils/initializeDemoData';
import { WelcomeDialog } from './components/WelcomeDialog';

function AppContent() {
  const { user } = useAuth();
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [currentPage, setCurrentPage] = useState('dives');

  useEffect(() => {
    // Initialize demo data on first load
    initializeDemoData();
  }, []);

  if (!user) {
    if (authMode === 'login') {
      return (
        <>
          <WelcomeDialog />
          <LoginPage onSwitchToRegister={() => setAuthMode('register')} />
        </>
      );
    }
    return <RegisterPage onSwitchToLogin={() => setAuthMode('login')} />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'profile':
        return <ProfilePage />;
      case 'dives':
        return <DiveLogPage />;
      case 'scubadex':
        return <ScubaDexPage />;
      case 'friends':
        return <FriendsPage />;
      case 'feed':
        return <ActivityFeedPage />;
      case 'stats':
        return <StatsPage />;
      case 'leaderboard':
        return <LeaderboardPage />;
      case 'notifications':
        return <NotificationsPage />;
      default:
        return <DiveLogPage />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation currentPage={currentPage} onNavigate={setCurrentPage} />
      <main>{renderPage()}</main>
      <Toaster />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}