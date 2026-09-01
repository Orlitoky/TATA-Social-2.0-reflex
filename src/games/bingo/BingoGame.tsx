import React, { useState } from 'react';
import { BingoCard, BingoGameState, GamePlayer, GameRoomDetailed } from '../types';
import { BINGO_LETTERS, getLetterForNumber } from './bingoEngine';
import { GameHeader } from '../components/GameHeader';
import { InGameChat } from '../components/InGameChat';
import { GameResultsModal } from '../components/GameResultsModal';
import { Sparkles, Trophy, CheckCircle, Zap, RefreshCw, Layers } from 'lucide-react';

interface BingoGameProps {
  room: GameRoomDetailed;
  currentPlayerId: string;
  onDrawNumber: () => void;
  onDaub: (cardId: string, row: number, col: number) => void;
  onLeave: () => void;
  onRematch: () => void;
  onSendMessage: (text: string) => void;
}

export const BingoGame: React.FC<BingoGameProps> = ({
  room,
  currentPlayerId,
  onDrawNumber,
  onDaub,
  onLeave,
  onRematch,
  onSendMessage,
}) => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  const state = room.bingoState;
  if (!state) return null;

  const myCards = state.cards.filter((c) => c.playerId === currentPlayerId);
  const currentPlayer = room.players.find((p) => p.id === currentPlayerId) || room.players[0];
  const lastDrawn = state.currentDrawnNumber;
  const lastLetter = lastDrawn ? getLetterForNumber(lastDrawn) : null;

  return (
    <div className="flex flex-col lg:flex-row gap-4 items-start w-full">
      <div className="flex-1 w-full space-y-4">
        {/* Game Header with Timer & Controls */}
        <GameHeader
          room={room}
          turnDeadline={state.turnDeadline}
          onLeave={onLeave}
          onToggleChat={() => setIsChatOpen(!isChatOpen)}
          chatUnreadCount={room.chatMessages.length}
        />

        {/* Action Status Bar */}
        <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-2.5 shadow-2xs">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-[#0D1420]">LOTO / BINGO 75</span>
            <span className="text-slate-300">•</span>
            <p className="text-xs text-slate-500 font-medium truncate">{state.lastActionSummary}</p>
          </div>
          <div className="flex items-center gap-3 text-xs font-bold">
            <span className="text-slate-400">Drawn:</span>
            <span className="text-[#1E9EF5] font-black">{state.drawnNumbers.length}/75</span>
          </div>
        </div>

        {/* Top Ball Hopper & Live Caller Arena */}
        <div className="rounded-3xl border border-slate-200 bg-gradient-to-br from-slate-900 via-sky-950 to-[#0D1420] p-6 text-white shadow-xl flex flex-col sm:flex-row items-center justify-between gap-6 relative overflow-hidden">
          <div className="absolute -top-12 -left-12 size-40 rounded-full bg-sky-500/20 blur-3xl" />
          <div className="absolute -bottom-12 -right-12 size-40 rounded-full bg-cyan-500/20 blur-3xl" />

          {/* Large Live Ball Display */}
          <div className="flex items-center gap-4 z-10">
            <div className="relative flex size-24 items-center justify-center rounded-full bg-gradient-to-tr from-amber-400 via-yellow-300 to-amber-200 text-[#0D1420] shadow-2xl shadow-amber-400/40 border-4 border-white/80 animate-pulse">
              <div className="text-center">
                <p className="text-xs font-black tracking-widest text-amber-900 leading-none">
                  {lastLetter || 'TATA'}
                </p>
                <p className="text-3xl font-black leading-none mt-1">
                  {lastDrawn !== null ? lastDrawn : '--'}
                </p>
              </div>
            </div>

            <div>
              <span className="rounded-full bg-sky-500/30 border border-sky-400/40 px-2.5 py-0.5 text-[10px] font-extrabold text-cyan-300 uppercase">
                Active Draw
              </span>
              <h2 className="text-xl font-black mt-1">
                {lastDrawn ? `${lastLetter}-${lastDrawn}` : 'Drawing First Ball...'}
              </h2>
              <p className="text-xs text-slate-300 font-medium">
                Line Prize: <strong className="text-amber-300">{state.linePrize} coins</strong> • Full
                Bingo:{' '}
                <strong className="text-emerald-400">{state.bingoPrize} coins</strong>
              </p>
            </div>
          </div>

          {/* Quick Draw Trigger Button */}
          <div className="z-10 flex flex-col sm:flex-row items-center gap-2">
            <button
              onClick={onDrawNumber}
              className="flex items-center gap-2 rounded-2xl bg-[#1E9EF5] hover:bg-sky-500 text-white px-5 py-3 text-xs font-black shadow-lg shadow-sky-500/30 transition-all active:scale-95"
            >
              <Zap className="size-4 fill-white" />
              <span>Draw Next Ball</span>
            </button>
          </div>
        </div>

        {/* Master Drawn Balls Board (Recent 15) */}
        <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-[#0D1420]">Recent Drawn Balls</h3>
            <span className="text-[11px] text-slate-400 font-medium">
              {state.drawnNumbers.length} total numbers drawn
            </span>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto p-1 scrollbar-none min-h-[44px]">
            {state.drawnNumbers.slice(-12).reverse().map((num) => {
              const letter = getLetterForNumber(num);
              return (
                <div
                  key={num}
                  className="flex size-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-tr from-sky-500 to-[#1E9EF5] text-white shadow-xs font-black text-xs"
                >
                  <div className="text-center leading-none">
                    <span className="text-[9px] opacity-80">{letter}</span>
                    <span className="block text-xs">{num}</span>
                  </div>
                </div>
              );
            })}
            {state.drawnNumbers.length === 0 && (
              <p className="text-xs text-slate-400 italic">No balls drawn yet.</p>
            )}
          </div>
        </div>

        {/* Player Bingo Cards */}
        <div className="space-y-4">
          <h3 className="text-sm font-black text-[#0D1420]">Your Bingo Cards ({myCards.length})</h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {myCards.map((card, cardIdx) => (
              <div
                key={card.id}
                className="rounded-3xl border-2 border-slate-200 bg-white p-4 shadow-md space-y-3 relative overflow-hidden"
              >
                {/* Card Title & Status */}
                <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                  <span className="text-xs font-black text-[#0D1420]">Card #{cardIdx + 1}</span>
                  {card.hasBingo ? (
                    <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-black text-emerald-800 animate-bounce">
                      🎉 BINGO COMPLETED!
                    </span>
                  ) : card.hasCompletedLine ? (
                    <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-black text-amber-800">
                      ★ LINE COMPLETED
                    </span>
                  ) : (
                    <span className="text-[10px] font-bold text-slate-400">Auto-Daub Active</span>
                  )}
                </div>

                {/* B-I-N-G-O 5x5 Grid */}
                <div className="grid grid-cols-5 gap-1.5 text-center">
                  {/* Column Headers */}
                  {BINGO_LETTERS.map((letter) => (
                    <div
                      key={letter}
                      className="rounded-xl bg-[#1E9EF5] py-1 text-xs font-black text-white shadow-2xs"
                    >
                      {letter}
                    </div>
                  ))}

                  {/* 5 Rows */}
                  {card.grid.map((row, rIdx) =>
                    row.map((cellNum, cIdx) => {
                      const isMarked = card.marked[rIdx][cIdx];
                      const isFree = cellNum === null;
                      const isRecentlyDrawn = cellNum === lastDrawn;

                      return (
                        <button
                          key={`${rIdx}_${cIdx}`}
                          onClick={() => onDaub(card.id, rIdx, cIdx)}
                          className={`aspect-square rounded-xl border flex flex-col items-center justify-center font-black text-xs transition-all ${
                            isMarked
                              ? 'bg-gradient-to-tr from-amber-400 to-yellow-300 border-amber-500 text-amber-950 shadow-xs scale-95 ring-2 ring-amber-200'
                              : 'bg-slate-50 border-slate-200 text-[#0D1420] hover:bg-sky-50 hover:border-sky-300'
                          } ${isRecentlyDrawn ? 'ring-4 ring-sky-400 animate-pulse' : ''}`}
                        >
                          {isFree ? (
                            <span className="text-[10px] font-black text-amber-900">FREE</span>
                          ) : (
                            <span>{cellNum}</span>
                          )}
                          {isMarked && <span className="text-[8px] leading-none mt-0.5">✓</span>}
                        </button>
                      );
                    })
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Side Chat Drawer */}
      {isChatOpen && (
        <div className="w-full lg:w-80 shrink-0">
          <InGameChat
            messages={room.chatMessages}
            currentPlayer={currentPlayer}
            onSendMessage={onSendMessage}
            onClose={() => setIsChatOpen(false)}
          />
        </div>
      )}

      {/* Match Completed Results Modal */}
      {state.bingoWinnerId && (
        <GameResultsModal
          room={room}
          winnerId={state.bingoWinnerId}
          currentPlayerId={currentPlayerId}
          onRematch={onRematch}
          onLeave={onLeave}
        />
      )}
    </div>
  );
};
