import React from 'react';
import { GamePlayer, GameRoomDetailed } from '../types';
import { Trophy, Award, Coins, RefreshCw, ArrowLeft, Flame, Sparkles } from 'lucide-react';
import confetti from 'canvas-confetti';

interface GameResultsModalProps {
  room: GameRoomDetailed;
  winnerId: string;
  currentPlayerId: string;
  onRematch: () => void;
  onLeave: () => void;
}

export const GameResultsModal: React.FC<GameResultsModalProps> = ({
  room,
  winnerId,
  currentPlayerId,
  onRematch,
  onLeave,
}) => {
  const winner = room.players.find((p) => p.id === winnerId);
  const isMeWinner = winnerId === currentPlayerId;
  const prizePool = room.players.length * (room.settings.entryFee || 100);
  const hasVotedRematch = room.rematchVotes.includes(currentPlayerId);

  React.useEffect(() => {
    confetti({
      particleCount: 120,
      spread: 80,
      origin: { y: 0.5 },
    });
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-xs animate-fadeIn">
      <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl text-center relative overflow-hidden">
        {/* Glow Header */}
        <div className="absolute -top-16 left-1/2 -translate-x-1/2 size-40 rounded-full bg-gradient-to-b from-amber-300/40 to-sky-400/20 blur-2xl" />

        {/* Winner Trophy Badge */}
        <div className="relative mx-auto mb-3 flex size-18 items-center justify-center rounded-2xl bg-gradient-to-tr from-amber-400 to-yellow-300 text-white shadow-lg shadow-amber-200">
          <Trophy className="size-10 fill-white drop-shadow-sm animate-bounce" />
        </div>

        <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-black uppercase tracking-wider text-amber-700">
          Match Complete
        </span>

        <h2 className="mt-2 text-2xl font-black text-[#0D1420]">
          {isMeWinner ? '🎉 You are Victorious!' : `${winner?.name || 'Winner'} Won!`}
        </h2>
        <p className="text-xs text-slate-500 font-medium">
          Congratulations! The prize pot has been disbursed to the winner.
        </p>

        {/* Prize Pot Badge */}
        <div className="my-4 flex items-center justify-center gap-2 rounded-2xl border border-emerald-200 bg-emerald-50/80 p-3 text-emerald-800">
          <Coins className="size-5 text-emerald-600" />
          <span className="text-sm font-extrabold">Prize Pool Payout:</span>
          <span className="text-lg font-black text-emerald-700">+{prizePool.toLocaleString()} Coins</span>
        </div>

        {/* Player Standings */}
        <div className="space-y-2 mb-6 text-left">
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Final Standings</p>
          {room.players.map((player, idx) => {
            const isPWinner = player.id === winnerId;
            return (
              <div
                key={player.id}
                className={`flex items-center justify-between rounded-xl p-2.5 border transition-colors ${
                  isPWinner
                    ? 'border-amber-300 bg-amber-50/60 font-bold text-[#0D1420]'
                    : 'border-slate-100 bg-slate-50 text-slate-600'
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <span className="text-xs font-black w-4 text-slate-400">#{idx + 1}</span>
                  <img
                    src={player.avatarUrl}
                    alt={player.name}
                    className="size-8 rounded-full object-cover ring-2 ring-white"
                  />
                  <div className="min-w-0 truncate">
                    <p className="text-xs font-bold truncate">{player.name}</p>
                    <p className="text-[10px] text-slate-400">
                      {player.isBot ? 'TATA AI Bot' : `@${player.username}`}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  {isPWinner ? (
                    <span className="rounded-md bg-amber-200/80 px-2 py-0.5 text-[11px] font-extrabold text-amber-900">
                      WINNER
                    </span>
                  ) : (
                    <span className="text-xs font-semibold text-slate-400">Runner-up</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Rematch & Leave Controls */}
        <div className="flex flex-col gap-2.5">
          <button
            onClick={onRematch}
            className={`flex w-full items-center justify-center gap-2 rounded-2xl py-3 text-sm font-extrabold text-white transition-all shadow-md ${
              hasVotedRematch
                ? 'bg-emerald-500 hover:bg-emerald-600'
                : 'bg-[#1E9EF5] hover:bg-sky-600 active:scale-[0.98]'
            }`}
          >
            <RefreshCw className="size-4" />
            <span>
              {hasVotedRematch
                ? `Voted Rematch (${room.rematchVotes.length}/${Math.ceil(room.players.length / 2)})`
                : 'Play Again / Rematch'}
            </span>
          </button>

          <button
            onClick={onLeave}
            className="flex w-full items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <ArrowLeft className="size-4" />
            <span>Back to Games Hub</span>
          </button>
        </div>
      </div>
    </div>
  );
};
