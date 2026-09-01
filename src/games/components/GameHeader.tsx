import React, { useState, useEffect } from 'react';
import { GamePlayer, GameRoomDetailed } from '../types';
import { sounds } from '../audio';
import {
  ArrowLeft,
  Volume2,
  VolumeX,
  Clock,
  Coins,
  Shield,
  MessageSquare,
  Copy,
  Check,
  Flame,
} from 'lucide-react';

interface GameHeaderProps {
  room: GameRoomDetailed;
  currentTurnPlayerId?: string;
  turnDeadline?: number;
  onLeave: () => void;
  onToggleChat?: () => void;
  chatUnreadCount?: number;
}

export const GameHeader: React.FC<GameHeaderProps> = ({
  room,
  currentTurnPlayerId,
  turnDeadline,
  onLeave,
  onToggleChat,
  chatUnreadCount = 0,
}) => {
  const [isMuted, setIsMuted] = useState(sounds.isMuted());
  const [copied, setCopied] = useState(false);
  const [timeLeft, setTimeLeft] = useState<number>(20);

  useEffect(() => {
    if (!turnDeadline) return;
    const interval = setInterval(() => {
      const diff = Math.max(0, Math.ceil((turnDeadline - Date.now()) / 1000));
      setTimeLeft(diff);
      if (diff <= 5 && diff > 0) {
        sounds.playTick();
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [turnDeadline]);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(room.code);
    setCopied(true);
    sounds.playClick();
    setTimeout(() => setCopied(false), 2000);
  };

  const handleToggleSound = () => {
    const active = sounds.toggleMute();
    setIsMuted(!active);
  };

  const turnPlayer = room.players.find((p) => p.id === currentTurnPlayerId);

  return (
    <div className="w-full rounded-2xl border border-slate-200 bg-white/95 backdrop-blur-md p-3 sm:p-4 shadow-sm mb-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Left: Back & Room Badge */}
        <div className="flex items-center gap-3">
          <button
            onClick={onLeave}
            className="flex size-9 items-center justify-center rounded-xl border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 transition-colors"
            title="Leave match"
          >
            <ArrowLeft className="size-4.5" />
          </button>

          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm sm:text-base font-extrabold text-[#0D1420] capitalize">
                {room.gameType}
              </span>
              <button
                onClick={handleCopyCode}
                className="flex items-center gap-1 rounded-lg bg-sky-50 px-2 py-0.5 text-xs font-bold text-[#1E9EF5] hover:bg-sky-100 transition-colors"
                title="Click to copy Room Code"
              >
                <span>{room.code}</span>
                {copied ? <Check className="size-3 text-emerald-500" /> : <Copy className="size-3" />}
              </button>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">
              Entry: {room.settings.entryFee} coins • Pot:{' '}
              <strong className="text-emerald-600 font-bold">
                {(room.settings.entryFee || 100) * room.players.length} coins
              </strong>
            </p>
          </div>
        </div>

        {/* Center: Turn Indicator & Timer */}
        {room.status === 'in_progress' && turnPlayer && (
          <div className="flex items-center gap-2.5 rounded-2xl border border-sky-100 bg-sky-50/60 px-3 py-1.5 shadow-2xs">
            <div className="relative">
              <img
                src={turnPlayer.avatarUrl}
                alt={turnPlayer.name}
                className="size-7 rounded-full object-cover ring-2 ring-[#1E9EF5]"
              />
              <span className="absolute -bottom-1 -right-1 flex size-3 items-center justify-center rounded-full bg-emerald-500 ring-1 ring-white" />
            </div>

            <div className="text-left">
              <div className="flex items-center gap-1">
                <span className="text-xs font-bold text-[#0D1420]">
                  {turnPlayer.name.split(' ')[0]}'s Turn
                </span>
                {turnPlayer.isBot && (
                  <span className="rounded bg-slate-200 px-1 text-[9px] font-extrabold text-slate-700">
                    BOT
                  </span>
                )}
              </div>
              <div className="flex items-center gap-1 text-[11px] font-semibold text-slate-500">
                <Clock className="size-3 text-[#1E9EF5]" />
                <span className={timeLeft <= 5 ? 'text-rose-500 font-black animate-pulse' : ''}>
                  {timeLeft}s remaining
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Right: Audio Sound & In-game Chat Toggle */}
        <div className="flex items-center gap-2">
          {onToggleChat && (
            <button
              onClick={onToggleChat}
              className="relative flex size-9 items-center justify-center rounded-xl border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 transition-colors"
              title="Open match chat & emojis"
            >
              <MessageSquare className="size-4.5" />
              {chatUnreadCount > 0 && (
                <span className="absolute -top-1 -right-1 flex size-4 items-center justify-center rounded-full bg-[#1E9EF5] text-[9px] font-bold text-white">
                  {chatUnreadCount}
                </span>
              )}
            </button>
          )}

          <button
            onClick={handleToggleSound}
            className={`flex size-9 items-center justify-center rounded-xl border transition-colors ${
              isMuted
                ? 'border-slate-200 bg-slate-100 text-slate-400'
                : 'border-sky-200 bg-sky-50 text-[#1E9EF5]'
            }`}
            title={isMuted ? 'Unmute game sounds' : 'Mute game sounds'}
          >
            {isMuted ? <VolumeX className="size-4.5" /> : <Volume2 className="size-4.5" />}
          </button>
        </div>
      </div>
    </div>
  );
};
