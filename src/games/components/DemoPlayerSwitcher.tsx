import React from 'react';
import { GamePlayer } from '../types';
import { DEMO_TEST_PLAYERS, gameManager } from '../roomStore';
import { UserCheck, Sparkles, RefreshCw, Zap, ShieldAlert } from 'lucide-react';

interface DemoPlayerSwitcherProps {
  currentActivePlayerId: string;
  onSelectPlayer: (playerId: string) => void;
  onQuickReset?: () => void;
  onOpenAdmin?: () => void;
}

export const DemoPlayerSwitcher: React.FC<DemoPlayerSwitcherProps> = ({
  currentActivePlayerId,
  onSelectPlayer,
  onQuickReset,
  onOpenAdmin,
}) => {
  return (
    <div className="w-full rounded-2xl border border-sky-200/80 bg-gradient-to-r from-sky-500 via-[#1E9EF5] to-cyan-500 p-2.5 sm:p-3 text-white shadow-md">
      <div className="flex flex-wrap items-center justify-between gap-2.5">
        {/* Left: Test Mode Badge */}
        <div className="flex items-center gap-2">
          <div className="flex size-7 items-center justify-center rounded-lg bg-white/20 backdrop-blur-xs font-black text-xs">
            <Zap className="size-4 text-amber-300 fill-amber-300" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-black uppercase tracking-wider">TATA Games Test Bar</span>
              <span className="rounded-full bg-emerald-400/30 px-1.5 py-0.2 text-[9px] font-extrabold border border-emerald-300/40">
                10,000 DEMO COINS
              </span>
            </div>
            <p className="text-[11px] text-sky-100 font-medium hidden sm:block">
              Switch viewpoints anytime to test real-time multiplayer turns & bot actions.
            </p>
          </div>
        </div>

        {/* Center: Quick Seat Selectors */}
        <div className="flex items-center gap-1.5 overflow-x-auto py-0.5">
          {DEMO_TEST_PLAYERS.map((player) => {
            const isSelected = player.id === currentActivePlayerId;
            return (
              <button
                key={player.id}
                onClick={() => onSelectPlayer(player.id)}
                className={`flex items-center gap-1.5 rounded-xl px-2.5 py-1 text-xs font-bold transition-all ${
                  isSelected
                    ? 'bg-white text-[#0D1420] shadow-sm ring-2 ring-amber-300 scale-105'
                    : 'bg-white/15 text-white hover:bg-white/25'
                }`}
              >
                <img
                  src={player.avatarUrl}
                  alt={player.name}
                  className="size-4.5 rounded-full object-cover ring-1 ring-white/40"
                />
                <span className="truncate max-w-[80px]">{player.name.split(' ')[0]}</span>
                {isSelected && <UserCheck className="size-3 text-[#1E9EF5]" />}
              </button>
            );
          })}
        </div>

        {/* Right Actions: Reset & Admin */}
        <div className="flex items-center gap-1.5">
          {onQuickReset && (
            <button
              onClick={onQuickReset}
              title="Reset match state"
              className="flex items-center gap-1 rounded-xl bg-white/15 hover:bg-white/25 px-2.5 py-1 text-xs font-bold text-white transition-colors"
            >
              <RefreshCw className="size-3.5" />
              <span className="hidden md:inline">Reset</span>
            </button>
          )}

          {onOpenAdmin && (
            <button
              onClick={onOpenAdmin}
              className="flex items-center gap-1 rounded-xl bg-[#0D1420]/80 hover:bg-[#0D1420] px-2.5 py-1 text-xs font-bold text-cyan-300 border border-cyan-400/30 transition-colors shadow-xs"
            >
              <ShieldAlert className="size-3.5" />
              <span>Admin Hub</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
