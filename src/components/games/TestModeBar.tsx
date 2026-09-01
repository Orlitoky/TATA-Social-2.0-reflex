import React from 'react';
import { useGames, TEST_PROFILES } from '../../context/GamesContext';
import { Volume2, VolumeX, RefreshCw, UserCheck, Shield, Bot } from 'lucide-react';

export const TestModeBar: React.FC<{ onOpenAdmin?: () => void }> = ({ onOpenAdmin }) => {
  const { activeDemoUser, setActiveDemoUser, isMuted, setIsMuted, resetMatch, currentRoom } = useGames();

  return (
    <div className="w-full mb-4 rounded-2xl bg-gradient-to-r from-[#0D1420] via-slate-900 to-[#0D1420] border border-sky-500/30 p-2.5 sm:p-3 text-white shadow-lg">
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Active Test Profile Selector */}
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 text-xs font-bold text-[#22D3EE] uppercase tracking-wider">
            <span className="inline-block size-2 rounded-full bg-[#22D3EE] animate-pulse" />
            <span>Test Mode:</span>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-800/80 p-1 rounded-xl border border-slate-700">
            {TEST_PROFILES.map((profile) => {
              const isActive = activeDemoUser.id === profile.id;
              return (
                <button
                  key={profile.id}
                  onClick={() => setActiveDemoUser(profile)}
                  title={`${profile.displayName} (${profile.username})`}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-[#1E9EF5] text-white shadow-xs font-bold'
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  <img
                    src={profile.avatarUrl}
                    alt={profile.displayName}
                    className="size-4.5 rounded-full object-cover ring-1 ring-white/30"
                  />
                  <span className="hidden sm:inline">{profile.displayName.split(' ')[0]}</span>
                  {profile.isBot && <Bot className="size-3 text-amber-300" />}
                </button>
              );
            })}
          </div>
        </div>

        {/* Global Controls: Sound, Reset, Admin */}
        <div className="flex items-center gap-2">
          {currentRoom && currentRoom.status === 'playing' && (
            <button
              onClick={resetMatch}
              title="Reset current match round"
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-amber-400 border border-slate-700 transition-colors"
            >
              <RefreshCw className="size-3.5" />
              <span className="hidden md:inline">Reset Round</span>
            </button>
          )}

          <button
            onClick={() => setIsMuted(!isMuted)}
            title={isMuted ? 'Unmute Audio' : 'Mute Audio'}
            className="flex items-center justify-center size-8 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          >
            {isMuted ? <VolumeX className="size-4 text-rose-400" /> : <Volume2 className="size-4 text-emerald-400" />}
          </button>

          {onOpenAdmin && (
            <button
              onClick={onOpenAdmin}
              title="Open TATA Games Hub Admin Panel"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-sky-600 to-[#1E9EF5] text-white text-xs font-bold hover:brightness-110 shadow-xs transition-all"
            >
              <Shield className="size-3.5" />
              <span>Admin</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
