import React, { useState } from 'react';
import { GamePlayer, GameRoomDetailed } from '../types';
import { sounds } from '../audio';
import {
  Users,
  Bot,
  Play,
  CheckCircle,
  Clock,
  Coins,
  Shield,
  Copy,
  Check,
  UserPlus,
  Trash2,
  Settings,
  Sparkles,
  ArrowLeft,
} from 'lucide-react';

interface RoomLobbyProps {
  room: GameRoomDetailed;
  currentPlayerId: string;
  onToggleReady: () => void;
  onStartGame: () => void;
  onAddBot: () => void;
  onRemovePlayer: (playerId: string) => void;
  onLeave: () => void;
}

export const RoomLobby: React.FC<RoomLobbyProps> = ({
  room,
  currentPlayerId,
  onToggleReady,
  onStartGame,
  onAddBot,
  onRemovePlayer,
  onLeave,
}) => {
  const [copied, setCopied] = useState(false);
  const isHost = room.hostId === currentPlayerId;
  const me = room.players.find((p) => p.id === currentPlayerId);
  const isMeReady = me?.isReady ?? false;
  const maxPlayers = room.settings.maxPlayers || 2;
  const canStart = room.players.length >= 2 && room.players.every((p) => p.isReady || p.isBot);

  const handleCopy = () => {
    navigator.clipboard.writeText(room.code);
    setCopied(true);
    sounds.playClick();
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mx-auto max-w-2xl space-y-4">
      {/* Header Banner */}
      <div className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm relative overflow-hidden">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={onLeave}
              className="flex size-9 items-center justify-center rounded-xl border border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100 transition-colors"
              title="Leave Room"
            >
              <ArrowLeft className="size-4.5" />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-black capitalize text-[#0D1420]">{room.title}</h1>
                <span className="rounded-md bg-sky-50 px-2 py-0.5 text-[11px] font-bold text-[#1E9EF5] uppercase">
                  {room.gameType}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                Created by {room.players.find((p) => p.isHost)?.name || 'Host'} • Max {maxPlayers} Players
              </p>
            </div>
          </div>

          {/* Room Code Pill */}
          <button
            onClick={handleCopy}
            className="flex items-center gap-2 rounded-2xl border border-sky-200 bg-sky-50/80 px-3 py-2 text-xs font-bold text-[#1E9EF5] hover:bg-sky-100 transition-colors shadow-2xs"
            title="Click to copy Room Code"
          >
            <span>Code: <strong>{room.code}</strong></span>
            {copied ? <Check className="size-3.5 text-emerald-500" /> : <Copy className="size-3.5" />}
          </button>
        </div>

        {/* Room Info Highlights */}
        <div className="mt-4 grid grid-cols-3 gap-2 border-t border-slate-100 pt-4 text-center">
          <div className="rounded-xl bg-slate-50 p-2">
            <p className="text-[10px] font-bold uppercase text-slate-400">Entry Fee</p>
            <p className="text-sm font-black text-[#0D1420]">{room.settings.entryFee} coins</p>
          </div>
          <div className="rounded-xl bg-slate-50 p-2">
            <p className="text-[10px] font-bold uppercase text-slate-400">Prize Pool</p>
            <p className="text-sm font-black text-emerald-600">
              {room.settings.entryFee * room.players.length} coins
            </p>
          </div>
          <div className="rounded-xl bg-slate-50 p-2">
            <p className="text-[10px] font-bold uppercase text-slate-400">Turn Timer</p>
            <p className="text-sm font-black text-sky-600">{room.settings.turnTimeLimitSeconds}s</p>
          </div>
        </div>
      </div>

      {/* Player Slots */}
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="size-4 text-[#1E9EF5]" />
            <h2 className="text-sm font-bold text-[#0D1420]">
              Players ({room.players.length}/{maxPlayers})
            </h2>
          </div>

          {isHost && room.players.length < maxPlayers && (
            <button
              onClick={onAddBot}
              className="flex items-center gap-1.5 rounded-xl border border-sky-200 bg-sky-50 px-3 py-1.5 text-xs font-bold text-[#1E9EF5] hover:bg-sky-100 transition-colors shadow-2xs"
            >
              <Bot className="size-3.5" />
              <span>+ Add TATA AI Bot</span>
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {room.players.map((player) => {
            const isMe = player.id === currentPlayerId;
            return (
              <div
                key={player.id}
                className="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/60 p-3"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="relative">
                    <img
                      src={player.avatarUrl}
                      alt={player.name}
                      className="size-10 rounded-full object-cover ring-2 ring-white"
                    />
                    {player.isHost && (
                      <span className="absolute -top-1 -right-1 flex size-4 items-center justify-center rounded-full bg-amber-400 text-[8px] font-black text-amber-950">
                        ★
                      </span>
                    )}
                  </div>
                  <div className="min-w-0 truncate">
                    <div className="flex items-center gap-1">
                      <p className="text-xs font-bold text-[#0D1420] truncate">{player.name}</p>
                      {isMe && (
                        <span className="rounded bg-sky-100 px-1 text-[9px] font-bold text-[#1E9EF5]">
                          You
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-slate-400 font-medium">
                      {player.isBot ? 'AI Bot Player' : `@${player.username}`}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {player.isReady ? (
                    <span className="flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-[10px] font-extrabold text-emerald-700">
                      <CheckCircle className="size-3" />
                      Ready
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 rounded-full bg-slate-200/80 px-2.5 py-0.5 text-[10px] font-bold text-slate-500">
                      <Clock className="size-3" />
                      Waiting
                    </span>
                  )}

                  {isHost && !player.isHost && (
                    <button
                      onClick={() => onRemovePlayer(player.id)}
                      className="text-slate-400 hover:text-rose-500 p-1"
                      title="Kick player/bot"
                    >
                      <Trash2 className="size-3.5" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}

          {/* Empty Seats */}
          {Array.from({ length: Math.max(0, maxPlayers - room.players.length) }).map((_, i) => (
            <div
              key={i}
              className="flex items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50/30 p-4 text-center text-xs font-semibold text-slate-400"
            >
              Waiting for player to join...
            </div>
          ))}
        </div>
      </div>

      {/* Action Footer */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <button
          onClick={onToggleReady}
          className={`flex-1 flex w-full items-center justify-center gap-2 rounded-2xl py-3 text-sm font-extrabold transition-all shadow-md ${
            isMeReady
              ? 'bg-slate-200 text-slate-700 hover:bg-slate-300'
              : 'bg-emerald-500 text-white hover:bg-emerald-600'
          }`}
        >
          <CheckCircle className="size-4.5" />
          <span>{isMeReady ? 'Cancel Ready' : 'I am Ready!'}</span>
        </button>

        {isHost ? (
          <button
            onClick={onStartGame}
            disabled={!canStart}
            className={`flex-1 flex w-full items-center justify-center gap-2 rounded-2xl py-3 text-sm font-extrabold text-white transition-all shadow-md ${
              canStart
                ? 'bg-[#1E9EF5] hover:bg-sky-600 active:scale-[0.98]'
                : 'bg-slate-300 text-slate-500 cursor-not-allowed'
            }`}
          >
            <Play className="size-4.5 fill-white" />
            <span>Start Match Now</span>
          </button>
        ) : (
          <div className="flex-1 text-center py-2 text-xs font-semibold text-slate-400">
            Waiting for host to start the game...
          </div>
        )}
      </div>
    </div>
  );
};
