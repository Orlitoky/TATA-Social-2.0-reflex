import React, { useState } from 'react';
import { DominoGameState, DominoTile, GamePlayer, GameRoomDetailed } from '../types';
import { getLegalMovesForPlayer } from './dominoEngine';
import { GameHeader } from '../components/GameHeader';
import { InGameChat } from '../components/InGameChat';
import { GameResultsModal } from '../components/GameResultsModal';
import { Sparkles, RefreshCw, Trophy, Layers, ArrowRight, ArrowLeft } from 'lucide-react';

interface DominoGameProps {
  room: GameRoomDetailed;
  currentPlayerId: string;
  onPlayTile: (tileIndex: number, side: 'left' | 'right' | 'start') => void;
  onDraw: () => void;
  onPass: () => void;
  onNextRound: () => void;
  onLeave: () => void;
  onRematch: () => void;
  onSendMessage: (text: string) => void;
}

// Visual Domino Tile component with SVG pips
export const DominoTileView: React.FC<{
  tile: DominoTile;
  vertical?: boolean;
  selected?: boolean;
  playable?: boolean;
  onClick?: () => void;
  size?: 'sm' | 'md' | 'lg';
}> = ({ tile, vertical = true, selected = false, playable = false, onClick, size = 'md' }) => {
  const [top, bottom] = tile;

  const renderPips = (count: number) => {
    const dotPositions: Record<number, number[][]> = {
      0: [],
      1: [[50, 50]],
      2: [
        [25, 25],
        [75, 75],
      ],
      3: [
        [25, 25],
        [50, 50],
        [75, 75],
      ],
      4: [
        [25, 25],
        [75, 25],
        [25, 75],
        [75, 75],
      ],
      5: [
        [25, 25],
        [75, 25],
        [50, 50],
        [25, 75],
        [75, 75],
      ],
      6: [
        [25, 20],
        [75, 20],
        [25, 50],
        [75, 50],
        [25, 80],
        [75, 80],
      ],
    };

    const dots = dotPositions[count] || [];

    return (
      <svg className="size-full" viewBox="0 0 100 100">
        {dots.map(([cx, cy], i) => (
          <circle key={i} cx={cx} cy={cy} r="10" fill="#0D1420" />
        ))}
      </svg>
    );
  };

  const dimClasses = {
    sm: vertical ? 'w-8 h-16' : 'w-16 h-8',
    md: vertical ? 'w-12 h-24' : 'w-24 h-12',
    lg: vertical ? 'w-14 h-28' : 'w-28 h-14',
  }[size];

  return (
    <div
      onClick={onClick}
      className={`relative rounded-xl border-2 bg-gradient-to-b from-white to-slate-100 shadow-md transition-all select-none ${dimClasses} ${
        playable
          ? 'border-[#1E9EF5] ring-2 ring-sky-300 ring-offset-1 cursor-pointer hover:-translate-y-1.5 hover:shadow-lg'
          : 'border-slate-300'
      } ${selected ? 'border-amber-400 ring-4 ring-amber-200 -translate-y-2' : ''}`}
    >
      <div
        className={`flex size-full ${
          vertical ? 'flex-col divide-y-2 divide-slate-300' : 'flex-row divide-x-2 divide-slate-300'
        }`}
      >
        <div className="flex-1 p-1 flex items-center justify-center">{renderPips(top)}</div>
        <div className="flex-1 p-1 flex items-center justify-center">{renderPips(bottom)}</div>
      </div>
    </div>
  );
};

export const DominoGame: React.FC<DominoGameProps> = ({
  room,
  currentPlayerId,
  onPlayTile,
  onDraw,
  onPass,
  onNextRound,
  onLeave,
  onRematch,
  onSendMessage,
}) => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedTileIndex, setSelectedTileIndex] = useState<number | null>(null);

  const state = room.dominoState;
  if (!state) return null;

  const playerIds = room.players.map((p) => p.id);
  const myHand = state.playerHands[currentPlayerId] || [];
  const isMyTurn = state.currentTurnPlayerId === currentPlayerId && !state.isRoundOver;
  const legalMoves = isMyTurn ? getLegalMovesForPlayer(myHand, state.openLeft, state.openRight) : [];
  const canDraw = isMyTurn && state.boneyard.length > 0;
  const canPass = isMyTurn && legalMoves.length === 0 && state.boneyard.length === 0;

  const currentSelectedLegal =
    selectedTileIndex !== null
      ? legalMoves.find((m) => m.tileIndex === selectedTileIndex)
      : null;

  const handleTileClick = (idx: number) => {
    if (!isMyTurn) return;
    const move = legalMoves.find((m) => m.tileIndex === idx);
    if (!move) return;

    if (state.placedChain.length === 0) {
      onPlayTile(idx, 'start');
      setSelectedTileIndex(null);
    } else if (move.canPlayLeft && move.canPlayRight && state.openLeft !== state.openRight) {
      // Both ends valid and different pips: prompt player choice
      setSelectedTileIndex(idx);
    } else if (move.canPlayLeft) {
      onPlayTile(idx, 'left');
      setSelectedTileIndex(null);
    } else {
      onPlayTile(idx, 'right');
      setSelectedTileIndex(null);
    }
  };

  const currentPlayer = room.players.find((p) => p.id === currentPlayerId) || room.players[0];

  return (
    <div className="flex flex-col lg:flex-row gap-4 items-start w-full">
      <div className="flex-1 w-full space-y-4">
        {/* Game Header with Timer & Controls */}
        <GameHeader
          room={room}
          currentTurnPlayerId={state.currentTurnPlayerId}
          turnDeadline={state.turnDeadline}
          onLeave={onLeave}
          onToggleChat={() => setIsChatOpen(!isChatOpen)}
          chatUnreadCount={room.chatMessages.length}
        />

        {/* Action Status Bar */}
        <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-2.5 shadow-2xs">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-[#0D1420]">Round {state.roundNumber}</span>
            <span className="text-slate-300">•</span>
            <p className="text-xs text-slate-500 font-medium truncate">{state.lastActionSummary}</p>
          </div>
          <div className="flex items-center gap-2 text-xs font-bold">
            <span className="text-slate-400">Target:</span>
            <span className="text-[#1E9EF5]">{(room.settings as any).targetScore || 100} pts</span>
          </div>
        </div>

        {/* Center Felt Board Arena */}
        <div className="relative min-h-[360px] sm:min-h-[420px] rounded-3xl border border-emerald-800/40 bg-gradient-to-b from-[#0b3323] via-[#0d3f2c] to-[#08261a] p-4 shadow-xl flex flex-col justify-between overflow-hidden">
          {/* Subtle felt texture overlay */}
          <div className="absolute inset-0 opacity-15 pointer-events-none bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:16px_16px]" />

          {/* Top Opponents Hand Summary */}
          <div className="flex flex-wrap items-center justify-around gap-4 z-10">
            {room.players
              .filter((p) => p.id !== currentPlayerId)
              .map((opponent) => {
                const count = (state.playerHands[opponent.id] || []).length;
                const isOppTurn = state.currentTurnPlayerId === opponent.id;
                const oppScore = state.roundScores[opponent.id] || 0;

                return (
                  <div
                    key={opponent.id}
                    className={`flex items-center gap-3 rounded-2xl px-3.5 py-2 transition-all ${
                      isOppTurn
                        ? 'bg-amber-400 text-amber-950 font-bold shadow-lg ring-2 ring-white scale-105'
                        : 'bg-black/30 border border-white/10 text-white'
                    }`}
                  >
                    <img
                      src={opponent.avatarUrl}
                      alt={opponent.name}
                      className="size-8 rounded-full object-cover ring-2 ring-white/50"
                    />
                    <div>
                      <p className="text-xs font-bold leading-tight">{opponent.name}</p>
                      <p className="text-[10px] opacity-80">
                        {count} tiles • {oppScore} pts
                      </p>
                    </div>
                  </div>
                );
              })}
          </div>

          {/* Center Domino Chain Layout */}
          <div className="my-auto py-6 flex flex-col items-center justify-center z-10">
            {state.placedChain.length === 0 ? (
              <div className="text-center text-white/60 space-y-1">
                <Layers className="size-8 mx-auto text-white/40 animate-pulse" />
                <p className="text-sm font-bold">The table is open</p>
                <p className="text-xs text-white/40">
                  {isMyTurn ? 'You have the first turn! Select any tile from your hand.' : 'Waiting for opening tile...'}
                </p>
              </div>
            ) : (
              <div className="w-full flex flex-col items-center">
                {/* Open Ends Indicators */}
                <div className="flex items-center justify-between w-full max-w-lg mb-2 px-2 text-[11px] font-black text-amber-300">
                  <span className="flex items-center gap-1 rounded-full bg-black/40 px-2.5 py-1 border border-amber-300/30">
                    <ArrowLeft className="size-3" /> Left End: [{state.openLeft}]
                  </span>
                  <span className="flex items-center gap-1 rounded-full bg-black/40 px-2.5 py-1 border border-amber-300/30">
                    Right End: [{state.openRight}] <ArrowRight className="size-3" />
                  </span>
                </div>

                {/* Domino Chain Cards */}
                <div className="flex items-center gap-1.5 overflow-x-auto max-w-full p-2 scrollbar-none">
                  {state.placedChain.map((pTile) => (
                    <DominoTileView
                      key={pTile.id}
                      tile={[pTile.displayLeftVal, pTile.displayRightVal]}
                      vertical={pTile.displayLeftVal === pTile.displayRightVal}
                      size="sm"
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Branch Selector Popup if tile matches both Left and Right */}
          {currentSelectedLegal && currentSelectedLegal.canPlayLeft && currentSelectedLegal.canPlayRight && (
            <div className="z-20 mx-auto rounded-2xl bg-white p-3 shadow-2xl border border-amber-300 flex items-center gap-2 animate-bounce">
              <span className="text-xs font-bold text-[#0D1420]">Choose placement side:</span>
              <button
                onClick={() => {
                  onPlayTile(currentSelectedLegal.tileIndex, 'left');
                  setSelectedTileIndex(null);
                }}
                className="rounded-xl bg-[#1E9EF5] px-3 py-1.5 text-xs font-bold text-white hover:bg-sky-600"
              >
                ← Left [{state.openLeft}]
              </button>
              <button
                onClick={() => {
                  onPlayTile(currentSelectedLegal.tileIndex, 'right');
                  setSelectedTileIndex(null);
                }}
                className="rounded-xl bg-emerald-500 px-3 py-1.5 text-xs font-bold text-white hover:bg-emerald-600"
              >
                Right [{state.openRight}] →
              </button>
            </div>
          )}

          {/* Bottom Active Player Controls & Boneyard */}
          <div className="flex items-end justify-between gap-3 z-10 border-t border-white/10 pt-3">
            {/* Boneyard Pile */}
            <div className="flex items-center gap-2">
              <button
                onClick={onDraw}
                disabled={!canDraw}
                className={`flex items-center gap-2 rounded-2xl px-3.5 py-2 text-xs font-bold transition-all shadow-md ${
                  canDraw
                    ? 'bg-amber-400 hover:bg-amber-500 text-amber-950 active:scale-95 cursor-pointer'
                    : 'bg-white/10 text-white/40 cursor-not-allowed'
                }`}
              >
                <Layers className="size-4" />
                <span>Boneyard ({state.boneyard.length})</span>
              </button>

              {canPass && (
                <button
                  onClick={onPass}
                  className="rounded-2xl bg-rose-500 hover:bg-rose-600 text-white px-3.5 py-2 text-xs font-extrabold shadow-md active:scale-95"
                >
                  Pass Turn
                </button>
              )}
            </div>

            {/* My Score Badge */}
            <div className="rounded-xl bg-black/40 px-3 py-1 text-right text-white">
              <p className="text-[10px] text-white/60 font-semibold uppercase">My Match Score</p>
              <p className="text-sm font-black text-amber-300">
                {state.roundScores[currentPlayerId] || 0} pts
              </p>
            </div>
          </div>
        </div>

        {/* Player Hand Tray */}
        <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-[#0D1420]">
              Your Hand ({myHand.length} tiles)
            </h3>
            {isMyTurn && (
              <span className="rounded-full bg-sky-100 px-2.5 py-0.5 text-[10px] font-extrabold text-[#1E9EF5] animate-pulse">
                Your Turn to Play
              </span>
            )}
          </div>

          <div className="flex items-center gap-2.5 overflow-x-auto p-2 scrollbar-none min-h-[110px]">
            {myHand.map((tile, idx) => {
              const isPlayable = legalMoves.some((m) => m.tileIndex === idx);
              return (
                <DominoTileView
                  key={idx}
                  tile={tile}
                  playable={isPlayable}
                  selected={selectedTileIndex === idx}
                  onClick={() => handleTileClick(idx)}
                />
              );
            })}
          </div>
        </div>

        {/* Round Over Banner */}
        {state.isRoundOver && !state.matchWinnerId && (
          <div className="rounded-2xl border border-amber-300 bg-gradient-to-r from-amber-50 to-yellow-50 p-4 shadow-md text-center space-y-2">
            <h3 className="text-base font-black text-[#0D1420]">Round {state.roundNumber} Finished!</h3>
            <p className="text-xs font-medium text-slate-600">{state.roundWinReason}</p>
            <button
              onClick={onNextRound}
              className="rounded-xl bg-[#1E9EF5] hover:bg-sky-600 text-white px-5 py-2 text-xs font-extrabold shadow-sm"
            >
              Start Next Round →
            </button>
          </div>
        )}
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
      {state.matchWinnerId && (
        <GameResultsModal
          room={room}
          winnerId={state.matchWinnerId}
          currentPlayerId={currentPlayerId}
          onRematch={onRematch}
          onLeave={onLeave}
        />
      )}
    </div>
  );
};
