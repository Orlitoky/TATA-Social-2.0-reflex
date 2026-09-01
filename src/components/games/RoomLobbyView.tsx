import React, { useState } from 'react';
import { useGames } from '../../context/GamesContext';
import { GameChatTray } from './GameChatTray';
import { InviteFriendsModal } from './InviteFriendsModal';
import {
  Users,
  Copy,
  Check,
  Crown,
  Bot,
  Play,
  UserPlus,
  ArrowLeft,
  Coins,
  Clock,
  Target,
  Sparkles,
  Shield,
  Trash2,
} from 'lucide-react';

export const RoomLobbyView: React.FC = () => {
  const { currentRoom, leaveRoom, toggleReady, addBot, kickPlayer, startGame, activeDemoUser } = useGames();
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!currentRoom) return null;

  const isHost = currentRoom.hostId === activeDemoUser.id;
  const myPlayer = currentRoom.players.find((p) => p.id === activeDemoUser.id);
  const isReady = myPlayer?.isReady ?? false;
  const canStart = currentRoom.players.length >= 2;

  const handleCopyCode = () => {
    navigator.clipboard.writeText(currentRoom.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getGameLabel = (type: string) => {
    switch (type) {
      case 'domino':
        return { name: 'Domino Double-Six', icon: '🀄', color: 'from-amber-500 to-amber-600' };
      case 'ludo':
        return { name: 'Royal Ludo 4P', icon: '🎲', color: 'from-rose-500 to-rose-600' };
      case 'loto':
        return { name: 'Loto / Bingo 75-Ball', icon: '✨', color: 'from-purple-500 to-purple-600' };
      case 'faritany':
        return { name: 'Faritany Province Strategy', icon: '🗺️', color: 'from-emerald-600 to-teal-700' };
      default:
        return { name: 'TATA Game', icon: '🎮', color: 'from-sky-500 to-blue-600' };
    }
  };

  const gameInfo = getGameLabel(currentRoom.gameType);

  return (
    <div className="w-full space-y-4">
      {/* Top Banner & Room Navigation */}
      <div className="flex items-center justify-between bg-white rounded-2xl border border-slate-200 p-3 sm:p-4 shadow-xs">
        <button
          onClick={leaveRoom}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors"
        >
          <ArrowLeft className="size-3.5" />
          <span>Leave Room</span>
        </button>

        {/* Room Title & Game badge */}
        <div className="text-center">
          <div className="flex items-center justify-center gap-1.5">
            <span className="text-base">{gameInfo.icon}</span>
            <h2 className="text-sm sm:text-base font-extrabold text-[#0D1420]">{currentRoom.title}</h2>
          </div>
          <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
            {gameInfo.name} • {currentRoom.players.length}/{currentRoom.maxPlayers} Players
          </p>
        </div>

        {/* Room Code & Invite Button */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopyCode}
            title="Copy 6-character room code"
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-sky-50 border border-sky-200 text-[#1E9EF5] text-xs font-mono font-bold hover:bg-sky-100 transition-colors"
          >
            <span>{currentRoom.code}</span>
            {copied ? <Check className="size-3.5 text-emerald-600" /> : <Copy className="size-3.5" />}
          </button>

          <button
            onClick={() => setShowInviteModal(true)}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-[#1E9EF5] text-white text-xs font-bold hover:bg-sky-600 shadow-xs transition-all"
          >
            <UserPlus className="size-3.5" />
            <span className="hidden sm:inline">Invite</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Player Slots & Settings vs Chat Tray */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left 2 Cols: Player Roster & Game Settings */}
        <div className="lg:col-span-2 space-y-4">
          {/* Player Roster Card */}
          <div className="bg-white rounded-3xl border border-slate-200 p-4 sm:p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Users className="size-4.5 text-[#1E9EF5]" />
                <h3 className="text-sm font-extrabold text-[#0D1420]">Player Lineup</h3>
              </div>

              {isHost && currentRoom.players.length < currentRoom.maxPlayers && (
                <button
                  onClick={() => addBot()}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs font-bold hover:bg-amber-100 transition-colors"
                >
                  <Bot className="size-3.5 text-amber-600" />
                  <span>+ Add AI Bot</span>
                </button>
              )}
            </div>

            {/* Grid of player slots */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {Array.from({ length: currentRoom.maxPlayers }).map((_, idx) => {
                const player = currentRoom.players[idx];
                return (
                  <div
                    key={idx}
                    className={`flex items-center justify-between p-3 rounded-2xl border transition-all ${
                      player
                        ? 'border-slate-200 bg-slate-50/70'
                        : 'border-dashed border-slate-200 bg-white'
                    }`}
                  >
                    {player ? (
                      <div className="flex items-center justify-between w-full">
                        <div className="flex items-center gap-2.5">
                          <div className="relative">
                            <img
                              src={player.avatarUrl}
                              alt={player.displayName}
                              className="size-10 rounded-full object-cover ring-2 ring-[#1E9EF5]/20"
                            />
                            {player.isHost && (
                              <span className="absolute -top-1 -right-1 size-4 bg-amber-400 text-white rounded-full flex items-center justify-center shadow-xs">
                                <Crown className="size-2.5" />
                              </span>
                            )}
                          </div>
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span className="text-xs font-bold text-[#0D1420]">
                                {player.displayName}
                              </span>
                              {player.isBot && (
                                <span className="text-[9px] font-bold bg-amber-100 text-amber-700 px-1.5 py-0.2 rounded-md">
                                  BOT
                                </span>
                              )}
                            </div>
                            <span className="text-[10px] text-slate-400">@{player.username}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded-lg text-[10px] font-bold ${
                              player.isReady
                                ? 'bg-emerald-100 text-emerald-700'
                                : 'bg-slate-200 text-slate-600'
                            }`}
                          >
                            {player.isReady ? 'READY ✓' : 'WAITING'}
                          </span>

                          {isHost && !player.isHost && (
                            <button
                              onClick={() => kickPlayer(player.id)}
                              title="Kick player"
                              className="text-slate-400 hover:text-rose-500 p-1"
                            >
                              <Trash2 className="size-3.5" />
                            </button>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center w-full py-2 text-slate-400 text-xs font-medium gap-1.5">
                        <span>Slot #{idx + 1} Open</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Room Settings Pill Strip */}
            <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
              <div className="flex items-center gap-2 p-2 rounded-xl bg-sky-50/60 border border-sky-100">
                <Coins className="size-4 text-[#1E9EF5]" />
                <div>
                  <span className="text-[10px] text-slate-400 block font-medium">Prize Pool</span>
                  <span className="font-extrabold text-[#0D1420]">{currentRoom.prizePool} Coins</span>
                </div>
              </div>

              <div className="flex items-center gap-2 p-2 rounded-xl bg-purple-50/60 border border-purple-100">
                <Clock className="size-4 text-purple-600" />
                <div>
                  <span className="text-[10px] text-slate-400 block font-medium">Turn Timer</span>
                  <span className="font-extrabold text-[#0D1420]">{currentRoom.settings.turnTimeSeconds}s</span>
                </div>
              </div>

              <div className="flex items-center gap-2 p-2 rounded-xl bg-emerald-50/60 border border-emerald-100 col-span-2 sm:col-span-1">
                <Target className="size-4 text-emerald-600" />
                <div>
                  <span className="text-[10px] text-slate-400 block font-medium">Rule Goal</span>
                  <span className="font-extrabold text-[#0D1420]">
                    {currentRoom.gameType === 'domino' ? `${currentRoom.settings.targetScore} Pts` : 'Standard'}
                  </span>
                </div>
              </div>
            </div>

            {/* Action Bar (Ready & Start Match) */}
            <div className="mt-5 flex items-center justify-between gap-3 pt-3 border-t border-slate-100">
              <button
                onClick={toggleReady}
                className={`flex-1 py-3 rounded-2xl font-extrabold text-xs transition-all shadow-xs ${
                  isReady
                    ? 'bg-emerald-500 text-white hover:bg-emerald-600'
                    : 'bg-slate-800 text-white hover:bg-slate-900'
                }`}
              >
                {isReady ? '✓ I AM READY (Click to Unready)' : 'CLICK TO READY UP'}
              </button>

              {isHost && (
                <button
                  onClick={startGame}
                  disabled={!canStart}
                  className="flex-1 flex items-center justify-center gap-2 py-3 rounded-2xl bg-gradient-to-r from-sky-500 to-[#1E9EF5] text-white font-extrabold text-xs disabled:opacity-40 hover:brightness-110 shadow-md shadow-sky-200 transition-all active:scale-[0.98]"
                >
                  <Play className="size-4 fill-white" />
                  <span>START MATCH NOW</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Right 1 Col: In-Room Chat Tray */}
        <div className="lg:col-span-1">
          <GameChatTray />
        </div>
      </div>

      {showInviteModal && <InviteFriendsModal onClose={() => setShowInviteModal(false)} />}
    </div>
  );
};
