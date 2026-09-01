import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, CoinTransaction } from '../types';
import { CURRENT_USER, SEED_COIN_HISTORY } from '../data/seedData';
import confetti from 'canvas-confetti';

interface AuthContextType {
  currentUser: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  coinTransactions: CoinTransaction[];
  hasClaimedDaily: boolean;
  login: (identifier: string, pass: string) => Promise<boolean>;
  signup: (displayName: string, username: string, email: string, pass: string) => Promise<boolean>;
  logout: () => void;
  updateProfile: (updates: Partial<User>) => void;
  addCoins: (amount: number, description: string, type?: CoinTransaction['type']) => void;
  claimDailyReward: () => void;
  deleteAccount: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AUTH_STORAGE_KEY = 'tata_auth_user';
const COINS_STORAGE_KEY = 'tata_coins_history';
const DAILY_STORAGE_KEY = 'tata_daily_claimed';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(() => {
    const saved = localStorage.getItem(AUTH_STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return CURRENT_USER;
      }
    }
    return CURRENT_USER;
  });

  const [coinTransactions, setCoinTransactions] = useState<CoinTransaction[]>(() => {
    const saved = localStorage.getItem(COINS_STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return SEED_COIN_HISTORY;
      }
    }
    return SEED_COIN_HISTORY;
  });

  const [hasClaimedDaily, setHasClaimedDaily] = useState<boolean>(() => {
    const saved = localStorage.getItem(DAILY_STORAGE_KEY);
    return saved === 'true';
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (currentUser) {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(currentUser));
    } else {
      localStorage.removeItem(AUTH_STORAGE_KEY);
    }
  }, [currentUser]);

  useEffect(() => {
    localStorage.setItem(COINS_STORAGE_KEY, JSON.stringify(coinTransactions));
  }, [coinTransactions]);

  const login = async (identifier: string, _pass: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    await new Promise((r) => setTimeout(r, 600));

    if (!identifier.trim()) {
      setError('Please enter your email or username');
      setIsLoading(false);
      return false;
    }

    // Restore or create user
    const user: User = {
      ...CURRENT_USER,
      username: identifier.includes('@') ? identifier.split('@')[0] : identifier,
      displayName: identifier.includes('@') ? identifier.split('@')[0] : identifier,
    };
    setCurrentUser(user);
    setIsLoading(false);
    return true;
  };

  const signup = async (
    displayName: string,
    username: string,
    email: string,
    _pass: string
  ): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    await new Promise((r) => setTimeout(r, 600));

    if (!displayName || !username || !email) {
      setError('Please fill out all required fields');
      setIsLoading(false);
      return false;
    }

    const newUser: User = {
      id: `usr_${Date.now()}`,
      username: username.toLowerCase().replace(/\s+/g, '.'),
      displayName,
      email,
      avatarUrl: `https://api.dicebear.com/7.x/notionists/svg?seed=${username}`,
      bio: 'New explorer on TATA Social! ✨',
      coinBalance: 500, // 500 bonus coins on signup!
      joinedDate: 'Just now',
      isOnline: true,
      postCount: 0,
      friendCount: 0,
      followerCount: 0,
      followingCount: 0,
    };

    const welcomeBonus: CoinTransaction = {
      id: `tx_${Date.now()}`,
      type: 'signup_bonus',
      amount: 500,
      description: 'Welcome to TATA Social signup bonus',
      timestamp: 'Just now',
    };

    setCurrentUser(newUser);
    setCoinTransactions((prev) => [welcomeBonus, ...prev]);
    setIsLoading(false);
    confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } });
    return true;
  };

  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem(AUTH_STORAGE_KEY);
  };

  const updateProfile = (updates: Partial<User>) => {
    if (!currentUser) return;
    setCurrentUser((prev) => (prev ? { ...prev, ...updates } : null));
  };

  const addCoins = (
    amount: number,
    description: string,
    type: CoinTransaction['type'] = 'game_win'
  ) => {
    if (!currentUser) return;
    const newTx: CoinTransaction = {
      id: `tx_${Date.now()}`,
      type,
      amount,
      description,
      timestamp: 'Just now',
    };
    setCurrentUser((prev) => (prev ? { ...prev, coinBalance: prev.coinBalance + amount } : null));
    setCoinTransactions((prev) => [newTx, ...prev]);
  };

  const claimDailyReward = () => {
    if (hasClaimedDaily || !currentUser) return;
    addCoins(100, 'Daily login streak reward', 'daily_reward');
    setHasClaimedDaily(true);
    localStorage.setItem(DAILY_STORAGE_KEY, 'true');
    confetti({ particleCount: 100, spread: 80, origin: { y: 0.5 } });
  };

  const deleteAccount = () => {
    setCurrentUser(null);
    localStorage.clear();
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        isAuthenticated: !!currentUser,
        isLoading,
        error,
        coinTransactions,
        hasClaimedDaily,
        login,
        signup,
        logout,
        updateProfile,
        addCoins,
        claimDailyReward,
        deleteAccount,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
