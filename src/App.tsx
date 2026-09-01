import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { SocialProvider } from './context/SocialContext';
import { Header } from './components/Header';
import { PrimaryRail } from './components/PrimaryRail';
import { ContactsRail } from './components/ContactsRail';
import { HomePage } from './pages/HomePage';
import { FriendsPage } from './pages/FriendsPage';
import { MessagesPage } from './pages/MessagesPage';
import { ProfilePage } from './pages/ProfilePage';
import { GamesPage } from './pages/GamesPage';
import { WalletPage } from './pages/WalletPage';
import { AuthPage } from './pages/AuthPage';

const AppContent: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [currentTab, setCurrentTab] = useState('home');

  if (!isAuthenticated) {
    return <AuthPage />;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-[#0D1420] pb-16 md:pb-6">
      {/* Top Sticky Header */}
      <Header currentTab={currentTab} setCurrentTab={setCurrentTab} />

      {/* Main Container Layout */}
      <main className="mx-auto max-w-7xl px-3 sm:px-6 pt-4 sm:pt-6">
        <div className="flex gap-5 items-start justify-center">
          {/* Left Primary Navigation Rail */}
          <PrimaryRail currentTab={currentTab} setCurrentTab={setCurrentTab} />

          {/* Central Workspace / Feed View */}
          <div className="w-full flex-1 max-w-2xl min-w-0">
            {currentTab === 'home' && <HomePage />}
            {currentTab === 'friends' && <FriendsPage setCurrentTab={setCurrentTab} />}
            {currentTab === 'messages' && <MessagesPage />}
            {currentTab === 'profile' && <ProfilePage />}
            {currentTab === 'games' && <GamesPage />}
            {currentTab === 'wallet' && <WalletPage />}
          </div>

          {/* Right Contacts & Discover Rail */}
          {currentTab === 'home' && <ContactsRail setCurrentTab={setCurrentTab} />}
        </div>
      </main>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <SocialProvider>
        <AppContent />
      </SocialProvider>
    </AuthProvider>
  );
}

export default App;
