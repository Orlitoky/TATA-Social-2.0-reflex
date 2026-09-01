import React from 'react';
import {
  Home,
  Users,
  MessageCircle,
  Gamepad2,
  User,
  Coins,
  Sparkles,
  Gift,
  Compass,
  Bookmark,
  ShieldCheck,
  Trash2,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface PrimaryRailProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export const PrimaryRail: React.FC<PrimaryRailProps> = ({ currentTab, setCurrentTab }) => {
  const { currentUser, claimDailyReward, hasClaimedDaily, deleteAccount } = useAuth();

  const navItems = [
    { id: 'home', label: 'Home Feed', icon: Home },
    { id: 'friends', label: 'People & Friends', icon: Users },
    { id: 'messages', label: 'Direct Messages', icon: MessageCircle },
    { id: 'games', label: 'Play & Games', icon: Gamepad2 },
    { id: 'wallet', label: 'TATA Coins Wallet', icon: Coins },
    { id: 'profile', label: 'My Profile', icon: User },
  ];

  if (!currentUser) return null;

  return (
    <aside className="hidden lg:flex w-64 shrink-0 flex-col gap-4">
      {/* Current User Card */}
      <div
        onClick={() => setCurrentTab('profile')}
        className="flex cursor-pointer items-center gap-3 rounded-2xl border border-slate-200 bg-white p-3.5 shadow-xs hover:border-[#1E9EF5] transition-colors"
      >
        <img
          src={currentUser.avatarUrl}
          alt={currentUser.displayName}
          className="size-11 rounded-full object-cover ring-2 ring-[#1E9EF5]/20"
        />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-bold text-[#0D1420]">{currentUser.displayName}</p>
          <p className="truncate text-xs font-medium text-slate-400">@{currentUser.username}</p>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex flex-col gap-1 rounded-2xl border border-slate-200 bg-white p-2 shadow-xs">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-semibold transition-all ${
                isActive
                  ? 'bg-sky-50 text-[#1E9EF5] font-bold'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-[#0D1420]'
              }`}
            >
              <Icon className={`size-4.5 ${isActive ? 'text-[#1E9EF5]' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* TATA Coins Balance Card & Daily Grant */}
      <div className="rounded-2xl border border-sky-100 bg-gradient-to-br from-sky-50 via-white to-cyan-50 p-4 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-sky-600">
            <Coins className="size-4" />
            <span className="text-[11px] font-bold uppercase tracking-wider">TATA Coins</span>
          </div>
          <span className="rounded-full bg-sky-200/60 px-2 py-0.5 text-[10px] font-extrabold text-[#1E9EF5]">
            VIRTUAL
          </span>
        </div>

        <div className="mt-2 flex items-baseline gap-1">
          <span className="text-2xl font-black tracking-tight text-[#0D1420]">
            {currentUser.coinBalance.toLocaleString()}
          </span>
          <span className="text-xs font-bold text-sky-500">coins</span>
        </div>

        <p className="mt-1 text-[11px] font-medium text-slate-500">
          Earn by posting, winning mini-games, or daily streak rewards.
        </p>

        <button
          onClick={claimDailyReward}
          disabled={hasClaimedDaily}
          className={`mt-3 flex w-full items-center justify-center gap-2 rounded-xl py-2 text-xs font-bold transition-all shadow-xs ${
            hasClaimedDaily
              ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
              : 'bg-[#1E9EF5] text-white hover:bg-sky-600 active:scale-[0.98]'
          }`}
        >
          <Gift className="size-3.5" />
          <span>{hasClaimedDaily ? 'Claimed Today (Streak Active)' : 'Claim Daily +100 Coins'}</span>
        </button>
      </div>

      {/* Quick Security & Integrity Info */}
      <div className="rounded-2xl border border-slate-200 bg-white p-3 text-xs text-slate-500">
        <div className="flex items-center gap-2 text-slate-700 font-semibold mb-1">
          <ShieldCheck className="size-4 text-emerald-500" />
          <span>TATA Platform Safety</span>
        </div>
        <p className="text-[11px] text-slate-400">
          Threaded messaging & community guidelines enforced.
        </p>
      </div>

      {/* Danger Zone Action */}
      <div className="px-2">
        <button
          onClick={() => {
            if (confirm('Are you sure you want to reset and delete your account data?')) {
              deleteAccount();
            }
          }}
          className="flex items-center gap-2 text-[11px] font-semibold text-slate-400 hover:text-rose-500 transition-colors"
        >
          <Trash2 className="size-3" />
          <span>Reset demo account</span>
        </button>
      </div>
    </aside>
  );
};
